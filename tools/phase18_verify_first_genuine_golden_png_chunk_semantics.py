#!/usr/bin/env python3
"""Fail-closed PNG chunk-semantics verifier for Phase 18 Candidate 1.

CPU-safe, stdlib-only, offline-only. This is preparatory and grants no authority.
It closes PNG semantic gaps not covered by byte framing alone: unknown critical
chunks, reserved-bit violations, non-consecutive IDAT, and PLTE ordering/duplication.
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

EXPECTED_SCHEMA = "pul7sar-phase18-first-genuine-golden-png-structure-v3"
OUTPUT_SCHEMA = "pul7sar-phase18-first-genuine-golden-png-chunk-semantics-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
KNOWN_CRITICAL = {"IHDR", "PLTE", "IDAT", "IEND"}


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_INVALID_EVIDENCE")
    return value


def _closed(payload: dict[str, Any]) -> None:
    for field in ("authoritative_gate", "network_download_authorized", "generation_authorized",
                  "human_visual_review_approved", "golden_quality_approved", "publication_ready",
                  "seeds_2_to_4_authorized"):
        if payload.get(field) is not False:
            raise RuntimeError(f"GOLDEN_PNG_CHUNK_SEMANTICS_AUTHORITY_DRIFT:{field}")


def verify(*, structure_path: Path, repo_root: Path) -> dict[str, Any]:
    evidence = _load(structure_path)
    if evidence.get("schema") != EXPECTED_SCHEMA:
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_SCHEMA_DRIFT")
    if evidence.get("branch") != "phase18/story-intelligence" or evidence.get("candidate") != 1:
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_IDENTITY_DRIFT")
    if evidence.get("cost_mode") != "$0-local" or evidence.get("offline_only") is not True:
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_POLICY_DRIFT")
    if evidence.get("png_structure_verified") is not True or evidence.get("canonical_encoding_verified") is not True:
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_UPSTREAM_NOT_VERIFIED")
    _closed(evidence)

    root = repo_root.resolve()
    raw_path = evidence.get("png_path")
    if not isinstance(raw_path, str) or not raw_path:
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_PATH_INVALID")
    candidate = Path(raw_path)
    png = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        png.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_PATH_OUTSIDE_REPO") from exc
    if not png.is_file() or png.is_symlink():
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_FILE_INVALID")
    data = png.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != evidence.get("png_sha256") or len(data) != evidence.get("png_bytes"):
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_PNG_IDENTITY_DRIFT")
    if not data.startswith(PNG_SIGNATURE):
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_SIGNATURE_INVALID")

    offset = len(PNG_SIGNATURE)
    names: list[str] = []
    seen_plte = False
    idat_started = False
    idat_ended = False
    while offset < len(data):
        if len(data) - offset < 12:
            raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_TRUNCATED")
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        ctype = data[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(data) or not re.fullmatch(rb"[A-Za-z]{4}", ctype):
            raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_CHUNK_INVALID")
        chunk = data[offset + 8:offset + 8 + length]
        expected_crc = struct.unpack(">I", data[offset + 8 + length:end])[0]
        actual_crc = zlib.crc32(chunk, zlib.crc32(ctype)) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_CRC_DRIFT")
        name = ctype.decode("ascii")
        names.append(name)
        if not name[2].isupper():
            raise RuntimeError(f"GOLDEN_PNG_CHUNK_SEMANTICS_RESERVED_BIT_INVALID:{name}")
        if name[0].isupper() and name not in KNOWN_CRITICAL:
            raise RuntimeError(f"GOLDEN_PNG_CHUNK_SEMANTICS_UNKNOWN_CRITICAL:{name}")
        if name == "PLTE":
            if seen_plte or idat_started:
                raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_PLTE_ORDER_INVALID")
            seen_plte = True
        elif name == "IDAT":
            if idat_ended:
                raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_IDAT_NOT_CONSECUTIVE")
            idat_started = True
        elif idat_started and name != "IEND":
            idat_ended = True
        if name == "IEND":
            if end != len(data):
                raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_IEND_NOT_TERMINAL")
            break
        offset = end

    if not names or names[0] != "IHDR" or names[-1] != "IEND" or not idat_started:
        raise RuntimeError("GOLDEN_PNG_CHUNK_SEMANTICS_REQUIRED_ORDER_INVALID")
    return {
        "schema": OUTPUT_SCHEMA,
        "status": "FIRST_GENUINE_GOLDEN_PNG_CHUNK_SEMANTICS_VERIFIED",
        "branch": "phase18/story-intelligence", "candidate": 1,
        "cost_mode": "$0-local", "offline_only": True,
        "source_commit_sha": evidence.get("source_commit_sha"),
        "png_sha256": sha, "png_bytes": len(data), "chunk_sequence": names,
        "known_critical_chunks_only": True, "reserved_bit_valid_for_all_chunks": True,
        "idat_consecutive": True, "plte_order_valid": True,
        "eligible_for_human_visual_review": True,
        "authoritative_gate": False, "network_download_authorized": False,
        "generation_authorized": False, "human_visual_review_approved": False,
        "golden_quality_approved": False, "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--structure", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(structure_path=args.structure, repo_root=args.repo_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
