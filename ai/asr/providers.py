"""ASR provider interface and implementations."""

from __future__ import annotations

import asyncio
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TranscriptSegment:
    """A time-aligned segment of transcribed speech."""
    text: str
    start: float
    end: float
    confidence: float = 1.0
    language: Optional[str] = None
    speaker: Optional[str] = None


@dataclass
class TranscriptionResult:
    """Complete transcription result from an ASR provider."""
    language: str
    text: str
    segments: list[TranscriptSegment] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    model_version: str = ""
    latency_ms: int = 0


class ASRProvider(ABC):
    """Abstract interface for all ASR providers."""

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> TranscriptionResult:
        """Transcribe audio data and return structured result with timestamps."""
        ...

    @abstractmethod
    def supported_languages(self) -> list[str]:
        """Return list of supported language codes."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...


class MockASRProvider(ASRProvider):
    """Mock ASR for development and demo mode.

    Returns realistic Tamil agriculture transcripts with proper timestamps.
    """

    MOCK_SCENARIOS = {
        "tamil_agriculture_01": {
            "language": "ta",
            "text": (
                "என் பெயர் ராமசாமி. நான் மதுரை மாவட்டம் திருமங்கலம் "
                "கிராமத்தில் இருக்கிறேன். என்கிட்ட இரண்டரை ஏக்கர் நிலம் "
                "இருக்கு. நெல் பயிர் போட்டிருக்கேன். கிணத்து நீர்ப்பாசனம் "
                "பயன்படுத்துறேன். இந்த வருஷம் மழை குறைவா இருக்கு. "
                "மண் வளம் நடுத்தரமா இருக்கு. யூரியா உரம் போட்டிருக்கேன். "
                "காய்ப்புழு பாதிப்பு இருக்கு. சுமார் முப்பது சதவிகிதம் "
                "பயிர் சேதம் ஆயிருக்கு. ஏறக்குறைய ஐம்பதாயிரம் ரூபாய் "
                "நஷ்டம் இருக்கும்னு நினைக்கிறேன். ஜூன் மாசம் விதைச்சேன். "
                "நவம்பர் மாசம் அறுவடை செய்யலாம்னு நினைக்கிறேன்."
            ),
            "segments": [
                {"text": "என் பெயர் ராமசாமி.", "start": 0.0, "end": 1.8, "confidence": 0.97},
                {"text": "நான் மதுரை மாவட்டம் திருமங்கலம் கிராமத்தில் இருக்கிறேன்.", "start": 2.0, "end": 5.2, "confidence": 0.94},
                {"text": "என்கிட்ட இரண்டரை ஏக்கர் நிலம் இருக்கு.", "start": 5.5, "end": 8.1, "confidence": 0.92},
                {"text": "நெல் பயிர் போட்டிருக்கேன்.", "start": 8.3, "end": 10.0, "confidence": 0.96},
                {"text": "கிணத்து நீர்ப்பாசனம் பயன்படுத்துறேன்.", "start": 10.2, "end": 12.8, "confidence": 0.91},
                {"text": "இந்த வருஷம் மழை குறைவா இருக்கு.", "start": 13.0, "end": 15.5, "confidence": 0.93},
                {"text": "மண் வளம் நடுத்தரமா இருக்கு.", "start": 15.8, "end": 18.0, "confidence": 0.90},
                {"text": "யூரியா உரம் போட்டிருக்கேன்.", "start": 18.2, "end": 20.5, "confidence": 0.95},
                {"text": "காய்ப்புழு பாதிப்பு இருக்கு.", "start": 20.8, "end": 23.0, "confidence": 0.88},
                {"text": "சுமார் முப்பது சதவிகிதம் பயிர் சேதம் ஆயிருக்கு.", "start": 23.2, "end": 26.5, "confidence": 0.85},
                {"text": "ஏறக்குறைய ஐம்பதாயிரம் ரூபாய் நஷ்டம் இருக்கும்னு நினைக்கிறேன்.", "start": 26.8, "end": 30.5, "confidence": 0.82},
                {"text": "ஜூன் மாசம் விதைச்சேன்.", "start": 30.8, "end": 32.5, "confidence": 0.93},
                {"text": "நவம்பர் மாசம் அறுவடை செய்யலாம்னு நினைக்கிறேன்.", "start": 32.8, "end": 36.0, "confidence": 0.90},
            ],
        },
        "tamil_agriculture_02": {
            "language": "ta",
            "text": (
                "என் பெயர் முருகன். பெரிய... அதாவது பெரியகுளம் பக்கத்தில் "
                "இருக்கிற சின்ன கிராமம். மூணு ஏக்கர் நிலம். வாழை "
                "பயிர் போட்டிருக்கேன். போர்வெல் தண்ணி பயன்படுத்துறேன். "
                "மழை பரவாயில்லை ஆனா போதாது. மண் நல்லா இருக்கு. "
                "DAP உரம் போட்டேன். பூச்சி பிரச்சனை இல்லை. "
                "பத்து சதவீதம் சேதம் இருக்கு காத்துல. "
                "இருபதாயிரம் ரூபா நஷ்டம் இருக்கும்."
            ),
            "segments": [
                {"text": "என் பெயர் முருகன்.", "start": 0.0, "end": 1.5, "confidence": 0.96},
                {"text": "பெரிய... அதாவது பெரியகுளம் பக்கத்தில் இருக்கிற சின்ன கிராமம்.", "start": 1.8, "end": 5.5, "confidence": 0.72},
                {"text": "மூணு ஏக்கர் நிலம்.", "start": 5.8, "end": 7.5, "confidence": 0.94},
                {"text": "வாழை பயிர் போட்டிருக்கேன்.", "start": 7.8, "end": 9.5, "confidence": 0.95},
                {"text": "போர்வெல் தண்ணி பயன்படுத்துறேன்.", "start": 9.8, "end": 12.0, "confidence": 0.91},
                {"text": "மழை பரவாயில்லை ஆனா போதாது.", "start": 12.3, "end": 14.5, "confidence": 0.89},
                {"text": "மண் நல்லா இருக்கு.", "start": 14.8, "end": 16.0, "confidence": 0.93},
                {"text": "DAP உரம் போட்டேன்.", "start": 16.3, "end": 18.0, "confidence": 0.92},
                {"text": "பூச்சி பிரச்சனை இல்லை.", "start": 18.3, "end": 20.0, "confidence": 0.95},
                {"text": "பத்து சதவீதம் சேதம் இருக்கு காத்துல.", "start": 20.3, "end": 23.0, "confidence": 0.86},
                {"text": "இருபதாயிரம் ரூபா நஷ்டம் இருக்கும்.", "start": 23.3, "end": 25.5, "confidence": 0.84},
            ],
        },
        "tamil_uncertain_01": {
            "language": "ta",
            "text": (
                "என் பெயர் செல்வம்... அல்லது செல்வராஜ். "
                "எங்க ஊர்... ம்... அது கோவை பக்கம் தான். "
                "நிலம் ஒரு ஏக்கர் இருக்கும்னு நினைக்கிறேன், "
                "சரியா தெரியல. தென்னை போட்டிருக்கேன்."
            ),
            "segments": [
                {"text": "என் பெயர் செல்வம்... அல்லது செல்வராஜ்.", "start": 0.0, "end": 3.0, "confidence": 0.55},
                {"text": "எங்க ஊர்... ம்... அது கோவை பக்கம் தான்.", "start": 3.3, "end": 7.0, "confidence": 0.48},
                {"text": "நிலம் ஒரு ஏக்கர் இருக்கும்னு நினைக்கிறேன், சரியா தெரியல.", "start": 7.3, "end": 11.5, "confidence": 0.60},
                {"text": "தென்னை போட்டிருக்கேன்.", "start": 11.8, "end": 13.5, "confidence": 0.92},
            ],
        },
    }

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
    ) -> TranscriptionResult:
        """Return a mock transcript. Uses scenario from context if provided."""
        # Simulate realistic latency
        await asyncio.sleep(random.uniform(0.5, 1.5))
        start_time = time.monotonic()

        scenario_key = (context or {}).get("scenario", "tamil_agriculture_01")
        scenario = self.MOCK_SCENARIOS.get(scenario_key, self.MOCK_SCENARIOS["tamil_agriculture_01"])

        segments = [
            TranscriptSegment(
                text=seg["text"],
                start=seg["start"],
                end=seg["end"],
                confidence=seg["confidence"],
                language=scenario["language"],
            )
            for seg in scenario["segments"]
        ]

        latency = int((time.monotonic() - start_time) * 1000)

        return TranscriptionResult(
            language=language or scenario["language"],
            text=scenario["text"],
            segments=segments,
            provider="mock",
            model="mock-asr-v1",
            model_version="1.0.0",
            latency_ms=latency,
        )

    def supported_languages(self) -> list[str]:
        return ["ta", "en", "hi", "te", "ml", "kn"]

    @property
    def provider_name(self) -> str:
        return "mock"


def get_asr_provider(provider_name: str, **kwargs: Any) -> ASRProvider:
    """Factory function for ASR providers."""
    providers = {
        "mock": MockASRProvider,
    }
    provider_cls = providers.get(provider_name)
    if provider_cls is None:
        raise ValueError(f"Unknown ASR provider: {provider_name}. Available: {list(providers.keys())}")
    return provider_cls(**kwargs)
