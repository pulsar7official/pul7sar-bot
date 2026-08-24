"""Curated zero-cost local image-model candidates for Phase 18.

Profiles describe evaluation intent and verified public metadata; they are not an
installation claim. In particular, a model with ``minimum_vram_gb=None`` may be
selected for a portable quality handoff, but local execution MUST fail closed
until a compatible hardware floor is proven by project evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from engine.intelligence.cost_policy import BillingClass, ProviderEconomics
from engine.intelligence.provider_capabilities import ProviderCapabilities, ProviderFeature


class ImageQualityTier(str, Enum):
    ELITE = "elite"
    PREMIUM = "premium"
    LIGHTWEIGHT = "lightweight"


class ImageModelRole(str, Enum):
    CINEMATIC_BASE_SCENE = "cinematic_base_scene"
    SUBJECT_DRIVEN_BASE_SCENE = "subject_driven_base_scene"
    ENGINEERING_FALLBACK = "engineering_fallback"


@dataclass(frozen=True)
class LocalModelCandidate:
    provider_id: str
    model_id: str
    license_id: str
    minimum_vram_gb: float | None
    maximum_megapixels: float
    supports_native_negative_prompt: bool
    supports_multi_reference: bool
    notes: str
    generation_alignment: int = 1
    quality_tier: ImageQualityTier = ImageQualityTier.LIGHTWEIGHT
    intended_role: ImageModelRole = ImageModelRole.ENGINEERING_FALLBACK
    runtime_adapter: str = "diffusers"
    repository_size_gb: float | None = None
    runtime_floor_proven: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.generation_alignment, int) or isinstance(self.generation_alignment, bool) or self.generation_alignment <= 0:
            raise ValueError("generation_alignment must be a positive integer")
        if not isinstance(self.quality_tier, ImageQualityTier):
            raise TypeError("quality_tier must be ImageQualityTier")
        if not isinstance(self.intended_role, ImageModelRole):
            raise TypeError("intended_role must be ImageModelRole")
        if not isinstance(self.runtime_adapter, str) or not self.runtime_adapter.strip():
            raise ValueError("runtime_adapter is required")
        if self.minimum_vram_gb is not None and self.minimum_vram_gb <= 0:
            raise ValueError("minimum_vram_gb must be positive or None")
        if self.runtime_floor_proven != (self.minimum_vram_gb is not None):
            raise ValueError("runtime_floor_proven must match presence of minimum_vram_gb")
        if self.maximum_megapixels <= 0:
            raise ValueError("maximum_megapixels must be positive")
        if self.repository_size_gb is not None and self.repository_size_gb <= 0:
            raise ValueError("repository_size_gb must be positive or None")

    @property
    def economics(self) -> ProviderEconomics:
        return ProviderEconomics(
            self.provider_id,
            BillingClass.LOCAL_FREE,
            requires_payment_method=False,
            notes="Open/local weights; no per-image API charge in local execution.",
        )

    @property
    def capabilities(self) -> ProviderCapabilities:
        features = {ProviderFeature.TEXT_TO_IMAGE, ProviderFeature.REFERENCE_IMAGE}
        if self.supports_multi_reference:
            features.add(ProviderFeature.MULTIPLE_REFERENCES)
        if self.supports_native_negative_prompt:
            features.add(ProviderFeature.NEGATIVE_INSTRUCTIONS)
        max_side = 2048
        return ProviderCapabilities(
            provider_id=self.provider_id,
            features=frozenset(features),
            max_width=max_side,
            max_height=max_side,
            supported_aspect_ratios=frozenset({"4:5", "9:16", "16:9"}),
            max_reference_images=4 if self.supports_multi_reference else 1,
            metadata={
                "model_id": self.model_id,
                "license_id": self.license_id,
                "minimum_vram_gb": self.minimum_vram_gb,
                "runtime_floor_proven": self.runtime_floor_proven,
                "maximum_megapixels": self.maximum_megapixels,
                "generation_alignment": self.generation_alignment,
                "quality_tier": self.quality_tier.value,
                "intended_role": self.intended_role.value,
                "runtime_adapter": self.runtime_adapter,
                "repository_size_gb": self.repository_size_gb,
                "local_only": True,
            },
        )

    def supports_canvas(self, width: int, height: int) -> bool:
        if width <= 0 or height <= 0:
            return False
        return (width * height) <= int(self.maximum_megapixels * 1_000_000)

    def align_canvas(self, width: int, height: int) -> tuple[int, int]:
        if width <= 0 or height <= 0:
            raise ValueError("canvas dimensions must be positive")
        alignment = self.generation_alignment
        aligned_width = ((width + alignment - 1) // alignment) * alignment
        aligned_height = ((height + alignment - 1) // alignment) * alignment
        if not self.supports_canvas(aligned_width, aligned_height):
            raise ValueError("aligned generation canvas exceeds selected local model envelope")
        return aligned_width, aligned_height


QWEN_IMAGE_2512_LOCAL = LocalModelCandidate(
    provider_id="local-qwen-image-2512",
    model_id="Qwen/Qwen-Image-2512",
    license_id="Apache-2.0",
    minimum_vram_gb=None,
    maximum_megapixels=4.0,
    supports_native_negative_prompt=True,
    supports_multi_reference=False,
    notes=(
        "Elite PUL7SAR cinematic-base candidate. Official model distribution uses "
        "QwenImagePipeline/Diffusers and is approximately 57.7 GB. The repository "
        "does not encode an official PUL7SAR-tested VRAM floor, so execution stays "
        "blocked until local hardware compatibility is proven. The 4 MP envelope "
        "is a conservative PUL7SAR production limit, not a permanent model maximum."
    ),
    generation_alignment=16,
    quality_tier=ImageQualityTier.ELITE,
    intended_role=ImageModelRole.CINEMATIC_BASE_SCENE,
    runtime_adapter="qwen_image_diffusers",
    repository_size_gb=57.7,
    runtime_floor_proven=False,
)


HIDREAM_O1_IMAGE_DEV_LOCAL = LocalModelCandidate(
    provider_id="local-hidream-o1-image-dev",
    model_id="HiDream-ai/HiDream-O1-Image-Dev",
    license_id="MIT",
    minimum_vram_gb=None,
    maximum_megapixels=4.0,
    supports_native_negative_prompt=True,
    supports_multi_reference=True,
    notes=(
        "Elite alternate for cinematic and subject-driven base-scene evaluation. "
        "Official model card describes generation, editing and subject-driven "
        "personalization up to 2048x2048; repository size is approximately 35.2 GB. "
        "Execution remains blocked until a PUL7SAR-tested VRAM floor is proven."
    ),
    generation_alignment=16,
    quality_tier=ImageQualityTier.ELITE,
    intended_role=ImageModelRole.SUBJECT_DRIVEN_BASE_SCENE,
    runtime_adapter="hidream_o1_transformers",
    repository_size_gb=35.2,
    runtime_floor_proven=False,
)


FLUX2_KLEIN_4B_LOCAL = LocalModelCandidate(
    provider_id="local-flux2-klein-4b",
    model_id="black-forest-labs/FLUX.2-klein-4B",
    license_id="Apache-2.0",
    minimum_vram_gb=13.0,
    maximum_megapixels=4.0,
    supports_native_negative_prompt=False,
    supports_multi_reference=True,
    notes=(
        "Lightweight zero-cost engineering fallback. Apache-2.0 4B FLUX.2 klein "
        "profile with text-to-image, editing and multi-reference support. PUL7SAR "
        "uses a conservative 13 GB local VRAM readiness floor from current BFL "
        "guidance/model-card documentation. It is not the Elite visual-quality target."
    ),
    generation_alignment=16,
    quality_tier=ImageQualityTier.LIGHTWEIGHT,
    intended_role=ImageModelRole.ENGINEERING_FALLBACK,
    runtime_adapter="flux2_klein_diffusers",
    runtime_floor_proven=True,
)


# Quality order is intentional: selectors may move downward only when the caller
# explicitly accepts a lower quality tier. No fallback may silently masquerade as
# an Elite/Golden candidate.
ZERO_COST_LOCAL_CANDIDATES = (
    QWEN_IMAGE_2512_LOCAL,
    HIDREAM_O1_IMAGE_DEV_LOCAL,
    FLUX2_KLEIN_4B_LOCAL,
)
