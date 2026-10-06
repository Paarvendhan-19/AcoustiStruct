"""Semantic extraction engine — extracts structured fields from transcripts.

Provider interface + mock implementation that simulates realistic extraction
with proper confidence, evidence, and uncertainty handling.
"""

from __future__ import annotations

import asyncio
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class FieldEvidence:
    """Evidence linking an extracted value to its source."""
    text: str
    start: float
    end: float
    segment_index: int | None = None


@dataclass
class ExtractedFieldResult:
    """A single extracted field with confidence and evidence."""
    field_key: str
    value: Any
    confidence: float
    status: str = "ai_extracted"
    # ai_extracted | needs_review | not_found | ambiguous
    certainty: str = "explicit"
    # explicit | inferred | uncertain | approximate | negated
    evidence: FieldEvidence | None = None
    raw_value: str | None = None  # Original text before normalization


@dataclass
class ExtractionResult:
    """Complete extraction result for a session."""
    fields: list[ExtractedFieldResult]
    provider: str = ""
    model: str = ""
    model_version: str = ""
    prompt_version: str = ""
    latency_ms: int = 0
    warnings: list[str] = field(default_factory=list)


class SemanticExtractor(ABC):
    """Abstract interface for semantic extraction providers."""

    @abstractmethod
    async def extract(
        self,
        transcript: str,
        segments: list[dict],
        schema: list[dict],
        language: str = "ta",
        dialect: str | None = None,
        domain: str = "agriculture",
        terminology: dict | None = None,
    ) -> ExtractionResult:
        """Extract structured fields from a transcript using a schema definition."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


class MockSemanticExtractor(SemanticExtractor):
    """Mock extractor returning realistic Tamil agriculture extractions.

    Maps scenario transcripts to pre-built extraction results with
    varying confidence levels, evidence, and deliberate uncertainty.
    """

    MOCK_EXTRACTIONS = {
        "tamil_agriculture_01": [
            ExtractedFieldResult(
                field_key="farmer_name",
                value="Ramasamy",
                confidence=0.97,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("என் பெயர் ராமசாமி.", 0.0, 1.8, 0),
                raw_value="ராமசாமி",
            ),
            ExtractedFieldResult(
                field_key="village",
                value="Thirumangalam",
                confidence=0.94,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("நான் மதுரை மாவட்டம் திருமங்கலம் கிராமத்தில் இருக்கிறேன்.", 2.0, 5.2, 1),
                raw_value="திருமங்கலம்",
            ),
            ExtractedFieldResult(
                field_key="district",
                value="Madurai",
                confidence=0.94,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("நான் மதுரை மாவட்டம் திருமங்கலம் கிராமத்தில் இருக்கிறேன்.", 2.0, 5.2, 1),
                raw_value="மதுரை",
            ),
            ExtractedFieldResult(
                field_key="land_area",
                value=2.5,
                confidence=0.92,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("என்கிட்ட இரண்டரை ஏக்கர் நிலம் இருக்கு.", 5.5, 8.1, 2),
                raw_value="இரண்டரை",
            ),
            ExtractedFieldResult(
                field_key="land_area_unit",
                value="acre",
                confidence=0.95,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("என்கிட்ட இரண்டரை ஏக்கர் நிலம் இருக்கு.", 5.5, 8.1, 2),
                raw_value="ஏக்கர்",
            ),
            ExtractedFieldResult(
                field_key="crop",
                value="rice",
                confidence=0.96,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("நெல் பயிர் போட்டிருக்கேன்.", 8.3, 10.0, 3),
                raw_value="நெல்",
            ),
            ExtractedFieldResult(
                field_key="irrigation_type",
                value="well_irrigation",
                confidence=0.91,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("கிணத்து நீர்ப்பாசனம் பயன்படுத்துறேன்.", 10.2, 12.8, 4),
                raw_value="கிணத்து நீர்ப்பாசனம்",
            ),
            ExtractedFieldResult(
                field_key="water_availability",
                value="insufficient",
                confidence=0.88,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("இந்த வருஷம் மழை குறைவா இருக்கு.", 13.0, 15.5, 5),
                raw_value="குறைவா",
            ),
            ExtractedFieldResult(
                field_key="rainfall_condition",
                value="below_normal",
                confidence=0.88,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("இந்த வருஷம் மழை குறைவா இருக்கு.", 13.0, 15.5, 5),
                raw_value="மழை குறைவா",
            ),
            ExtractedFieldResult(
                field_key="soil_condition",
                value="moderate",
                confidence=0.90,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("மண் வளம் நடுத்தரமா இருக்கு.", 15.8, 18.0, 6),
                raw_value="நடுத்தரமா",
            ),
            ExtractedFieldResult(
                field_key="fertilizer_usage",
                value="urea",
                confidence=0.95,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("யூரியா உரம் போட்டிருக்கேன்.", 18.2, 20.5, 7),
                raw_value="யூரியா உரம்",
            ),
            ExtractedFieldResult(
                field_key="pest_problem",
                value="stem_borer",
                confidence=0.85,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("காய்ப்புழு பாதிப்பு இருக்கு.", 20.8, 23.0, 8),
                raw_value="காய்ப்புழு",
            ),
            ExtractedFieldResult(
                field_key="crop_damage",
                value=30,
                confidence=0.82,
                status="needs_review",
                certainty="approximate",
                evidence=FieldEvidence("சுமார் முப்பது சதவிகிதம் பயிர் சேதம் ஆயிருக்கு.", 23.2, 26.5, 9),
                raw_value="சுமார் முப்பது சதவிகிதம்",
            ),
            ExtractedFieldResult(
                field_key="estimated_loss",
                value=50000,
                confidence=0.72,
                status="needs_review",
                certainty="uncertain",
                evidence=FieldEvidence("ஏறக்குறைய ஐம்பதாயிரம் ரூபாய் நஷ்டம் இருக்கும்னு நினைக்கிறேன்.", 26.8, 30.5, 10),
                raw_value="ஏறக்குறைய ஐம்பதாயிரம் ரூபாய்",
            ),
            ExtractedFieldResult(
                field_key="sowing_date",
                value="2026-06-01",
                confidence=0.88,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("ஜூன் மாசம் விதைச்சேன்.", 30.8, 32.5, 11),
                raw_value="ஜூன் மாசம்",
            ),
            ExtractedFieldResult(
                field_key="harvest_date",
                value="2026-11-01",
                confidence=0.78,
                status="needs_review",
                certainty="uncertain",
                evidence=FieldEvidence("நவம்பர் மாசம் அறுவடை செய்யலாம்னு நினைக்கிறேன்.", 32.8, 36.0, 12),
                raw_value="நவம்பர் மாசம்",
            ),
            ExtractedFieldResult(
                field_key="remarks",
                value=None,
                confidence=0.0,
                status="not_found",
                certainty="explicit",
            ),
        ],
        "tamil_agriculture_02": [
            ExtractedFieldResult(
                field_key="farmer_name",
                value="Murugan",
                confidence=0.96,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("என் பெயர் முருகன்.", 0.0, 1.5, 0),
                raw_value="முருகன்",
            ),
            ExtractedFieldResult(
                field_key="village",
                value=None,
                confidence=0.35,
                status="needs_review",
                certainty="uncertain",
                evidence=FieldEvidence("பெரிய... அதாவது பெரியகுளம் பக்கத்தில் இருக்கிற சின்ன கிராமம்.", 1.8, 5.5, 1),
                raw_value="பெரியகுளம் பக்கத்தில் சின்ன கிராமம்",
            ),
            ExtractedFieldResult(
                field_key="district",
                value="Theni",
                confidence=0.65,
                status="needs_review",
                certainty="inferred",
                evidence=FieldEvidence("பெரிய... அதாவது பெரியகுளம் பக்கத்தில் இருக்கிற சின்ன கிராமம்.", 1.8, 5.5, 1),
                raw_value="பெரியகுளம்",
            ),
            ExtractedFieldResult(
                field_key="land_area",
                value=3.0,
                confidence=0.94,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("மூணு ஏக்கர் நிலம்.", 5.8, 7.5, 2),
                raw_value="மூணு",
            ),
            ExtractedFieldResult(
                field_key="land_area_unit",
                value="acre",
                confidence=0.95,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("மூணு ஏக்கர் நிலம்.", 5.8, 7.5, 2),
            ),
            ExtractedFieldResult(
                field_key="crop",
                value="banana",
                confidence=0.95,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("வாழை பயிர் போட்டிருக்கேன்.", 7.8, 9.5, 3),
                raw_value="வாழை",
            ),
            ExtractedFieldResult(
                field_key="irrigation_type",
                value="borewell",
                confidence=0.91,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("போர்வெல் தண்ணி பயன்படுத்துறேன்.", 9.8, 12.0, 4),
                raw_value="போர்வெல்",
            ),
            ExtractedFieldResult(
                field_key="water_availability",
                value="adequate",
                confidence=0.82,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("மழை பரவாயில்லை ஆனா போதாது.", 12.3, 14.5, 5),
                raw_value="பரவாயில்லை ஆனா போதாது",
            ),
            ExtractedFieldResult(
                field_key="soil_condition",
                value="good",
                confidence=0.93,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("மண் நல்லா இருக்கு.", 14.8, 16.0, 6),
                raw_value="நல்லா",
            ),
            ExtractedFieldResult(
                field_key="fertilizer_usage",
                value="dap_fertilizer",
                confidence=0.92,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("DAP உரம் போட்டேன்.", 16.3, 18.0, 7),
                raw_value="DAP",
            ),
            ExtractedFieldResult(
                field_key="pest_problem",
                value="none",
                confidence=0.95,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("பூச்சி பிரச்சனை இல்லை.", 18.3, 20.0, 8),
            ),
            ExtractedFieldResult(
                field_key="crop_damage",
                value=10,
                confidence=0.86,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("பத்து சதவீதம் சேதம் இருக்கு காத்துல.", 20.3, 23.0, 9),
                raw_value="பத்து சதவீதம்",
            ),
            ExtractedFieldResult(
                field_key="estimated_loss",
                value=20000,
                confidence=0.78,
                status="needs_review",
                certainty="uncertain",
                evidence=FieldEvidence("இருபதாயிரம் ரூபா நஷ்டம் இருக்கும்.", 23.3, 25.5, 10),
                raw_value="இருபதாயிரம் ரூபா",
            ),
        ],
        "tamil_uncertain_01": [
            ExtractedFieldResult(
                field_key="farmer_name",
                value=None,
                confidence=0.42,
                status="needs_review",
                certainty="uncertain",
                evidence=FieldEvidence("என் பெயர் செல்வம்... அல்லது செல்வராஜ்.", 0.0, 3.0, 0),
                raw_value="செல்வம் / செல்வராஜ்",
            ),
            ExtractedFieldResult(
                field_key="village",
                value=None,
                confidence=0.30,
                status="needs_review",
                certainty="uncertain",
                evidence=FieldEvidence("எங்க ஊர்... ம்... அது கோவை பக்கம் தான்.", 3.3, 7.0, 1),
                raw_value="கோவை பக்கம்",
            ),
            ExtractedFieldResult(
                field_key="district",
                value="Coimbatore",
                confidence=0.60,
                status="needs_review",
                certainty="inferred",
                evidence=FieldEvidence("எங்க ஊர்... ம்... அது கோவை பக்கம் தான்.", 3.3, 7.0, 1),
                raw_value="கோவை",
            ),
            ExtractedFieldResult(
                field_key="land_area",
                value=1.0,
                confidence=0.55,
                status="needs_review",
                certainty="uncertain",
                evidence=FieldEvidence("நிலம் ஒரு ஏக்கர் இருக்கும்னு நினைக்கிறேன், சரியா தெரியல.", 7.3, 11.5, 2),
                raw_value="ஒரு ஏக்கர் இருக்கும்னு நினைக்கிறேன்",
            ),
            ExtractedFieldResult(
                field_key="land_area_unit",
                value="acre",
                confidence=0.90,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("நிலம் ஒரு ஏக்கர் இருக்கும்னு நினைக்கிறேன், சரியா தெரியல.", 7.3, 11.5, 2),
            ),
            ExtractedFieldResult(
                field_key="crop",
                value="coconut",
                confidence=0.92,
                status="ai_extracted",
                certainty="explicit",
                evidence=FieldEvidence("தென்னை போட்டிருக்கேன்.", 11.8, 13.5, 3),
                raw_value="தென்னை",
            ),
        ],
    }

    async def extract(
        self,
        transcript: str,
        segments: list[dict],
        schema: list[dict],
        language: str = "ta",
        dialect: str | None = None,
        domain: str = "agriculture",
        terminology: dict | None = None,
    ) -> ExtractionResult:
        """Return mock extraction results based on transcript matching."""
        await asyncio.sleep(random.uniform(0.8, 2.0))
        start_time = time.monotonic()

        # Try to match transcript to known scenario
        scenario_key = None
        for key, fields in self.MOCK_EXTRACTIONS.items():
            # Check if the first field's evidence text is in the transcript
            if fields and fields[0].evidence and fields[0].evidence.text in transcript:
                scenario_key = key
                break

        if scenario_key is None:
            scenario_key = "tamil_agriculture_01"

        fields = self.MOCK_EXTRACTIONS[scenario_key]

        # Filter to only fields that exist in the provided schema
        schema_keys = {f.get("field_key", f.get("id", "")) for f in schema} if schema else set()
        if schema_keys:
            filtered = [f for f in fields if f.field_key in schema_keys]
        else:
            filtered = fields

        latency = int((time.monotonic() - start_time) * 1000)

        warnings = []
        # Detect fields that need clarification
        needs_review = [f for f in filtered if f.status == "needs_review"]
        if needs_review:
            warnings.append(f"{len(needs_review)} field(s) need human review due to low confidence or ambiguity")

        return ExtractionResult(
            fields=filtered,
            provider="mock",
            model="mock-semantic-v1",
            model_version="1.0.0",
            prompt_version="extraction_v1",
            latency_ms=latency,
            warnings=warnings,
        )

    @property
    def provider_name(self) -> str:
        return "mock"


def get_semantic_extractor(provider_name: str, **kwargs) -> SemanticExtractor:
    """Factory for semantic extraction providers."""
    providers = {"mock": MockSemanticExtractor}
    cls = providers.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown semantic provider: {provider_name}")
    return cls(**kwargs)
