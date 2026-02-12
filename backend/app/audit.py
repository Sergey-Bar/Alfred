from typing import Optional, Dict
import json
from sqlmodel import Session
from .models import AuditLog
import uuid


def log_audit(
    session: Session,
    actor_user_id: Optional[uuid.UUID],
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[Dict] = None,
):
    """Write an append-only audit log entry and commit.

    This is intentionally synchronous and commits immediately to ensure the
    audit entry is persisted even if the surrounding transaction continues.
    """
    try:
        details_json = json.dumps(details) if details is not None else None
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details_json=details_json,
        )
        session.add(entry)
        session.commit()
    except Exception:
        # Avoid raising to caller; log to standard logger
        import logging

        logging.getLogger("alfred.audit").exception("Failed to write audit log")
*** End Patch