"""Verified entity theme/accent resolution for PUL7SAR visuals.

The resolver never scrapes colors and never guesses them from a team name. It
accepts explicit verified palette evidence and returns a single approved accent
for tintable PUL7SAR elements. General stories fall back to PUL7SAR red.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EntityPaletteEvidence:
    entity_name: str
    primary_hex: str
    confidence: float
    source: str

    def __post_init__(self) -> None:
        if not isinstance(self.entity_name, str) or not self.entity_name.strip():
            raise ValueError("entity_name must be non-empty")
        if not isinstance(self.source, str) or not self.source.strip():
            raise ValueError("source must be non-empty")
        if not isinstance(self.confidence, (int, float)):
            raise TypeError("confidence must be numeric")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "primary_hex", EntityThemeResolver.normalize_hex(self.primary_hex))


@dataclass(frozen=True)
class EntityTheme:
    accent_hex: str
    source: str
    entity_name: Optional[str] = None
    verified: bool = False


class EntityThemeResolver:
    PUL7SAR_RED = "#E10600"

    def __init__(self, *, minimum_confidence: float = 0.80):
        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError("minimum_confidence must be between 0 and 1")
        self.minimum_confidence = minimum_confidence

    def resolve(self, evidence: Optional[EntityPaletteEvidence]) -> EntityTheme:
        if evidence is None or evidence.confidence < self.minimum_confidence:
            return EntityTheme(self.PUL7SAR_RED, "pul7sar_default", verified=False)
        return EntityTheme(
            evidence.primary_hex,
            evidence.source,
            entity_name=evidence.entity_name,
            verified=True,
        )

    @staticmethod
    def normalize_hex(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError("color must be a hex string")
        value = value.strip().upper()
        if not value.startswith("#"):
            value = "#" + value
        if len(value) != 7 or any(ch not in "0123456789ABCDEF" for ch in value[1:]):
            raise ValueError("color must be #RRGGBB")
        return value
