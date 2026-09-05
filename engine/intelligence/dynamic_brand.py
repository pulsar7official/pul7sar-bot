"""Deterministic dynamic-brand policy for PUL7SAR Phase 18.

PUL7SAR is not a diffusion-generated logo. The brand has stable geometry and a
contextual accent state. Default 7/pulse is PUL7SAR red. A verified fact-driven
story-dominant entity (winner, transfer destination, champion, etc.) may own the
accent when its palette is verified and belongs to that exact entity. Ambiguity,
entity mismatch, or missing evidence fails to red.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from engine.intelligence.entity_theme import EntityPaletteEvidence, EntityThemeResolver


class BrandAccentReason(str, Enum):
    DEFAULT_GENERAL = "default_general"
    VERIFIED_HERO = "verified_hero"
    VERIFIED_DOMINANT_ENTITY = "verified_dominant_entity"
    AMBIGUOUS_HERO = "ambiguous_hero"
    LOW_CONFIDENCE = "low_confidence"
    PALETTE_UNAVAILABLE = "palette_unavailable"
    PALETTE_ENTITY_MISMATCH = "palette_entity_mismatch"


@dataclass(frozen=True)
class StoryHeroEvidence:
    entity_name: str
    confidence: float
    is_unambiguous: bool
    palette: Optional[EntityPaletteEvidence] = None

    def __post_init__(self) -> None:
        if not self.entity_name.strip():
            raise ValueError("entity_name is required")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class DynamicBrandDecision:
    accent_hex: str
    reason: BrandAccentReason
    hero_entity: Optional[str]
    contextual: bool
    story_dominance_reason: Optional[str] = None
    structure_locked: bool = True
    generator_may_draw_brand: bool = False
    tint_scope: tuple[str, ...] = ("seven", "pulse")


class DynamicBrandResolver:
    """Resolve accent state without ever changing brand structure."""

    def __init__(self, *, hero_confidence_floor: float = 0.85, palette_confidence_floor: float = 0.80):
        self.hero_confidence_floor = hero_confidence_floor
        self._themes = EntityThemeResolver(minimum_confidence=palette_confidence_floor)

    def resolve(self, hero: Optional[StoryHeroEvidence], *, dominance_reason: str | None = None) -> DynamicBrandDecision:
        default = EntityThemeResolver.PUL7SAR_RED
        if hero is None:
            return DynamicBrandDecision(default, BrandAccentReason.DEFAULT_GENERAL, None, False)
        if not hero.is_unambiguous:
            return DynamicBrandDecision(default, BrandAccentReason.AMBIGUOUS_HERO, None, False)
        if hero.confidence < self.hero_confidence_floor:
            return DynamicBrandDecision(default, BrandAccentReason.LOW_CONFIDENCE, None, False)
        if hero.palette is None:
            return DynamicBrandDecision(default, BrandAccentReason.PALETTE_UNAVAILABLE, hero.entity_name, False)
        if hero.palette.entity_name.strip().casefold() != hero.entity_name.strip().casefold():
            return DynamicBrandDecision(default, BrandAccentReason.PALETTE_ENTITY_MISMATCH, hero.entity_name, False)
        theme = self._themes.resolve(hero.palette)
        if not theme.verified:
            return DynamicBrandDecision(default, BrandAccentReason.LOW_CONFIDENCE, hero.entity_name, False)
        reason = BrandAccentReason.VERIFIED_DOMINANT_ENTITY if dominance_reason else BrandAccentReason.VERIFIED_HERO
        return DynamicBrandDecision(
            theme.accent_hex,
            reason,
            hero.entity_name,
            True,
            story_dominance_reason=dominance_reason,
        )
