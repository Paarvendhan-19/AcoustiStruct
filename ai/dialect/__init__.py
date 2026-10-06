"""Dialect module."""
from ai.dialect.classifier import (
    DialectClassifier, MockDialectClassifier, DialectPrediction,
    DialectLexicon, LexiconEntry, get_dialect_classifier,
)
__all__ = [
    "DialectClassifier", "MockDialectClassifier", "DialectPrediction",
    "DialectLexicon", "LexiconEntry", "get_dialect_classifier",
]
