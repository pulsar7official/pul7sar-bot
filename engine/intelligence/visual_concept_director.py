"""Story-specific visual concept direction for original PUL7SAR imagery.

This layer chooses the *idea of the picture* before any renderer is selected.
Production policy is ORIGINAL-FIRST: third-party/source photographs may inform
verification and reference analysis, but they are not the default final pixels.
Exact facts, identities, readable copy and PUL7SAR branding remain deterministic.
Legacy photographic concepts remain explicit reference/study routes only.
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
    contract: str = "pul7sar-visual-concept-director-v2-original-first"

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
    """Choose an original-first picture idea from verified story evidence."""

    _COMMON_FORBIDDEN = (
        "generic one-template layout",
        "unexplained decorative pulse outside PUL7SAR brand",
        "decorative full pitch when story does not require pitch information",
        "fabricated readable text",
        "fabricated club crest",
        "fabricated identity",
        "source-news photograph as default publication canvas",
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
                    hero="original identity-conditioned player/coach presence",
                    environment="original destination-club light and architecture remain secondary",
                    assets=("verified_subject_reference", "exact_club_assets"),
                    rationale="a confirmed person-led move should become an original arrival scene while verified identity remains a reference constraint",
                    extra_forbidden=("third-party subject photo as final publication pixels",),
                )
            return self._decision(
                family, VisualConceptArchetype.SYMBOLIC_SIGNING_REVEAL,
                hero="one exact club-owned transfer symbol or deterministic signing object",
                environment="original minimal premium reveal with strong negative space",
                assets=("exact_club_assets",),
                rationale="without a safe identity-conditioned subject runtime, remain original and symbolic rather than reuse or fabricate a person",
            )

        if family is EditorialSceneFamily.RESULT_STATEMENT:
            # Photographs may verify the story and guide art direction, but the
            # publication concept remains an original PUL7SAR construction.
            if signals.safe_generated_context:
                return self._decision(
                    family, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE,
                    hero="original story-specific match atmosphere",
                    environment="new non-identifying football-event world; exact score and club assets remain deterministic",
                    assets=("exact_score", "exact_club_assets", "verified_match_reference_optional"),
                    rationale="results should become original PUL7SAR scenes; verified match imagery may guide truth and mood but not supply the default final pixels",
                    extra_forbidden=("mandatory stadium background", "winner dominance through loser degradation", "third-party match photograph as final publication canvas"),
                )
            return self._decision(
                family, VisualConceptArchetype.SCORE_MONUMENT,
                hero="exact final score",
                environment="original restrained context only; stadium is optional rather than mandatory",
                assets=("exact_score", "exact_club_assets"),
                rationale="when original scene generation is unavailable, deterministic score-led art is safer than publishing third-party match pixels",
                extra_forbidden=("mandatory stadium background", "winner dominance through loser degradation", "third-party match photograph as final publication canvas"),
            )

        if family is EditorialSceneFamily.VERIFIED_SUBJECT_NEWS:
            if signals.verified_detail_asset and not signals.story_requires_person:
                return self._decision(
                    family, VisualConceptArchetype.VERIFIED_EVIDENCE_DETAIL,
                    hero="verified factual detail represented in an original editorial construction",
                    environment="original quiet documentary/editorial depth",
                    assets=("verified_detail_reference",),
                    rationale="a precise verified detail can constrain an original scene without manufacturing emotion on a face",
                    extra_forbidden=("third-party detail photograph as default publication canvas",),
                )
            if signals.verified_subject_asset:
                return self._decision(
                    family, VisualConceptArchetype.HERO_ARRIVAL,
                    hero="original identity-conditioned verified subject",
                    environment="original restrained editorial atmosphere shaped by story tone",
                    assets=("verified_subject_reference",),
                    rationale="identity-led news ultimately needs an original subject rendering constrained by verified identity rather than a reused press photograph",
                    extra_forbidden=("fabricated injury expression", "fantasy medical staging", "third-party portrait as final publication pixels"),
                )
            return self._decision(
                family, VisualConceptArchetype.MINIMAL_EVENT_SYMBOL,
                hero="one original non-identifying story symbol",
                environment="minimal original negative-space editorial field",
                assets=(),
                rationale="without a verified identity reference, do not fabricate or reuse a person",
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
                environment="original abstract editorial depth subordinate to the verified datum",
                assets=("exact_data_anchor",),
                rationale="data stories need one memorable verified object, not a dense dashboard",
                extra_forbidden=("dense infographic wall", "decorative stadium background"),
            )

        if signals.safe_generated_context:
            return self._decision(
                family, VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE,
                hero="original story-specific non-identifying sports atmosphere",
                environment="new photorealistic but deliberately non-identifying sports-event world; deterministic layers own all exact facts",
                assets=("verified_context_reference_optional",),
                rationale="general news should create its own visual world; verified context imagery may guide truth but should not become the default final canvas",
                extra_forbidden=("specific real venue identity without verified reference", "specific real-person depiction", "abstract portal as default hero", "duplicate PUL7SAR pulse motif", "third-party context photograph as final publication canvas"),
            )
        return self._decision(
            family, VisualConceptArchetype.MINIMAL_EVENT_SYMBOL,
            hero="one story-specific original non-brand symbolic cue",
            environment="minimal original negative-space editorial field",
            assets=(),
            rationale="when original atmosphere generation is unavailable, remain minimal and story-specific rather than reuse source imagery or fabricate realism",
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
            metadata={
                "provider_agnostic": True,
                "concept_selected_before_renderer": True,
                "renderer_is_not_the_visual_idea": True,
                "brand_pulse_exclusive_to_brand_master": True,
                "original_publication_pixels_required": True,
                "third_party_photos_reference_only_by_default": True,
                "publication_ready": False,
            },
        )
