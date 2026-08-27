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
import re

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
    """Compile dynamic concepts into a single-scene identity-neutral base prompt."""

    CONTRACT = "pul7sar-dynamic-renderer-prompt-v2-identity-neutral"

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

    _EVENT_CONTEXT = {
        EditorialEvent.TRANSFER_CONFIRMED: "Convey a confirmed move into a new professional chapter without depicting any real person, club identity or readable announcement. ",
        EditorialEvent.TRANSFER_RUMOUR: "Convey uncertainty around a possible move without implying confirmation, a real person likeness, club identity or readable announcement. ",
        EditorialEvent.CONTRACT: "Convey a professional agreement or commitment through environment and material cues only, without signatures, documents, readable text or real-person likeness. ",
        EditorialEvent.INJURY: "Convey absence, interruption or recovery in a restrained sports-editorial environment without depicting an identifiable person or medical claim. ",
        EditorialEvent.RESULT: "Convey a completed competitive outcome without readable score, crests, humiliation, collapse imagery or disrespect toward the losing side. ",
        EditorialEvent.PREVIEW: "Convey anticipation before competition without implying a completed result, a specific real venue or a specific real-person depiction. ",
    }

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
            scene = self._generic_scene(story, concept)
            risk = "controlled"

        person_rule = "" if verified_person_asset else self._NO_PERSON_RULE
        safe_event_context = self._EVENT_CONTEXT.get(
            event,
            "Convey the verified editorial meaning through atmosphere and physical environment only, without inventing exact facts, identity or branding. ",
        )

        prompt = (
            "Premium global-sports editorial base image. "
            + self._ABSOLUTE_BASE_RULES
            + person_rule
            + safe_event_context
            + scene
            + " Reserve a calm low-detail area for later deterministic headline and brand layers. "
            + "The generated base must look like an original editorial photograph/set, not a social-media template."
        )
        self._assert_identity_neutral(prompt, story)
        return RendererPromptDecision(
            concept_id=concept.concept_id,
            prompt=prompt,
            renderer_risk=risk,
            verified_person_asset=verified_person_asset,
        )

    @classmethod
    def _generic_scene(cls, story: StoryBrief, concept: VisualConceptCandidate) -> str:
        camera = cls._strip_known_entities(concept.camera_language, story)
        focal = cls._strip_known_entities(concept.focal_strategy, story)
        negative_space = cls._strip_known_entities(concept.negative_space_strategy, story)
        return (
            "Create one story-specific, non-identifying sports-editorial environment in a single coherent camera view. "
            f"Camera language: {camera}. "
            f"Primary focal strategy: {focal}. "
            f"Negative-space strategy: {negative_space}. "
        )

    @staticmethod
    def _transfer_scene(concept: VisualConceptCandidate) -> tuple[str, str]:
        cid = concept.concept_id
        if cid == "dynamic-transfer-two-worlds":
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
        return (
            "Create one restrained, non-identifying sports-editorial environment with one clear focal hierarchy and deliberate negative space. ",
            "controlled",
        )

    @staticmethod
    def _strip_known_entities(value: str, story: StoryBrief) -> str:
        text = str(value or "").strip()
        entities = [story.primary_entity, *story.secondary_entities]
        for entity in entities:
            if not entity:
                continue
            text = re.sub(re.escape(entity), "anonymous subject", text, flags=re.IGNORECASE)
        text = re.sub(r"\b(?:pul7sar|pulsar)\b", "platform", text, flags=re.IGNORECASE)
        return text or "restrained editorial framing"

    @staticmethod
    def _assert_identity_neutral(prompt: str, story: StoryBrief) -> None:
        folded = prompt.casefold()
        if "pul7sar" in folded or "pulsar" in folded:
            raise ValueError("DYNAMIC_RENDERER_PROMPT_PLATFORM_NAME_LEAK")
        for entity in (story.primary_entity, *story.secondary_entities):
            if entity and entity.casefold() in folded:
                raise ValueError("DYNAMIC_RENDERER_PROMPT_ENTITY_NAME_LEAK")


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
