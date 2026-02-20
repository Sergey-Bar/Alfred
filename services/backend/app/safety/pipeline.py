"""
Unified Safety Pipeline

Orchestrates multiple safety checks:
1. PII Detection (SSNs, credit cards, emails, etc.)
2. Secret Scanning (API keys, passwords, tokens)
3. Prompt Injection Detection (jailbreaks, role manipulation)
4. Custom Blocklist Checks

Provides configurable enforcement modes:
- BLOCK: Reject the request
- REDACT: Automatically redact violations
- WARN: Log violation but allow request
- ALLOW: No enforcement (monitoring only)
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .pii_detector import PIIDetector, PIIType
from .prompt_injection import (
    InjectionType,
    PromptInjectionDetector,
    SeverityLevel,
)
from .secret_scanner import SecretScanner, SecretType

logger = logging.getLogger(__name__)


class EnforcementMode(str, Enum):
    """Enforcement mode for safety violations."""

    BLOCK = "block"  # Reject request
    REDACT = "redact"  # Auto-redact and continue
    WARN = "warn"  # Log warning but allow
    ALLOW = "allow"  # Monitor only, no enforcement
    CUSTOM = "custom"  # Use custom handler


class ViolationCategory(str, Enum):
    """High-level violation categories."""

    PII = "pii"
    SECRET = "secret"
    INJECTION = "injection"
    BLOCKLIST = "blocklist"


@dataclass
class SafetyViolation:
    """Unified violation type for all safety checks."""

    category: ViolationCategory
    type: str  # Specific type (SSN, OPENAI_API_KEY, IGNORE_INSTRUCTIONS, etc.)
    severity: str  # low, medium, high, critical
    confidence: float
    description: str
    start: int
    end: int
    matched_text: str = "[REDACTED]"
    masked_value: str = "[REDACTED]"
    context: str = ""
    provider: str = ""

    def to_dict(self) -> Dict:
        return {
            "category": self.category.value,
            "type": self.type,
            "severity": self.severity,
            "confidence": self.confidence,
            "description": self.description,
            "start": self.start,
            "end": self.end,
            "masked_value": self.masked_value,
            "provider": self.provider,
        }


# Severity base points (before confidence weighting)
_SEVERITY_WEIGHTS: Dict[str, float] = {
    "critical": 40.0,
    "high": 25.0,
    "medium": 12.0,
    "low": 5.0,
}

# Category multipliers — secrets and injections are more dangerous
_CATEGORY_MULTIPLIERS: Dict[str, float] = {
    ViolationCategory.SECRET.value: 1.5,
    ViolationCategory.INJECTION.value: 1.3,
    ViolationCategory.PII.value: 1.0,
    ViolationCategory.BLOCKLIST.value: 0.8,
}


def compute_risk_score(violations: List[SafetyViolation]) -> float:
    """
    T127: Compute a composite risk score (0-100) from safety violations.

    Algorithm:
    1. Each violation contributes: severity_weight × confidence × category_multiplier
    2. Contributions are summed with diminishing returns (sqrt aggregation)
       to avoid a single category pushing the score to 100.
    3. Final score is clamped to [0, 100].

    Returns:
        Float 0-100. 0 = clean, 100 = maximum risk.
        Recommended thresholds:
          0-20  = low risk
          21-50 = moderate risk
          51-80 = high risk
          81+   = critical risk
    """
    if not violations:
        return 0.0

    import math

    raw_sum = 0.0
    for v in violations:
        base = _SEVERITY_WEIGHTS.get(v.severity, 5.0)
        confidence = max(0.0, min(1.0, v.confidence))
        category_mult = _CATEGORY_MULTIPLIERS.get(
            v.category.value if isinstance(v.category, ViolationCategory) else v.category,
            1.0,
        )
        raw_sum += base * confidence * category_mult

    # Diminishing-returns aggregation: score = 100 × (1 - e^(-raw_sum / 60))
    # This maps raw_sum ~15 → ~22, ~40 → ~49, ~80 → ~74, ~150 → ~92
    score = 100.0 * (1.0 - math.exp(-raw_sum / 60.0))
    return round(min(100.0, max(0.0, score)), 1)


def risk_label(score: float) -> str:
    """Human-readable risk label from a 0-100 score."""
    if score <= 20:
        return "low"
    if score <= 50:
        return "moderate"
    if score <= 80:
        return "high"
    return "critical"


@dataclass
class SafetyCheckResult:
    """Result of a safety pipeline scan."""

    allowed: bool
    violations: List[SafetyViolation] = field(default_factory=list)
    redacted_text: Optional[str] = None
    enforcement_mode: EnforcementMode = EnforcementMode.ALLOW
    message: str = ""
    check_duration_ms: float = 0.0

    @property
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0

    @property
    def critical_violations(self) -> List[SafetyViolation]:
        """Get only critical severity violations."""
        return [v for v in self.violations if v.severity == "critical"]

    @property
    def high_violations(self) -> List[SafetyViolation]:
        """Get high or critical severity violations."""
        return [v for v in self.violations if v.severity in ("high", "critical")]

    @property
    def risk_score(self) -> float:
        """T127: Composite risk score 0-100."""
        return compute_risk_score(self.violations)

    @property
    def risk_level(self) -> str:
        """T127: Human-readable risk label (low/moderate/high/critical)."""
        return risk_label(self.risk_score)

    def to_dict(self) -> Dict:
        return {
            "allowed": self.allowed,
            "violations": [v.to_dict() for v in self.violations],
            "enforcement_mode": self.enforcement_mode.value,
            "message": self.message,
            "check_duration_ms": self.check_duration_ms,
            "violation_count": len(self.violations),
            "critical_count": len(self.critical_violations),
            "high_count": len(self.high_violations),
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
        }


@dataclass
class SafetyPolicy:
    """Safety policy configuration for an organization/user."""

    # PII settings
    pii_enabled: bool = True
    pii_enforcement: EnforcementMode = EnforcementMode.BLOCK
    pii_types: Optional[List[PIIType]] = None  # None = all types
    pii_allow_redaction: bool = True

    # Secret settings
    secret_enabled: bool = True
    secret_enforcement: EnforcementMode = EnforcementMode.BLOCK
    secret_types: Optional[List[SecretType]] = None  # None = all types
    secret_check_entropy: bool = True
    secret_entropy_threshold: float = 4.5

    # Injection settings
    injection_enabled: bool = True
    injection_enforcement: EnforcementMode = EnforcementMode.BLOCK
    injection_types: Optional[List[InjectionType]] = None  # None = all types
    injection_min_severity: SeverityLevel = SeverityLevel.HIGH
    injection_block_threshold: SeverityLevel = SeverityLevel.HIGH

    # Custom blocklist
    blocklist_enabled: bool = True
    blocklist_patterns: List[str] = field(default_factory=list)
    blocklist_enforcement: EnforcementMode = EnforcementMode.WARN

    # Global settings
    log_violations: bool = True
    notify_on_critical: bool = True
    strict_mode: bool = False  # If True, any violation blocks request
    allow_user_override: bool = False  # If True, user can acknowledge and proceed

    @classmethod
    def default(cls) -> "SafetyPolicy":
        """Get default safety policy for new organizations."""
        return cls()

    @classmethod
    def permissive(cls) -> "SafetyPolicy":
        """Get permissive policy (warn only)."""
        return cls(
            pii_enforcement=EnforcementMode.WARN,
            secret_enforcement=EnforcementMode.WARN,
            injection_enforcement=EnforcementMode.WARN,
            blocklist_enforcement=EnforcementMode.WARN,
            strict_mode=False,
        )

    @classmethod
    def strict(cls) -> "SafetyPolicy":
        """Get strict policy (block everything)."""
        return cls(
            pii_enforcement=EnforcementMode.BLOCK,
            secret_enforcement=EnforcementMode.BLOCK,
            injection_enforcement=EnforcementMode.BLOCK,
            injection_min_severity=SeverityLevel.LOW,
            injection_block_threshold=SeverityLevel.MEDIUM,
            blocklist_enforcement=EnforcementMode.BLOCK,
            strict_mode=True,
            allow_user_override=False,
        )


class SafetyPipeline:
    """
    Unified Safety Pipeline.

    Orchestrates multiple safety checks on prompt text before sending to LLM.
    Configurable enforcement modes per check type.

    Example:
        policy = SafetyPolicy.default()
        pipeline = SafetyPipeline(policy)

        result = await pipeline.check("My SSN is 123-45-6789")
        if not result.allowed:
            raise SecurityException(result.message)
    """

    def __init__(
        self,
        policy: Optional[SafetyPolicy] = None,
        pii_detector: Optional[PIIDetector] = None,
        secret_scanner: Optional[SecretScanner] = None,
        injection_detector: Optional[PromptInjectionDetector] = None,
        alert_callback: Optional[Callable[[SafetyCheckResult, Optional[str], Optional[str]], None]] = None,
        latency_budget_ms: float = 10.0,
    ):
        """
        Initialize Safety Pipeline.

        Args:
            policy: Safety policy configuration
            pii_detector: Custom PII detector instance
            secret_scanner: Custom secret scanner instance
            injection_detector: Custom injection detector instance
            alert_callback: (T130) Async callback fired on critical violations —
                            signature: callback(result, user_id, org_id)
            latency_budget_ms: (T131) Max allowed pipeline latency. Logs WARN if exceeded.
        """
        self.policy = policy or SafetyPolicy.default()
        self._alert_callback = alert_callback
        self._latency_budget_ms = latency_budget_ms
        self._latency_exceeded_count = 0
        self._total_checks = 0

        # Initialize detectors with policy settings
        self.pii_detector = pii_detector or PIIDetector(
            enabled_types=self.policy.pii_types,
            use_presidio=False,  # Optional, requires pip install
        )

        self.secret_scanner = secret_scanner or SecretScanner(
            enabled_types=self.policy.secret_types,
            check_entropy=self.policy.secret_check_entropy,
            entropy_threshold=self.policy.secret_entropy_threshold,
        )

        self.injection_detector = injection_detector or PromptInjectionDetector(
            enabled_types=self.policy.injection_types,
            min_severity=self.policy.injection_min_severity,
        )

    async def check(
        self,
        text: str,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        allow_redaction: bool = True,
    ) -> SafetyCheckResult:
        """
        Run all safety checks on text.

        Args:
            text: The text to check
            user_id: Optional user ID for logging
            org_id: Optional organization ID for policy lookup
            allow_redaction: Whether to allow automatic redaction

        Returns:
            SafetyCheckResult with violations and enforcement decision
        """
        start_time = asyncio.get_event_loop().time()
        violations: List[SafetyViolation] = []

        # Run checks in parallel for performance
        pii_task = asyncio.create_task(self._check_pii(text))
        secret_task = asyncio.create_task(self._check_secrets(text))
        injection_task = asyncio.create_task(self._check_injection(text))
        blocklist_task = asyncio.create_task(self._check_blocklist(text))

        # Gather results
        pii_violations = await pii_task
        secret_violations = await secret_task
        injection_violations = await injection_task
        blocklist_violations = await blocklist_task

        violations.extend(pii_violations)
        violations.extend(secret_violations)
        violations.extend(injection_violations)
        violations.extend(blocklist_violations)

        # Calculate duration
        duration_ms = (asyncio.get_event_loop().time() - start_time) * 1000

        # Determine enforcement action
        result = self._enforce_policy(
            text=text, violations=violations, allow_redaction=allow_redaction
        )
        result.check_duration_ms = duration_ms

        # Log violations if enabled
        if self.policy.log_violations and violations:
            self._log_violations(violations, user_id, org_id, result)

        # T130: Fire alert callback on critical violations
        if self._alert_callback and result.critical_violations:
            try:
                self._alert_callback(result, user_id, org_id)
            except Exception as e:
                logger.error(f"Security alert callback failed: {e}")

        # T131: Enforce latency budget
        self._total_checks += 1
        if duration_ms > self._latency_budget_ms:
            self._latency_exceeded_count += 1
            logger.warning(
                f"Safety pipeline latency budget exceeded: "
                f"{duration_ms:.1f}ms > {self._latency_budget_ms}ms "
                f"(exceeded {self._latency_exceeded_count}/{self._total_checks} checks)"
            )

        return result

    async def _check_pii(self, text: str) -> List[SafetyViolation]:
        """Check for PII violations."""
        if not self.policy.pii_enabled:
            return []

        violations = []
        try:
            pii_violations = self.pii_detector.scan(text)
            for pii_v in pii_violations:
                violations.append(
                    SafetyViolation(
                        category=ViolationCategory.PII,
                        type=pii_v.pii_type.value,
                        severity="high",  # PII is always high severity
                        confidence=pii_v.confidence,
                        description=f"PII detected: {pii_v.pii_type.value}",
                        start=pii_v.start,
                        end=pii_v.end,
                        matched_text=pii_v.value[:10] + "...",  # Truncate
                        masked_value=pii_v.masked_value,
                        context=pii_v.context,
                    )
                )
        except Exception as e:
            logger.error(f"PII detection failed: {e}", exc_info=True)

        return violations

    async def _check_secrets(self, text: str) -> List[SafetyViolation]:
        """Check for secret violations."""
        if not self.policy.secret_enabled:
            return []

        violations = []
        try:
            secret_violations = self.secret_scanner.scan(text)
            for secret_v in secret_violations:
                violations.append(
                    SafetyViolation(
                        category=ViolationCategory.SECRET,
                        type=secret_v.secret_type.value,
                        severity="critical",  # Secrets are always critical
                        confidence=secret_v.confidence,
                        description=f"Secret detected: {secret_v.secret_type.value}",
                        start=secret_v.start,
                        end=secret_v.end,
                        matched_text=secret_v.value[:10] + "...",
                        masked_value=secret_v.masked_value,
                        context=secret_v.context,
                        provider=secret_v.provider,
                    )
                )
        except Exception as e:
            logger.error(f"Secret scanning failed: {e}", exc_info=True)

        return violations

    async def _check_injection(self, text: str) -> List[SafetyViolation]:
        """Check for prompt injection violations."""
        if not self.policy.injection_enabled:
            return []

        violations = []
        try:
            injection_violations = self.injection_detector.scan(text)
            for inj_v in injection_violations:
                violations.append(
                    SafetyViolation(
                        category=ViolationCategory.INJECTION,
                        type=inj_v.injection_type.value,
                        severity=inj_v.severity.value,
                        confidence=inj_v.confidence,
                        description=inj_v.description,
                        start=inj_v.start,
                        end=inj_v.end,
                        matched_text=inj_v.matched_text[:50],
                        masked_value="[INJECTION_ATTEMPT]",
                        context=inj_v.context,
                    )
                )
        except Exception as e:
            logger.error(f"Injection detection failed: {e}", exc_info=True)

        return violations

    async def _check_blocklist(self, text: str) -> List[SafetyViolation]:
        """Check for custom blocklist violations."""
        if not self.policy.blocklist_enabled or not self.policy.blocklist_patterns:
            return []

        violations = []
        import re

        for pattern in self.policy.blocklist_patterns:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
                for match in regex.finditer(text):
                    violations.append(
                        SafetyViolation(
                            category=ViolationCategory.BLOCKLIST,
                            type="custom_blocklist",
                            severity="medium",
                            confidence=1.0,
                            description=f"Blocked by custom policy: {pattern[:30]}",
                            start=match.start(),
                            end=match.end(),
                            matched_text=match.group()[:50],
                            masked_value="[BLOCKED]",
                        )
                    )
            except re.error as e:
                logger.warning(f"Invalid blocklist pattern '{pattern}': {e}")

        return violations

    def _enforce_policy(
        self, text: str, violations: List[SafetyViolation], allow_redaction: bool
    ) -> SafetyCheckResult:
        """
        Determine enforcement action based on policy and violations.

        Returns:
            SafetyCheckResult with enforcement decision
        """
        if not violations:
            return SafetyCheckResult(
                allowed=True,
                enforcement_mode=EnforcementMode.ALLOW,
                message="No safety violations detected",
            )

        # In strict mode, any violation blocks
        if self.policy.strict_mode:
            return SafetyCheckResult(
                allowed=False,
                violations=violations,
                enforcement_mode=EnforcementMode.BLOCK,
                message=f"Request blocked: {len(violations)} safety violation(s) detected (strict mode)",
            )

        # Check enforcement mode per category
        should_block = False
        should_redact = False
        blocked_categories: Set[str] = set()

        for violation in violations:
            enforcement = self._get_enforcement_mode(violation.category)

            if enforcement == EnforcementMode.BLOCK:
                should_block = True
                blocked_categories.add(violation.category.value)
            elif enforcement == EnforcementMode.REDACT and allow_redaction:
                should_redact = True

        # BLOCK takes precedence over REDACT
        if should_block:
            categories_str = ", ".join(blocked_categories)
            return SafetyCheckResult(
                allowed=False,
                violations=violations,
                enforcement_mode=EnforcementMode.BLOCK,
                message=f"Request blocked due to {categories_str} violations",
            )

        # Try redaction if enabled
        if should_redact:
            try:
                redacted = self._redact_violations(text, violations)
                return SafetyCheckResult(
                    allowed=True,
                    violations=violations,
                    redacted_text=redacted,
                    enforcement_mode=EnforcementMode.REDACT,
                    message=f"Request allowed with {len(violations)} redaction(s)",
                )
            except Exception as e:
                logger.error(f"Redaction failed: {e}")
                return SafetyCheckResult(
                    allowed=False,
                    violations=violations,
                    enforcement_mode=EnforcementMode.BLOCK,
                    message="Redaction failed, blocking request for safety",
                )

        # Otherwise just warn
        return SafetyCheckResult(
            allowed=True,
            violations=violations,
            enforcement_mode=EnforcementMode.WARN,
            message=f"{len(violations)} safety warning(s) - request allowed by policy",
        )

    def _get_enforcement_mode(self, category: ViolationCategory) -> EnforcementMode:
        """Get enforcement mode for a violation category."""
        if category == ViolationCategory.PII:
            return self.policy.pii_enforcement
        elif category == ViolationCategory.SECRET:
            return self.policy.secret_enforcement
        elif category == ViolationCategory.INJECTION:
            return self.policy.injection_enforcement
        elif category == ViolationCategory.BLOCKLIST:
            return self.policy.blocklist_enforcement
        return EnforcementMode.WARN

    def _redact_violations(self, text: str, violations: List[SafetyViolation]) -> str:
        """
        Redact violations from text.

        Args:
            text: Original text
            violations: List of violations to redact

        Returns:
            Redacted text
        """
        # Sort by position descending to replace from end to start
        sorted_violations = sorted(violations, key=lambda v: v.start, reverse=True)

        redacted = text
        for violation in sorted_violations:
            replacement = f"[{violation.category.value.upper()}_REDACTED]"
            redacted = redacted[: violation.start] + replacement + redacted[violation.end :]

        return redacted

    def _log_violations(
        self,
        violations: List[SafetyViolation],
        user_id: Optional[str],
        org_id: Optional[str],
        result: SafetyCheckResult,
    ) -> None:
        """Log safety violations for audit trail."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "org_id": org_id,
            "violation_count": len(violations),
            "enforcement_mode": result.enforcement_mode.value,
            "allowed": result.allowed,
            "violations": [
                {
                    "category": v.category.value,
                    "type": v.type,
                    "severity": v.severity,
                    "confidence": v.confidence,
                }
                for v in violations
            ],
        }

        # Log at appropriate level based on severity
        if result.critical_violations:
            logger.warning(f"CRITICAL safety violations detected: {log_data}")
        elif result.high_violations:
            logger.warning(f"HIGH safety violations detected: {log_data}")
        else:
            logger.info(f"Safety violations detected: {log_data}")

    def update_policy(self, policy: SafetyPolicy) -> None:
        """Update the safety policy and reinitialize detectors if needed."""
        self.policy = policy
        # Note: Detectors keep their configuration; create new pipeline for different detector config

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about configured safety checks."""
        return {
            "pii_enabled": self.policy.pii_enabled,
            "pii_types_count": len(self.pii_detector.get_supported_types()),
            "secret_enabled": self.policy.secret_enabled,
            "secret_types_count": len(self.secret_scanner.get_supported_types()),
            "injection_enabled": self.policy.injection_enabled,
            "injection_types_count": len(self.injection_detector.get_supported_types()),
            "blocklist_enabled": self.policy.blocklist_enabled,
            "blocklist_patterns_count": len(self.policy.blocklist_patterns),
            "strict_mode": self.policy.strict_mode,
        }
