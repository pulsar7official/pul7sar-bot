#!/usr/bin/env python3
"""Build the 6-family x 7-platform PUL7SAR adaptive brand pixel matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.adaptive_brand_overlay import AdaptiveBrandOverlayRenderer
from engine.intelligence.adaptive_brand_placement import AdaptiveBrandPlacementResolver
from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def build(output: str) -> dict[str, object]:
    profiles = PlatformProfileRegistry()
    resolver = AdaptiveBrandPlacementResolver()
    embedded = EmbeddedBrandMasterLoader().load()
    reference_size = embedded.metallic.size
    rows: list[dict[str, object]] = []

    for family in EditorialSceneFamily:
        for platform in SocialPlatform:
            profile = profiles.get(platform)
            adaptive = resolver.resolve(family=family, profile=profile)
            placement, height = AdaptiveBrandOverlayRenderer.resolve_placement(
                adaptive=adaptive,
                profile=profile,
                reference_size=reference_size,
            )
            clearance = round(min(profile.width, profile.height) * adaptive.minimum_clearance_ratio)
            safe = {
                "left": profile.safe_area.left + clearance,
                "right": profile.width - profile.safe_area.right - clearance,
                "top": profile.safe_area.top + clearance,
                "bottom": profile.height - profile.safe_area.bottom - clearance,
            }
            inside_safe_area = (
                placement.x >= safe["left"]
                and placement.x + placement.width <= safe["right"]
                and placement.y >= safe["top"]
                and placement.y + height <= safe["bottom"]
            )
            width_within_contract = placement.width <= round(profile.width * adaptive.max_width_ratio)
            height_within_contract = height <= round(profile.height * adaptive.max_height_ratio)
            historic_fixed_width_removed = placement.width != 870
            if not all((inside_safe_area, width_within_contract, height_within_contract, historic_fixed_width_removed)):
                raise RuntimeError(
                    "ADAPTIVE_BRAND_PIXEL_MATRIX_VIOLATION: "
                    f"family={family.value}; platform={platform.value}"
                )
            rows.append({
                "family": family.value,
                "platform": platform.value,
                "canvas": {"width": profile.width, "height": profile.height},
                "zone": adaptive.zone.value,
                "center_ratio": {"x": adaptive.center_x_ratio, "y": adaptive.center_y_ratio},
                "max_width_ratio": adaptive.max_width_ratio,
                "max_height_ratio": adaptive.max_height_ratio,
                "minimum_clearance_ratio": adaptive.minimum_clearance_ratio,
                "pixel_box": {
                    "x": placement.x,
                    "y": placement.y,
                    "width": placement.width,
                    "height": height,
                },
                "safe_box_after_clearance": safe,
                "inside_safe_area": inside_safe_area,
                "width_within_contract": width_within_contract,
                "height_within_contract": height_within_contract,
                "historic_fixed_width_removed": historic_fixed_width_removed,
            })

    manifest = {
        "manifest_version": "pul7sar-adaptive-brand-pixel-matrix-v1",
        "overlay_contract": "pul7sar-adaptive-brand-overlay-v1",
        "placement_contract": "pul7sar-adaptive-brand-placement-v1",
        "platform_profile_version": PlatformProfileRegistry.VERSION,
        "embedded_bundle_sha256": embedded.receipt.bundle_sha256,
        "reference_size": {"width": reference_size[0], "height": reference_size[1]},
        "family_count": len(EditorialSceneFamily),
        "platform_count": len(SocialPlatform),
        "decision_count": len(rows),
        "historic_fixed_brand_width_px": 870,
        "all_inside_safe_area": all(row["inside_safe_area"] for row in rows),
        "all_within_family_scale_contract": all(
            row["width_within_contract"] and row["height_within_contract"] for row in rows
        ),
        "historic_fixed_width_removed_everywhere": all(row["historic_fixed_width_removed"] for row in rows),
        "image_created": False,
        "generator_used": False,
        "network_used": False,
        "publication_ready": False,
        "placements": rows,
    }
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="output/phase18_adaptive_brand_pixel_matrix/manifest.json")
    args = parser.parse_args()
    print(json.dumps(build(args.output), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
