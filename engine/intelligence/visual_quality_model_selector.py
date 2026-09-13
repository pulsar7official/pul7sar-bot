"""Quality-first local image-model selection for PUL7SAR Phase 18.

The selector separates visual ambition from runtime availability. An Elite request
may produce a portable handoff for an Elite candidate even when the current host
cannot execute it; it may never silently downgrade to a lightweight model and
still claim Golden/Elite quality.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.zero_cost_models import (
    HIDREAM_O1_IMAGE_DEV_LOCAL,
    QWEN_IMAGE_2512_LOCAL,
    ZERO_COST_LOCAL_CANDIDATES,
    ImageModelRole,
    ImageQualityTier,
    LocalModelCandidate,
)


class QualitySelectionMode(str, Enum):
    STRICT = "strict"
    EXPLICIT_DOWNGRADE = "explicit_downgrade"


@dataclass(frozen=True)
class VisualQualityModelDecision:
    candidate: LocalModelCandidate
    requested_tier: ImageQualityTier
    selected_tier: ImageQualityTier
    portable_only: bool
    downgrade_used: bool
    reason: str
    contract: str = "pul7sar-visual-quality-model-decision-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, LocalModelCandidate):
            raise TypeError("candidate must be LocalModelCandidate")
        if not isinstance(self.requested_tier, ImageQualityTier) or not isinstance(self.selected_tier, ImageQualityTier):
            raise TypeError("quality tiers must be ImageQualityTier")
        if self.selected_tier is not self.candidate.quality_tier:
            raise ValueError("selected tier must match candidate")
        if self.downgrade_used and self.requested_tier is self.selected_tier:
            raise ValueError("downgrade_used cannot be true without tier change")
        if not self.reason.strip():
            raise ValueError("selection reason is required")


class VisualQualityModelSelector:
    """Select by intended visual quality, never by accidental runtime convenience."""

    _RANK = {
        ImageQualityTier.LIGHTWEIGHT: 1,
        ImageQualityTier.PREMIUM: 2,
        ImageQualityTier.ELITE: 3,
    }

    def __init__(self, candidates: tuple[LocalModelCandidate, ...] = ZERO_COST_LOCAL_CANDIDATES) -> None:
        if not candidates:
            raise ValueError("at least one local model candidate is required")
        if len({candidate.provider_id for candidate in candidates}) != len(candidates):
            raise ValueError("duplicate provider_id in local model candidates")
        self._candidates = tuple(candidates)

    @staticmethod
    def _role_score(candidate: LocalModelCandidate, preferred_role: ImageModelRole) -> int:
        if candidate.intended_role is preferred_role:
            return 3
        # HiDream subject-driven is still suitable as a cinematic alternate.
        if preferred_role is ImageModelRole.CINEMATIC_BASE_SCENE and candidate is HIDREAM_O1_IMAGE_DEV_LOCAL:
            return 2
        # Qwen cinematic can service generic base scenes when no identity-driven edit is required.
        if preferred_role is ImageModelRole.SUBJECT_DRIVEN_BASE_SCENE and candidate is QWEN_IMAGE_2512_LOCAL:
            return 1
        return 0

    def select(
        self,
        *,
        requested_tier: ImageQualityTier,
        preferred_role: ImageModelRole = ImageModelRole.CINEMATIC_BASE_SCENE,
        mode: QualitySelectionMode = QualitySelectionMode.STRICT,
    ) -> VisualQualityModelDecision:
        if not isinstance(requested_tier, ImageQualityTier):
            raise TypeError("requested_tier must be ImageQualityTier")
        if not isinstance(preferred_role, ImageModelRole):
            raise TypeError("preferred_role must be ImageModelRole")
        if not isinstance(mode, QualitySelectionMode):
            raise TypeError("mode must be QualitySelectionMode")

        requested_rank = self._RANK[requested_tier]
        exact = [c for c in self._candidates if c.quality_tier is requested_tier and self._role_score(c, preferred_role) > 0]
        if exact:
            candidate = sorted(
                exact,
                key=lambda c: (-self._role_score(c, preferred_role), c.repository_size_gb or 10_000, c.provider_id),
            )[0]
            return VisualQualityModelDecision(
                candidate=candidate,
                requested_tier=requested_tier,
                selected_tier=candidate.quality_tier,
                portable_only=not candidate.runtime_floor_proven,
                downgrade_used=False,
                reason=(
                    f"selected {candidate.model_id} for {requested_tier.value} {preferred_role.value}; "
                    + ("runtime floor unproven, portable handoff only" if not candidate.runtime_floor_proven else "runtime floor proven")
                ),
            )

        if mode is QualitySelectionMode.STRICT:
            raise ValueError(f"NO_{requested_tier.value.upper()}_MODEL_AVAILABLE_FOR_{preferred_role.value.upper()}")

        eligible = [
            c for c in self._candidates
            if self._RANK[c.quality_tier] < requested_rank and self._role_score(c, preferred_role) > 0
        ]
        if not eligible:
            raise ValueError("NO_EXPLICIT_DOWNGRADE_CANDIDATE_AVAILABLE")
        candidate = sorted(
            eligible,
            key=lambda c: (-self._RANK[c.quality_tier], -self._role_score(c, preferred_role), c.provider_id),
        )[0]
        return VisualQualityModelDecision(
            candidate=candidate,
            requested_tier=requested_tier,
            selected_tier=candidate.quality_tier,
            portable_only=not candidate.runtime_floor_proven,
            downgrade_used=True,
            reason=f"explicit caller-approved downgrade from {requested_tier.value} to {candidate.quality_tier.value}",
        )
