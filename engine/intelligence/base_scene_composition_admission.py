"""Bind an approved base scene to immutable provenance before family composition."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from PIL import Image

from engine.intelligence.base_scene_execution_gate import BaseSceneExecutionDecision
from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.zero_cost_models import ImageQualityTier


@dataclass(frozen=True)
class BaseSceneCompositionAdmission:
    png_path: str
    png_sha256: str
    provenance: LocalGenerationProvenance
    quality_tier: ImageQualityTier
    semantic_inspection_complete: bool
    layer_ownership_clean: bool
    composition_allowed: bool
    publication_ready: bool = False
    contract: str = "pul7sar-base-scene-composition-admission-v1"

    def __post_init__(self) -> None:
        if not isinstance(self.provenance, LocalGenerationProvenance):
            raise TypeError("provenance must be LocalGenerationProvenance")
        if not isinstance(self.quality_tier, ImageQualityTier):
            raise TypeError("quality_tier must be ImageQualityTier")
        if not self.semantic_inspection_complete or not self.layer_ownership_clean or not self.composition_allowed:
            raise ValueError("BASE_SCENE_ADMISSION_REQUIRES_COMPLETE_CLEAN_APPROVAL")
        if self.publication_ready:
            raise ValueError("BASE_SCENE_ADMISSION_ALONE_CANNOT_AUTHORIZE_PUBLICATION")

    def assert_bytes_unchanged(self) -> None:
        path = Path(self.png_path)
        if not path.is_file():
            raise FileNotFoundError(self.png_path)
        if sha256(path.read_bytes()).hexdigest() != self.png_sha256:
            raise ValueError("BASE_SCENE_BYTES_CHANGED_AFTER_ADMISSION")


class BaseSceneCompositionAdmissionCompiler:
    def compile(
        self,
        *,
        png_path: str,
        provenance: LocalGenerationProvenance,
        execution_decision: BaseSceneExecutionDecision,
        quality_tier: ImageQualityTier,
    ) -> BaseSceneCompositionAdmission:
        if not isinstance(provenance, LocalGenerationProvenance):
            raise TypeError("provenance must be LocalGenerationProvenance")
        if not isinstance(execution_decision, BaseSceneExecutionDecision):
            raise TypeError("execution_decision must be BaseSceneExecutionDecision")
        if not isinstance(quality_tier, ImageQualityTier):
            raise TypeError("quality_tier must be ImageQualityTier")
        if not execution_decision.allowed or not execution_decision.inspection_complete or execution_decision.blockers:
            raise ValueError("BASE_SCENE_EXECUTION_DECISION_NOT_APPROVED")
        path = Path(png_path)
        if not path.is_file():
            raise FileNotFoundError(png_path)
        with Image.open(path) as image:
            if image.size != (provenance.width, provenance.height):
                raise ValueError("BASE_SCENE_DIMENSIONS_DO_NOT_MATCH_PROVENANCE")
            image.verify()
        digest = sha256(path.read_bytes()).hexdigest()
        return BaseSceneCompositionAdmission(
            png_path=str(path),
            png_sha256=digest,
            provenance=provenance,
            quality_tier=quality_tier,
            semantic_inspection_complete=True,
            layer_ownership_clean=True,
            composition_allowed=True,
        )
