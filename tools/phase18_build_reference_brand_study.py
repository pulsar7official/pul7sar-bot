#!/usr/bin/env python3
"""Build exact-shape PUL7SAR brand studies from the approved identity board.

This command is intentionally local and zero-cost. It requires the exact approved
identity-board file as input, verifies its SHA through BrandReferenceRenderer,
and renders club/story accent variants from the same separated raster geometry.
It performs no network access and invokes no image generator.
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


def build(*, source_board: str, output_dir: str) -> dict[str, object]:
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
            "source_sha256": receipt.source_sha256,
            "crop_pixel_sha256": receipt.crop_pixel_sha256,
            "metallic_pixel_sha256": receipt.metallic_pixel_sha256,
            "accent_pixel_sha256": receipt.accent_pixel_sha256,
            "football_pixel_sha256": receipt.football_pixel_sha256,
            "exact_reference_shape_used": receipt.exact_reference_shape_used,
            "transparent_reference_layers_used": receipt.transparent_reference_layers_used,
            "background_board_pixels_composited": receipt.background_board_pixels_composited,
            "font_recreation_used": receipt.font_recreation_used,
            "generic_ecg_recreation_used": receipt.generic_ecg_recreation_used,
            "publication_ready": receipt.publication_ready,
        })

    base.unlink(missing_ok=True)
    manifest = {
        "manifest_version": "pul7sar-reference-brand-study-v1",
        "renderer_contract": "pul7sar-brand-reference-renderer-v2-layered",
        "zero_cost": True,
        "network_used": False,
        "image_generator_used": False,
        "source_board_required": True,
        "reference_shape_is_source_of_truth": True,
        "metallic_wordmark_fixed": True,
        "seven_and_pulse_tintable": True,
        "football_fixed": True,
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
    parser.add_argument("--source-board", required=True)
    parser.add_argument("--output-dir", default="output/phase18_reference_brand_study")
    args = parser.parse_args()
    print(json.dumps(build(source_board=args.source_board, output_dir=args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
