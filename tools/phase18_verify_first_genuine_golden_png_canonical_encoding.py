#!/usr/bin/env python3
"""Verify that Candidate 1 uses PUL7SAR's canonical normalized PNG encoding.

CPU-safe, stdlib-only and fail-closed. The platform canvas normalizer converts
its final image to Pillow ``RGB`` and saves it as PNG. The upstream structural
verifier already parses and SHA-binds the exact Candidate 1 PNG; this verifier
narrows that accepted structure to the canonical normalized representation:
8-bit truecolour RGB, non-interlaced, three channels / 24 bits per pixel.

This tool performs no generation, network access, Human Review, Golden approval,
publication, or queue mutation. Passing it only proves encoding conformance for
an already structurally verified Candidate 1.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
# CS481 promoted the structural evidence contract to v3 when canonical RGB8
# enforcement moved into the critical structural gate. Keep this verifier
# pinned to that exact schema so stale v2 evidence fails closed.
STRUCTURE_SCHEMA = "pul7sar-phase18-first-genuine-golden-png-structure-v3"
OUTPUT_SCHEMA = "pul7sar-phase18-first-genuine-golden-png-canonical-encoding-v1"
EXPECTED_BIT_DEPTH = 8
EXPECTED_COLOR_TYPE = 2
EXPECTED_CHANNELS = 3
EXPECTED_BITS_PER_PIXEL = 24
EXPECTED_INTERLACE = 0

AUTHORITY_FIELDS = (
    "authoritative_gate",
    "network_download_authorized",
    "generation_authorized",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
    "seeds_2_to_4_authorized",
)

STRUCTURE_FLAGS = (
    "png_structure_verified",
    "crc_verified_for_all_chunks",
    "idat_zlib_stream_verified",
    "zlib_stream_terminated_exactly",
    "decoded_scanline_layout_verified",
    "scanline_filter_bytes_verified",
    "iend_terminal",
    "no_trailing_bytes",
    "canonical_encoding_verified",
)


def _load(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GOLDEN_PNG_CANONICAL_ENCODING_INVALID_JSON:{path}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_INVALID_OBJECT")
    return payload


def _require_closed_authority(payload: dict[str, Any]) -> None:
    for field in AUTHORITY_FIELDS:
        if payload.get(field) is not False:
            raise RuntimeError(f"GOLDEN_PNG_CANONICAL_ENCODING_AUTHORITY_DRIFT:{field}")


def verify(*, structure_path: Path) -> dict[str, Any]:
    structure = _load(structure_path)
    if structure.get("schema") != STRUCTURE_SCHEMA:
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_STRUCTURE_SCHEMA_DRIFT")
    if structure.get("status") != "FIRST_GENUINE_GOLDEN_PNG_STRUCTURE_VERIFIED":
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_STRUCTURE_STATUS_DRIFT")
    if structure.get("branch") != EXPECTED_BRANCH or structure.get("candidate") != 1:
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_IDENTITY_DRIFT")
    if structure.get("cost_mode") != EXPECTED_COST_MODE or structure.get("offline_only") is not True:
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_POLICY_DRIFT")
    if structure.get("eligible_for_human_visual_review") is not True:
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_NOT_REVIEW_ELIGIBLE")

    source_sha = structure.get("source_commit_sha")
    png_sha = structure.get("png_sha256")
    if not re.fullmatch(r"[0-9a-f]{40}", str(source_sha or "")):
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_SOURCE_SHA_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", str(png_sha or "")):
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_PNG_SHA_INVALID")
    if not isinstance(structure.get("png_bytes"), int) or structure["png_bytes"] <= 0:
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_PNG_BYTES_INVALID")

    for field in STRUCTURE_FLAGS:
        if structure.get(field) is not True:
            raise RuntimeError(f"GOLDEN_PNG_CANONICAL_ENCODING_STRUCTURE_FLAG_DRIFT:{field}")
    if structure.get("canonical_encoding") != "RGB8_TRUECOLOUR_NON_INTERLACED":
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_CONTRACT_DRIFT")

    expected = {
        "bit_depth": EXPECTED_BIT_DEPTH,
        "color_type": EXPECTED_COLOR_TYPE,
        "channels": EXPECTED_CHANNELS,
        "bits_per_pixel": EXPECTED_BITS_PER_PIXEL,
        "interlace_method": EXPECTED_INTERLACE,
    }
    for field, value in expected.items():
        if structure.get(field) != value:
            raise RuntimeError(
                f"GOLDEN_PNG_CANONICAL_ENCODING_PIXEL_FORMAT_DRIFT:{field}:"
                f"expected={value}:actual={structure.get(field)!r}"
            )

    width = structure.get("width")
    height = structure.get("height")
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_WIDTH_INVALID")
    if not isinstance(height, int) or isinstance(height, bool) or height <= 0:
        raise RuntimeError("GOLDEN_PNG_CANONICAL_ENCODING_HEIGHT_INVALID")

    _require_closed_authority(structure)

    return {
        "schema": OUTPUT_SCHEMA,
        "status": "FIRST_GENUINE_GOLDEN_PNG_CANONICAL_ENCODING_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "source_commit_sha": source_sha,
        "png_path": structure.get("png_path"),
        "png_sha256": png_sha,
        "png_bytes": structure["png_bytes"],
        "width": width,
        "height": height,
        "canonical_color_mode": "RGB8",
        "bit_depth": EXPECTED_BIT_DEPTH,
        "color_type": EXPECTED_COLOR_TYPE,
        "channels": EXPECTED_CHANNELS,
        "bits_per_pixel": EXPECTED_BITS_PER_PIXEL,
        "interlace_method": EXPECTED_INTERLACE,
        "canonical_platform_encoding_verified": True,
        "eligible_for_human_visual_review": True,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(structure_path=args.structure)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
