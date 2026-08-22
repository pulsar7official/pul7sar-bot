"""Curated zero-cost local model candidates for Phase 18 development.

This module contains declared evaluation profiles, not runtime installation code.
A profile being present here does not mean the model is installed or available
on the current machine.
"""

from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.cost_policy import BillingClass, ProviderEconomics
from engine.intelligence.provider_capabilities import ProviderCapabilities, ProviderFeature


@dataclass(frozen=True)
class LocalModelCandidate:
    provider_id: str
    model_id: str
    license_id: str
    minimum_vram_gb: float
    maximum_megapixels: float
    supports_native_negative_prompt: bool
    supports_multi_reference: bool
    notes: str
    generation_alignment: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.generation_alignment, int) or isinstance(self.generation_alignment, bool) or self.generation_alignment <= 0:
            raise ValueError("generation_alignment must be a positive integer")

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
        return ProviderCapabilities(
            provider_id=self.provider_id,
            features=frozenset(features),
            max_width=2048,
            max_height=2048,
            supported_aspect_ratios=frozenset({"4:5", "9:16", "16:9"}),
            max_reference_images=4 if self.supports_multi_reference else 1,
            metadata={
                "model_id": self.model_id,
                "license_id": self.license_id,
                "minimum_vram_gb": self.minimum_vram_gb,
                "maximum_megapixels": self.maximum_megapixels,
                "generation_alignment": self.generation_alignment,
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


FLUX2_KLEIN_4B_LOCAL = LocalModelCandidate(
    provider_id="local-flux2-klein-4b",
    model_id="black-forest-labs/FLUX.2-klein-4B",
    license_id="Apache-2.0",
    minimum_vram_gb=13.0,
    maximum_megapixels=4.0,
    supports_native_negative_prompt=False,
    supports_multi_reference=True,
    notes=(
        "First zero-cost local evaluation candidate. Apache-2.0 4B FLUX.2 klein "
        "profile with text-to-image, editing and multi-reference support. PUL7SAR "
        "uses a conservative 13 GB local VRAM readiness floor from current BFL "
        "guidance/model-card documentation. Diffusers Flux2KleinPipeline packs VAE "
        "latents and expects image dimensions aligned to 16 pixels, so PUL7SAR "
        "generates on an aligned native canvas and deterministically normalizes to "
        "the exact destination canvas afterward. Negative constraints are positively reframed."
    ),
    generation_alignment=16,
)

ZERO_COST_LOCAL_CANDIDATES = (FLUX2_KLEIN_4B_LOCAL,)
