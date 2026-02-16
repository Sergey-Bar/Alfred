# [AI GENERATED]
# Model: GitHub Copilot (Claude Opus 4.5)
# Logic: Safety module initialization for Alfred's prompt safety pipeline.
# Why: Centralizes PII detection, secret scanning, and prompt injection detection.
# Root Cause: Enterprise customers require content filtering for compliance (GDPR, HIPAA, SOC2).
# Context: This module integrates with the proxy router to scan all prompts before LLM calls.
# Model Suitability: Claude Opus 4.5 used for critical security infrastructure implementation.

"""
Alfred Safety Pipeline Module

Provides comprehensive content filtering and prompt safety checks:
- PII Detection (emails, SSNs, credit cards, etc.)
- Secret Scanning (API keys, passwords, tokens)
- Prompt Injection Detection
- Custom Blocklist Support
"""

from .pii_detector import PIIDetector, PIIViolation
from .pipeline import SafetyCheckResult, SafetyPipeline, SafetyViolation
from .prompt_injection import InjectionViolation, PromptInjectionDetector
from .secret_scanner import SecretScanner, SecretViolation

__all__ = [
    "PIIDetector",
    "PIIViolation",
    "SecretScanner",
    "SecretViolation",
    "PromptInjectionDetector",
    "InjectionViolation",
    "SafetyPipeline",
    "SafetyCheckResult",
    "SafetyViolation",
]
