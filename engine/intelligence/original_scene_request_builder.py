"""Translate a VisualConceptDecision into a provider-neutral synthesis request."""
from __future__ import annotations

from engine.intelligence.original_scene_runtime_contract import OriginalSceneRequest, OriginalSceneRuntimeKind
from engine.intelligence.visual_concept_director import VisualConceptArchetype, VisualConceptDecision


class OriginalSceneRequestBuilder:
    _RESERVED = ("readable_text", "pul7sar_brand", "exact_score", "club_crest")

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
        forbidden = tuple(dict.fromkeys((*decision.forbidden_motifs, "readable signage generated into scene", "PUL7SAR logo generated into scene", "club crest generated into scene")))
        return OriginalSceneRequest(
            archetype=decision.archetype,
            runtime_kind=runtime_kind,
            scene_intent=f"{decision.hero}; {decision.environment_role}",
            emotional_tone=emotional_tone,
            safe_negative_space=safe_negative_space,
            forbidden_visual_claims=forbidden,
            exact_fact_roles_reserved_for_compositor=self._RESERVED,
            identity_reference_ids=identity_reference_ids,
            context_reference_ids=context_reference_ids,
            seed=seed,
        )
