#!/usr/bin/env python3
"""Structurally validate the exact first-Golden Candidate 1 PNG.

CPU-safe, stdlib-only and fail-closed. This verifier performs no generation,
network access, Human Review, Golden approval, publication, or queue mutation.
It proves that the already-bound PNG is a complete PNG byte stream with valid
chunk framing/CRC, a valid IHDR, at least one IDAT whose zlib stream decodes,
exactly one terminal IEND, and no trailing bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path
from typing import Any

EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
MANIFEST_SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v3"
OUTPUT_SCHEMA = "pul7sar-phase18-first-genuine-golden-png-structure-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"GOLDEN_PNG_STRUCTURE_INVALID_JSON:{path}") from exc
    if not isinstance(value, dict):
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_INVALID_MANIFEST_OBJECT")
    return value


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _inside_repo(root: Path, value: str) -> Path:
    path = Path(value)
    target = path.resolve() if path.is_absolute() else (root / path).resolve()
    root = root.resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_PATH_OUTSIDE_REPO") from exc
    return target


def _require_closed_authority(payload: dict[str, Any]) -> None:
    for field in (
        "authoritative_gate", "network_download_authorized", "generation_authorized",
        "human_visual_review_approved", "golden_quality_approved", "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if payload.get(field) is not False:
            raise RuntimeError(f"GOLDEN_PNG_STRUCTURE_AUTHORITY_DRIFT:{field}")


def _validate_png(data: bytes) -> dict[str, Any]:
    if not data.startswith(PNG_SIGNATURE):
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_SIGNATURE_INVALID")
    offset = len(PNG_SIGNATURE)
    chunks: list[str] = []
    idat = bytearray()
    ihdr: tuple[int, int, int, int, int, int, int] | None = None
    seen_iend = False

    while offset < len(data):
        if len(data) - offset < 12:
            raise RuntimeError("GOLDEN_PNG_STRUCTURE_TRUNCATED_CHUNK_HEADER")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(data):
            raise RuntimeError("GOLDEN_PNG_STRUCTURE_TRUNCATED_CHUNK_DATA")
        if not re.fullmatch(rb"[A-Za-z]{4}", chunk_type):
            raise RuntimeError("GOLDEN_PNG_STRUCTURE_CHUNK_TYPE_INVALID")
        chunk_data = data[offset + 8:offset + 8 + length]
        expected_crc = struct.unpack(">I", data[offset + 8 + length:end])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(chunk_data, actual_crc) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise RuntimeError(f"GOLDEN_PNG_STRUCTURE_CRC_INVALID:{chunk_type.decode('ascii')}")
        name = chunk_type.decode("ascii")
        chunks.append(name)

        if not chunks[:-1] and name != "IHDR":
            raise RuntimeError("GOLDEN_PNG_STRUCTURE_IHDR_NOT_FIRST")
        if name == "IHDR":
            if ihdr is not None or length != 13:
                raise RuntimeError("GOLDEN_PNG_STRUCTURE_IHDR_INVALID")
            ihdr = struct.unpack(">IIBBBBB", chunk_data)
        elif name == "IDAT":
            if ihdr is None or seen_iend:
                raise RuntimeError("GOLDEN_PNG_STRUCTURE_IDAT_ORDER_INVALID")
            idat.extend(chunk_data)
        elif name == "IEND":
            if length != 0 or seen_iend:
                raise RuntimeError("GOLDEN_PNG_STRUCTURE_IEND_INVALID")
            seen_iend = True
            offset = end
            if offset != len(data):
                raise RuntimeError("GOLDEN_PNG_STRUCTURE_TRAILING_BYTES")
            break
        offset = end

    if ihdr is None:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_IHDR_MISSING")
    if not seen_iend:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_IEND_MISSING")
    if not idat:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_IDAT_MISSING")

    width, height, bit_depth, color_type, compression, filter_method, interlace = ihdr
    if width <= 0 or height <= 0:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_DIMENSIONS_INVALID")
    valid_depths = {
        0: {1, 2, 4, 8, 16}, 2: {8, 16}, 3: {1, 2, 4, 8},
        4: {8, 16}, 6: {8, 16},
    }
    if color_type not in valid_depths or bit_depth not in valid_depths[color_type]:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_PIXEL_FORMAT_INVALID")
    if compression != 0 or filter_method != 0 or interlace not in (0, 1):
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_IHDR_METHOD_INVALID")
    try:
        decoded = zlib.decompress(bytes(idat))
    except zlib.error as exc:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_IDAT_ZLIB_INVALID") from exc
    if not decoded:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_IDAT_DECODE_EMPTY")

    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "interlace_method": interlace,
        "chunk_count": len(chunks),
        "idat_bytes": len(idat),
        "decoded_scanline_bytes": len(decoded),
        "iend_terminal": True,
        "crc_verified_for_all_chunks": True,
        "idat_zlib_stream_verified": True,
        "no_trailing_bytes": True,
    }


def verify(*, manifest_path: Path, repo_root: Path) -> dict[str, Any]:
    manifest = _load(manifest_path)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_MANIFEST_SCHEMA_DRIFT")
    if manifest.get("branch") != EXPECTED_BRANCH or manifest.get("candidate") != 1:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_IDENTITY_DRIFT")
    if manifest.get("cost_mode") != EXPECTED_COST_MODE or manifest.get("offline_only") is not True:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_POLICY_DRIFT")
    if manifest.get("eligible_for_human_visual_review") is not True:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_NOT_REVIEW_ELIGIBLE")
    _require_closed_authority(manifest)

    evidence = manifest.get("evidence")
    if not isinstance(evidence, dict) or not isinstance(evidence.get("png"), dict):
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_PNG_EVIDENCE_MISSING")
    record = evidence["png"]
    path_value = record.get("path")
    expected_sha = manifest.get("png_sha256")
    if not isinstance(path_value, str) or not path_value:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_PATH_INVALID")
    if not re.fullmatch(r"[0-9a-f]{64}", str(expected_sha or "")):
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_SHA_INVALID")
    if record.get("sha256") != expected_sha:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_EVIDENCE_SHA_DRIFT")

    png = _inside_repo(repo_root, path_value)
    if not png.is_file() or png.is_symlink():
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_FILE_INVALID")
    data = png.read_bytes()
    if _sha256_bytes(data) != expected_sha:
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_FILE_SHA_DRIFT")
    if record.get("bytes") != len(data):
        raise RuntimeError("GOLDEN_PNG_STRUCTURE_FILE_SIZE_DRIFT")
    structure = _validate_png(data)

    return {
        "schema": OUTPUT_SCHEMA,
        "status": "FIRST_GENUINE_GOLDEN_PNG_STRUCTURE_VERIFIED",
        "branch": EXPECTED_BRANCH,
        "candidate": 1,
        "cost_mode": EXPECTED_COST_MODE,
        "offline_only": True,
        "source_commit_sha": manifest.get("source_commit_sha"),
        "png_path": str(png),
        "png_sha256": expected_sha,
        "png_bytes": len(data),
        "png_structure_verified": True,
        **structure,
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
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(manifest_path=args.manifest, repo_root=args.repo_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
