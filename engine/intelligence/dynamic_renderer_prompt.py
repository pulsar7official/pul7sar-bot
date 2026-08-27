"""Renderer-safe prompt compilation for dynamic PUL7SAR visual concepts.

The DynamicVisualBrain is editorial: it may describe a story using names, opposing
worlds, or conceptual transitions. A text-to-image renderer must not be handed
that language verbatim when it can trigger fabricated identities, split-screen
layouts, pseudo-branding, or literal football cliches.

This compiler translates an approved dynamic concept into one continuous,
identity-neutral base-scene prompt. Exact people, crests, typography, scores and
other factual assets remain deterministic/reference-owned later layers.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.models import StoryBrief
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_brain import VisualConceptCandidate


@dataclass(frozen=True)
class RendererPromptDecision:
    concept_id: str
    prompt: str
    renderer_risk: str
    verified_person_asset: bool
    publication_ready: bool = False


class DynamicRendererPromptCompiler:
    """Compile dynamic concepts into a single-scene FLUX-safe base prompt."""

    CONTRACT = "pul7sar-dynamic-renderer-prompt-v1"

    _ABSOLUTE_BASE_RULES = (
        "ONE continuous physical scene only; never split-screen, diptych, collage, poster halves, panels, borders, before-and-after layout, or image-within-image. "
        "No readable text, pseudo-text, numbers, jersey lettering, logos, crests, sponsor marks, watermarks, or imitation branding. "
        "No football pitch, goal, goal net, penalty box, touchline, centre circle, corner flag, or tactical markings unless exact verified geometry is supplied later. "
        "Use physically coherent perspective, scale, shadows, materials and lighting. "
    )

    _NO_PERSON_RULE = (
        "NO people or human figures anywhere in frame: no player, athlete, silhouette, face, body, hands, crowd portrait, mannequin, reflected person, or distant recognizable human form. "
        "Communicate the story only through environment, material, light and spatial design. "
    )

    def compile(
        self,
        *,
        story: StoryBrief,
        event: EditorialEvent,
        concept: VisualConceptCandidate,
        verified_person_asset: bool = False,
    ) -> RendererPromptDecision:
        if not isinstance(concept, VisualConceptCandidate):
            raise TypeError("concept must be VisualConceptCandidate")

        if event in {EditorialEvent.TRANSFER_CONFIRMED, EditorialEvent.TRANSFER_RUMOUR, EditorialEvent.CONTRACT}:
            scene, risk = self._transfer_scene(concept)
        else:
            scene = self._generic_scene(concept)
            risk = "controlled"

        person_rule = "" if verified_person_asset else self._NO_PERSON_RULE
        story_fact = (story.summary or story.headline).strip()
        # Keep the factual meaning but deliberately omit entity names when there is
        # no verified identity asset. Names strongly bias text-to-image systems
        # toward invented player portraits and fake kit branding.
        factual_context = (
            f"Editorial meaning to convey without literal text: {story_fact}. "
            if story_fact
            else ""
        )

        prompt = (
            "Premium global-sports editorial base image. "
            + self._ABSOLUTE_BASE_RULES
            + person_rule
            + factual_context
            + scene
            + " Reserve a calm low-detail area for later deterministic PUL7SAR headline and branding layers. "
            + "The generated base must look like an original editorial photograph/set, not a social-media template."
        )
        return RendererPromptDecision(
            concept_id=concept.concept_id,
            prompt=prompt,
            renderer_risk=risk,
            verified_person_asset=verified_person_asset,
        )

    @staticmethod
    def _generic_scene(concept: VisualConceptCandidate) -> str:
        return (
            f"Visual idea: {concept.editorial_metaphor}. "
            f"Camera language: {concept.camera_language}. "
            f"Primary focal strategy: {concept.focal_strategy}. "
            f"Negative-space strategy: {concept.negative_space_strategy}. "
        )

    @staticmethod
    def _transfer_scene(concept: VisualConceptCandidate) -> tuple[str, str]:
        cid = concept.concept_id
        if cid == "dynamic-transfer-two-worlds":
            # Do not literally say two worlds/zones: image models often translate
            # that into a split-screen. Preserve the editorial idea as one spatial
            # light transition inside a single architectural environment.
            return (
                "Create one believable modern sports-architecture interior or arrival corridor in a single camera view. "
                "A continuous gradient of practical light changes gradually from a cooler, dimmer foreground into a warmer destination glow deeper in the same space. "
                "Use one uninterrupted floor plane, one uninterrupted ceiling/wall system, and one vanishing point; there must be no central divider, seam, border or duplicated scene. "
                "The visual hero is the gradual transition of light and material suggesting movement into a new chapter, not a person and not club identity. ",
                "multi-zone-concept-normalized-to-single-scene",
            )
        if cid == "dynamic-transfer-threshold":
            return (
                "Create one original non-branded architectural threshold within a single premium sports facility environment. "
                "The threshold is defined by believable destination light, tactile materials and forward depth, with no signing-room, airport, scarf, shirt or presentation cliches. ",
                "low",
            )
        if cid == "dynamic-transfer-object":
            return (
                "Create one intimate premium still-life in a non-branded arrival/locker environment: a prepared but anonymous destination space awaiting its occupant. "
                "Use restrained material detail and practical light; no jersey, nameplate, contract, boots with logos, football, or readable markings. ",
                "low",
            )
        return DynamicRendererPromptCompiler._generic_scene(concept), "controlled"


class DynamicConceptRenderSelector:
    """Prefer the strongest concept that is also robust for a raw T2I renderer."""

    _RISK_PENALTY = {
        "dynamic-transfer-two-worlds": 0.05,
    }

    def choose(self, concepts: tuple[VisualConceptCandidate, ...]) -> VisualConceptCandidate:
        if not concepts:
            raise ValueError("concepts cannot be empty")
        return max(
            concepts,
            key=lambda c: c.preflight_score - self._RISK_PENALTY.get(c.concept_id, 0.0),
        )
