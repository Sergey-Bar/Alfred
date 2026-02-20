"""
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Alert deduplication (T074) and escalation ladder
             (T075). Redis-backed dedup window prevents the
             same alert from firing twice within N minutes.
             Escalation ladder routes alerts to progressively
             wider audiences based on severity threshold.
Root Cause:  Sprint tasks T074-T075 — Notification governance.
Context:     Wraps NotificationManager to add dedup + escalation
             before fanning out to providers.
Suitability: L2 — Redis dedup + configurable escalation chain.
──────────────────────────────────────────────────────────────

Alfred Alert Deduplication & Escalation Engine
Prevents alert fatigue and routes critical events to the right people.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .base import EventType, NotificationEvent

logger = logging.getLogger(__name__)


class AlertDeduplicator:
    """
    Redis-backed alert deduplication.

    Prevents the same alert from firing more than once within
    a configurable window (default: 15 minutes). The dedup key
    is a hash of (event_type, user_id, team_id, severity).

    Falls back to in-memory dict if Redis is unavailable.
    """

    def __init__(
        self,
        redis_client: Optional[Any] = None,
        default_window_seconds: int = 900,  # 15 minutes
        window_overrides: Optional[Dict[EventType, int]] = None,
        key_prefix: str = "alfred:alert:dedup:",
    ):
        """
        Args:
            redis_client:           Redis async client (aioredis / redis.asyncio).
            default_window_seconds: Default dedup window in seconds.
            window_overrides:       Per-event-type window overrides.
            key_prefix:             Redis key prefix.
        """
        self._redis = redis_client
        self._default_window = default_window_seconds
        self._overrides = window_overrides or {}
        self._prefix = key_prefix
        # Fallback in-memory store: key → expiry timestamp
        self._memory_store: Dict[str, float] = {}

    def _dedup_key(self, event: NotificationEvent) -> str:
        """Generate a dedup key from event dimensions."""
        raw = f"{event.event_type.value}:{event.user_id or ''}:{event.team_id or ''}:{event.severity}"
        # Include significant data keys (e.g., wallet_id, threshold)
        for k in sorted(event.data.keys()):
            if k in ("wallet_id", "threshold", "provider", "rule_id"):
                raw += f":{k}={event.data[k]}"
        digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
        return f"{self._prefix}{digest}"

    def _window_for(self, event_type: EventType) -> int:
        """Get the dedup window for a given event type."""
        return self._overrides.get(event_type, self._default_window)

    async def is_duplicate(self, event: NotificationEvent) -> bool:
        """
        Check if an identical alert was already fired within the dedup window.

        Returns True if this is a duplicate (should be suppressed).
        """
        key = self._dedup_key(event)
        window = self._window_for(event.event_type)

        if self._redis:
            try:
                exists = await self._redis.exists(key)
                if exists:
                    logger.debug(f"alert_dedup: suppressing duplicate {key}")
                    return True
                # Mark as seen
                await self._redis.setex(key, window, "1")
                return False
            except Exception as e:
                logger.warning(f"alert_dedup: Redis error ({e}), falling back to memory")

        # In-memory fallback
        now = time.time()
        # Clean expired entries (lazy)
        expired = [k for k, exp in self._memory_store.items() if exp < now]
        for k in expired:
            del self._memory_store[k]

        if key in self._memory_store:
            logger.debug(f"alert_dedup: suppressing duplicate {key} (memory)")
            return True

        self._memory_store[key] = now + window
        return False

    async def clear(self, event: Optional[NotificationEvent] = None) -> None:
        """Clear dedup state, optionally for a specific event."""
        if event:
            key = self._dedup_key(event)
            if self._redis:
                try:
                    await self._redis.delete(key)
                except Exception:
                    pass
            self._memory_store.pop(key, None)
        else:
            # Full clear
            if self._redis:
                try:
                    # SCAN and delete matching keys
                    cursor = 0
                    while True:
                        cursor, keys = await self._redis.scan(cursor, match=f"{self._prefix}*", count=100)
                        if keys:
                            await self._redis.delete(*keys)
                        if cursor == 0:
                            break
                except Exception:
                    pass
            self._memory_store.clear()


class EscalationLevel(str, Enum):
    """Escalation audience tiers."""
    TEAM_LEAD = "team_lead"      # First line — team lead
    FINOPS = "finops"            # Finance/Ops team
    MANAGEMENT = "management"    # Department management
    ALL_STAKEHOLDERS = "all"     # Everyone — critical only


@dataclass
class EscalationTarget:
    """A single escalation target."""
    level: EscalationLevel
    emails: List[str] = field(default_factory=list)
    slack_channels: List[str] = field(default_factory=list)
    webhook_urls: List[str] = field(default_factory=list)


@dataclass
class EscalationRule:
    """
    Maps a threshold crossing to an escalation level.

    Example:
        EscalationRule(threshold_pct=80, level=EscalationLevel.TEAM_LEAD)
        EscalationRule(threshold_pct=95, level=EscalationLevel.FINOPS)
        EscalationRule(threshold_pct=100, level=EscalationLevel.ALL_STAKEHOLDERS)
    """
    threshold_pct: float            # Budget % that triggers this level
    level: EscalationLevel
    event_types: Set[EventType] = field(default_factory=lambda: {
        EventType.QUOTA_WARNING,
        EventType.QUOTA_EXCEEDED,
        EventType.TEAM_POOL_WARNING,
        EventType.TEAM_POOL_DEPLETED,
    })


# Default escalation ladder per the PRD
DEFAULT_ESCALATION_RULES: List[EscalationRule] = [
    EscalationRule(threshold_pct=80, level=EscalationLevel.TEAM_LEAD),
    EscalationRule(threshold_pct=90, level=EscalationLevel.FINOPS),
    EscalationRule(threshold_pct=95, level=EscalationLevel.FINOPS),
    EscalationRule(threshold_pct=100, level=EscalationLevel.ALL_STAKEHOLDERS),
]


class EscalationLadder:
    """
    Determines which audience should receive an alert based on
    threshold percentage and configurable escalation rules.

    Default ladder:
      80% → team lead
      90% → team lead + FinOps
      95% → FinOps
      100% → all stakeholders
    """

    def __init__(
        self,
        rules: Optional[List[EscalationRule]] = None,
        targets: Optional[Dict[EscalationLevel, EscalationTarget]] = None,
    ):
        self._rules = sorted(
            rules or DEFAULT_ESCALATION_RULES,
            key=lambda r: r.threshold_pct,
        )
        self._targets = targets or {}

    def add_target(self, target: EscalationTarget) -> None:
        """Register an escalation target."""
        self._targets[target.level] = target

    def get_target(self, level: EscalationLevel) -> Optional[EscalationTarget]:
        """Get a target by level."""
        return self._targets.get(level)

    def determine_levels(
        self,
        event: NotificationEvent,
        threshold_pct: Optional[float] = None,
    ) -> List[EscalationLevel]:
        """
        Determine which escalation levels should be notified.

        Args:
            event:         The notification event.
            threshold_pct: Current budget usage %. If in event.data
                           as 'threshold' or 'usage_pct', it's used.
        Returns:
            List of escalation levels to notify, from lowest to highest.
        """
        pct = threshold_pct
        if pct is None:
            pct = event.data.get("threshold") or event.data.get("usage_pct")
        if pct is None:
            # For non-threshold events, use severity mapping
            severity_levels = {
                "info": [],
                "warning": [EscalationLevel.TEAM_LEAD],
                "error": [EscalationLevel.TEAM_LEAD, EscalationLevel.FINOPS],
                "critical": [
                    EscalationLevel.TEAM_LEAD,
                    EscalationLevel.FINOPS,
                    EscalationLevel.ALL_STAKEHOLDERS,
                ],
            }
            return severity_levels.get(event.severity, [])

        # Walk the ladder
        levels: List[EscalationLevel] = []
        for rule in self._rules:
            if event.event_type not in rule.event_types:
                continue
            if float(pct) >= rule.threshold_pct:
                if rule.level not in levels:
                    levels.append(rule.level)

        return levels

    def get_targets_for_event(
        self,
        event: NotificationEvent,
        threshold_pct: Optional[float] = None,
    ) -> List[EscalationTarget]:
        """Get all escalation targets that should receive this event."""
        levels = self.determine_levels(event, threshold_pct)
        targets = []
        for level in levels:
            tgt = self._targets.get(level)
            if tgt:
                targets.append(tgt)
        return targets

    def get_all_emails(
        self,
        event: NotificationEvent,
        threshold_pct: Optional[float] = None,
    ) -> List[str]:
        """Collect all unique email addresses across matched escalation levels."""
        targets = self.get_targets_for_event(event, threshold_pct)
        emails: List[str] = []
        seen: Set[str] = set()
        for t in targets:
            for email in t.emails:
                if email not in seen:
                    emails.append(email)
                    seen.add(email)
        return emails

    def get_all_slack_channels(
        self,
        event: NotificationEvent,
        threshold_pct: Optional[float] = None,
    ) -> List[str]:
        """Collect all unique Slack channels across matched escalation levels."""
        targets = self.get_targets_for_event(event, threshold_pct)
        channels: List[str] = []
        seen: Set[str] = set()
        for t in targets:
            for ch in t.slack_channels:
                if ch not in seen:
                    channels.append(ch)
                    seen.add(ch)
        return channels
