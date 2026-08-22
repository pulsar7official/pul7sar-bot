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
        features = {
            ProviderFeature.TEXT_TO_IMAGE,
            ProviderFeature.REFERENCE_IMAGE,
        }
        if self.supports_multi_reference:
            features.add(ProviderFeature.MULTIPLE_REFERENCES)
        if self.supports_native_negative_prompt:
            features.add(ProviderFeature.NEGATIVE_INSTRUCTIONS)
        # PUL7SAR post-composites official assets; provider-side exact asset
        # compositing is deliberately not required.
        return ProviderCapabilities(
            provider_id=self.provider_id,
            features=frozenset(features),
            max_width=2000,
            max_height=2000,
            supported_aspect_ratios=frozenset({"4:5", "9:16", "16:9"}),
            max_reference_images=4 if self.supports_multi_reference else 1,
            metadata={
                "model_id": self.model_id,
                "license_id": self.license_id,
                "minimum_vram_gb": self.minimum_vram_gb,
                "maximum_megapixels": self.maximum_megapixels,
                "local_only": True,
            },
        )

    def supports_canvas(self, width: int, height: int) -> bool:
        if width <= 0 or height <= 0:
            return False
        return (width * height) <= int(self.maximum_megapixels * 1_000_000)


FLUX2_KLEIN_4B_LOCAL = LocalModelCandidate(
    provider_id="local-flux2-klein-4b",
    model_id="black-forest-labs/FLUX.2-klein-4B",
    license_id="Apache-2.0",
    minimum_vram_gb=13.0,
    maximum_megapixels=4.0,
    supports_native_negative_prompt=False,
    supports_multi_reference=True,
    notes=(
        "First zero-cost local evaluation candidate. Fully open 4B FLUX.2 klein "
        "profile with text-to-image and multi-reference editing. Negative visual "
        "constraints must be positively reframed by PUL7SAR before execution."
    ),
)


ZERO_COST_LOCAL_CANDIDATES = (FLUX2_KLEIN_4B_LOCAL,)
