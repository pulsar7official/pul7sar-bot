#!/usr/bin/env python3
"""Build self-contained exact-shape PUL7SAR reference-brand studies.

Default execution loads the checksum-locked reference-derived layered master from
this repository. An approved source identity board may be supplied only as an
audit/re-derivation input. No network access, image generator, paid provider, or
font recreation is used for the brand mark.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

from engine.intelligence.brand_reference_renderer import (
    BrandReferencePlacement,
    BrandReferenceRenderer,
)


DEFAULT_VARIANTS = (
    ("pul7sar-default", "#D10F18"),
    ("chelsea-blue", "#034694"),
    ("real-white", "#F2F2F2"),
    ("dortmund-gold", "#FDE100"),
)


def _base(path: Path, *, width: int = 1080, height: int = 420) -> None:
    image = Image.new("RGB", (width, height), (2, 7, 14))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        t = y / max(1, height - 1)
        value = round(6 + 12 * (1.0 - abs(0.5 - t) * 2.0))
        draw.line((0, y, width, y), fill=(2, value, value + 8))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def build(*, output_dir: str, source_board: str | None = None) -> dict[str, object]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    base = root / ".reference-brand-base.png"
    _base(base)

    renderer = BrandReferenceRenderer()
    entries = []
    for name, accent in DEFAULT_VARIANTS:
        target = root / f"{name}.png"
        receipt = renderer.render_on_file(
            base_path=str(base),
            source_board_path=source_board,
            output_path=str(target),
            placement=BrandReferencePlacement(x=70, y=62, width=940),
            accent_hex=accent,
        )
        entries.append({
            "name": name,
            "accent_hex": receipt.accent_hex,
            "png": target.name,
            "png_sha256": receipt.output_sha256,
            "source_reference_sha256": receipt.source_reference_sha256,
            "brand_source_mode": receipt.brand_source_mode,
            "embedded_bundle_sha256": receipt.embedded_bundle_sha256,
            "metallic_layer_sha256": receipt.metallic_layer_sha256,
            "accent_layer_sha256": receipt.accent_layer_sha256,
            "football_layer_sha256": receipt.football_layer_sha256,
            "exact_reference_shape_used": receipt.exact_reference_shape_used,
            "transparent_reference_layers_used": receipt.transparent_reference_layers_used,
            "background_board_pixels_composited": receipt.background_board_pixels_composited,
            "font_recreation_used": receipt.font_recreation_used,
            "generic_ecg_recreation_used": receipt.generic_ecg_recreation_used,
            "generator_used": receipt.generator_used,
            "network_used": receipt.network_used,
            "publication_ready": receipt.publication_ready,
        })

    base.unlink(missing_ok=True)
    manifest = {
        "manifest_version": "pul7sar-reference-brand-study-v2-self-contained",
        "renderer_contract": "pul7sar-brand-reference-renderer-v3-embedded-layered",
        "zero_cost": True,
        "network_used": False,
        "image_generator_used": False,
        "external_source_board_required": False,
        "embedded_master_is_default": source_board is None,
        "source_board_audit_mode": source_board is not None,
        "reference_shape_is_source_of_truth": True,
        "metallic_wordmark_fixed": True,
        "seven_and_pulse_tintable": True,
        "football_fixed": True,
        "font_recreation_for_brand": False,
        "generic_ecg_recreation": False,
        "human_owner_approval_required": True,
        "publication_ready": False,
        "variants": entries,
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-board", default=None, help="Optional approved-board audit/re-derivation path")
    parser.add_argument("--output-dir", default="output/phase18_reference_brand_study")
    args = parser.parse_args()
    print(json.dumps(build(output_dir=args.output_dir, source_board=args.source_board), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
