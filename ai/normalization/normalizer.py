"""Deterministic normalization for numbers, dates, units, and quantities.

This module handles normalization WITHOUT relying on LLMs.
It uses rule-based parsing for Tamil and English numeric expressions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

# ─── Tamil number words ───
TAMIL_UNITS = {
    "ஒன்று": 1, "ஒரு": 1,
    "இரண்டு": 2, "ரெண்டு": 2,
    "மூன்று": 3, "மூணு": 3,
    "நான்கு": 4, "நாலு": 4,
    "ஐந்து": 5, "அஞ்சு": 5,
    "ஆறு": 6,
    "ஏழு": 7, "ஏழ": 7,
    "எட்டு": 8,
    "ஒன்பது": 9,
    "பத்து": 10, "பத்": 10,
}

TAMIL_TENS = {
    "பத்து": 10, "பத்": 10,
    "இருபது": 20, "இருவது": 20,
    "முப்பது": 30,
    "நாற்பது": 40,
    "ஐம்பது": 50,
    "அறுபது": 60,
    "எழுபது": 70,
    "எண்பது": 80,
    "தொண்ணூறு": 90,
}

TAMIL_MULTIPLIERS = {
    "நூறு": 100, "நூத்": 100,
    "ஆயிரம்": 1000, "ஆயிரத்": 1000,
    "லட்சம்": 100_000, "லட்ச": 100_000,
    "கோடி": 10_000_000,
}

TAMIL_FRACTIONS = {
    "அரை": 0.5, "அர": 0.5,
    "கால்": 0.25,
    "முக்கால்": 0.75,
}

# Combined Tamil + English fraction patterns
FRACTION_PATTERN = re.compile(r"(\d+)\s*[/]\s*(\d+)")
DECIMAL_PATTERN = re.compile(r"(\d+)[.,](\d+)")
NUMERIC_PATTERN = re.compile(r"\d+")

# ─── Unit normalization ───
UNIT_ALIASES = {
    # Area
    "ஏக்கர்": "acre", "எக்கர்": "acre", "acre": "acre", "acres": "acre",
    "ஹெக்டேர்": "hectare", "hectare": "hectare", "hectares": "hectare", "ha": "hectare",
    "சென்ட்": "cent", "cent": "cent", "cents": "cent",
    # Weight
    "கிலோ": "kg", "kg": "kg", "கிலோகிராம்": "kg", "kilogram": "kg",
    "டன்": "tonne", "tonne": "tonne", "ton": "tonne",
    "குவிண்டால்": "quintal", "quintal": "quintal",
    # Volume
    "லிட்டர்": "litre", "litre": "litre", "liter": "litre",
    # Distance
    "கிலோமீட்டர்": "km", "km": "km",
    # Currency
    "ரூபாய்": "rupee", "ரூபா": "rupee", "rupee": "rupee", "rupees": "rupee", "rs": "rupee",
    # Percentage
    "சதவிகிதம்": "percent", "சதவீதம்": "percent", "%": "percent", "percent": "percent",
}

# ─── Tamil month names ───
TAMIL_MONTHS = {
    "ஜனவரி": 1, "பிப்ரவரி": 2, "மார்ச்": 3, "ஏப்ரல்": 4,
    "மே": 5, "ஜூன்": 6, "ஜூலை": 7, "ஆகஸ்ட்": 8,
    "செப்டம்பர்": 9, "அக்டோபர்": 10, "நவம்பர்": 11, "டிசம்பர்": 12,
}

# ─── Uncertainty markers ───
UNCERTAINTY_MARKERS_TA = [
    "நினைக்கிறேன்", "இருக்கும்", "சுமார்", "ஏறக்குறைய",
    "தெரியல", "தெரியாது", "கிட்டத்தட்ட", "மாதிரி",
]


@dataclass
class NormalizedValue:
    """Result of normalizing a spoken expression."""
    value: float | int | str | None
    unit: str | None = None
    certainty: str = "explicit"  # explicit | uncertain | approximate | negated
    raw_text: str = ""
    parse_method: str = "deterministic"


@dataclass
class NormalizedDate:
    """Result of normalizing a date expression."""
    date_value: date | None = None
    month: int | None = None
    year: int | None = None
    certainty: str = "explicit"
    raw_text: str = ""
    is_relative: bool = False


def parse_tamil_number(text: str) -> float | None:
    """Parse a Tamil numeric expression into a float.

    Handles: word numbers, combined expressions like 'இரண்டரை' (2.5),
    Indian number system (lakh, crore), and mixed digit+word forms.
    """
    text = text.strip()

    # Try direct digit parsing first
    if DECIMAL_PATTERN.match(text):
        m = DECIMAL_PATTERN.match(text)
        return float(f"{m.group(1)}.{m.group(2)}")

    if NUMERIC_PATTERN.match(text) and NUMERIC_PATTERN.match(text).group() == text:
        return float(text)

    # Try fraction patterns
    if FRACTION_PATTERN.match(text):
        m = FRACTION_PATTERN.match(text)
        return float(m.group(1)) / float(m.group(2))

    # Tamil word numbers
    result = 0.0
    current = 0.0
    found_any = False

    # Handle compound words like "இரண்டரை" (two-and-a-half)
    for fraction_word, fraction_val in TAMIL_FRACTIONS.items():
        if fraction_word in text:
            # Check if there's a number before the fraction
            for word, val in {**TAMIL_UNITS, **TAMIL_TENS}.items():
                if word in text and text.index(word) < text.index(fraction_word):
                    return val + fraction_val
            return fraction_val

    # Parse word-by-word
    words = text.split()
    for word in words:
        if word in TAMIL_UNITS:
            current += TAMIL_UNITS[word]
            found_any = True
        elif word in TAMIL_TENS:
            current += TAMIL_TENS[word]
            found_any = True
        elif word in TAMIL_MULTIPLIERS:
            if current == 0:
                current = 1
            current *= TAMIL_MULTIPLIERS[word]
            result += current
            current = 0
            found_any = True
        elif NUMERIC_PATTERN.match(word):
            current += float(NUMERIC_PATTERN.match(word).group())
            found_any = True

    if found_any:
        return result + current

    # Try compound Tamil numbers (no spaces)
    for word, val in sorted(TAMIL_MULTIPLIERS.items(), key=lambda x: -x[1]):
        if word in text:
            parts = text.split(word, 1)
            before = parse_tamil_number(parts[0]) if parts[0].strip() else 1
            after = parse_tamil_number(parts[1]) if len(parts) > 1 and parts[1].strip() else 0
            if before is not None:
                return (before * val) + (after or 0)

    return None


def normalize_quantity(text: str) -> NormalizedValue:
    """Normalize a spoken quantity expression into value + unit + certainty."""
    text = text.strip()
    raw = text

    # Detect uncertainty
    certainty = "explicit"
    for marker in UNCERTAINTY_MARKERS_TA:
        if marker in text:
            certainty = "uncertain"
            break

    if "சுமார்" in text or "ஏறக்குறைய" in text or "கிட்டத்தட்ட" in text:
        certainty = "approximate"

    # Extract unit
    unit = None
    for alias, canonical in sorted(UNIT_ALIASES.items(), key=lambda x: -len(x[0])):
        if alias in text.lower() or alias in text:
            unit = canonical
            text = text.replace(alias, "").strip()
            break

    # Parse the numeric value
    value = parse_tamil_number(text)

    # Fallback: try to find any digit in the remaining text
    if value is None:
        digits = NUMERIC_PATTERN.findall(text)
        if digits:
            value = float(digits[0])

    return NormalizedValue(
        value=value,
        unit=unit,
        certainty=certainty,
        raw_text=raw,
    )


def normalize_unit(unit_text: str) -> str | None:
    """Normalize a unit string to its canonical form."""
    unit_text = unit_text.strip().lower()
    return UNIT_ALIASES.get(unit_text)


def normalize_date(text: str, reference_date: date | None = None) -> NormalizedDate:
    """Normalize a Tamil/English date expression.

    Handles: month names, relative dates, and refuses to hallucinate exact dates.
    """
    text = text.strip()
    ref = reference_date or date.today()

    # Relative expressions (Tamil)
    if "இன்று" in text or "today" in text.lower():
        return NormalizedDate(date_value=ref, certainty="explicit", raw_text=text, is_relative=True)
    if "நேற்று" in text or "yesterday" in text.lower():
        return NormalizedDate(date_value=ref - timedelta(days=1), certainty="explicit", raw_text=text, is_relative=True)
    if "நாளை" in text or "tomorrow" in text.lower():
        return NormalizedDate(date_value=ref + timedelta(days=1), certainty="explicit", raw_text=text, is_relative=True)

    # Month extraction
    month = None
    for month_name, month_num in TAMIL_MONTHS.items():
        if month_name in text:
            month = month_num
            break

    # English month names fallback
    if month is None:
        en_months = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12,
        }
        for m_name, m_num in en_months.items():
            if m_name in text.lower():
                month = m_num
                break

    # Year extraction
    year_match = re.search(r"20\d{2}", text)
    year = int(year_match.group()) if year_match else None

    if month and not year:
        # Use reference year, but mark as uncertain since year was inferred
        year = ref.year
        certainty = "uncertain"
    elif month and year:
        certainty = "explicit"
    else:
        certainty = "uncertain"

    date_value = None
    if month and year:
        try:
            date_value = date(year, month, 1)  # Day 1 since no day was specified
        except ValueError:
            pass

    return NormalizedDate(
        date_value=date_value,
        month=month,
        year=year,
        certainty=certainty,
        raw_text=text,
        is_relative=False,
    )


def detect_negation(text: str) -> bool:
    """Detect if a Tamil text contains negation."""
    negation_markers = ["இல்லை", "இல்ல", "மாட்டேன்", "கிடையாது", "வேண்டாம்", "இல்ல"]
    return any(m in text for m in negation_markers)
