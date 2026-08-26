#!/usr/bin/env python3
"""Continue a provenance-locked first Golden PNG through editorial v6 semantic QA.

The filename is retained for compatibility with earlier Phase 18 notebooks and
workflow references. Its behavior is intentionally no longer "Hybrid v5": a
generic football PREVIEW must preserve the generated editorial base unchanged.
No deterministic pitch is composited, no pitch-replacement stage is required,
and semantic QA evaluates the base scene only.

Even on success this stage cannot authorize Golden visual quality or publication.
Exact PUL7SAR branding and typography remain later deterministic layers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from tools.phase18_colab_one_command import _review_editorial_base

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_HANDOFF_STATUS = "COLAB_REAL_GOLDEN_EDITORIAL_GENERATED"
ACCEPTED_HANDOFF_STATUSES = {
    EXPECTED_HANDOFF_STATUS,
    "COLAB_GOLDEN_EDITORIAL_ALREADY_EXISTS",
}
EXPECTED_MANIFEST = "pul7sar-golden-batch-v6"
LATEST = ROOT / "output" / "phase18_colab" / "latest.json"
DEFAULT_RECEIPT = ROOT / "output" / "phase18_gpu_smoke" / "editorial-semantic-continuation.json"


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("EDITORIAL_CONTINUATION_BRANCH_RESOLUTION_FAILED")
    return completed.stdout.strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside_root(value: str | Path, *, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    path = path.resolve()
    root = ROOT.resolve()
    if path != root and root not in path.parents:
        raise RuntimeError(f"EDITORIAL_CONTINUATION_{label}_ESCAPES_REPOSITORY")
    return path


def _load_handoff(path: Path, *, candidate: int) -> tuple[dict[str, object], Path]:
    if not path.is_file():
        raise RuntimeError("EDITORIAL_CONTINUATION_HANDOFF_MISSING")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") not in ACCEPTED_HANDOFF_STATUSES:
        raise RuntimeError(f"EDITORIAL_CONTINUATION_HANDOFF_STATUS_DRIFT: status={payload.get('status')!r}")
    expected = {
        "branch": EXPECTED_BRANCH,
        "manifest_version": EXPECTED_MANIFEST,
        "candidate": candidate,
        "cost_mode": "$0-local",
        "resolved_dtype": "bfloat16",
        "hybrid_surface_replacement_required": False,
        "generated_sport_geometry_allowed": False,
        "generated_branding_allowed": False,
        "visual_grammar_surface_visibility": "context_only",
        "football_camera_preset": "editorial_environmental_oblique",
        "publication_ready": False,
    }
    failures = [
        f"{key}={payload.get(key)!r}" for key, value in expected.items()
        if payload.get(key) != value
    ]
    if failures:
        raise RuntimeError("EDITORIAL_CONTINUATION_HANDOFF_DRIFT: " + "; ".join(failures))

    png_value = payload.get("png")
    if not isinstance(png_value, str) or not png_value.strip():
        raise RuntimeError("EDITORIAL_CONTINUATION_BASE_PNG_MISSING")
    png = _inside_root(png_value, label="BASE_PNG")
    if not png.is_file() or png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("EDITORIAL_CONTINUATION_BASE_PNG_INVALID")
    actual_sha = _sha256(png)
    declared_sha = payload.get("base_png_sha256")
    if not isinstance(declared_sha, str) or declared_sha != actual_sha:
        raise RuntimeError("EDITORIAL_CONTINUATION_BASE_PNG_SHA256_MISMATCH")
    return payload, png


def _require_semantic_success(
    result: dict[str, object],
    *,
    candidate: int,
    expected_png: Path,
) -> dict[str, object]:
    if result.get("status") != "GOLDEN_EDITORIAL_BASE_SEMANTICALLY_CLEAN":
        raise RuntimeError("EDITORIAL_CONTINUATION_UNEXPECTED_RESULT_STATUS")
    if result.get("candidate") != candidate:
        raise RuntimeError("EDITORIAL_CONTINUATION_CANDIDATE_DRIFT")
    if result.get("publication_ready") is not False:
        raise RuntimeError("EDITORIAL_CONTINUATION_PUBLICATION_AUTHORITY_DRIFT")
    if result.get("deterministic_pitch_applied") is not False:
        raise RuntimeError("EDITORIAL_CONTINUATION_PITCH_MUST_NOT_BE_APPLIED")
    if result.get("pitch_replacement_required") is not False:
        raise RuntimeError("EDITORIAL_CONTINUATION_PITCH_REPLACEMENT_MUST_REMAIN_FALSE")

    layer_gate = result.get("base_scene_layer_gate")
    if not isinstance(layer_gate, dict) or layer_gate.get("allowed") is not True or layer_gate.get("inspection_complete") is not True:
        raise RuntimeError("EDITORIAL_CONTINUATION_BASE_LAYER_GATE_FAILED")

    semantic = result.get("semantic_visual_inspection")
    if not isinstance(semantic, dict) or semantic.get("approved") is not True:
        raise RuntimeError("EDITORIAL_CONTINUATION_BASE_SEMANTIC_FAILED")

    editorial_value = result.get("editorial_png")
    if not isinstance(editorial_value, str) or not editorial_value.strip():
        raise RuntimeError("EDITORIAL_CONTINUATION_EDITORIAL_PNG_MISSING")
    editorial_png = _inside_root(editorial_value, label="EDITORIAL_PNG")
    if editorial_png != expected_png.resolve():
        raise RuntimeError("EDITORIAL_CONTINUATION_PIXEL_IDENTITY_DRIFT")
    if not editorial_png.is_file() or editorial_png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("EDITORIAL_CONTINUATION_EDITORIAL_PNG_INVALID")

    return {
        "schema": "pul7sar-first-png-editorial-semantic-continuation-v2",
        "status": "FIRST_GOLDEN_EDITORIAL_SEMANTIC_PROOF_READY",
        "branch": EXPECTED_BRANCH,
        "manifest_version": EXPECTED_MANIFEST,
        "candidate": candidate,
        "editorial_png": str(editorial_png),
        "editorial_png_sha256": _sha256(editorial_png),
        "pixel_identity_preserved": True,
        "visual_grammar_surface_visibility": "context_only",
        "deterministic_pitch_applied": False,
        "pitch_replacement_required": False,
        "base_scene_layer_gate": layer_gate,
        "semantic_visual_inspection": semantic,
        "semantic_layer_gate_approved": True,
        "golden_quality_approved": False,
        "dynamic_brand_applied": result.get("dynamic_brand_applied", False),
        "typography_applied": result.get("typography_applied", False),
        "publication_ready": False,
        "next_gate": "human Golden visual review of focal hierarchy, depth, atmosphere and negative space",
    }


def run(*, candidate: int = 1, handoff_path: Path = LATEST, output_path: Path = DEFAULT_RECEIPT) -> dict[str, object]:
    branch = _branch()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"EDITORIAL_CONTINUATION_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")
    if candidate != 1:
        raise RuntimeError("EDITORIAL_CONTINUATION_REQUIRES_CANDIDATE_1")
    if handoff_path.resolve() != LATEST.resolve():
        raise RuntimeError("EDITORIAL_CONTINUATION_CANONICAL_HANDOFF_REQUIRED")

    _, base_png = _load_handoff(handoff_path, candidate=candidate)
    result = _review_editorial_base(candidate)
    receipt = _require_semantic_success(result, candidate=candidate, expected_png=base_png)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Continue proven Candidate 1 through strict Golden editorial v6 semantic QA")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--handoff", type=Path, default=LATEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    receipt = run(candidate=args.candidate, handoff_path=args.handoff, output_path=args.output)
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
