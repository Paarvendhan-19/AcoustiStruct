"""Dialect classification and lexicon system."""

from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DialectPrediction:
    dialect: str  # northern_tamil | southern_tamil | western_tamil | central_tamil | unknown
    confidence: float
    status: str = "probable"  # confirmed | probable | uncertain | unknown
    features: list[str] = field(default_factory=list)


@dataclass
class LexiconEntry:
    surface_form: str
    language: str
    dialect: str
    canonical_concept: str
    domain: str
    notes: str = ""
    confidence: float = 1.0
    source: str = "verified"  # verified | heuristic | model_generated


class DialectClassifier(ABC):
    @abstractmethod
    async def classify(self, text: str, language: str = "ta") -> DialectPrediction:
        ...


class MockDialectClassifier(DialectClassifier):
    """Mock classifier that uses keyword heuristics for demo."""

    # Dialect markers (simplified for demo — NOT linguistically authoritative)
    DIALECT_MARKERS = {
        "southern_tamil": ["இருக்கு", "போட்டிருக்கேன்", "பயன்படுத்துறேன்", "மாசம்"],
        "western_tamil": ["இருக்குங்க", "பண்ணுங்க", "சொல்லுங்க"],
        "northern_tamil": ["இருக்குது", "பண்றது", "சொல்றது"],
        "central_tamil": ["இருக்கிறது", "செய்கிறேன்", "போகிறேன்"],
    }

    async def classify(self, text: str, language: str = "ta") -> DialectPrediction:
        await asyncio.sleep(0.05)

        if language != "ta":
            return DialectPrediction(dialect="unknown", confidence=0.0, status="unknown")

        scores = {}
        for dialect, markers in self.DIALECT_MARKERS.items():
            score = sum(1 for m in markers if m in text)
            if score > 0:
                scores[dialect] = score

        if not scores:
            return DialectPrediction(dialect="unknown", confidence=0.3, status="uncertain")

        best = max(scores, key=scores.get)
        total = sum(scores.values())
        conf = scores[best] / max(total, 1) * 0.85  # Cap at 0.85 — never claim certainty

        status = "probable" if conf > 0.5 else "uncertain"
        return DialectPrediction(
            dialect=best,
            confidence=round(conf, 2),
            status=status,
            features=[m for m in self.DIALECT_MARKERS[best] if m in text],
        )


class DialectLexicon:
    """Configurable dialect/domain terminology lookup."""

    def __init__(self):
        self._entries: list[LexiconEntry] = []
        self._load_seed_lexicon()

    def _load_seed_lexicon(self):
        """Load seed Tamil agriculture terminology."""
        seed = [
            # Crop names
            LexiconEntry("நெல்", "ta", "southern_tamil", "rice", "agriculture", "paddy/rice"),
            LexiconEntry("நெல்லு", "ta", "western_tamil", "rice", "agriculture", "dialectal form"),
            LexiconEntry("வாழை", "ta", "southern_tamil", "banana", "agriculture"),
            LexiconEntry("தென்னை", "ta", "southern_tamil", "coconut", "agriculture"),
            LexiconEntry("கரும்பு", "ta", "southern_tamil", "sugarcane", "agriculture"),
            LexiconEntry("பருத்தி", "ta", "southern_tamil", "cotton", "agriculture"),
            LexiconEntry("கம்பு", "ta", "southern_tamil", "pearl_millet", "agriculture"),
            LexiconEntry("சோளம்", "ta", "southern_tamil", "maize", "agriculture"),
            LexiconEntry("ராகி", "ta", "southern_tamil", "finger_millet", "agriculture"),
            # Irrigation
            LexiconEntry("கிணத்து நீர்ப்பாசனம்", "ta", "southern_tamil", "well_irrigation", "agriculture"),
            LexiconEntry("கிணத்து தண்ணி", "ta", "western_tamil", "well_irrigation", "agriculture", "dialectal"),
            LexiconEntry("போர்வெல்", "ta", "southern_tamil", "borewell", "agriculture"),
            LexiconEntry("ஆற்று நீர்", "ta", "southern_tamil", "river_irrigation", "agriculture"),
            LexiconEntry("மழை நீர்", "ta", "southern_tamil", "rainfed", "agriculture"),
            LexiconEntry("குழாய் நீர்", "ta", "southern_tamil", "canal_irrigation", "agriculture"),
            LexiconEntry("டிரிப்", "ta", "southern_tamil", "drip_irrigation", "agriculture", "English loanword"),
            # Units
            LexiconEntry("ஏக்கர்", "ta", "southern_tamil", "acre", "agriculture"),
            LexiconEntry("எக்கர்", "ta", "western_tamil", "acre", "agriculture", "dialectal pronunciation"),
            LexiconEntry("ஹெக்டேர்", "ta", "southern_tamil", "hectare", "agriculture"),
            LexiconEntry("சென்ட்", "ta", "southern_tamil", "cent", "agriculture"),
            # Fertilizer
            LexiconEntry("யூரியா", "ta", "southern_tamil", "urea", "agriculture"),
            LexiconEntry("DAP", "ta", "southern_tamil", "dap_fertilizer", "agriculture", "English abbreviation"),
            LexiconEntry("உரம்", "ta", "southern_tamil", "fertilizer", "agriculture"),
            # Pest
            LexiconEntry("காய்ப்புழு", "ta", "southern_tamil", "stem_borer", "agriculture"),
            LexiconEntry("பூச்சி", "ta", "southern_tamil", "pest", "agriculture"),
            LexiconEntry("நோய்", "ta", "southern_tamil", "disease", "agriculture"),
            # Conditions
            LexiconEntry("குறைவா", "ta", "southern_tamil", "insufficient", "agriculture", "informal"),
            LexiconEntry("நடுத்தரமா", "ta", "southern_tamil", "moderate", "agriculture"),
            LexiconEntry("நல்லா", "ta", "southern_tamil", "good", "agriculture"),
            LexiconEntry("பரவாயில்லை", "ta", "southern_tamil", "adequate", "agriculture"),
        ]
        self._entries = seed

    def lookup(
        self,
        surface_form: str,
        language: str = "ta",
        dialect: str | None = None,
        domain: str | None = None,
    ) -> list[LexiconEntry]:
        """Find canonical concept(s) for a surface form."""
        results = []
        for entry in self._entries:
            if entry.surface_form in surface_form and entry.language == language:
                if dialect and entry.dialect != dialect and entry.dialect != "southern_tamil":
                    continue
                if domain and entry.domain != domain:
                    continue
                results.append(entry)
        return results

    def get_canonical(self, surface_form: str, language: str = "ta") -> str | None:
        """Get the canonical English concept for a surface form."""
        matches = self.lookup(surface_form, language)
        if matches:
            # Prefer verified entries
            verified = [m for m in matches if m.source == "verified"]
            return (verified[0] if verified else matches[0]).canonical_concept
        return None

    def add_entry(self, entry: LexiconEntry):
        self._entries.append(entry)

    @property
    def size(self) -> int:
        return len(self._entries)


def get_dialect_classifier(provider_name: str = "mock") -> DialectClassifier:
    providers = {"mock": MockDialectClassifier}
    cls = providers.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown dialect provider: {provider_name}")
    return cls()
