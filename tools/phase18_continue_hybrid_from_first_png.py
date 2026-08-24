#!/usr/bin/env python3
"""Continue a provenance-locked first Golden PNG through Hybrid v5 semantic QA.

This command consumes the canonical ``output/phase18_colab/latest.json`` emitted
by the first-PNG Hybrid handoff. It does not run FLUX or mutate the durable
queue. It reuses the exact proven Candidate 1 bytes, requires Qwen semantic
inspection, applies deterministic football geometry, and fails closed unless
both BASE_SCENE and HYBRID_SURFACE semantic checks approve.

Even on success this stage cannot authorize Golden quality or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from tools.phase18_colab_one_command import _compose_hybrid

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "phase18/story-intelligence"
EXPECTED_HANDOFF_STATUS = "FIRST_GOLDEN_PNG_HYBRID_HANDOFF_READY"
EXPECTED_MANIFEST = "pul7sar-golden-batch-v5"
LATEST = ROOT / "output" / "phase18_colab" / "latest.json"
DEFAULT_RECEIPT = ROOT / "output" / "phase18_gpu_smoke" / "hybrid-semantic-continuation.json"


def _branch() -> str:
    completed = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError("HYBRID_CONTINUATION_BRANCH_RESOLUTION_FAILED")
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
        raise RuntimeError(f"HYBRID_CONTINUATION_{label}_ESCAPES_REPOSITORY")
    return path


def _load_handoff(path: Path, *, candidate: int) -> dict[str, object]:
    if not path.is_file():
        raise RuntimeError("HYBRID_CONTINUATION_HANDOFF_MISSING")
    payload = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "status": EXPECTED_HANDOFF_STATUS,
        "branch": EXPECTED_BRANCH,
        "manifest_version": EXPECTED_MANIFEST,
        "candidate": candidate,
        "cost_mode": "$0-local",
        "resolved_dtype": "bfloat16",
        "hybrid_surface_replacement_required": True,
        "generated_sport_geometry_allowed": False,
        "generated_branding_allowed": False,
        "semantic_layer_gate_approved": False,
        "hybrid_semantic_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    failures = [
        f"{key}={payload.get(key)!r}" for key, value in expected.items()
        if payload.get(key) != value
    ]
    if failures:
        raise RuntimeError("HYBRID_CONTINUATION_HANDOFF_DRIFT: " + "; ".join(failures))

    png_value = payload.get("png")
    if not isinstance(png_value, str) or not png_value.strip():
        raise RuntimeError("HYBRID_CONTINUATION_BASE_PNG_MISSING")
    png = _inside_root(png_value, label="BASE_PNG")
    if not png.is_file() or png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("HYBRID_CONTINUATION_BASE_PNG_INVALID")
    actual_sha = _sha256(png)
    if payload.get("base_png_sha256") != actual_sha:
        raise RuntimeError("HYBRID_CONTINUATION_BASE_PNG_SHA256_MISMATCH")
    return payload


def _require_semantic_success(result: dict[str, object], *, candidate: int) -> dict[str, object]:
    if result.get("status") != "GOLDEN_HYBRID_SURFACE_READY":
        raise RuntimeError("HYBRID_CONTINUATION_UNEXPECTED_RESULT_STATUS")
    if result.get("candidate") != candidate:
        raise RuntimeError("HYBRID_CONTINUATION_CANDIDATE_DRIFT")
    if result.get("publication_ready") is not False:
        raise RuntimeError("HYBRID_CONTINUATION_PUBLICATION_AUTHORITY_DRIFT")

    artifact = result.get("artifact_integrity")
    if not isinstance(artifact, dict) or artifact.get("valid") is not True:
        raise RuntimeError("HYBRID_CONTINUATION_ARTIFACT_INTEGRITY_FAILED")
    base_gate = result.get("base_scene_layer_gate")
    if not isinstance(base_gate, dict) or base_gate.get("allowed") is not True or base_gate.get("inspection_complete") is not True:
        raise RuntimeError("HYBRID_CONTINUATION_BASE_LAYER_GATE_FAILED")

    semantic = result.get("semantic_visual_inspection")
    if not isinstance(semantic, dict):
        raise RuntimeError("HYBRID_CONTINUATION_SEMANTIC_REPORT_MISSING")
    for stage in ("base_scene", "hybrid_surface"):
        stage_payload = semantic.get(stage)
        if not isinstance(stage_payload, dict) or stage_payload.get("approved") is not True:
            raise RuntimeError(f"HYBRID_CONTINUATION_{stage.upper()}_SEMANTIC_FAILED")

    hybrid_value = result.get("hybrid_png")
    if not isinstance(hybrid_value, str) or not hybrid_value.strip():
        raise RuntimeError("HYBRID_CONTINUATION_HYBRID_PNG_MISSING")
    hybrid_png = _inside_root(hybrid_value, label="HYBRID_PNG")
    if not hybrid_png.is_file() or hybrid_png.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("HYBRID_CONTINUATION_HYBRID_PNG_INVALID")

    return {
        "schema": "pul7sar-first-png-hybrid-semantic-continuation-v1",
        "status": "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY",
        "branch": EXPECTED_BRANCH,
        "manifest_version": EXPECTED_MANIFEST,
        "candidate": candidate,
        "base_png": result.get("base_png"),
        "hybrid_png": str(hybrid_png),
        "hybrid_png_sha256": _sha256(hybrid_png),
        "artifact_integrity": artifact,
        "base_scene_layer_gate": base_gate,
        "semantic_visual_inspection": semantic,
        "deterministic_geometry_applied": result.get("deterministic_geometry_applied"),
        "generated_pitch_markings_replaced": result.get("generated_pitch_markings_replaced"),
        "semantic_layer_gate_approved": True,
        "hybrid_semantic_review_approved": True,
        "golden_quality_approved": False,
        "dynamic_brand_applied": result.get("dynamic_brand_applied"),
        "typography_applied": result.get("typography_applied"),
        "publication_ready": False,
        "next_gate": "human pitch integration review and SHA-bound Golden 8.5/9.0 quality review",
    }


def run(*, candidate: int = 1, handoff_path: Path = LATEST, output_path: Path = DEFAULT_RECEIPT) -> dict[str, object]:
    branch = _branch()
    if branch != EXPECTED_BRANCH:
        raise RuntimeError(f"HYBRID_CONTINUATION_BRANCH_BLOCKED: expected {EXPECTED_BRANCH}, found {branch}")
    if candidate != 1:
        raise RuntimeError("HYBRID_CONTINUATION_REQUIRES_CANDIDATE_1")

    _load_handoff(handoff_path, candidate=candidate)
    result = _compose_hybrid(candidate, "qwen")
    receipt = _require_semantic_success(result, candidate=candidate)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Continue proven Candidate 1 through strict Hybrid v5 semantic QA")
    parser.add_argument("--candidate", type=int, default=1)
    parser.add_argument("--handoff", type=Path, default=LATEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()
    receipt = run(candidate=args.candidate, handoff_path=args.handoff, output_path=args.output)
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
