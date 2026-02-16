"""
Alfred - Enterprise AI Credit Governance Platform
Input Hardening & Security Guardrails

[ARCHITECTURAL ROLE]
This module serves as the primary defense-in-depth layer for inbound data.
It performs structural validation, semantic sniffing for prompt injection,
and financial sanity checks.

[SECURITY THREAT MODELS]
1. Prompt Injection: Prevent users from overriding system instructions (DAN, ignore previous).
2. Resource Exhaustion: Capping message lengths to prevent OOM/Budget drain.
3. Financial Manipulation: Validating credit amounts to prevent floating-point exploits.
4. XSS/Injection: Scanning for HTML/Script tags in text payloads.
"""

import re
from typing import List

from fastapi import HTTPException

from .models import ChatMessage


class InputValidator:
    """
    Unified Input Gatekeeper.

    Implements a set of static validators designed to identify and block
    malicious payloads before they reach the LLM or the Database.
    """

    # --- Heuristic Signatures for Prompt Injection & Attacks ---
    # These regexes identify common 'jailbreak' techniques and web attack vectors.
    SUSPICIOUS_PATTERNS = [
        r"ignore\s+(previous|all)\s+instructions",  # System Override Attempts
        r"system\s*:\s*you\s+are\s+now",  # Roleplay Forced Change
        r"<\s*script[^>]*>",  # Classic XSS
        r"javascript\s*:",  # Proto-XSS
        r"\b(union|select|insert|update|delete|drop)\s+",  # SQLi Keywords
        r"<\s*iframe",  # Clickjacking Prep
        r"on(load|error|click)\s*=",  # Event Handler Injection
    ]

    # Operational Constraints
    MAX_MESSAGE_LENGTH = 50000  # Safety cap (~12k tokens)
    MAX_MESSAGES_PER_REQUEST = 100  # Prevent 'Context Stuffing' attacks

    @classmethod
    def validate_chat_messages(cls, messages: List[ChatMessage]) -> None:
        """
        Deep Inspector for Chat Payloads.

        Performs structural and semantic analysis on the entire message history.

        Logic:
        - Must contain at least one message.
        - Must not exceed strict length/count caps.
        - Must follow OpenAI-standard Role-Value structure.
        - Scans for injection signatures (Warning Level - logs for audit).
        """
        if not messages:
            raise HTTPException(400, "Inbound payload must contain at least one message.")

        if len(messages) > cls.MAX_MESSAGES_PER_REQUEST:
            raise HTTPException(
                400,
                f"Protocol Violation: Context history exceeds limit of {cls.MAX_MESSAGES_PER_REQUEST}.",
            )

        for idx, msg in enumerate(messages):
            # Schema Integrity
            if not msg.role or not msg.content:
                raise HTTPException(400, f"Malformed Message at Index {idx}: Role/Content missing.")

            # White-listed Role Verification
            if msg.role not in ["system", "user", "assistant"]:
                raise HTTPException(
                    400, f"Auth Error at Index {idx}: Unsupported role '{msg.role}'."
                )

            # Length Contraint (Protection against payload bombing)
            if len(msg.content) > cls.MAX_MESSAGE_LENGTH:
                raise HTTPException(
                    400,
                    f"Data Overflow at Index {idx}: Content exceeds {cls.MAX_MESSAGE_LENGTH} characters.",
                )

            # --- Pattern Sniffing ---
            # [BUG-014 FIX] Added setting-based control and pattern hashing to
            # protect sensitive content signatures in logs.
            from .config import settings

            if settings.log_suspicious_patterns:
                for pattern in cls.SUSPICIOUS_PATTERNS:
                    if re.search(pattern, msg.content, re.IGNORECASE):
                        from .logging_config import get_logger

                        logger = get_logger(__name__)

                        # Use a hash of the pattern to identify the rule triggered
                        # without logging the actual signature string.
                        import hashlib

                        pattern_id = hashlib.sha256(pattern.encode()).hexdigest()[:12]

                        logger.warning(
                            "Security Event: Suspicious Sequence Detected",
                            extra={
                                "threat_id": f"pattern_{pattern_id}",
                                "msg_idx": idx,
                                "msg_role": msg.role,
                            },
                        )

    @classmethod
    def validate_credit_amount(cls, amount: float, max_amount: float = 1_000_000) -> None:
        """
        Financial Integrity Guard.

        Prevents overflow/underflow attacks and rounding exploits in the
        credit reallocation system.
        """
        if amount <= 0:
            raise HTTPException(400, "Financial Logic: Reallocation amount must be > 0.")

        if amount > max_amount:
            raise HTTPException(
                400, f"Policy Violation: Transfer exceeds organizational cap of {max_amount}."
            )

        # Precision Hardening
        # Prevents 'Salami Slicing' attacks where fractional credits are manipulated.
        if len(str(amount).split(".")[-1]) > 2:
            raise HTTPException(400, "Constraint: Credit precision halted at 2 decimal places.")
