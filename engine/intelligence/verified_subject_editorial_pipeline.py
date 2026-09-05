"""Execution order for identity-led PUL7SAR editorial visuals.

This is the orchestration contract for transfer, injury and statement visuals
whose hero is a real verified person. It prevents accidental layer inversion:
atmosphere is prepared first, verified subject pixels enter next, exact marks and
copy remain deterministic, then PUL7SAR branding is applied before QA/export.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from engine.intelligence.sports_editorial_scene import EditorialSceneFamily, SportsEditorialScenePlan


class VerifiedSubjectStage(str, Enum):
    PREPARE_ATMOSPHERE = "prepare_atmosphere"
    COMPOSE_VERIFIED_SUBJECT = "compose_verified_subject"
    APPLY_EXACT_CONTEXT_ASSETS = "apply_exact_context_assets"
    APPLY_EDITORIAL_COPY = "apply_editorial_copy"
    APPLY_PUL7SAR_IDENTITY = "apply_pul7sar_identity"
    VISUAL_QA = "visual_qa"
    EXPORT_CANDIDATE = "export_candidate"


@dataclass(frozen=True)
class VerifiedSubjectPipelineStep:
    stage: VerifiedSubjectStage
    owner: str
    instruction: str


@dataclass(frozen=True)
class VerifiedSubjectEditorialPipeline:
    family: str
    steps: tuple[VerifiedSubjectPipelineStep, ...]
    generator_may_own_subject: bool
    placeholder_allowed_in_real_candidate: bool
    publication_ready: bool
    metadata: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


class VerifiedSubjectEditorialPipelinePlanner:
    _SUPPORTED = {
        EditorialSceneFamily.TRANSFER_SIGNATURE,
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
    }

    def compile(self, scene: SportsEditorialScenePlan) -> VerifiedSubjectEditorialPipeline:
        if not isinstance(scene, SportsEditorialScenePlan):
            raise TypeError("scene must be SportsEditorialScenePlan")
        if scene.family not in self._SUPPORTED:
            raise ValueError("verified-subject editorial pipeline accepts only identity-led scene families")

        steps = (
            VerifiedSubjectPipelineStep(
                VerifiedSubjectStage.PREPARE_ATMOSPHERE,
                "scene_engine",
                "Prepare story-appropriate atmosphere only. Do not render a readable brand, exact crest, score, statistics, or person identity.",
            ),
            VerifiedSubjectPipelineStep(
                VerifiedSubjectStage.COMPOSE_VERIFIED_SUBJECT,
                "verified_subject_compositor",
                "Composite exact SHA-locked verified subject pixels after IdentityPlan approval; no face generation, redraw, identity swap, or placeholder.",
            ),
            VerifiedSubjectPipelineStep(
                VerifiedSubjectStage.APPLY_EXACT_CONTEXT_ASSETS,
                "deterministic_compositor",
                "Apply exact approved club/competition context assets without generative reinterpretation.",
            ),
            VerifiedSubjectPipelineStep(
                VerifiedSubjectStage.APPLY_EDITORIAL_COPY,
                "typography_renderer",
                "Render concise approved editorial copy deterministically with locale-aware typography and safe-area geometry.",
            ),
            VerifiedSubjectPipelineStep(
                VerifiedSubjectStage.APPLY_PUL7SAR_IDENTITY,
                "brand_renderer",
                "Apply exact PUL7SAR Brand Master last among visual identity layers: fixed metallic body, enlarged 7, pulse below, football near R; only 7/pulse may receive verified accent.",
            ),
            VerifiedSubjectPipelineStep(
                VerifiedSubjectStage.VISUAL_QA,
                "quality_gates",
                "Verify subject provenance, identity match, text, brand geometry, exact assets, story neutrality, composition quality and artifact hashes.",
            ),
            VerifiedSubjectPipelineStep(
                VerifiedSubjectStage.EXPORT_CANDIDATE,
                "candidate_gate",
                "Export a review candidate only after QA; publication remains independently gated.",
            ),
        )
        return VerifiedSubjectEditorialPipeline(
            family=scene.family.value,
            steps=steps,
            generator_may_own_subject=False,
            placeholder_allowed_in_real_candidate=False,
            publication_ready=False,
            metadata={
                "contract": "pul7sar-verified-subject-editorial-pipeline-v1",
                "provider_agnostic": True,
                "zero_cost_compatible": True,
                "subject_source": "exact_verified_asset_only",
                "brand_identity_id": scene.brand_identity_id,
            },
        )
