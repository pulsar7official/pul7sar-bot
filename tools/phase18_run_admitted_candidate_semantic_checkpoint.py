#!/usr/bin/env python3
"""Advance one CS303-admitted Qwen candidate through CS304 and CS305 only.

The checkpoint is deliberately fail-closed. It runs the pinned local Qwen2.5-VL
BASE_SCENE semantic inspection against the exact CS303-admitted PNG. Only when
CS304 passes does it derive the lineage-bound CS305 pixel-identity-review
requirement. It never approves identity, Human Review, Golden quality, final
semantics, materialization, or publication.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    run_identity_requirement,
    verify_identity_requirement,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    run_canonical_candidate_semantic_base_qa,
    verify_canonical_candidate_semantic_base_qa,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-admitted-candidate-semantic-checkpoint-v1"
_FORBIDDEN_TRUE = (
    "identity_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _inside_repo_dir(repo_root: Path, path: Path) -> Path:
    if path.is_symlink():
        raise ValueError("QWEN_SEMANTIC_CHECKPOINT_OUTPUT_SYMLINK_FORBIDDEN")
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_SEMANTIC_CHECKPOINT_OUTPUT_OUTSIDE_REPOSITORY") from exc
    return resolved


def _write_summary(path: Path, payload: dict[str, Any]) -> None:
    payload = dict(payload)
    payload["receipt_sha256"] = sha256_json(payload)
    tmp = path.parent / f".{path.name}.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def _assert_authorities_closed(receipt: dict[str, Any], prefix: str) -> None:
    for field in _FORBIDDEN_TRUE:
        if receipt.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def run_checkpoint(candidate_admission: Path, output_root: Path, *, repo_root: Path) -> tuple[Path, bool]:
    root = _inside_repo_dir(repo_root, output_root)
    if root.exists():
        raise ValueError("QWEN_SEMANTIC_CHECKPOINT_OUTPUT_ALREADY_EXISTS")
    if not root.parent.is_dir():
        raise ValueError("QWEN_SEMANTIC_CHECKPOINT_OUTPUT_PARENT_INVALID")
    root.mkdir(mode=0o700)

    semantic_dir = root / "cs304-semantic-base-qa"
    semantic_run = run_canonical_candidate_semantic_base_qa(
        candidate_admission,
        semantic_dir,
        repo_root=repo_root,
    )
    semantic = verify_canonical_candidate_semantic_base_qa(
        semantic_run.receipt_path,
        repo_root=repo_root,
    )
    _assert_authorities_closed(semantic, "QWEN_SEMANTIC_CHECKPOINT_CS304")

    summary_path = root / "semantic_checkpoint_receipt.json"
    base: dict[str, Any] = {
        "schema": SCHEMA,
        "story_snapshot_sha256": semantic.get("story_snapshot_sha256"),
        "candidate_png": semantic.get("candidate_png"),
        "cs304_receipt": str(semantic_run.receipt_path.resolve().relative_to(repo_root.resolve())),
        "semantic_inspection_executed": semantic.get("semantic_inspection_executed") is True,
        "semantic_base_scene_approved": semantic.get("semantic_base_scene_approved") is True,
        "identity_requirement_classified": False,
        "pixel_identity_review_required": None,
        "identity_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    if semantic.get("semantic_base_scene_approved") is not True:
        base["status"] = "QWEN_IMAGE_ADMITTED_CANDIDATE_REJECTED_AT_SEMANTIC_BASE_QA"
        _write_summary(summary_path, base)
        return summary_path, False

    identity_dir = root / "cs305-identity-requirement"
    identity_run = run_identity_requirement(
        semantic_run.receipt_path,
        identity_dir,
        repo_root=repo_root,
    )
    identity = verify_identity_requirement(identity_run.receipt_path, repo_root=repo_root)
    _assert_authorities_closed(identity, "QWEN_SEMANTIC_CHECKPOINT_CS305")
    if identity.get("story_snapshot_sha256") != semantic.get("story_snapshot_sha256"):
        raise ValueError("QWEN_SEMANTIC_CHECKPOINT_STORY_LINEAGE_DRIFT")
    if identity.get("candidate_png") != semantic.get("candidate_png"):
        raise ValueError("QWEN_SEMANTIC_CHECKPOINT_CANDIDATE_LINEAGE_DRIFT")

    base.update(
        {
            "status": "QWEN_IMAGE_ADMITTED_CANDIDATE_SEMANTIC_CHECKPOINT_PASSED",
            "cs305_receipt": str(identity_run.receipt_path.resolve().relative_to(repo_root.resolve())),
            "identity_requirement_classified": True,
            "pixel_identity_review_required": identity.get("pixel_identity_review_required"),
        }
    )
    _write_summary(summary_path, base)
    return summary_path, True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run fail-closed CS304 semantic Base QA and CS305 identity-requirement classification on one CS303 admission."
    )
    parser.add_argument("--candidate-admission", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    summary, passed = run_checkpoint(
        args.candidate_admission,
        args.output_root,
        repo_root=args.repo_root,
    )
    payload = json.loads(summary.read_text(encoding="utf-8"))
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
