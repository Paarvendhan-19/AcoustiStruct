"""Evidence linker — maps semantic fields back to exact audio timestamps."""

from __future__ import annotations

from typing import Optional
from dataclasses import dataclass
from ai.asr.providers import TranscriptSegment

@dataclass
class EvidenceMatch:
    text: str
    start_time: float
    end_time: float
    segment_index: int | None = None
    match_score: float = 1.0


def find_evidence_in_transcript(
    evidence_text: str,
    segments: list[TranscriptSegment],
) -> EvidenceMatch | None:
    """Find the best matching timestamp for a piece of evidence text."""
    if not evidence_text or not segments:
        return None
        
    # Exact match in a single segment
    for i, seg in enumerate(segments):
        if evidence_text in seg.text:
            return EvidenceMatch(
                text=evidence_text,
                start_time=seg.start,
                end_time=seg.end,
                segment_index=i,
                match_score=1.0,
            )
            
    # Fuzzy/overlap match would go here for real implementation
    # For now, if we can't find an exact substring, we just return the first segment as fallback
    # (In a real system, we'd use fuzzy string matching or DTW)
    
    return None
