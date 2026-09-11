#!/usr/bin/env python3
"""Fail-closed verifier for a First Genuine Golden v6 artifact bundle.

This verifier is intentionally CPU-safe. It does not generate pixels, load models,
perform network access, or grant Human Review / Golden Quality / publication
authority. It independently replays the final resource-lock receipt, every bound
evidence file, and the PNG bytes present in an extracted workflow artifact.
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
EXPECTED_EVIDENCE = frozenset(
    {
        "gpu_host_qualification",
        "host_memory_preflight",
        "cache_budget",
        "semantic_preflight",
        "qwen_model_cache",
        "flux_model_cache",
        "runtime_fingerprint_pre",
        "runtime_fingerprint_post",
        "strict_golden_staging",
    }
)
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
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PATH_ESCAPES_ARTIFACT_ROOT")
    candidate = root.joinpath(*relative.parts).resolve()
    if candidate != root and root not in candidate.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PATH_ESCAPES_ARTIFACT_ROOT")
    return candidate


def _artifact_output_file(root: Path, recorded: str, *, kind: str) -> Path:
    """Resolve one producer-recorded ``output/...`` path inside an artifact.

    The producer records repository/runner paths, often absolute. upload-artifact
    receives several ``output/...`` paths and may strip that least-common-ancestor
    directory. Only the suffix rooted at the literal ``output`` segment may be
    rebased into the extracted artifact; arbitrary runner paths are never trusted.
    """
    normalized = recorded.replace("\\", "/")
    parts = PurePosixPath(normalized).parts
    try:
        output_index = parts.index("output")
    except ValueError as exc:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_{kind}_PATH_NOT_OUTPUT_ROOTED") from exc

    suffix = PurePosixPath(*parts[output_index + 1 :])
    if not suffix.parts or ".." in suffix.parts:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_PATH_ESCAPES_ARTIFACT_ROOT")

    candidates = (
        _safe_candidate(root, suffix),
        _safe_candidate(root, PurePosixPath("output") / suffix),
    )
    existing = [candidate for candidate in candidates if candidate.is_file()]
    if not existing:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_{kind}_MISSING")
    if len(existing) > 1 and existing[0] != existing[1]:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_{kind}_PATH_AMBIGUOUS")
    return existing[0]


def _artifact_png(root: Path, recorded: str) -> Path:
    return _artifact_output_file(root, recorded, kind="PNG")


def _verify_evidence(root: Path, payload: dict[str, object]) -> dict[str, Path]:
    evidence = payload.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != EXPECTED_EVIDENCE:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_EVIDENCE_SET_INCOMPLETE")

    resolved: dict[str, Path] = {}
    for label in sorted(EXPECTED_EVIDENCE):
        record = evidence.get(label)
        if not isinstance(record, dict):
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_EVIDENCE_RECORD_INVALID:{label}")
        recorded_path = record.get("path")
        expected_sha = record.get("sha256")
        expected_bytes = record.get("bytes")
        if not isinstance(recorded_path, str) or not recorded_path.strip():
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_EVIDENCE_PATH_INVALID:{label}")
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_EVIDENCE_SHA_INVALID:{label}")
        if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_EVIDENCE_BYTE_COUNT_INVALID:{label}")

        evidence_path = _artifact_output_file(root, recorded_path, kind="EVIDENCE")
        if evidence_path.stat().st_size != expected_bytes:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_EVIDENCE_BYTE_COUNT_DRIFT:{label}")
        if _sha256(evidence_path) != expected_sha:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_EVIDENCE_SHA_DRIFT:{label}")
        resolved[label] = evidence_path
    return resolved


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

    resolved_evidence = _verify_evidence(root, payload)

    staging_receipt = payload.get("staging_receipt")
    if not isinstance(staging_receipt, str) or not staging_receipt.strip():
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_STAGING_RECEIPT_PATH_MISSING")
    resolved_staging = _artifact_output_file(root, staging_receipt, kind="STAGING_RECEIPT")
    if resolved_staging != resolved_evidence["strict_golden_staging"]:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_STAGING_RECEIPT_BINDING_DRIFT")

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
        "evidence_files_verified": len(resolved_evidence),
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
