"""PUL7SAR visual-brain contracts: concept competition before rendering and
fail-closed visual criticism after rendering.

The image renderer is deliberately treated as replaceable.  The durable product
logic lives here: propose meaningfully different editorial concepts, reject
near-duplicate/template concepts, and accept pixels only when they are both
factually safe *and* visually worth publishing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class VisualConceptCandidate:
    concept_id: str
    title: str
    editorial_metaphor: str
    scene_prompt: str
    camera_language: str
    focal_strategy: str
    negative_space_strategy: str
    signature_elements: tuple[str, ...]
    forbidden_elements: tuple[str, ...]
    preflight_score: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("concept_id", "title", "editorial_metaphor", "scene_prompt", "camera_language", "focal_strategy", "negative_space_strategy"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not 0.0 <= self.preflight_score <= 1.0:
            raise ValueError("preflight_score must be between 0 and 1")
        object.__setattr__(self, "signature_elements", tuple(self.signature_elements))
        object.__setattr__(self, "forbidden_elements", tuple(self.forbidden_elements))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class VisualConceptCompetition:
    """Return diverse, story-authorized concepts rather than seed variants.

    This first benchmark is intentionally deterministic so CI can prove the
    architecture.  A future reasoning model may propose candidates, but it must
    still satisfy the same diversity and safety contract before rendering.
    """

    CONTRACT = "pul7sar-visual-brain-v1"

    _COMMON_FORBIDDEN = (
        "readable text, numerals, logos, signage or pseudo-text",
        "specific identifiable real venue, club or person",
        "goal frame or goal net",
        "penalty-area or goal-area lines",
        "corner arc or corner flag",
        "centre circle or halfway line",
        "partial regulation football geometry",
        "collage, split-screen, grid or image-within-image",
    )

    def preview_season_return(self) -> tuple[VisualConceptCandidate, ...]:
        concepts = (
            VisualConceptCandidate(
                concept_id="preview-light-awakening",
                title="The Lights Wake First",
                editorial_metaphor="the season returns as a dormant arena waking before the crowd",
                scene_prompt=(
                    "Create one premium cinematic editorial photograph about the return of football, set at blue hour inside a deliberately generic non-identifying stadium. "
                    "The playing surface must not be visible. Frame upward and across layered roof structure and dark seating so a sequence of floodlights is visibly coming alive through atmospheric haze, with one powerful bank of light as the hero and the rest receding in depth. "
                    "Use architectural scale, contrast and anticipation rather than a literal pitch, tunnel, trophy or player. Keep one naturally calm shadow region available for later editorial typography. The image must feel like a singular authored magazine cover photograph, not stock stadium coverage."
                ),
                camera_language="low oblique architectural view, 35mm editorial lens language, no broadcast viewpoint",
                focal_strategy="one awakening floodlight bank against dormant stadium structure",
                negative_space_strategy="natural dark roof/stand shadow, not an artificial blank box",
                signature_elements=("floodlight ignition", "blue-hour haze", "layered roof depth"),
                forbidden_elements=self._COMMON_FORBIDDEN + ("visible playing surface", "players tunnel as hero"),
                preflight_score=0.94,
            ),
            VisualConceptCandidate(
                concept_id="preview-seats-before-roar",
                title="Before the Roar",
                editorial_metaphor="empty seats hold the energy of the crowd just before a new season begins",
                scene_prompt=(
                    "Create one sophisticated editorial image expressing football's return through anticipation rather than match action. Show a close, diagonal rhythm of generic stadium seats in the foreground, mostly in shadow, with distant anonymous crowd arrival rendered only as soft human-scale atmosphere and warm concourse light far behind. "
                    "No pitch or regulation football geometry may be visible. Build depth through repeating seat forms, selective practical light and shallow atmospheric separation. One seat row catches the first warm light and becomes the focal rhythm. Leave a naturally quieter upper region for later typography. Avoid documentary blandness: compose it like a premium sports-culture magazine opener."
                ),
                camera_language="close environmental 50mm perspective along seat rows, shallow layered depth",
                focal_strategy="first warm-lit row within a dark repeating seat rhythm",
                negative_space_strategy="soft upper background falloff created by depth, not empty canvas",
                signature_elements=("seat rhythm", "warm concourse glow", "arrival anticipation"),
                forbidden_elements=self._COMMON_FORBIDDEN + ("visible playing surface", "tunnel focal point"),
                preflight_score=0.91,
            ),
            VisualConceptCandidate(
                concept_id="preview-gates-open",
                title="The Gates Open",
                editorial_metaphor="a new season begins as the stadium opens to supporters",
                scene_prompt=(
                    "Create a cinematic sports-editorial scene outside the inner bowl of a deliberately generic football venue at dusk: monumental anonymous entry gates and concrete/metal architecture opening toward a wash of warm stadium light, with a few distant unidentifiable supporter silhouettes moving toward it. "
                    "Do not show the pitch, goals, markings, club signage, readable tickets or text. The visual hero is the threshold of warm light between dark architectural masses, symbolizing the season reopening. Use strong foreground-to-background depth and restrained realism, with a quiet side plane suitable for later editorial copy. It must feel designed for a global premium sports publication, not like a travel photograph."
                ),
                camera_language="ground-level wide-normal editorial perspective through architectural threshold",
                focal_strategy="warm luminous threshold framed by dark structural masses",
                negative_space_strategy="restrained side wall/sky gradient integrated into architecture",
                signature_elements=("opening gates", "warm threshold", "supporter silhouettes"),
                forbidden_elements=self._COMMON_FORBIDDEN + ("visible playing surface", "readable gate signage"),
                preflight_score=0.90,
            ),
            VisualConceptCandidate(
                concept_id="preview-sound-before-kickoff",
                title="A Stadium Holding Its Breath",
                editorial_metaphor="anticipation is shown through atmosphere and scale before the event begins",
                scene_prompt=(
                    "Create one restrained, high-end editorial photograph from beneath a generic stadium canopy at dusk, looking across layered crowd architecture and luminous atmospheric haze without revealing the playing surface. "
                    "A suspended bank of practical stadium lights and drifting mist create a strong diagonal beam through the frame; anonymous crowd texture remains secondary and no individual is identifiable. The hero is the tension between darkness and the incoming light, as if the venue is holding its breath before the season begins. Preserve a naturally calm region for later headline composition. No literal football icons, tunnel hero, pitch, trophy or scoreboard."
                ),
                camera_language="compressed oblique canopy view, cinematic 70mm depth, no central symmetry",
                focal_strategy="diagonal light beam crossing layered crowd architecture",
                negative_space_strategy="dark atmospheric falloff beside the beam",
                signature_elements=("canopy", "diagonal light beam", "crowd texture"),
                forbidden_elements=self._COMMON_FORBIDDEN + ("visible playing surface", "scoreboard", "tunnel hero"),
                preflight_score=0.92,
            ),
        )
        self.assert_diverse(concepts)
        return concepts

    @staticmethod
    def assert_diverse(concepts: Sequence[VisualConceptCandidate]) -> None:
        if len(concepts) < 3:
            raise ValueError("concept competition requires at least three alternatives")
        ids = [item.concept_id for item in concepts]
        if len(ids) != len(set(ids)):
            raise ValueError("concept ids must be unique")
        signatures = [frozenset(item.signature_elements) for item in concepts]
        for left_index, left in enumerate(signatures):
            for right in signatures[left_index + 1:]:
                union = left | right
                overlap = (len(left & right) / len(union)) if union else 1.0
                if overlap > 0.50:
                    raise ValueError("concept competition collapsed into near-duplicate visual templates")


@dataclass(frozen=True)
class VisualCriticEvidence:
    concept_id: str
    geometry_violation: bool = False
    pseudo_text_detected: bool = False
    identity_violation: bool = False
    factual_violation: bool = False
    generation_defect: bool = False
    editorial_specificity: float = 0.0
    visual_impact: float = 0.0
    composition_quality: float = 0.0
    photographic_coherence: float = 0.0
    concept_fidelity: float = 0.0
    ordinary_stock_risk: float = 1.0

    def __post_init__(self) -> None:
        if not self.concept_id.strip():
            raise ValueError("concept_id must be non-empty")
        for name in ("editorial_specificity", "visual_impact", "composition_quality", "photographic_coherence", "concept_fidelity", "ordinary_stock_risk"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class VisualCriticDecision:
    accepted: bool
    score: float
    failures: tuple[str, ...]


class VisualCriticGate:
    """Reject technically safe but visually ordinary images as well as hard errors."""

    CONTRACT = "pul7sar-visual-critic-v1"

    def evaluate(self, evidence: VisualCriticEvidence) -> VisualCriticDecision:
        failures: list[str] = []
        hard = {
            "sport geometry violation": evidence.geometry_violation,
            "generated pseudo-text/readable text": evidence.pseudo_text_detected,
            "identity violation": evidence.identity_violation,
            "factual violation": evidence.factual_violation,
            "generation defect": evidence.generation_defect,
        }
        failures.extend(name for name, present in hard.items() if present)
        thresholds = {
            "editorial specificity below premium floor": (evidence.editorial_specificity, 0.72),
            "visual impact below premium floor": (evidence.visual_impact, 0.72),
            "composition quality below premium floor": (evidence.composition_quality, 0.75),
            "photographic coherence below premium floor": (evidence.photographic_coherence, 0.78),
            "concept fidelity below premium floor": (evidence.concept_fidelity, 0.75),
        }
        failures.extend(label for label, (value, floor) in thresholds.items() if value < floor)
        if evidence.ordinary_stock_risk > 0.35:
            failures.append("technically correct but visually ordinary/stock-like")
        score = (
            evidence.editorial_specificity * 0.20
            + evidence.visual_impact * 0.25
            + evidence.composition_quality * 0.20
            + evidence.photographic_coherence * 0.15
            + evidence.concept_fidelity * 0.20
        )
        if failures:
            score = 0.0
        return VisualCriticDecision(not failures, round(score, 6), tuple(failures))
