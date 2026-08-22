"""Provider capability and eligibility contracts for PUL7SAR original scenes.

No vendor is selected here. This module describes what a provider can do and
rejects providers that cannot satisfy a specific generation package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping


class ProviderFeature(str, Enum):
    TEXT_TO_IMAGE = "text_to_image"
    REFERENCE_IMAGE = "reference_image"
    IDENTITY_REFERENCE = "identity_reference"
    MULTIPLE_REFERENCES = "multiple_references"
    TRANSPARENT_PNG_INPUT = "transparent_png_input"
    EXACT_ASSET_COMPOSITING = "exact_asset_compositing"
    NEGATIVE_INSTRUCTIONS = "negative_instructions"
    DETERMINISTIC_SEED = "deterministic_seed"
    POST_COMPOSITING = "post_compositing"


@dataclass(frozen=True)
class ProviderCapabilities:
    provider_id: str
    features: frozenset[ProviderFeature]
    max_width: int
    max_height: int
    supported_aspect_ratios: frozenset[str] = field(default_factory=frozenset)
    max_reference_images: int = 0
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.provider_id, str) or not self.provider_id.strip():
            raise ValueError("provider_id must be non-empty")
        features = frozenset(self.features)
        if any(not isinstance(item, ProviderFeature) for item in features):
            raise TypeError("features must contain ProviderFeature values")
        for name in ("max_width", "max_height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.max_reference_images, int) or isinstance(self.max_reference_images, bool) or self.max_reference_images < 0:
            raise ValueError("max_reference_images must be a non-negative integer")
        object.__setattr__(self, "features", features)
        object.__setattr__(self, "supported_aspect_ratios", frozenset(self.supported_aspect_ratios))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True)
class ProviderRequirements:
    width: int
    height: int
    aspect_ratio: str
    required_features: frozenset[ProviderFeature] = field(default_factory=frozenset)
    reference_image_count: int = 0

    def __post_init__(self) -> None:
        for name in ("width", "height"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if not isinstance(self.aspect_ratio, str) or not self.aspect_ratio.strip():
            raise ValueError("aspect_ratio must be non-empty")
        features = frozenset(self.required_features)
        if any(not isinstance(item, ProviderFeature) for item in features):
            raise TypeError("required_features must contain ProviderFeature values")
        if not isinstance(self.reference_image_count, int) or isinstance(self.reference_image_count, bool) or self.reference_image_count < 0:
            raise ValueError("reference_image_count must be non-negative")
        object.__setattr__(self, "required_features", features)


@dataclass(frozen=True)
class ProviderEligibilityDecision:
    provider_id: str
    eligible: bool
    missing_features: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


class ProviderEligibilityGate:
    """Reject capability mismatches before authorization/execution."""

    def evaluate(self, capabilities: ProviderCapabilities, requirements: ProviderRequirements) -> ProviderEligibilityDecision:
        if not isinstance(capabilities, ProviderCapabilities):
            raise TypeError("capabilities must be ProviderCapabilities")
        if not isinstance(requirements, ProviderRequirements):
            raise TypeError("requirements must be ProviderRequirements")

        reasons: list[str] = []
        missing = sorted(feature.value for feature in requirements.required_features - capabilities.features)
        if missing:
            reasons.append("missing required features: " + ", ".join(missing))
        if requirements.width > capabilities.max_width or requirements.height > capabilities.max_height:
            reasons.append(
                f"requested canvas {requirements.width}x{requirements.height} exceeds provider maximum {capabilities.max_width}x{capabilities.max_height}"
            )
        if capabilities.supported_aspect_ratios and requirements.aspect_ratio not in capabilities.supported_aspect_ratios:
            reasons.append(f"unsupported aspect ratio: {requirements.aspect_ratio}")
        if requirements.reference_image_count > capabilities.max_reference_images:
            reasons.append(
                f"requires {requirements.reference_image_count} reference images but provider supports {capabilities.max_reference_images}"
            )
        return ProviderEligibilityDecision(
            provider_id=capabilities.provider_id,
            eligible=not reasons,
            missing_features=tuple(missing),
            reasons=tuple(reasons),
        )

    def assert_eligible(self, capabilities: ProviderCapabilities, requirements: ProviderRequirements) -> None:
        decision = self.evaluate(capabilities, requirements)
        if not decision.eligible:
            raise ValueError("provider is not eligible: " + "; ".join(decision.reasons))
