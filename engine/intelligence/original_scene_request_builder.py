"""Translate a VisualConceptDecision into a provider-neutral synthesis request."""
from __future__ import annotations

from engine.intelligence.original_scene_runtime_contract import OriginalSceneRequest, OriginalSceneRuntimeKind
from engine.intelligence.visual_concept_director import VisualConceptArchetype, VisualConceptDecision


class OriginalSceneRequestBuilder:
    _RESERVED = ("readable_text", "pul7sar_brand", "exact_score", "club_crest", "sport_geometry")
    _COMMON_GENERATION_FORBIDDEN = (
        "no generated branding, wordmarks, readable text, numerals or pseudo-text",
        "no collage or multi-panel layout",
    )

    def build(
        self,
        decision: VisualConceptDecision,
        *,
        emotional_tone: str,
        safe_negative_space: str,
        identity_reference_ids: tuple[str, ...] = (),
        context_reference_ids: tuple[str, ...] = (),
        seed: int = 0,
    ) -> OriginalSceneRequest:
        if not isinstance(decision, VisualConceptDecision):
            raise TypeError("decision must be VisualConceptDecision")
        if decision.archetype is VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE:
            runtime_kind = OriginalSceneRuntimeKind.ATMOSPHERE
        elif decision.archetype is VisualConceptArchetype.HERO_ARRIVAL:
            runtime_kind = OriginalSceneRuntimeKind.IDENTITY_CONDITIONED
        else:
            raise ValueError(f"VISUAL_CONCEPT_DOES_NOT_REQUIRE_ORIGINAL_SCENE_RUNTIME:{decision.archetype.value}")

        # VisualConceptDecision.forbidden_motifs intentionally mixes high-level
        # orchestration policy (for example, do not reuse source-news pixels) with
        # pixel-generation constraints.  Do not pass orchestration-only phrases to
        # model prompting.  Normalize the subset that the synthesis runtime owns.
        forbidden = list(self._COMMON_GENERATION_FORBIDDEN)
        motifs = tuple(item.casefold() for item in decision.forbidden_motifs)
        if runtime_kind is OriginalSceneRuntimeKind.ATMOSPHERE:
            if any("venue" in item or "stadium" in item or "arena" in item for item in motifs):
                forbidden.append("no specific identifiable real venue")
            if any("identity" in item or "real-person" in item or "real person" in item or "likeness" in item for item in motifs):
                forbidden.append("no specific real-person depiction")
        return OriginalSceneRequest(
            archetype=decision.archetype,
            runtime_kind=runtime_kind,
            scene_intent=f"{decision.hero}; {decision.environment_role}",
            emotional_tone=emotional_tone,
            safe_negative_space=safe_negative_space,
            forbidden_visual_claims=tuple(dict.fromkeys(forbidden)),
            exact_fact_roles_reserved_for_compositor=self._RESERVED,
            identity_reference_ids=identity_reference_ids,
            context_reference_ids=context_reference_ids,
            seed=seed,
        )
