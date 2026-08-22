"""Serializable inspection manifest for PUL7SAR pre-generation review."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from engine.intelligence.batch_scene import PlatformScenePackage


@dataclass(frozen=True)
class DryRunManifest:
    story_id: str
    manifest_version: str
    platforms: Mapping[str, Mapping[str, Any]]

    def __post_init__(self) -> None:
        if not isinstance(self.story_id, str) or not self.story_id.strip():
            raise ValueError("story_id must be non-empty")
        if not self.platforms:
            raise ValueError("manifest must contain at least one platform")
        object.__setattr__(self, "platforms", MappingProxyType(dict(self.platforms)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "story_id": self.story_id,
            "manifest_version": self.manifest_version,
            "platforms": {key: dict(value) for key, value in self.platforms.items()},
        }


class DryRunManifestCompiler:
    VERSION = "pul7sar-phase18-manifest-v2"

    def compile(self, story_id: str, packages: tuple[PlatformScenePackage, ...]) -> DryRunManifest:
        packages = tuple(packages)
        if not packages:
            raise ValueError("packages must not be empty")
        data: dict[str, Mapping[str, Any]] = {}
        for item in packages:
            spec = item.specification
            package = item.generation_package
            key = spec.platform.value
            if key in data:
                raise ValueError(f"duplicate platform package: {key}")

            brand = None
            if item.brand_plan is not None:
                brand = {
                    "logo_asset_id": item.brand_plan.logo_asset_id,
                    "pulse_asset_id": item.brand_plan.pulse_asset_id,
                    "pulse_tint_hex": item.brand_plan.pulse_tint_hex,
                    "preserve_wordmark_exact": item.brand_plan.preserve_wordmark_exact,
                    "preserve_team_crests_exact": item.brand_plan.preserve_team_crests_exact,
                }

            theme = None
            if item.theme is not None:
                theme = {
                    "accent_hex": item.theme.accent_hex,
                    "source": item.theme.source,
                    "entity_name": item.theme.entity_name,
                    "verified": item.theme.verified,
                }

            data[key] = MappingProxyType({
                "canvas": package.canvas,
                "aspect_ratio": spec.aspect_ratio,
                "safe_area": dict(spec.safe_area),
                "layout_boxes": {role: dict(box) for role, box in package.layout_boxes.items()},
                "accent_hex": package.accent_hex,
                "theme": theme,
                "brand_plan": brand,
                "asset_ids": list(package.asset_ids),
                "factual_constraints": list(package.factual_constraints),
                "negative_constraints": list(package.negative_constraints),
                "scene_prompt": package.scene_prompt,
                "metadata": dict(package.metadata),
            })
        return DryRunManifest(story_id.strip(), self.VERSION, MappingProxyType(data))
