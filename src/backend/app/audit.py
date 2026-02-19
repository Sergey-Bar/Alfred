"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       Immutable hash-chained audit log writer + daily
             integrity verification job. Uses SHA-256 hash chain
             where each entry's hash includes the previous entry's
             hash, creating a tamper-evident chain. Verification
             walks the full chain and detects any breaks.
Root Cause:  Sprint tasks T138-T140 — Audit log system.
Context:     LEDGER SAFETY — append-only, no UPDATE/DELETE.
             Financial and compliance-critical infrastructure.
Suitability: L4 — cryptographic correctness is essential.
──────────────────────────────────────────────────────────────

ROLLBACK: To revert this change:
1. Run: alembic downgrade -1
2. Deploy tag: v<previous-tag>
3. Notify: Sergey Bar + on-call engineer
"""

import asyncio
import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlmodel import Session

from .models import AuditLog

logger = logging.getLogger(__name__)

# Genesis hash — the "previous_hash" for the very first entry.
GENESIS_HASH = "0" * 64


# ─── Hash Chain Computation ──────────────────────────────────


def compute_entry_hash(
    sequence_number: int,
    action: str,
    actor_user_id: Optional[str],
    actor_type: str,
    target_type: Optional[str],
    target_id: Optional[str],
    details_json: Optional[str],
    previous_hash: str,
    created_at: str,
) -> str:
    """
    Compute SHA-256 hash for an audit log entry.

    The hash chain is: H(seq|action|actor|actor_type|target|details|prev_hash|ts)

    This function MUST remain deterministic — same inputs ALWAYS produce
    the same hash. Any change to the algorithm breaks chain verification
    for all existing entries.
    """
    payload = "|".join([
        str(sequence_number),
        action,
        str(actor_user_id or ""),
        actor_type,
        str(target_type or ""),
        str(target_id or ""),
        str(details_json or ""),
        previous_hash,
        created_at,
    ])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ─── Legacy Compatibility ────────────────────────────────────


def log_audit(
    session: Session,
    actor_user_id: Optional[uuid.UUID],
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Legacy-compatible append-only audit entry generator.
    Now produces hash-chained entries.

    Args:
        session: Active database session.
        actor_user_id: The ID of the administrator performing the action.
        action: Canonical action identifier (e.g. 'user.suspension').
        target_type: The entity type affected (e.g. 'user', 'team').
        target_id: The specific ID of the target entity.
        details: Metadata or 'Before/After' state representation.
    """
    try:
        writer = AuditLogWriter(session)
        writer.log_sync(
            action=action,
            actor_user_id=actor_user_id,
            actor_type="user",
            target_type=target_type,
            target_id=target_id,
            details=details,
        )
    except Exception:
        logging.getLogger("alfred.audit").exception(
            f"SECURITY ALERT: Failed to record audit log for action '{action}' by {actor_user_id}"
        )


# ─── Audit Log Writer (T139) ────────────────────────────────


class AuditLogWriter:
    """
    Append-only audit log writer with cryptographic hash chain.

    LEDGER SAFETY RULES:
    - All writes are wrapped in database transactions
    - No UPDATE or DELETE operations on audit_logs — ever
    - Entries are WRITE-ONCE and immutable post-commit
    - Hash chain ensures tamper detection
    """

    def __init__(self, session: Session):
        self._session = session

    def log_sync(
        self,
        action: str,
        actor_user_id: Optional[uuid.UUID] = None,
        actor_type: str = "user",
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synchronous version of log() for use in sync contexts."""
        details_json = json.dumps(details, sort_keys=True, default=str) if details else None
        now = datetime.now(timezone.utc)
        created_at_str = now.isoformat()

        # Get the latest entry for chain continuation
        result = self._session.exec(
            text(
                "SELECT sequence_number, entry_hash FROM audit_logs "
                "ORDER BY sequence_number DESC LIMIT 1 FOR UPDATE"
            )
        )
        latest = result.first()

        if latest:
            sequence_number = latest[0] + 1
            previous_hash = latest[1]
        else:
            sequence_number = 1
            previous_hash = GENESIS_HASH

        entry_hash = compute_entry_hash(
            sequence_number=sequence_number,
            action=action,
            actor_user_id=str(actor_user_id) if actor_user_id else None,
            actor_type=actor_type,
            target_type=target_type,
            target_id=target_id,
            details_json=details_json,
            previous_hash=previous_hash,
            created_at=created_at_str,
        )

        entry_id = uuid.uuid4()
        self._session.exec(
            text(
                "INSERT INTO audit_logs "
                "(id, sequence_number, actor_user_id, actor_type, action, "
                "target_type, target_id, details_json, ip_address, user_agent, "
                "previous_hash, entry_hash, created_at) "
                "VALUES (:id, :seq, :actor_id, :actor_type, :action, "
                ":target_type, :target_id, :details, :ip, :ua, "
                ":prev_hash, :entry_hash, :created_at)"
            ),
            params={
                "id": str(entry_id),
                "seq": sequence_number,
                "actor_id": str(actor_user_id) if actor_user_id else None,
                "actor_type": actor_type,
                "action": action,
                "target_type": target_type,
                "target_id": target_id,
                "details": details_json,
                "ip": ip_address,
                "ua": user_agent,
                "prev_hash": previous_hash,
                "entry_hash": entry_hash,
                "created_at": now,
            },
        )
        self._session.commit()

        logger.info(
            "audit_log.append seq=%d action=%s hash=%s...",
            sequence_number, action, entry_hash[:16],
        )

        return {
            "id": str(entry_id),
            "sequence_number": sequence_number,
            "entry_hash": entry_hash,
        }

    async def log(
        self,
        action: str,
        actor_user_id: Optional[uuid.UUID] = None,
        actor_type: str = "user",
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Async wrapper for log_sync()."""
        return self.log_sync(
            action=action,
            actor_user_id=actor_user_id,
            actor_type=actor_type,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )


# ─── Standard Action Names ──────────────────────────────────


class AuditActions:
    """Canonical audit action names."""
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"
    USER_ROTATE_KEY = "user.rotate_key"
    USER_ROLE_CHANGE = "user.role_change"

    WALLET_CREATE = "wallet.create"
    WALLET_DEDUCT = "wallet.deduct"
    WALLET_REFUND = "wallet.refund"
    WALLET_TOPUP = "wallet.topup"
    WALLET_RESET = "wallet.reset"
    WALLET_SUSPEND = "wallet.suspend"
    WALLET_LIMIT_CHANGE = "wallet.limit_change"

    TRANSFER_CREATE = "transfer.create"
    TRANSFER_APPROVE = "transfer.approve"
    TRANSFER_REJECT = "transfer.reject"

    TEAM_CREATE = "team.create"
    TEAM_UPDATE = "team.update"
    TEAM_DELETE = "team.delete"
    TEAM_MEMBER_ADD = "team.member_add"
    TEAM_MEMBER_REMOVE = "team.member_remove"

    POLICY_CREATE = "policy.create"
    POLICY_UPDATE = "policy.update"
    POLICY_DELETE = "policy.delete"

    ROUTING_RULE_CREATE = "routing.rule_create"
    ROUTING_RULE_UPDATE = "routing.rule_update"
    ROUTING_RULE_DELETE = "routing.rule_delete"

    SAFETY_BLOCK = "safety.block"
    SAFETY_ALERT = "safety.alert"

    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_CONFIG_CHANGE = "system.config_change"


# ─── Hash Chain Verifier (T140) ──────────────────────────────


class HashChainVerifier:
    """
    Daily integrity verification job for the audit log hash chain.

    Walks the entire chain from genesis to latest entry, recomputing
    each hash and comparing against the stored value. Any mismatch
    indicates tampering.
    """

    def __init__(self, session: Session):
        self._session = session

    async def verify(self, batch_size: int = 5000) -> Dict[str, Any]:
        """
        Verify the entire hash chain.

        Returns:
            {
                "valid": bool,
                "entries_checked": int,
                "first_break_at": Optional[int],
                "errors": List[str],
                "duration_ms": float,
            }
        """
        import time
        start = time.monotonic()

        errors: List[str] = []
        total_checked = 0
        first_break_at = None
        expected_previous_hash = GENESIS_HASH
        offset = 0

        while True:
            result = self._session.exec(
                text(
                    "SELECT sequence_number, action, actor_user_id, actor_type, "
                    "target_type, target_id, details_json, previous_hash, "
                    "entry_hash, created_at "
                    "FROM audit_logs "
                    "ORDER BY sequence_number ASC "
                    "LIMIT :limit OFFSET :offset"
                ),
                params={"limit": batch_size, "offset": offset},
            )
            rows = result.fetchall()

            if not rows:
                break

            for row in rows:
                (seq, action, actor_id, actor_type, target_type, target_id,
                    details_json, stored_prev_hash, stored_entry_hash, created_at) = row

                total_checked += 1

                # Check 1: previous_hash matches expected
                if stored_prev_hash != expected_previous_hash:
                    error_msg = (
                        f"Chain break at seq={seq}: "
                        f"stored previous_hash={stored_prev_hash[:16]}... "
                        f"!= expected={expected_previous_hash[:16]}..."
                    )
                    errors.append(error_msg)
                    if first_break_at is None:
                        first_break_at = seq
                    logger.error(error_msg)

                # Check 2: recompute entry_hash
                created_at_str = (
                    created_at.isoformat()
                    if hasattr(created_at, "isoformat")
                    else str(created_at)
                )
                recomputed = compute_entry_hash(
                    sequence_number=seq,
                    action=action,
                    actor_user_id=str(actor_id) if actor_id else None,
                    actor_type=actor_type or "user",
                    target_type=target_type,
                    target_id=target_id,
                    details_json=details_json,
                    previous_hash=stored_prev_hash,
                    created_at=created_at_str,
                )

                if recomputed != stored_entry_hash:
                    error_msg = (
                        f"Hash mismatch at seq={seq}: "
                        f"stored={stored_entry_hash[:16]}... "
                        f"!= recomputed={recomputed[:16]}..."
                    )
                    errors.append(error_msg)
                    if first_break_at is None:
                        first_break_at = seq
                    logger.error(error_msg)

                expected_previous_hash = stored_entry_hash

            offset += batch_size

        duration_ms = (time.monotonic() - start) * 1000
        valid = len(errors) == 0

        if valid:
            logger.info(
                "Audit log chain verified: %d entries, chain intact, %.1fms",
                total_checked, duration_ms,
            )
        else:
            logger.error(
                "AUDIT LOG INTEGRITY FAILURE: %d errors in %d entries, first break at seq=%s",
                len(errors), total_checked, first_break_at,
            )

        return {
            "valid": valid,
            "entries_checked": total_checked,
            "first_break_at": first_break_at,
            "errors": errors[:100],
            "duration_ms": round(duration_ms, 2),
        }


# ─── Daily Verification Cron (T140) ─────────────────────────


async def daily_audit_verification_loop(get_session_fn):
    """
    Async cron loop that runs hash chain verification daily at 03:00 UTC.
    """
    logger.info("audit_verification_cron: started")
    last_check_date = None

    while True:
        try:
            await asyncio.sleep(600)  # Check every 10 minutes
            now = datetime.now(timezone.utc)

            if now.hour == 3 and now.date() != last_check_date:
                last_check_date = now.date()
                logger.info("audit_verification_cron: starting daily verification")

                async for session in get_session_fn():
                    verifier = HashChainVerifier(session)
                    result = await verifier.verify()

                    if not result["valid"]:
                        logger.critical(
                            "AUDIT LOG INTEGRITY FAILURE: %d errors, first break at seq=%s",
                            len(result["errors"]), result["first_break_at"],
                        )

                    logger.info(
                        "audit_verification_cron: valid=%s entries=%d duration=%.1fms",
                        result["valid"], result["entries_checked"], result["duration_ms"],
                    )
                    break

        except asyncio.CancelledError:
            logger.info("audit_verification_cron: shutting down")
            return
        except Exception as e:
            logger.error(f"audit_verification_cron error: {e}", exc_info=True)
