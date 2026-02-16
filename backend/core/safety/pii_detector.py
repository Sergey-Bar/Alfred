# [AI GENERATED]
# Model: GitHub Copilot (Claude Opus 4.5)
# Logic: PII Detection Engine for prompt safety using regex patterns and optional Presidio.
# Why: Prevents sensitive data (SSNs, credit cards, emails, phones) from being sent to LLMs.
# Root Cause: Enterprise compliance (GDPR Article 32, CCPA, HIPAA, PCI-DSS) requires PII filtering.
# Context: Integrates with SafetyPipeline for pre-request scanning. Supports redaction mode.
# Model Suitability: Claude Opus 4.5 used for critical security infrastructure.

"""
PII Detection Engine

Detects Personally Identifiable Information (PII) in prompts:
- Social Security Numbers (SSN)
- Credit Card Numbers
- Email Addresses
- Phone Numbers
- US Physical Addresses
- IP Addresses
- Dates of Birth

Uses regex patterns with optional Presidio integration for advanced NER-based detection.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class PIIType(str, Enum):
    """Types of PII that can be detected."""
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    BANK_ACCOUNT = "bank_account"
    CUSTOM = "custom"


@dataclass
class PIIViolation:
    """Represents a detected PII violation."""
    pii_type: PIIType
    value: str
    masked_value: str
    start: int
    end: int
    confidence: float = 1.0
    context: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "type": self.pii_type.value,
            "value": self.masked_value,  # Never expose full value in logs
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "context": self.context
        }


class PIIDetector:
    """
    PII Detection Engine.
    
    Detects and optionally redacts PII from text using regex patterns
    and optional Presidio NLP-based detection.
    
    Example:
        detector = PIIDetector()
        violations = detector.scan("My SSN is 123-45-6789")
        # Returns [PIIViolation(type=SSN, masked_value="***-**-6789", ...)]
    """
    
    # Regex patterns for common PII types
    PATTERNS: Dict[PIIType, Tuple[str, str]] = {
        # (pattern, mask_format)
        PIIType.SSN: (
            r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",
            "***-**-{last4}"
        ),
        PIIType.CREDIT_CARD: (
            r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
            "****-****-****-{last4}"
        ),
        PIIType.EMAIL: (
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "{first3}***@{domain}"
        ),
        PIIType.PHONE: (
            r"\b(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "(***) ***-{last4}"
        ),
        PIIType.IP_ADDRESS: (
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "{first}.{second}.***.***"
        ),
        PIIType.DATE_OF_BIRTH: (
            r"\b(?:0?[1-9]|1[0-2])[-/](?:0?[1-9]|[12]\d|3[01])[-/](?:19|20)\d{2}\b",
            "**/**/****"
        ),
        PIIType.PASSPORT: (
            r"\b[A-Z]{1,2}\d{6,9}\b",
            "**{last4}"
        ),
        PIIType.BANK_ACCOUNT: (
            r"\b\d{8,17}\b",
            "****{last4}"
        ),
    }
    
    # US State abbreviations for address detection
    US_STATES = r"(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)"
    ADDRESS_PATTERN = rf"\b\d{{1,5}}\s+\w+(?:\s+\w+)*\s*,?\s*\w+\s*,?\s*{US_STATES}\s*\d{{5}}(?:-\d{{4}})?\b"
    
    def __init__(
        self,
        enabled_types: Optional[List[PIIType]] = None,
        custom_patterns: Optional[Dict[str, str]] = None,
        use_presidio: bool = False,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize PII Detector.
        
        Args:
            enabled_types: List of PII types to detect (default: all)
            custom_patterns: Additional regex patterns {name: pattern}
            use_presidio: Use Microsoft Presidio for NER-based detection
            confidence_threshold: Minimum confidence for presidio detections
        """
        self.enabled_types = enabled_types or list(PIIType)
        self.custom_patterns = custom_patterns or {}
        self.confidence_threshold = confidence_threshold
        
        # Compile regex patterns for performance
        self._compiled_patterns: Dict[PIIType, re.Pattern] = {}
        for pii_type in self.enabled_types:
            if pii_type in self.PATTERNS:
                pattern, _ = self.PATTERNS[pii_type]
                self._compiled_patterns[pii_type] = re.compile(pattern, re.IGNORECASE)
        
        # Add address pattern
        if PIIType.ADDRESS in self.enabled_types:
            self._compiled_patterns[PIIType.ADDRESS] = re.compile(
                self.ADDRESS_PATTERN, re.IGNORECASE
            )
        
        # Compile custom patterns
        self._custom_compiled: Dict[str, re.Pattern] = {}
        for name, pattern in self.custom_patterns.items():
            try:
                self._custom_compiled[name] = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                logger.warning(f"Invalid custom pattern '{name}': {e}")
        
        # Optional Presidio integration
        self.presidio_analyzer = None
        self.presidio_anonymizer = None
        if use_presidio:
            self._init_presidio()
    
    def _init_presidio(self) -> None:
        """Initialize Microsoft Presidio for NER-based detection."""
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine
            
            self.presidio_analyzer = AnalyzerEngine()
            self.presidio_anonymizer = AnonymizerEngine()
            logger.info("Presidio NER-based PII detection enabled")
        except ImportError:
            logger.warning(
                "Presidio not installed. Install with: "
                "pip install presidio-analyzer presidio-anonymizer"
            )
    
    def _mask_value(self, value: str, pii_type: PIIType) -> str:
        """Mask a PII value for safe logging."""
        if pii_type == PIIType.SSN:
            # Show only last 4 digits
            digits = re.sub(r"\D", "", value)
            return f"***-**-{digits[-4:]}" if len(digits) >= 4 else "***-**-****"
        
        elif pii_type == PIIType.CREDIT_CARD:
            digits = re.sub(r"\D", "", value)
            return f"****-****-****-{digits[-4:]}" if len(digits) >= 4 else "****-****-****-****"
        
        elif pii_type == PIIType.EMAIL:
            if "@" in value:
                local, domain = value.split("@", 1)
                masked_local = local[:3] + "***" if len(local) > 3 else "***"
                return f"{masked_local}@{domain}"
            return "***@***.***"
        
        elif pii_type == PIIType.PHONE:
            digits = re.sub(r"\D", "", value)
            return f"(***) ***-{digits[-4:]}" if len(digits) >= 4 else "(***) ***-****"
        
        elif pii_type == PIIType.IP_ADDRESS:
            parts = value.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.***.***"
            return "***.***.***.***"
        
        elif pii_type in (PIIType.DATE_OF_BIRTH, PIIType.ADDRESS):
            return "[REDACTED]"
        
        else:
            # Generic masking: show first/last 2 chars
            if len(value) > 4:
                return f"{value[:2]}***{value[-2:]}"
            return "****"
    
    def _get_context(self, text: str, start: int, end: int, context_chars: int = 20) -> str:
        """Extract surrounding context for a match."""
        ctx_start = max(0, start - context_chars)
        ctx_end = min(len(text), end + context_chars)
        return text[ctx_start:ctx_end]
    
    def scan(self, text: str) -> List[PIIViolation]:
        """
        Scan text for PII violations.
        
        Args:
            text: The text to scan
            
        Returns:
            List of PIIViolation objects for each detected PII
        """
        violations: List[PIIViolation] = []
        seen_positions: set = set()  # Avoid duplicate detections
        
        # Regex-based detection
        for pii_type, pattern in self._compiled_patterns.items():
            for match in pattern.finditer(text):
                pos_key = (match.start(), match.end())
                if pos_key in seen_positions:
                    continue
                seen_positions.add(pos_key)
                
                value = match.group()
                violations.append(PIIViolation(
                    pii_type=pii_type,
                    value=value,
                    masked_value=self._mask_value(value, pii_type),
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0,  # Regex matches are deterministic
                    context=self._get_context(text, match.start(), match.end())
                ))
        
        # Custom pattern detection
        for name, pattern in self._custom_compiled.items():
            for match in pattern.finditer(text):
                pos_key = (match.start(), match.end())
                if pos_key in seen_positions:
                    continue
                seen_positions.add(pos_key)
                
                value = match.group()
                violations.append(PIIViolation(
                    pii_type=PIIType.CUSTOM,
                    value=value,
                    masked_value=f"[{name.upper()}]",
                    start=match.start(),
                    end=match.end(),
                    confidence=1.0,
                    context=self._get_context(text, match.start(), match.end())
                ))
        
        # Presidio NER-based detection (if enabled)
        if self.presidio_analyzer:
            violations.extend(self._scan_with_presidio(text, seen_positions))
        
        # Sort by position
        violations.sort(key=lambda v: v.start)
        
        return violations
    
    def _scan_with_presidio(
        self, 
        text: str, 
        seen_positions: set
    ) -> List[PIIViolation]:
        """Use Presidio for NER-based PII detection."""
        violations = []
        
        try:
            results = self.presidio_analyzer.analyze(
                text=text,
                language="en",
                entities=None  # Detect all supported entities
            )
            
            for result in results:
                if result.score < self.confidence_threshold:
                    continue
                
                pos_key = (result.start, result.end)
                if pos_key in seen_positions:
                    continue
                seen_positions.add(pos_key)
                
                value = text[result.start:result.end]
                
                # Map Presidio entity types to our PIIType
                pii_type = self._map_presidio_entity(result.entity_type)
                
                violations.append(PIIViolation(
                    pii_type=pii_type,
                    value=value,
                    masked_value=self._mask_value(value, pii_type),
                    start=result.start,
                    end=result.end,
                    confidence=result.score,
                    context=self._get_context(text, result.start, result.end)
                ))
        
        except Exception as e:
            logger.error(f"Presidio analysis failed: {e}")
        
        return violations
    
    def _map_presidio_entity(self, entity_type: str) -> PIIType:
        """Map Presidio entity types to our PIIType enum."""
        mapping = {
            "US_SSN": PIIType.SSN,
            "CREDIT_CARD": PIIType.CREDIT_CARD,
            "EMAIL_ADDRESS": PIIType.EMAIL,
            "PHONE_NUMBER": PIIType.PHONE,
            "IP_ADDRESS": PIIType.IP_ADDRESS,
            "DATE_TIME": PIIType.DATE_OF_BIRTH,
            "US_PASSPORT": PIIType.PASSPORT,
            "US_DRIVER_LICENSE": PIIType.DRIVER_LICENSE,
            "US_BANK_NUMBER": PIIType.BANK_ACCOUNT,
            "LOCATION": PIIType.ADDRESS,
        }
        return mapping.get(entity_type, PIIType.CUSTOM)
    
    def redact(self, text: str, replacement: str = "[REDACTED]") -> Tuple[str, List[PIIViolation]]:
        """
        Scan and redact PII from text.
        
        Args:
            text: The text to redact
            replacement: The replacement string for PII
            
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
            redacted = (
                redacted[:violation.start] + 
                replacement + 
                redacted[violation.end:]
            )
        
        return redacted, violations
    
    def get_supported_types(self) -> List[str]:
        """Return list of supported PII types."""
        return [t.value for t in self.enabled_types]
