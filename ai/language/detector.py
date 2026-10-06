"""Language detection provider interface and implementations."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LanguageDetectionResult:
    language: str
    confidence: float
    alternatives: list[dict] = None

    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class LanguageDetector(ABC):
    @abstractmethod
    async def detect(self, text: str) -> LanguageDetectionResult:
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


class MockLanguageDetector(LanguageDetector):
    """Returns Tamil with high confidence for demo mode."""

    async def detect(self, text: str) -> LanguageDetectionResult:
        await asyncio.sleep(0.05)
        # Simple heuristic: check for Tamil Unicode range
        tamil_chars = sum(1 for c in text if '\u0B80' <= c <= '\u0BFF')
        total_chars = max(len(text.replace(" ", "")), 1)
        ratio = tamil_chars / total_chars

        if ratio > 0.3:
            return LanguageDetectionResult(
                language="ta",
                confidence=min(0.95, 0.6 + ratio * 0.4),
                alternatives=[{"language": "en", "confidence": 0.05}],
            )
        return LanguageDetectionResult(
            language="en",
            confidence=0.8,
            alternatives=[{"language": "ta", "confidence": 0.15}],
        )

    @property
    def provider_name(self) -> str:
        return "mock"


def get_language_detector(provider_name: str) -> LanguageDetector:
    providers = {"mock": MockLanguageDetector}
    cls = providers.get(provider_name)
    if cls is None:
        raise ValueError(f"Unknown language provider: {provider_name}")
    return cls()
