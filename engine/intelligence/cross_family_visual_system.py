"""Cross-family visual system for PUL7SAR original editorial scenes.

This prevents Phase 18 from overfitting to result graphics. Every editorial family
gets multiple scene archetypes, explicit hero ownership, optional deterministic
assets and anti-repetition selection. The selected archetype is a scene grammar,
not a fixed template.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from random import Random

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


@dataclass(frozen=True)
class FamilyVisualArchetype:
    id: str
    hero: str
    spatial_grammar: str
    optional_layers: tuple[str, ...]
    forbidden_shortcuts: tuple[str, ...] = ("card grid", "generic centered template", "fabricated exact identity")


@dataclass(frozen=True)
class CrossFamilyVisualDecision:
    family: EditorialSceneFamily
    archetype: FamilyVisualArchetype
    seed: int
    anti_repetition_applied: bool
    contract: str = "pul7sar-cross-family-visual-system-v1"


class CrossFamilyVisualSystem:
    CONTRACT = "pul7sar-cross-family-visual-system-v1"

    _LIBRARY = {
        EditorialSceneFamily.TRANSFER_SIGNATURE: (
            FamilyVisualArchetype("threshold_arrival", "verified subject or symbolic arrival cue", "asymmetric threshold / destination depth", ("exact destination crest", "club color light", "architectural tunnel", "shirt texture")),
            FamilyVisualArchetype("identity_transition", "verified subject identity", "two-environment transition without split-screen", ("exact club crests", "color migration", "negative-space headline")),
            FamilyVisualArchetype("signing_object", "verified transfer object/fact", "close editorial object study", ("exact crest", "shirt number only if verified", "contract motif only when signing confirmed")),
            FamilyVisualArchetype("destination_monument", "destination club identity", "large environmental club-color structure", ("exact crest", "city/venue cue only if verified", "subject silhouette only when safe")),
        ),
        EditorialSceneFamily.RESULT_STATEMENT: (
            FamilyVisualArchetype("score_monument", "exact score", "free-standing score object in atmosphere", ("exact crests", "club light fields", "ball", "competition mark if verified")),
            FamilyVisualArchetype("club_duel_space", "balanced club identities and exact score", "opposed depth fields with off-axis score", ("exact crests", "flags without invented marks", "crowd depth")),
            FamilyVisualArchetype("aftermath_editorial", "factual outcome", "quiet post-match spatial composition", ("exact score", "club accents", "restrained surface reflection")),
            FamilyVisualArchetype("arena_outcome", "outcome within sporting environment", "wide arena geometry; score is secondary focal object", ("exact crests", "ball", "generic crowd", "verified competition identity")),
        ),
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS: (
            FamilyVisualArchetype("portrait_depth", "verified subject asset", "off-center portrait with deep editorial environment", ("club accent", "exact crest", "story-symbol layer")),
            FamilyVisualArchetype("subject_detail", "verified non-fabricated subject detail", "tight detail-led composition", ("equipment detail", "exact number if verified", "quiet typography zone")),
            FamilyVisualArchetype("absence_space", "verified absence/injury/suspension fact", "intentional negative space / missing-presence metaphor", ("exact crest", "bench/tunnel abstraction", "medical symbol only if contextually appropriate")),
            FamilyVisualArchetype("statement_stage", "verified statement/appointment fact", "editorial press-stage abstraction", ("verified subject", "exact crest", "microphone/light cues without fabricated quotes")),
        ),
        EditorialSceneFamily.TACTICAL_BOARD: (
            FamilyVisualArchetype("topology_map", "exact tactical structure", "top-down deterministic geometry", ("verified positions", "movement arrows", "zones")),
            FamilyVisualArchetype("phase_corridor", "one verified tactical mechanism", "cropped pitch corridor / phase-of-play focus", ("player markers", "passing lanes", "pressure zones")),
            FamilyVisualArchetype("layered_shape", "formation relationships", "stacked spatial bands rather than full pitch", ("lines", "distances", "role labels")),
            FamilyVisualArchetype("duel_mechanism", "verified matchup mechanism", "two interacting tactical structures", ("zones", "arrows", "exact labels")),
        ),
        EditorialSceneFamily.DATA_MONUMENT: (
            FamilyVisualArchetype("number_sculpture", "one exact number", "large material data object with sparse context", ("exact crest", "rank marker", "competition mark")),
            FamilyVisualArchetype("table_rise", "exact ranking/table change", "vertical ranking movement", ("exact rows", "club crests", "movement indicator")),
            FamilyVisualArchetype("draw_orbit", "exact draw pairings", "orbital/bracket spatial system", ("exact crests", "competition mark", "round label")),
            FamilyVisualArchetype("schedule_axis", "exact schedule/time fact", "timeline / axis composition", ("exact crests", "venue only if verified", "date/time")),
        ),
        EditorialSceneFamily.EVENT_EDITORIAL: (
            FamilyVisualArchetype("event_horizon", "single verified event anchor", "deep atmospheric horizon with off-center focal object", ("competition mark", "sport object", "generic crowd")),
            FamilyVisualArchetype("object_story", "verified symbolic sports object", "close object-led editorial scene", ("ball/equipment", "environmental light", "exact event mark")),
            FamilyVisualArchetype("anticipation_tunnel", "upcoming-event tension", "forward-depth tunnel / entrance grammar", ("generic venue light", "competition colors", "anonymous crowd")),
            FamilyVisualArchetype("minimal_signal", "single factual signal", "minimal negative-space composition", ("exact date", "event mark", "restrained sport geometry")),
        ),
    }

    @classmethod
    def archetypes(cls, family: EditorialSceneFamily) -> tuple[FamilyVisualArchetype, ...]:
        return cls._LIBRARY[family]

    @classmethod
    def choose(cls, *, family: EditorialSceneFamily, story_key: str, recent_archetypes: tuple[str, ...] = (), seed: int = 0) -> CrossFamilyVisualDecision:
        if not isinstance(family, EditorialSceneFamily):
            raise TypeError("family must be EditorialSceneFamily")
        if not story_key.strip():
            raise ValueError("story_key is required")
        library = cls.archetypes(family)
        recent = set(recent_archetypes[-3:])
        candidates = [a for a in library if a.id not in recent]
        anti = bool(recent and len(candidates) != len(library))
        if not candidates:
            candidates = list(library)
        stable = int.from_bytes(sha256(f"{family.value}|{story_key}|{seed}".encode()).digest()[:8], "big")
        rng = Random(stable)
        return CrossFamilyVisualDecision(family, candidates[rng.randrange(len(candidates))], stable, anti)
