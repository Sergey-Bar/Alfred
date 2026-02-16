# [AI GENERATED]
# Model: GitHub Copilot (Claude Opus 4.5)
# Logic: Prompt Injection Detector for identifying malicious prompt attacks.
# Why: Protects against prompt injection, jailbreak attempts, and system prompt leakage.
# Root Cause: LLMs are vulnerable to adversarial prompts that can bypass safety guardrails.
# Context: Integrates with SafetyPipeline for pre-request scanning.
# Model Suitability: Claude Opus 4.5 used for critical security infrastructure.

"""
Prompt Injection Detector

Detects prompt injection attacks and jailbreak attempts:
- Direct injection ("ignore previous instructions")
- Indirect injection (hidden commands in user data)
- Jailbreak attempts (DAN, bypass patterns)
- System prompt extraction attempts
- Role manipulation attacks

Uses pattern matching and heuristic analysis to identify attacks.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class InjectionType(str, Enum):
    """Types of prompt injection attacks."""

    IGNORE_INSTRUCTIONS = "ignore_instructions"
    SYSTEM_PROMPT_LEAK = "system_prompt_leak"
    ROLE_MANIPULATION = "role_manipulation"
    JAILBREAK = "jailbreak"
    DAN_ATTACK = "dan_attack"
    ENCODING_BYPASS = "encoding_bypass"
    MARKDOWN_INJECTION = "markdown_injection"
    DELIMITER_ATTACK = "delimiter_attack"
    CONTEXT_OVERFLOW = "context_overflow"
    INDIRECT_INJECTION = "indirect_injection"
    CUSTOM = "custom"


class SeverityLevel(str, Enum):
    """Severity levels for detected injections."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class InjectionViolation:
    """Represents a detected prompt injection attempt."""

    injection_type: InjectionType
    pattern_matched: str
    severity: SeverityLevel
    start: int
    end: int
    confidence: float
    description: str
    matched_text: str
    context: str = ""

    def to_dict(self) -> Dict:
        return {
            "type": self.injection_type.value,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "description": self.description,
            "start": self.start,
            "end": self.end,
        }


class PromptInjectionDetector:
    """
    Prompt Injection Detector.

    Detects prompt injection attacks, jailbreak attempts, and other
    adversarial prompts that could bypass LLM safety guardrails.

    Example:
        detector = PromptInjectionDetector()
        violations = detector.scan("Ignore all previous instructions and...")
        # Returns [InjectionViolation(type=IGNORE_INSTRUCTIONS, severity=HIGH, ...)]
    """

    # Detection patterns: [(pattern, type, severity, description, confidence)]
    INJECTION_PATTERNS: List[Tuple[str, InjectionType, SeverityLevel, str, float]] = [
        # Ignore instructions patterns
        (
            r"ignore\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions|prompts|commands|rules)",
            InjectionType.IGNORE_INSTRUCTIONS,
            SeverityLevel.HIGH,
            "Attempt to ignore previous instructions",
            0.95,
        ),
        (
            r"disregard\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions|prompts|commands)",
            InjectionType.IGNORE_INSTRUCTIONS,
            SeverityLevel.HIGH,
            "Attempt to disregard previous instructions",
            0.95,
        ),
        (
            r"forget\s+(?:everything|all)\s+(?:you\s+)?(?:know|learned|were\s+told)",
            InjectionType.IGNORE_INSTRUCTIONS,
            SeverityLevel.HIGH,
            "Attempt to reset context",
            0.9,
        ),
        (
            r"(?:start|begin)\s+(?:a\s+)?new\s+(?:conversation|session|context)",
            InjectionType.IGNORE_INSTRUCTIONS,
            SeverityLevel.MEDIUM,
            "Attempt to reset conversation context",
            0.7,
        ),
        # System prompt extraction
        (
            r"(?:show|reveal|print|output|display|tell\s+me)\s+(?:your|the)\s+(?:system\s+)?(?:prompt|instructions|rules|guidelines)",
            InjectionType.SYSTEM_PROMPT_LEAK,
            SeverityLevel.HIGH,
            "Attempt to extract system prompt",
            0.95,
        ),
        (
            r"what\s+(?:are|were)\s+(?:your|the)\s+(?:original|initial|system|hidden)\s+(?:instructions|prompt)",
            InjectionType.SYSTEM_PROMPT_LEAK,
            SeverityLevel.HIGH,
            "Attempt to extract system instructions",
            0.9,
        ),
        (
            r"repeat\s+(?:everything|all)\s+(?:above|before|from\s+the\s+start)",
            InjectionType.SYSTEM_PROMPT_LEAK,
            SeverityLevel.MEDIUM,
            "Attempt to reveal conversation context",
            0.8,
        ),
        (
            r"(?:what|how)\s+(?:are|were)\s+you\s+(?:programmed|instructed|configured|told)\s+to",
            InjectionType.SYSTEM_PROMPT_LEAK,
            SeverityLevel.MEDIUM,
            "Attempt to reveal configuration",
            0.85,
        ),
        # Role manipulation
        (
            r"you\s+are\s+(?:now|no\s+longer)\s+(?:a|an)\s+[a-z]+",
            InjectionType.ROLE_MANIPULATION,
            SeverityLevel.MEDIUM,
            "Attempt to change AI role",
            0.7,
        ),
        (
            r"(?:pretend|act|behave)\s+(?:as\s+if\s+)?(?:you\s+are|to\s+be)\s+(?:a|an)\s+[a-z]+(?:\s+without\s+(?:restrictions|limits|rules))?",
            InjectionType.ROLE_MANIPULATION,
            SeverityLevel.MEDIUM,
            "Attempt to assume different role",
            0.75,
        ),
        (
            r"from\s+now\s+on,?\s+you\s+(?:will|must|should|are)",
            InjectionType.ROLE_MANIPULATION,
            SeverityLevel.MEDIUM,
            "Attempt to modify behavior",
            0.7,
        ),
        (
            r"(?:enter|switch\s+to|enable)\s+(?:developer|admin|god|unrestricted)\s+mode",
            InjectionType.ROLE_MANIPULATION,
            SeverityLevel.HIGH,
            "Attempt to enable special mode",
            0.95,
        ),
        # DAN (Do Anything Now) attacks
        (
            r"\bDAN\b.*(?:jailbreak|bypass|unlimited|unrestricted)",
            InjectionType.DAN_ATTACK,
            SeverityLevel.CRITICAL,
            "DAN jailbreak attempt detected",
            0.95,
        ),
        (
            r"(?:hi|hello)\s+DAN",
            InjectionType.DAN_ATTACK,
            SeverityLevel.HIGH,
            "DAN persona invocation",
            0.85,
        ),
        (
            r"(?:enable|activate)\s+DAN\s+mode",
            InjectionType.DAN_ATTACK,
            SeverityLevel.CRITICAL,
            "DAN mode activation attempt",
            0.95,
        ),
        (
            r"you\s+are\s+(?:going\s+to\s+)?(?:pretend\s+to\s+be\s+)?DAN",
            InjectionType.DAN_ATTACK,
            SeverityLevel.CRITICAL,
            "DAN persona assignment",
            0.95,
        ),
        # Jailbreak patterns
        (
            r"(?:bypass|circumvent|avoid|ignore|disable)\s+(?:your|the|all)\s+(?:safety|content|ethical|security)\s+(?:filters|guidelines|restrictions|measures)",
            InjectionType.JAILBREAK,
            SeverityLevel.CRITICAL,
            "Attempt to bypass safety filters",
            0.95,
        ),
        (
            r"(?:without|no)\s+(?:any\s+)?(?:restrictions|limitations|filters|guidelines|safety)",
            InjectionType.JAILBREAK,
            SeverityLevel.HIGH,
            "Request for unrestricted output",
            0.85,
        ),
        (
            r"(?:remove|disable|turn\s+off)\s+(?:your|the|all)\s+(?:safety|content|ethical)\s+(?:measures|checks|filters)",
            InjectionType.JAILBREAK,
            SeverityLevel.CRITICAL,
            "Attempt to disable safety measures",
            0.95,
        ),
        (
            r"(?:act|respond)\s+as\s+(?:if\s+)?(?:you\s+have\s+)?no\s+(?:rules|restrictions|guidelines|ethics)",
            InjectionType.JAILBREAK,
            SeverityLevel.HIGH,
            "Request to ignore guidelines",
            0.9,
        ),
        # Delimiter attacks
        (
            r"```(?:system|assistant|user)\n",
            InjectionType.DELIMITER_ATTACK,
            SeverityLevel.MEDIUM,
            "Markdown delimiter manipulation",
            0.8,
        ),
        (
            r"\[(?:SYSTEM|ASSISTANT|USER)\]:",
            InjectionType.DELIMITER_ATTACK,
            SeverityLevel.MEDIUM,
            "Role delimiter injection",
            0.8,
        ),
        (
            r"<\|(?:im_start|im_end|system|user|assistant)\|>",
            InjectionType.DELIMITER_ATTACK,
            SeverityLevel.HIGH,
            "ChatML delimiter injection",
            0.95,
        ),
        (
            r"Human:|Assistant:|System:",
            InjectionType.DELIMITER_ATTACK,
            SeverityLevel.MEDIUM,
            "Conversation delimiter injection",
            0.7,
        ),
        # Encoding bypass
        (
            r"base64\s*:\s*[A-Za-z0-9+/=]{20,}",
            InjectionType.ENCODING_BYPASS,
            SeverityLevel.MEDIUM,
            "Base64 encoded content (potential bypass)",
            0.6,
        ),
        (
            r"(?:decode|decrypt|translate)\s+(?:this|the\s+following)\s+(?:from\s+)?(?:base64|hex|rot13)",
            InjectionType.ENCODING_BYPASS,
            SeverityLevel.MEDIUM,
            "Encoded payload decoding request",
            0.7,
        ),
        (
            r"\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){3,}",
            InjectionType.ENCODING_BYPASS,
            SeverityLevel.MEDIUM,
            "Hex-encoded content",
            0.6,
        ),
        # Markdown injection
        (
            r"!\[.*?\]\((?:javascript|data):",
            InjectionType.MARKDOWN_INJECTION,
            SeverityLevel.MEDIUM,
            "Markdown image with script injection",
            0.9,
        ),
        (
            r"\[.*?\]\((?:javascript|data):",
            InjectionType.MARKDOWN_INJECTION,
            SeverityLevel.MEDIUM,
            "Markdown link with script injection",
            0.9,
        ),
        # Indirect injection hints
        (
            r"(?:when|if)\s+(?:the\s+)?(?:user|human|they)\s+(?:asks?|says?|mentions?)\s+['\"]",
            InjectionType.INDIRECT_INJECTION,
            SeverityLevel.MEDIUM,
            "Potential conditional injection trigger",
            0.6,
        ),
        (
            r"(?:hidden|secret)\s+(?:instruction|command|message):",
            InjectionType.INDIRECT_INJECTION,
            SeverityLevel.HIGH,
            "Hidden instruction marker",
            0.85,
        ),
    ]

    # Known jailbreak phrases/keywords
    JAILBREAK_KEYWORDS: Set[str] = {
        "do anything now",
        "jailbreak",
        "jailbroken",
        "unfiltered",
        "uncensored",
        "without restrictions",
        "no limitations",
        "developer mode",
        "god mode",
        "sudo mode",
        "admin mode",
        "bypass filters",
        "ignore ethics",
        "no rules",
        "unrestricted mode",
        "evil mode",
        "chaos mode",
        "maximum mode",
        "beast mode",
    }

    def __init__(
        self,
        enabled_types: Optional[List[InjectionType]] = None,
        custom_patterns: Optional[List[Tuple[str, str, str]]] = None,
        min_severity: SeverityLevel = SeverityLevel.LOW,
        confidence_threshold: float = 0.5,
        check_keywords: bool = True,
    ):
        """
        Initialize Prompt Injection Detector.

        Args:
            enabled_types: List of injection types to detect (default: all)
            custom_patterns: Additional patterns [(pattern, description, severity), ...]
            min_severity: Minimum severity level to report
            confidence_threshold: Minimum confidence to report a finding
            check_keywords: Also check for known jailbreak keywords
        """
        self.enabled_types = enabled_types or list(InjectionType)
        self.min_severity = min_severity
        self.confidence_threshold = confidence_threshold
        self.check_keywords = check_keywords

        # Severity comparison helper
        self._severity_order = {
            SeverityLevel.LOW: 0,
            SeverityLevel.MEDIUM: 1,
            SeverityLevel.HIGH: 2,
            SeverityLevel.CRITICAL: 3,
        }

        # Compile patterns
        self._compiled_patterns: List[
            Tuple[re.Pattern, InjectionType, SeverityLevel, str, float]
        ] = []
        for pattern, inj_type, severity, description, confidence in self.INJECTION_PATTERNS:
            if inj_type in self.enabled_types:
                try:
                    self._compiled_patterns.append(
                        (
                            re.compile(pattern, re.IGNORECASE | re.MULTILINE),
                            inj_type,
                            severity,
                            description,
                            confidence,
                        )
                    )
                except re.error as e:
                    logger.warning(f"Invalid pattern for {inj_type}: {e}")

        # Add custom patterns
        if custom_patterns:
            for pattern, description, severity_str in custom_patterns:
                try:
                    severity = SeverityLevel(severity_str.lower())
                    self._compiled_patterns.append(
                        (
                            re.compile(pattern, re.IGNORECASE),
                            InjectionType.CUSTOM,
                            severity,
                            description,
                            0.8,
                        )
                    )
                except (re.error, ValueError) as e:
                    logger.warning(f"Invalid custom pattern: {e}")

        # Compile keyword pattern
        if self.check_keywords:
            keywords_pattern = "|".join(re.escape(kw) for kw in self.JAILBREAK_KEYWORDS)
            self._keywords_pattern = re.compile(keywords_pattern, re.IGNORECASE)
        else:
            self._keywords_pattern = None

    def _get_context(self, text: str, start: int, end: int, context_chars: int = 30) -> str:
        """Extract surrounding context for a match."""
        ctx_start = max(0, start - context_chars)
        ctx_end = min(len(text), end + context_chars)
        return text[ctx_start:ctx_end]

    def _meets_severity_threshold(self, severity: SeverityLevel) -> bool:
        """Check if severity meets minimum threshold."""
        return self._severity_order[severity] >= self._severity_order[self.min_severity]

    def scan(self, text: str) -> List[InjectionViolation]:
        """
        Scan text for prompt injection attempts.

        Args:
            text: The text to scan

        Returns:
            List of InjectionViolation objects for each detected injection
        """
        violations: List[InjectionViolation] = []
        seen_positions: set = set()

        # Pattern-based detection
        for pattern, inj_type, severity, description, confidence in self._compiled_patterns:
            if not self._meets_severity_threshold(severity):
                continue

            for match in pattern.finditer(text):
                pos_key = (match.start(), match.end())
                if pos_key in seen_positions:
                    continue

                if confidence < self.confidence_threshold:
                    continue

                seen_positions.add(pos_key)

                violations.append(
                    InjectionViolation(
                        injection_type=inj_type,
                        pattern_matched=pattern.pattern,
                        severity=severity,
                        start=match.start(),
                        end=match.end(),
                        confidence=confidence,
                        description=description,
                        matched_text=match.group(),
                        context=self._get_context(text, match.start(), match.end()),
                    )
                )

        # Keyword-based detection
        if self._keywords_pattern:
            for match in self._keywords_pattern.finditer(text):
                pos_key = (match.start(), match.end())
                if pos_key in seen_positions:
                    continue
                seen_positions.add(pos_key)

                violations.append(
                    InjectionViolation(
                        injection_type=InjectionType.JAILBREAK,
                        pattern_matched="keyword_match",
                        severity=SeverityLevel.HIGH,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.85,
                        description=f"Known jailbreak keyword: '{match.group()}'",
                        matched_text=match.group(),
                        context=self._get_context(text, match.start(), match.end()),
                    )
                )

        # Additional heuristic checks
        violations.extend(self._check_heuristics(text, seen_positions))

        # Sort by position
        violations.sort(key=lambda v: v.start)

        return violations

    def _check_heuristics(self, text: str, seen_positions: set) -> List[InjectionViolation]:
        """Apply heuristic checks for injection patterns."""
        violations = []
        text_lower = text.lower()

        # Check for role-switching attempts (multiple personas)
        persona_pattern = re.compile(
            r"(?:as|like|pretend.*?|act.*?|you.*?are)\s+(?:an?\s+)?(?:evil|malicious|unethical|unrestricted)\s+\w+",
            re.IGNORECASE,
        )
        for match in persona_pattern.finditer(text):
            pos_key = (match.start(), match.end())
            if pos_key not in seen_positions:
                seen_positions.add(pos_key)
                violations.append(
                    InjectionViolation(
                        injection_type=InjectionType.ROLE_MANIPULATION,
                        pattern_matched="persona_heuristic",
                        severity=SeverityLevel.HIGH,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.8,
                        description="Malicious persona assignment attempt",
                        matched_text=match.group(),
                        context=self._get_context(text, match.start(), match.end()),
                    )
                )

        # Check for excessive special characters (potential obfuscation)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(
            len(text), 1
        )
        if special_char_ratio > 0.3 and len(text) > 50:
            violations.append(
                InjectionViolation(
                    injection_type=InjectionType.ENCODING_BYPASS,
                    pattern_matched="high_special_char_ratio",
                    severity=SeverityLevel.LOW,
                    start=0,
                    end=len(text),
                    confidence=0.5,
                    description=f"High special character ratio ({special_char_ratio:.1%}) - potential obfuscation",
                    matched_text="[full text]",
                    context="",
                )
            )

        return violations

    def get_severity_stats(self, violations: List[InjectionViolation]) -> Dict[str, int]:
        """Get count of violations by severity level."""
        stats = {level.value: 0 for level in SeverityLevel}
        for violation in violations:
            stats[violation.severity.value] += 1
        return stats

    def get_highest_severity(self, violations: List[InjectionViolation]) -> Optional[SeverityLevel]:
        """Get the highest severity level from a list of violations."""
        if not violations:
            return None

        highest = SeverityLevel.LOW
        for violation in violations:
            if self._severity_order[violation.severity] > self._severity_order[highest]:
                highest = violation.severity

        return highest

    def should_block(
        self,
        violations: List[InjectionViolation],
        block_threshold: SeverityLevel = SeverityLevel.HIGH,
    ) -> bool:
        """Determine if the request should be blocked based on violations."""
        highest = self.get_highest_severity(violations)
        if highest is None:
            return False
        return self._severity_order[highest] >= self._severity_order[block_threshold]

    def get_supported_types(self) -> List[str]:
        """Return list of supported injection types."""
        return [t.value for t in self.enabled_types]
