#!/usr/bin/env python3
"""Fail-closed verifier for a First Genuine Golden v6 artifact bundle.

This verifier is intentionally CPU-safe. It does not generate pixels, load models,
perform network access, or grant Human Review / Golden Quality / publication
authority. It only replays the final resource-lock receipt against the PNG bytes
present in an extracted workflow artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

EXPECTED_SCHEMA = "pul7sar-first-genuine-golden-v6-resource-lock-v4"
EXPECTED_STATUS = "FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED"
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_COST_MODE = "$0-local"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FAIL_CLOSED_FIELDS = (
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
    "seeds_2_to_4_authorized",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_candidate(root: Path, relative: PurePosixPath) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_ESCAPES_ARTIFACT_ROOT")
    candidate = root.joinpath(*relative.parts).resolve()
    if candidate != root and root not in candidate.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_ESCAPES_ARTIFACT_ROOT")
    return candidate


def _artifact_png(root: Path, recorded: str) -> Path:
    """Resolve a runner-recorded output path inside an extracted upload-artifact.

    The producer records repository/runner paths (often absolute). The workflow
    uploads multiple ``output/...`` paths, so upload-artifact uses their least
    common ancestor as the archive root. A downloaded artifact can therefore
    contain ``phase18_generated/...`` rather than ``output/phase18_generated/...``.
    Only the suffix rooted at the literal ``output`` segment is eligible for
    rebasing; arbitrary absolute paths are never trusted.
    """
    normalized = recorded.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    try:
        output_index = parts.index("output")
    except ValueError as exc:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_PATH_NOT_OUTPUT_ROOTED") from exc

    suffix = PurePosixPath(*parts[output_index + 1 :])
    if not suffix.parts or ".." in suffix.parts:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_ESCAPES_ARTIFACT_ROOT")

    # Support both the native upload-artifact layout (LCA ``output`` stripped)
    # and an explicitly rewrapped extraction that retains the ``output`` folder.
    candidates = (
        _safe_candidate(root, suffix),
        _safe_candidate(root, PurePosixPath("output") / suffix),
    )
    existing = [candidate for candidate in candidates if candidate.is_file()]
    if not existing:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_MISSING")
    if len(existing) > 1 and existing[0] != existing[1]:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_PATH_AMBIGUOUS")
    return existing[0]


def verify(receipt_path: Path, *, artifact_root: Path | None = None) -> dict[str, object]:
    receipt_path = receipt_path.resolve()
    if not receipt_path.is_file():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_RECEIPT_MISSING")
    root = (artifact_root or receipt_path.parent).resolve()
    if not root.is_dir():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ARTIFACT_ROOT_MISSING")

    payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_RECEIPT_INVALID")
    if payload.get("schema") != EXPECTED_SCHEMA:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SCHEMA_DRIFT")
    if payload.get("status") != EXPECTED_STATUS:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_STATUS_NOT_VERIFIED")
    if payload.get("branch") != EXPECTED_BRANCH or payload.get("candidate") != 1:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_IDENTITY_DRIFT")
    if payload.get("cost_mode") != EXPECTED_COST_MODE:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_COST_MODE_DRIFT")
    if payload.get("native_bf16_proven") is not True or payload.get("gpu_eligible") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_GPU_BF16_UNPROVEN")
    if payload.get("semantic_preflight_bound") is not True or payload.get("runtime_stable_across_generation") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SEMANTIC_RUNTIME_UNPROVEN")
    for field in FAIL_CLOSED_FIELDS:
        if payload.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ILLEGAL_AUTHORITY:{field}")

    png_value = payload.get("png")
    if not isinstance(png_value, str) or not png_value.strip():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_PATH_MISSING")
    png = _artifact_png(root, png_value)
    with png.open("rb") as handle:
        if handle.read(8) != PNG_SIGNATURE:
            raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_SIGNATURE_INVALID")

    actual_sha = _sha256(png)
    expected_sha = payload.get("png_sha256")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64 or actual_sha != expected_sha:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_SHA_DRIFT")

    expected_bytes = payload.get("png_bytes")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 8:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_BYTE_COUNT_INVALID")
    if png.stat().st_size != expected_bytes:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_BYTE_COUNT_DRIFT")

    return {
        "status": "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_REPLAY_VERIFIED",
        "candidate": 1,
        "branch": EXPECTED_BRANCH,
        "cost_mode": EXPECTED_COST_MODE,
        "png": str(png),
        "png_sha256": actual_sha,
        "png_bytes": expected_bytes,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--artifact-root", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(verify(args.receipt, artifact_root=args.artifact_root), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
