"""
[AI GENERATED - GOVERNANCE PROTOCOL]
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L4
Logic:       NER-based PII detection using spaCy NER + Presidio
             for high-precision name, DOB, medical entity detection.
Root Cause:  Sprint task T124 — NER-based PII detection.
Context:     Extends existing regex PII detector with ML models.
Suitability: L4 — precision matters for PII, security-critical.
──────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class NEREntityType(str, Enum):
    PERSON_NAME = "PERSON_NAME"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    MEDICAL_TERM = "MEDICAL_TERM"
    ORGANIZATION = "ORGANIZATION"
    LOCATION = "LOCATION"
    MEDICAL_CONDITION = "MEDICAL_CONDITION"
    MEDICATION = "MEDICATION"
    PROCEDURE = "PROCEDURE"


@dataclass
class NERDetection:
    entity_type: NEREntityType
    text: str
    start: int
    end: int
    confidence: float
    source: str = "rule_based"  # "rule_based" or "ml_model"


@dataclass
class NERDetectorConfig:
    enabled: bool = True
    use_ml_model: bool = False  # Set True when spaCy/Presidio available
    min_confidence: float = 0.7
    detect_names: bool = True
    detect_dob: bool = True
    detect_medical: bool = True
    detect_organizations: bool = True
    detect_locations: bool = True


class NERDetector:
    """NER-based PII detector with rule-based fallback and optional ML model."""

    def __init__(self, config: Optional[NERDetectorConfig] = None):
        self.config = config or NERDetectorConfig()
        self._nlp = None
        self._analyzer = None

        # Try to load ML models if configured
        if self.config.use_ml_model:
            self._try_load_ml_models()

        # Rule-based patterns
        self._name_patterns = self._compile_name_patterns()
        self._dob_patterns = self._compile_dob_patterns()
        self._medical_patterns = self._compile_medical_patterns()

    def _try_load_ml_models(self) -> None:
        """Attempt to load spaCy and Presidio models."""
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
        except (ImportError, OSError):
            pass  # Fall back to rule-based

        try:
            from presidio_analyzer import AnalyzerEngine
            self._analyzer = AnalyzerEngine()
        except ImportError:
            pass

    def detect(self, text: str) -> list[NERDetection]:
        """Detect NER entities in text using available methods."""
        if not self.config.enabled or not text:
            return []

        detections: list[NERDetection] = []

        # ML-based detection (if available)
        if self._nlp is not None:
            detections.extend(self._detect_with_spacy(text))

        if self._analyzer is not None:
            detections.extend(self._detect_with_presidio(text))

        # Rule-based detection (always runs as fallback/supplement)
        detections.extend(self._detect_with_rules(text))

        # Deduplicate overlapping detections
        detections = self._deduplicate(detections)

        # Filter by confidence
        detections = [
            d for d in detections if d.confidence >= self.config.min_confidence
        ]

        return detections

    def _detect_with_spacy(self, text: str) -> list[NERDetection]:
        """Detect entities using spaCy NER model."""
        detections: list[NERDetection] = []
        doc = self._nlp(text)

        entity_map = {
            "PERSON": NEREntityType.PERSON_NAME,
            "ORG": NEREntityType.ORGANIZATION,
            "GPE": NEREntityType.LOCATION,
            "LOC": NEREntityType.LOCATION,
        }

        for ent in doc.ents:
            ner_type = entity_map.get(ent.label_)
            if ner_type is None:
                continue

            if ner_type == NEREntityType.PERSON_NAME and not self.config.detect_names:
                continue
            if ner_type == NEREntityType.ORGANIZATION and not self.config.detect_organizations:
                continue
            if ner_type == NEREntityType.LOCATION and not self.config.detect_locations:
                continue

            detections.append(NERDetection(
                entity_type=ner_type,
                text=ent.text,
                start=ent.start_char,
                end=ent.end_char,
                confidence=0.85,
                source="spacy",
            ))

        return detections

    def _detect_with_presidio(self, text: str) -> list[NERDetection]:
        """Detect entities using Microsoft Presidio."""
        detections: list[NERDetection] = []

        entities_to_detect = []
        if self.config.detect_names:
            entities_to_detect.append("PERSON")
        if self.config.detect_locations:
            entities_to_detect.extend(["LOCATION", "GPE"])
        if self.config.detect_organizations:
            entities_to_detect.append("ORG")
        if self.config.detect_dob:
            entities_to_detect.append("DATE_TIME")

        if not entities_to_detect:
            return detections

        results = self._analyzer.analyze(
            text=text,
            entities=entities_to_detect,
            language="en",
        )

        presidio_map = {
            "PERSON": NEREntityType.PERSON_NAME,
            "LOCATION": NEREntityType.LOCATION,
            "GPE": NEREntityType.LOCATION,
            "ORG": NEREntityType.ORGANIZATION,
            "DATE_TIME": NEREntityType.DATE_OF_BIRTH,
        }

        for result in results:
            ner_type = presidio_map.get(result.entity_type)
            if ner_type is None:
                continue

            detections.append(NERDetection(
                entity_type=ner_type,
                text=text[result.start:result.end],
                start=result.start,
                end=result.end,
                confidence=result.score,
                source="presidio",
            ))

        return detections

    def _detect_with_rules(self, text: str) -> list[NERDetection]:
        """Rule-based NER detection as fallback."""
        detections: list[NERDetection] = []

        if self.config.detect_names:
            detections.extend(self._detect_names(text))

        if self.config.detect_dob:
            detections.extend(self._detect_dob(text))

        if self.config.detect_medical:
            detections.extend(self._detect_medical(text))

        return detections

    def _detect_names(self, text: str) -> list[NERDetection]:
        """Detect person names using patterns."""
        detections: list[NERDetection] = []

        for pattern in self._name_patterns:
            for match in pattern.finditer(text):
                name = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group()
                # Filter out common false positives
                if name.lower() in _COMMON_WORDS:
                    continue
                if len(name.split()) < 2:
                    continue  # Require at least first + last name

                detections.append(NERDetection(
                    entity_type=NEREntityType.PERSON_NAME,
                    text=name.strip(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.75,
                    source="rule_based",
                ))

        return detections

    def _detect_dob(self, text: str) -> list[NERDetection]:
        """Detect dates of birth using patterns."""
        detections: list[NERDetection] = []

        for pattern in self._dob_patterns:
            for match in pattern.finditer(text):
                detections.append(NERDetection(
                    entity_type=NEREntityType.DATE_OF_BIRTH,
                    text=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.80,
                    source="rule_based",
                ))

        return detections

    def _detect_medical(self, text: str) -> list[NERDetection]:
        """Detect medical terms, conditions, medications."""
        detections: list[NERDetection] = []
        text_lower = text.lower()

        for term_type, terms in _MEDICAL_TERMS.items():
            for term in terms:
                idx = text_lower.find(term)
                while idx != -1:
                    ner_type = NEREntityType.MEDICAL_CONDITION
                    if term_type == "medication":
                        ner_type = NEREntityType.MEDICATION
                    elif term_type == "procedure":
                        ner_type = NEREntityType.PROCEDURE
                    elif term_type == "general":
                        ner_type = NEREntityType.MEDICAL_TERM

                    detections.append(NERDetection(
                        entity_type=ner_type,
                        text=text[idx:idx + len(term)],
                        start=idx,
                        end=idx + len(term),
                        confidence=0.85,
                        source="rule_based",
                    ))
                    idx = text_lower.find(term, idx + 1)

        return detections

    @staticmethod
    def _compile_name_patterns() -> list[re.Pattern]:
        """Compile regex patterns for person name detection."""
        return [
            # "My name is John Smith" / "patient: Jane Doe"
            re.compile(
                r"(?:my name is|patient[:\s]+|dr\.?\s+|mr\.?\s+|mrs\.?\s+|ms\.?\s+|"
                r"contact[:\s]+|from[:\s]+|signed[:\s]+|by[:\s]+)"
                r"\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
                re.IGNORECASE,
            ),
            # Capitalized first + last name in isolation (higher false positive rate)
            re.compile(
                r"\b([A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,20})\b",
            ),
        ]

    @staticmethod
    def _compile_dob_patterns() -> list[re.Pattern]:
        """Compile regex patterns for date of birth detection."""
        return [
            # "DOB: 01/15/1990" or "born on 1990-01-15"
            re.compile(
                r"(?:dob|date of birth|born|birthday|birth date)[:\s]*"
                r"(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})",
                re.IGNORECASE,
            ),
            # Standalone date near age/birth context
            re.compile(
                r"(?:born|age|dob)\s+(?:on\s+)?(\w+\s+\d{1,2},?\s+\d{4})",
                re.IGNORECASE,
            ),
        ]

    @staticmethod
    def _compile_medical_patterns() -> list[re.Pattern]:
        """Compile regex patterns for medical term detection."""
        return [
            re.compile(
                r"\b(?:diagnosed with|symptoms? of|treatment for|prescribed)\s+(\w[\w\s]{3,40})",
                re.IGNORECASE,
            ),
        ]

    @staticmethod
    def _deduplicate(detections: list[NERDetection]) -> list[NERDetection]:
        """Remove overlapping detections, keeping highest confidence."""
        if not detections:
            return detections

        # Sort by start position, then by confidence (descending)
        sorted_dets = sorted(detections, key=lambda d: (d.start, -d.confidence))

        result: list[NERDetection] = [sorted_dets[0]]
        for det in sorted_dets[1:]:
            last = result[-1]
            if det.start < last.end:
                # Overlapping — keep higher confidence
                if det.confidence > last.confidence:
                    result[-1] = det
            else:
                result.append(det)

        return result

    def redact(self, text: str, detections: Optional[list[NERDetection]] = None) -> str:
        """Redact detected entities from text."""
        if detections is None:
            detections = self.detect(text)

        if not detections:
            return text

        # Sort by start position descending for safe replacement
        sorted_dets = sorted(detections, key=lambda d: d.start, reverse=True)

        result = text
        counters: dict[str, int] = {}
        for det in sorted_dets:
            etype = det.entity_type.value
            counters[etype] = counters.get(etype, 0) + 1
            placeholder = f"[{etype}_{counters[etype]}]"
            result = result[:det.start] + placeholder + result[det.end:]

        return result


# Common words to exclude from name detection
_COMMON_WORDS = frozenset({
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "her",
    "was", "one", "our", "out", "day", "get", "has", "him", "his", "how",
    "its", "may", "new", "now", "old", "see", "way", "who", "did", "got",
    "let", "say", "she", "too", "use", "data", "that", "this", "with",
    "have", "from", "they", "been", "will", "more", "when", "very",
    "just", "know", "take", "come", "could", "than", "look", "only",
    "good", "give", "most", "also", "back", "after", "work", "first",
    "even", "want", "because", "these", "some", "make", "like",
    "long", "time", "what", "about", "which", "their", "each",
    "open", "last", "next", "should", "would", "dear", "hello",
})

# Medical terminology for rule-based detection
_MEDICAL_TERMS: dict[str, list[str]] = {
    "condition": [
        "diabetes", "hypertension", "asthma", "cancer", "hiv", "aids",
        "epilepsy", "depression", "anxiety", "bipolar", "schizophrenia",
        "alzheimer", "parkinson", "arthritis", "fibromyalgia", "lupus",
        "multiple sclerosis", "hepatitis", "tuberculosis", "pneumonia",
        "stroke", "heart attack", "myocardial infarction", "copd",
        "chronic pain", "ptsd", "adhd", "autism",
    ],
    "medication": [
        "metformin", "insulin", "lisinopril", "atorvastatin", "amlodipine",
        "metoprolol", "omeprazole", "losartan", "gabapentin", "sertraline",
        "fluoxetine", "amoxicillin", "prednisone", "ibuprofen", "aspirin",
        "warfarin", "levothyroxine", "albuterol", "hydrocodone", "oxycodone",
        "morphine", "fentanyl", "adderall", "ritalin", "xanax", "valium",
    ],
    "procedure": [
        "surgery", "biopsy", "mri", "ct scan", "x-ray", "ultrasound",
        "colonoscopy", "endoscopy", "chemotherapy", "radiation therapy",
        "dialysis", "transplant", "amputation", "catheterization",
        "mammography", "laparoscopy", "angioplasty",
    ],
    "general": [
        "diagnosis", "prognosis", "treatment plan", "medical record",
        "lab results", "blood test", "pathology", "radiology",
        "prescription", "dosage", "side effects", "allergic reaction",
        "medical history", "family history", "blood pressure",
        "cholesterol", "hemoglobin", "white blood cell",
    ],
}
