"""Provider-neutral original-scene specification and dry-run compiler.

The scene specification is the last structured artifact before an authorized
image provider. It is deliberately explicit about platform dimensions, safe
areas, subject identity, composition, brand/entity assets, factual constraints,
and forbidden visual elements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional

from engine.intelligence.concept_director import ConceptBrief, ProposedConcept
from engine.intelligence.models import IdentityPlan, IdentityStatus, LockedClaim, VisualIntent
from engine.intelligence.platform_profiles import PlatformImageProfile, SocialPlatform


@dataclass(frozen=True)
class SceneIdentityReference:
    entity_name: str
    sport: Optional[str] = None
    role: Optional[str] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    affiliation: Optional[str] = None
    confidence: float = 0.0

    @classmethod
    def from_identity_plan(cls, plan: IdentityPlan) -> "SceneIdentityReference":
        if plan.status is not IdentityStatus.VERIFIED or not plan.depiction_allowed:
            raise ValueError("scene identity requires verified depiction-allowed IdentityPlan")
        if not plan.entity_name:
            raise ValueError("verified identity requires entity_name")
        return cls(
            entity_name=plan.entity_name,
            sport=plan.sport,
            role=plan.role,
            gender=plan.gender,
            nationality=plan.nationality,
            affiliation=plan.team_or_affiliation,
            confidence=plan.confidence,
        )


@dataclass(frozen=True)
class OriginalSceneSpecification:
    platform: SocialPlatform
    width: int
    height: int
    aspect_ratio: str
    safe_area: Mapping[str, int]
    family: str
    concept: str
    subject: Optional[str]
    identity_reference: Optional[SceneIdentityReference]
    environment: str
    composition: str
    camera_direction: str
    emotional_mood: str
    palette_strategy: Optional[str]
    required_assets: tuple[str, ...] = field(default_factory=tuple)
    visual_copy: Optional[str] = None
    factual_constraints: tuple[str, ...] = field(default_factory=tuple)
    forbidden_visual_elements: tuple[str, ...] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be positive integer")
        for name in ("aspect_ratio", "family", "concept", "environment", "composition", "camera_direction", "emotional_mood"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        object.__setattr__(self, "safe_area", MappingProxyType(dict(self.safe_area)))
        object.__setattr__(self, "required_assets", tuple(self.required_assets))
        object.__setattr__(self, "factual_constraints", tuple(self.factual_constraints))
        object.__setattr__(self, "forbidden_visual_elements", tuple(self.forbidden_visual_elements))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class SceneSpecCompiler:
    """Compile approved editorial state into a dry-run scene specification."""

    _DEFAULT_ENVIRONMENT = {
        "results": "sport-specific arena or stadium atmosphere tied to the verified event",
        "transfers": "premium editorial transfer environment suggesting movement or negotiation",
        "matchday": "anticipatory venue environment before competition",
        "player_stories": "sport-specific editorial portrait environment",
        "serious_news": "restrained factual editorial environment",
        "organization": "institutional editorial environment",
        "general_world": "global sports editorial world led by PUL7SAR identity",
    }

    _DEFAULT_CAMERA = {
        "results": "dynamic medium-wide hero framing with clear result hierarchy",
        "transfers": "cinematic medium shot with directional depth and restrained symbolism",
        "matchday": "wide-to-medium anticipatory framing with venue context",
        "player_stories": "editorial portrait framing with sport-authentic posture",
        "serious_news": "restrained documentary-style framing",
        "organization": "balanced institutional composition",
        "general_world": "wide premium editorial framing in one continuous physical scene with one coherent perspective and one dominant visual hierarchy",
    }

    def compile(
        self,
        *,
        profile: PlatformImageProfile,
        intent: VisualIntent,
        concept_brief: ConceptBrief,
        proposed_concept: ProposedConcept,
        locked_claims: tuple[LockedClaim, ...] = (),
        required_assets: tuple[str, ...] = (),
        extra_forbidden_elements: tuple[str, ...] = (),
    ) -> OriginalSceneSpecification:
        if intent.family != concept_brief.family:
            raise ValueError("intent and concept brief family mismatch")

        identity_reference = None
        if intent.identity_plan is not None:
            identity_reference = SceneIdentityReference.from_identity_plan(intent.identity_plan)

        constraints = tuple(sorted(item.value for item in concept_brief.required_constraints))
        factual_constraints = tuple(
            claim.text for claim in locked_claims if getattr(claim.kind, "value", None) == "fact"
        )

        forbidden = tuple(dict.fromkeys(constraints + tuple(extra_forbidden_elements)))
        safe_area = {
            "top": profile.safe_area.top,
            "right": profile.safe_area.right,
            "bottom": profile.safe_area.bottom,
            "left": profile.safe_area.left,
        }

        return OriginalSceneSpecification(
            platform=profile.platform,
            width=profile.width,
            height=profile.height,
            aspect_ratio=profile.aspect_ratio,
            safe_area=safe_area,
            family=intent.family,
            concept=proposed_concept.description,
            subject=intent.hero_entity,
            identity_reference=identity_reference,
            environment=self._DEFAULT_ENVIRONMENT.get(intent.family, "premium sports editorial environment"),
            composition=(
                f"art-directed composition inside {profile.width}x{profile.height}; "
                f"keep critical face, logo, score, headline and social footer inside safe area"
            ),
            camera_direction=self._DEFAULT_CAMERA.get(intent.family, "balanced editorial framing"),
            emotional_mood=intent.sentiment.value,
            palette_strategy=intent.color_strategy,
            required_assets=required_assets,
            visual_copy=intent.visual_copy,
            factual_constraints=factual_constraints,
            forbidden_visual_elements=forbidden,
            metadata={
                "profile_version": "2026-08-pul7sar-v1",
                "crop_strategy": profile.crop_strategy,
                "surface": profile.metadata.get("surface"),
                "dry_run": True,
            },
        )
