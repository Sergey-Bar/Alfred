"""
Secret Scanner

Detects secrets and credentials in prompts:
- API Keys (AWS, OpenAI, Google, Azure, GitHub, etc.)
- Private Keys (RSA, SSH, PGP)
- Passwords and tokens
- Database connection strings
- High-entropy strings (potential secrets)

Uses pattern matching and entropy analysis to identify potential secrets.
"""

import logging
import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class SecretType(str, Enum):
    """Types of secrets that can be detected."""

    AWS_ACCESS_KEY = "aws_access_key"
    AWS_SECRET_KEY = "aws_secret_key"
    OPENAI_API_KEY = "openai_api_key"
    ANTHROPIC_API_KEY = "anthropic_api_key"
    GOOGLE_API_KEY = "google_api_key"
    AZURE_KEY = "azure_key"
    GITHUB_TOKEN = "github_token"
    GITHUB_PAT = "github_pat"
    GITLAB_TOKEN = "gitlab_token"
    SLACK_TOKEN = "slack_token"
    STRIPE_KEY = "stripe_key"
    TWILIO_KEY = "twilio_key"
    SENDGRID_KEY = "sendgrid_key"
    DATABASE_URL = "database_url"
    PRIVATE_KEY = "private_key"
    JWT_TOKEN = "jwt_token"
    GENERIC_API_KEY = "generic_api_key"
    GENERIC_SECRET = "generic_secret"
    PASSWORD = "password"
    HIGH_ENTROPY = "high_entropy"
    CUSTOM = "custom"


@dataclass
class SecretViolation:
    """Represents a detected secret violation."""

    secret_type: SecretType
    value: str
    masked_value: str
    start: int
    end: int
    confidence: float = 1.0
    context: str = ""
    provider: str = ""

    def to_dict(self) -> Dict:
        return {
            "type": self.secret_type.value,
            "masked_value": self.masked_value,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "provider": self.provider,
        }


class SecretScanner:
    """
    Secret Scanner.

    Detects API keys, passwords, tokens, and other secrets in text
    using pattern matching and entropy analysis.

    Example:
        scanner = SecretScanner()
        violations = scanner.scan("My key is sk-abc123xyz789...")
        # Returns [SecretViolation(type=OPENAI_API_KEY, masked_value="sk-***", ...)]
    """

    # Secret patterns: (pattern, secret_type, provider, confidence)
    PATTERNS: List[Tuple[str, SecretType, str, float]] = [
        # AWS
        (r"\bAKIA[0-9A-Z]{16}\b", SecretType.AWS_ACCESS_KEY, "AWS", 1.0),
        (r"\b[A-Za-z0-9/+=]{40}\b(?=.*aws)", SecretType.AWS_SECRET_KEY, "AWS", 0.8),
        # OpenAI
        (
            r"\bsk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}\b",
            SecretType.OPENAI_API_KEY,
            "OpenAI",
            1.0,
        ),
        (r"\bsk-proj-[a-zA-Z0-9_-]{40,}\b", SecretType.OPENAI_API_KEY, "OpenAI", 1.0),
        (r"\bsk-[a-zA-Z0-9]{32,}\b", SecretType.OPENAI_API_KEY, "OpenAI", 0.9),
        # Anthropic
        (r"\bsk-ant-[a-zA-Z0-9_-]{40,}\b", SecretType.ANTHROPIC_API_KEY, "Anthropic", 1.0),
        # Google
        (r"\bAIza[0-9A-Za-z_-]{35}\b", SecretType.GOOGLE_API_KEY, "Google", 1.0),
        # Azure
        (r"\b[a-zA-Z0-9]{32}(?=.*azure)\b", SecretType.AZURE_KEY, "Azure", 0.8),
        # GitHub
        (r"\bghp_[a-zA-Z0-9]{36}\b", SecretType.GITHUB_PAT, "GitHub", 1.0),
        (r"\bgho_[a-zA-Z0-9]{36}\b", SecretType.GITHUB_TOKEN, "GitHub", 1.0),
        (r"\bghu_[a-zA-Z0-9]{36}\b", SecretType.GITHUB_TOKEN, "GitHub", 1.0),
        (r"\bghs_[a-zA-Z0-9]{36}\b", SecretType.GITHUB_TOKEN, "GitHub", 1.0),
        (r"\bghr_[a-zA-Z0-9]{36}\b", SecretType.GITHUB_TOKEN, "GitHub", 1.0),
        # GitLab
        (r"\bglpat-[a-zA-Z0-9_-]{20,}\b", SecretType.GITLAB_TOKEN, "GitLab", 1.0),
        # Slack
        (
            r"\bxox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}\b",
            SecretType.SLACK_TOKEN,
            "Slack",
            1.0,
        ),
        # Stripe
        (r"\bsk_live_[a-zA-Z0-9]{24,}\b", SecretType.STRIPE_KEY, "Stripe", 1.0),
        (r"\bsk_test_[a-zA-Z0-9]{24,}\b", SecretType.STRIPE_KEY, "Stripe", 1.0),
        (r"\brk_live_[a-zA-Z0-9]{24,}\b", SecretType.STRIPE_KEY, "Stripe", 1.0),
        # Twilio
        (r"\bSK[a-f0-9]{32}\b", SecretType.TWILIO_KEY, "Twilio", 0.9),
        # SendGrid
        (r"\bSG\.[a-zA-Z0-9_-]{22}\.[a-zA-Z0-9_-]{43}\b", SecretType.SENDGRID_KEY, "SendGrid", 1.0),
        # Database URLs
        (
            r"(?:postgres|mysql|mongodb|redis)(?:ql)?:\/\/[^\s]+:[^\s]+@[^\s]+",
            SecretType.DATABASE_URL,
            "Database",
            1.0,
        ),
        # Private Keys
        (
            r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
            SecretType.PRIVATE_KEY,
            "Crypto",
            1.0,
        ),
        (r"-----BEGIN PGP PRIVATE KEY BLOCK-----", SecretType.PRIVATE_KEY, "PGP", 1.0),
        # JWT Tokens
        (
            r"\beyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\b",
            SecretType.JWT_TOKEN,
            "JWT",
            0.95,
        ),
        # Generic patterns (lower confidence)
        (
            r"\b(?:api[_-]?key|apikey)\s*[=:]\s*['\"]?([a-zA-Z0-9_-]{20,})['\"]?",
            SecretType.GENERIC_API_KEY,
            "Unknown",
            0.7,
        ),
        (
            r"\b(?:secret|token)\s*[=:]\s*['\"]?([a-zA-Z0-9_-]{20,})['\"]?",
            SecretType.GENERIC_SECRET,
            "Unknown",
            0.7,
        ),
        (
            r"\b(?:password|passwd|pwd)\s*[=:]\s*['\"]?([^\s'\"]{8,})['\"]?",
            SecretType.PASSWORD,
            "Unknown",
            0.8,
        ),
    ]

    def __init__(
        self,
        enabled_types: Optional[List[SecretType]] = None,
        custom_patterns: Optional[List[Tuple[str, str, str]]] = None,
        check_entropy: bool = True,
        entropy_threshold: float = 4.5,
        min_secret_length: int = 16,
        confidence_threshold: float = 0.7,
    ):
        """
        Initialize Secret Scanner.

        Args:
            enabled_types: List of secret types to detect (default: all)
            custom_patterns: Additional patterns [(pattern, name, provider), ...]
            check_entropy: Enable high-entropy string detection
            entropy_threshold: Minimum Shannon entropy for high-entropy detection
            min_secret_length: Minimum string length for entropy check
            confidence_threshold: Minimum confidence to report a finding
        """
        self.enabled_types = enabled_types or list(SecretType)
        self.check_entropy = check_entropy
        self.entropy_threshold = entropy_threshold
        self.min_secret_length = min_secret_length
        self.confidence_threshold = confidence_threshold

        # Compile patterns
        self._compiled_patterns: List[Tuple[re.Pattern, SecretType, str, float]] = []
        for pattern, secret_type, provider, confidence in self.PATTERNS:
            if secret_type in self.enabled_types:
                try:
                    self._compiled_patterns.append(
                        (
                            re.compile(pattern, re.IGNORECASE | re.MULTILINE),
                            secret_type,
                            provider,
                            confidence,
                        )
                    )
                except re.error as e:
                    logger.warning(f"Invalid pattern for {secret_type}: {e}")

        # Add custom patterns
        if custom_patterns:
            for pattern, name, provider in custom_patterns:
                try:
                    self._compiled_patterns.append(
                        (re.compile(pattern, re.IGNORECASE), SecretType.CUSTOM, provider, 0.8)
                    )
                except re.error as e:
                    logger.warning(f"Invalid custom pattern '{name}': {e}")

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0

        # Count character frequencies
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1

        # Calculate entropy
        length = len(text)
        entropy = 0.0
        for count in freq.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def _mask_secret(self, value: str, secret_type: SecretType) -> str:
        """Mask a secret value for safe logging."""
        if len(value) <= 8:
            return "***"

        # Show prefix based on secret type
        if secret_type in (SecretType.OPENAI_API_KEY, SecretType.ANTHROPIC_API_KEY):
            # Show recognizable prefix
            prefix_len = min(7, len(value) // 4)
            return f"{value[:prefix_len]}***"

        elif secret_type == SecretType.AWS_ACCESS_KEY:
            return "AKIA***"

        elif secret_type == SecretType.GITHUB_PAT:
            return "ghp_***"

        elif secret_type == SecretType.STRIPE_KEY:
            return f"{value[:7]}***"

        elif secret_type == SecretType.DATABASE_URL:
            # Mask password in connection string
            return re.sub(r"://[^:]+:[^@]+@", "://***:***@", value)

        elif secret_type == SecretType.PRIVATE_KEY:
            return "-----BEGIN PRIVATE KEY----- [REDACTED] -----END PRIVATE KEY-----"

        elif secret_type == SecretType.JWT_TOKEN:
            return "eyJ***"

        else:
            # Generic masking
            show_chars = min(4, len(value) // 4)
            return f"{value[:show_chars]}***"

    def _get_context(self, text: str, start: int, end: int, context_chars: int = 20) -> str:
        """Extract surrounding context for a match."""
        ctx_start = max(0, start - context_chars)
        ctx_end = min(len(text), end + context_chars)
        return text[ctx_start:ctx_end]

    def _detect_high_entropy_strings(self, text: str) -> List[SecretViolation]:
        """Detect high-entropy strings that might be secrets."""
        violations = []

        # Find potential tokens (alphanumeric strings)
        token_pattern = re.compile(r"\b[a-zA-Z0-9_-]{" + str(self.min_secret_length) + r",}\b")

        for match in token_pattern.finditer(text):
            value = match.group()
            entropy = self._calculate_entropy(value)

            if entropy >= self.entropy_threshold:
                # Calculate confidence based on entropy
                confidence = min(0.9, (entropy - self.entropy_threshold) / 2 + 0.6)

                violations.append(
                    SecretViolation(
                        secret_type=SecretType.HIGH_ENTROPY,
                        value=value,
                        masked_value=self._mask_secret(value, SecretType.HIGH_ENTROPY),
                        start=match.start(),
                        end=match.end(),
                        confidence=confidence,
                        context=self._get_context(text, match.start(), match.end()),
                        provider="Unknown",
                    )
                )

        return violations

    def scan(self, text: str) -> List[SecretViolation]:
        """
        Scan text for secrets.

        Args:
            text: The text to scan

        Returns:
            List of SecretViolation objects for each detected secret
        """
        violations: List[SecretViolation] = []
        seen_positions: set = set()

        # Pattern-based detection
        for pattern, secret_type, provider, confidence in self._compiled_patterns:
            for match in pattern.finditer(text):
                pos_key = (match.start(), match.end())
                if pos_key in seen_positions:
                    continue

                # Skip low confidence findings
                if confidence < self.confidence_threshold:
                    continue

                seen_positions.add(pos_key)

                # Get the matched value (use group 1 if available, else group 0)
                try:
                    value = match.group(1) if match.lastindex else match.group()
                except IndexError:
                    value = match.group()

                violations.append(
                    SecretViolation(
                        secret_type=secret_type,
                        value=value,
                        masked_value=self._mask_secret(value, secret_type),
                        start=match.start(),
                        end=match.end(),
                        confidence=confidence,
                        context=self._get_context(text, match.start(), match.end()),
                        provider=provider,
                    )
                )

        # High-entropy detection (if enabled)
        if self.check_entropy and SecretType.HIGH_ENTROPY in self.enabled_types:
            entropy_violations = self._detect_high_entropy_strings(text)
            for violation in entropy_violations:
                pos_key = (violation.start, violation.end)
                if pos_key not in seen_positions:
                    seen_positions.add(pos_key)
                    violations.append(violation)

        # Sort by position
        violations.sort(key=lambda v: v.start)

        return violations

    def redact(self, text: str, replacement: str = "[SECRET]") -> Tuple[str, List[SecretViolation]]:
        """
        Scan and redact secrets from text.

        Args:
            text: The text to redact
            replacement: The replacement string for secrets

        Returns:
            Tuple of (redacted_text, list of violations)
        """
        violations = self.scan(text)

        if not violations:
            return text, []

        # Sort by position descending to replace from end to start
        violations_sorted = sorted(violations, key=lambda v: v.start, reverse=True)

        redacted = text
        for violation in violations_sorted:
            redacted = redacted[: violation.start] + replacement + redacted[violation.end :]

        return redacted, violations

    def get_supported_types(self) -> List[str]:
        """Return list of supported secret types."""
        return [t.value for t in self.enabled_types]

    def get_provider_patterns(self) -> Dict[str, List[str]]:
        """Return patterns grouped by provider."""
        providers: Dict[str, List[str]] = {}
        for _, secret_type, provider, _ in self.PATTERNS:
            if provider not in providers:
                providers[provider] = []
            providers[provider].append(secret_type.value)
        return providers
