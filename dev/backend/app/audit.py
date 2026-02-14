"""
Alfred - Enterprise AI Credit Governance Platform
Administrative Ledger & Compliance Auditing

[ARCHITECTURAL ROLE]
This module provides the 'Immutable Paper Trail' required for regulatory compliance
(SOC2, HIPAA, ISO27001). It records high-privileged actions that modify the state
of the organization, such as quota injections, user suspensions, or key rotations.

[DESIGN PRINCIPLE]
Immediate Persistence: Audit entries are committed immediately to the database.
This ensures that even if a subsequent business process fails, the attempt 
and the actor's identity are permanently recorded.
"""

import json
import uuid
from typing import Any, Dict, Optional

from sqlmodel import Session

from .models import AuditLog


def log_audit(
    session: Session,
    actor_user_id: Optional[uuid.UUID],
    action: str,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Append-Only Audit Entry Generator.
    
    Args:
        session: Active database session.
        actor_user_id: The ID of the administrator performing the action.
        action: Canonical action identifier (e.g. 'user.suspension').
        target_type: The entity type affected (e.g. 'user', 'team').
        target_id: The specific ID of the target entity.
        details: Metadata or 'Before/After' state representation.
    """
    try:
        # Serialize metadata for persistent storage
        details_json = json.dumps(details) if details is not None else None
        
        entry = AuditLog(
            actor_user_id=actor_user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details_json=details_json,
        )
        
        # We use an isolated commit to guarantee the audit trail is written 
        # regardless of the outcome of the primary transaction.
        session.add(entry)
        session.commit()
        
    except Exception:
        # Resilience: Failure to audit must not crash the primary business flow,
        # but it must be logged to the standard system logger as a security event.
        import logging
        logging.getLogger("alfred.audit").exception(
            f"SECURITY ALERT: Failed to record audit log for action '{action}' by {actor_user_id}"
        )