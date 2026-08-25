"""Story-specific visual concept direction for premium PUL7SAR imagery.

This layer chooses the *idea of the picture* before any renderer is selected.
It prevents a family renderer from becoming the visual concept by default.
Result coverage prioritizes verified decisive action, celebration and real match
moments before score-led fallback. Exact facts, identities, readable copy and
PUL7SAR branding remain deterministic.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class VisualConceptArchetype(str, Enum):
    HERO_ARRIVAL = "hero_arrival"
    SYMBOLIC_SIGNING_REVEAL = "symbolic_signing_reveal"
    DECISIVE_MOMENT = "decisive_moment"
    CELEBRATION_MOMENT = "celebration_moment"
    VERIFIED_MATCH_MOMENT = "verified_match_moment"
    SCORE_MONUMENT = "score_monument"
    VERIFIED_PORTRAIT = "verified_portrait"
    VERIFIED_EVIDENCE_DETAIL = "verified_evidence_detail"
    TACTICAL_SPATIAL_MAP = "tactical_spatial_map"
    DATA_MONOLITH = "data_monolith"
    PHOTOGRAPHIC_EVENT = "photographic_event"
    GENERATIVE_EVENT_ATMOSPHERE = "generative_event_atmosphere"
    MINIMAL_EVENT_SYMBOL = "minimal_event_symbol"


@dataclass(frozen=True)
class VisualConceptSignals:
    verified_subject_asset: bool = False
    verified_action_photo: bool = False
    verified_match_photo: bool = False
    verified_celebration_photo: bool = False
    verified_context_photo: bool = False
    verified_detail_asset: bool = False
    exact_club_assets: bool = False
    exact_tactical_data: bool = False
    exact_data_anchor: bool = False
    decisive_moment_known: bool = False
    story_requires_person: bool = False
    story_requires_pitch: bool = False
    safe_generated_context: bool = False
    score_margin: int | None = None

    def __post_init__(self) -> None:
        if self.score_margin is not None and self.score_margin < 0:
            raise ValueError("score_margin must be non-negative")
        if self.verified_action_photo and not self.verified_subject_asset:
            raise ValueError("verified action photo requires verified subject provenance")
        if self.verified_match_photo and not self.verified_subject_asset:
            raise ValueError("verified match photo requires verified subject provenance")
        if self.verified_celebration_photo and not self.verified_subject_asset:
            raise ValueError("verified celebration photo requires verified subject provenance")
        if self.story_requires_pitch and not self.exact_tactical_data:
            raise ValueError("pitch requirement is only valid with exact tactical data in concept routing")


@dataclass(frozen=True)
class VisualConceptDecision:
    family: EditorialSceneFamily
    archetype: VisualConceptArchetype
    hero: str
    environment_role: str
    asset_priority: tuple[str, ...]
    forbidden_motifs: tuple[str, ...]
    rationale: str
    metadata: Mapping[str, object]
    contract: str = "pul7sar-visual-concept-director-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.family, EditorialSceneFamily):
            raise TypeError("family must be EditorialSceneFamily")
        if not isinstance(self.archetype, VisualConceptArchetype):
            raise TypeError("archetype must be VisualConceptArchetype")
        if not self.hero.strip() or not self.environment_role.strip() or not self.rationale.strip():
            raise ValueError("visual concept strings must be non-empty")
        object.__setattr__(self, "asset_priority", tuple(self.asset_priority))
        object.__setattr__(self, "forbidden_motifs", tuple(self.forbidden_motifs))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        if "generic one-template layout" not in self.forbidden_motifs:
            raise ValueError("concept must explicitly forbid generic template fallback")


class VisualConceptDirector:
    """Choose a picture idea from verified story evidence before pixel routing."""

    _COMMON_FORBIDDEN = (
        "generic one-template layout",
        "unexplained decorative pulse outside PUL7SAR brand",
        "decorative full pitch when story does not require pitch information",
        "fabricated readable text",
        "fabricated club crest",
        "fabricated identity",
    )

    def direct(self, family: EditorialSceneFamily, signals: VisualConceptSignals) -> VisualConceptDecision:
        if not isinstance(family, EditorialSceneFamily):
            raise TypeError("family must be EditorialSceneFamily")
        if not isinstance(signals, VisualConceptSignals):
            raise TypeError("signals must be VisualConceptSignals")

        if family is EditorialSceneFamily.TRANSFER_SIGNATURE:
            if signals.verified_subject_asset:
                return self._decision(
                    family, VisualConceptArchetype.HERO_ARRIVAL,
                    hero="verified player/coach presence",
                    environment="destination-club light and architecture remain secondary",
                    assets=("verified_subject_asset", "exact_club_assets", "context_photo_optional"),
                    rationale="a confirmed person-led move should feel like an arrival, not a data card",
                )
            return self._decision(
                family, VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL,
                hero="one verified transfer symbol or exact club object",
                environment="minimal premium reveal with strong negative space",
                assets=("verified_nonperson_transfer_detail", "exact_club_assets"),
                rationale="without a publishable verified subject, stay symbolic rather than fabricate a person",
            )

        if family is EditorialSceneFamily.RESULT_STATEMENT:
            if signals.verified_action_photo and signals.decisive_moment_known:
                return self._decision(
                    family, VisualConceptArchetype.DECISIVE_MOMENT,
                    hero="verified decisive match moment",
                    environment="actual match atmosphere with exact score integrated as secondary factual layer",
                    assets=("verified_action_photo", "exact_club_assets", "exact_score"),
                    rationale="when the decisive moment is verified, the story should be experienced before it is diagrammed",
                    extra_forbidden=("scoreboard-first composition when decisive verified moment exists",),
                )
            if signals.verified_celebration_photo:
                return self._decision(
                    family, VisualConceptArchetype.CELEBRATION_MOMENT,
                    hero="verified winner celebration",
                    environment="photographic celebration atmosphere; loser remains neutral and absent from ridicule",
                    assets=("verified_celebration_photo", "exact_club_assets", "exact_score"),
                    rationale="a verified celebration carries more emotional truth than a generic stadium background",
                    extra_forbidden=("humiliation or collapse imagery for losing side",),
                )
            if signals.verified_match_photo:
                return self._decision(
                    family, VisualConceptArchetype.VERIFIED_MATCH_MOMENT,
                    hero="verified photographic moment from the actual match",
                    environment="real match texture with restrained exact result overlay",
                    assets=("verified_match_photo", "exact_club_assets", "exact_score"),
                    rationale="a truthful match photograph is visually richer and more specific than generic stadium atmosphere even when it is not the decisive action",
                    extra_forbidden=("claiming non-decisive match photo depicts decisive goal", "mandatory stadium background"),
                )
            return self._decision(
                family, VisualConceptArchetype.SCORE_MONUMENT,
                hero="exact final score",
                environment="restrained context only; stadium is optional rather than mandatory",
                assets=("exact_score", "exact_club_assets", "verified_context_photo_optional"),
                rationale="score-led art is the safe fallback only when no stronger verified story moment exists",
                extra_forbidden=("mandatory stadium background", "winner dominance through loser degradation"),
            )

        if family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            if signals.verified_detail_asset and not signals.story_requires_person:
                return self._decision(
                    family, VisualConceptArchetype.VERIFIED_EVIDENCE_DETAIL,
                    hero="verified factual detail asset",
                    environment="quiet documentary/editorial depth",
                    assets=("verified_detail_asset", "verified_context_photo_optional"),
                    rationale="a precise verified detail can tell the story without manufacturing emotion on a face",
                )
            return self._decision(
                family, VisualConceptArchetype.VERIFIED_PORTRAIT,
                hero="verified subject asset",
                environment="restrained editorial atmosphere shaped by the story tone",
                assets=("verified_subject_asset", "verified_context_photo_optional"),
                rationale="identity-led news must keep the real subject and real expression as the visual truth",
                extra_forbidden=("fabricated pose", "fabricated injury expression", "fantasy medical staging"),
            )

        if family is EditorialSceneFamily.TACTICAL_BOARD:
            if not signals.exact_tactical_data:
                raise ValueError("TACTICAL_CONCEPT_REQUIRES_EXACT_TACTICAL_DATA")
            return self._decision(
                family, VisualConceptArchetype.TACTICAL_SPATIAL_MAP,
                hero="exact tactical relationships and movement",
                environment="deterministic football geometry as information surface",
                assets=("exact_tactical_data",),
                rationale="the field appears because spatial football information is the story itself",
                extra_forbidden=("decorative player portrait as tactical hero", "generated pitch geometry"),
            )

        if family is EditorialSceneFamily.DATA_MONUMENT:
            if not signals.exact_data_anchor:
                raise ValueError("DATA_CONCEPT_REQUIRES_EXACT_DATA_ANCHOR")
            return self._decision(
                family, VisualConceptArchetype.DATA_MONOLITH,
                hero="one exact number/table/draw fact",
                environment="abstract editorial depth subordinate to the verified datum",
                assets=("exact_data_anchor",),
                rationale="data stories need one memorable verified object, not a dense dashboard",
                extra_forbidden=("dense infographic wall", "decorative stadium background"),
            )

        if signals.verified_context_photo:
            return self._decision(
                family, VisualConceptArchetype.PHOTOGRAPHIC_EVENT,
                hero="verified story context photograph",
                environment="photographic scene owns atmosphere while deterministic layers own facts",
                assets=("verified_context_photo",),
                rationale="general news should use real contextual texture when it exists instead of inventing a symbolic portal",
                extra_forbidden=("abstract portal as default hero", "duplicate PUL7SAR pulse motif"),
            )
        if signals.safe_generated_context:
            return self._decision(
                family, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE,
                hero="story-specific non-identifying sports atmosphere",
                environment=("photorealistic but deliberately non-identifying sports-event world; deterministic layers own all exact facts"),
                assets=(),
                rationale=("when no verified context image exists but non-factual atmosphere is safe, generate a generic event world without inventing a real venue, person or factual visual claim"),
                extra_forbidden=("specific real venue identity without verified context", "specific real-person depiction", "abstract portal as default hero", "duplicate PUL7SAR pulse motif"),
            )
        return self._decision(
            family, VisualConceptArchetype.MINIMAL_EVENT_SYMBOL,
            hero="one story-specific non-brand symbolic cue",
            environment="minimal negative-space editorial field",
            assets=(),
            rationale="when no verified context image exists, remain minimal and story-specific rather than fabricate realism",
            extra_forbidden=("generic stadium", "abstract portal as default hero", "duplicate PUL7SAR pulse motif"),
        )

    def _decision(self, family: EditorialSceneFamily, archetype: VisualConceptArchetype, *, hero: str, environment: str, assets: tuple[str, ...], rationale: str, extra_forbidden: tuple[str, ...] = ()) -> VisualConceptDecision:
        return VisualConceptDecision(
            family=family,
            archetype=archetype,
            hero=hero,
            environment_role=environment,
            asset_priority=assets,
            forbidden_motifs=tuple(dict.fromkeys((*self._COMMON_FORBIDDEN, *extra_forbidden))),
            rationale=rationale,
            metadata={"provider_agnostic": True, "concept_selected_before_renderer": True, "renderer_is_not_the_visual_idea": True, "brand_pulse_exclusive_to_brand_master": True, "publication_ready": False},
        )
