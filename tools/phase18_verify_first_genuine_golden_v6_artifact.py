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
from pathlib import Path

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
    png = Path(png_value)
    if not png.is_absolute():
        # Workflow receipts may store repository-relative output paths. When an
        # artifact has been extracted elsewhere, bind those paths to artifact_root.
        png = root / png
    png = png.resolve()
    if png != root and root not in png.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_ESCAPES_ARTIFACT_ROOT")
    if not png.is_file():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_MISSING")
    with png.open("rb") as handle:
        if handle.read(8) != PNG_SIGNATURE:
            raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_SIGNATURE_INVALID")

    actual_sha = _sha256(png)
    expected_sha = payload.get("png_sha256")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64 or actual_sha != expected_sha:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PNG_SHA_DRIFT")

    return {
        "status": "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_REPLAY_VERIFIED",
        "candidate": 1,
        "branch": EXPECTED_BRANCH,
        "cost_mode": EXPECTED_COST_MODE,
        "png": str(png),
        "png_sha256": actual_sha,
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
