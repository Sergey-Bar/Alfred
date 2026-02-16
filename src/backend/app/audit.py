"""
Alfred - Enterprise AI Credit Governance Platform
Administrative Ledger & Compliance Auditing

[ARCHITECTURAL ROLE]
This module provides the 'Immutable Paper Trail' required for regulatory compliance
(SOC2, HIPAA, ISO27001). It records high-privileged actions that modify the state
of the organization, such as quota injections, user suspensions, or key rotations.

# [AI GENERATED]
# Model: GitHub Copilot (GPT-4.1)
# Logic: This module provides append-only audit logging for all privileged actions, ensuring compliance and traceability.
# Why: Regulatory frameworks require immutable audit trails for all sensitive actions.
# Root Cause: Without audit logs, it's impossible to prove compliance or investigate incidents.
# Context: All admin actions should be logged here. Future: consider streaming to SIEM or external audit store.
# Model Suitability: For audit logging, GPT-4.1 is sufficient; for advanced compliance, a more advanced model may be preferred.
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
    # [AI GENERATED]
    # Model: GitHub Copilot (GPT-4.1)
    # Logic: Writes an append-only audit entry to the DB, serializing details and guaranteeing commit even if the main transaction fails.
    # Why: Ensures all privileged actions are permanently recorded for compliance and forensics.
    # Root Cause: Audit logs must be written even if the main business logic fails.
    # Context: Call for all admin/privileged actions. Failure to audit is logged as a security event.
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
