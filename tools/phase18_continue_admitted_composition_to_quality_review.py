#!/usr/bin/env python3
"""Continue one exact CS321 admitted composition through CS273 and CS274.

Change Set 322 closes the operator wiring gap after CS321. It consumes the
non-authoritative CS321 checkpoint, independently replays the exact CS272 byte
admission referenced by that checkpoint, runs pinned Qwen2.5-VL HYBRID_SURFACE
semantic QA (CS273), independently re-verifies CS273, and only when CS273 passes
builds/re-verifies the byte-bound visual-quality review request (CS274).

This stage never fabricates visual-quality scores, never performs Human Review,
never grants Golden/global semantic/publication authority, and never generates
or composes pixels.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    SCHEMA as CS272_SCHEMA,
    verify_composed_candidate_byte_admission,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
    run_composed_candidate_hybrid_surface_semantic_qa,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    SCHEMA as CS274_SCHEMA,
    build_composed_candidate_visual_quality_review_request,
    verify_composed_candidate_visual_quality_review_request,
)

CS321_SCHEMA = "pul7sar-phase18-bound-composition-execution-and-admission-checkpoint-v1"
SCHEMA = "pul7sar-phase18-admitted-composition-quality-review-checkpoint-v1"
_DOWNSTREAM_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _inside_repo_file(repo_root: Path, path: Path, code: str) -> Path:
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(code) from exc
    if path.is_symlink() or not resolved.is_file():
        raise ValueError(code)
    return resolved


def _inside_repo_output(repo_root: Path, path: Path, code: str) -> Path:
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(code) from exc
    if resolved.exists() or not resolved.parent.is_dir():
        raise ValueError(code)
    return resolved


def _read_json(path: Path, code: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(payload, dict):
        raise ValueError(code)
    return payload


def _assert_downstream_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _resolve_checkpoint_receipt(
    repo_root: Path,
    checkpoint: Mapping[str, Any],
    field: str,
    code: str,
) -> Path:
    relative = checkpoint.get(field)
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise ValueError(code)
    return _inside_repo_file(repo_root, repo_root / relative, code)


def continue_admitted_composition_to_quality_review(
    cs321_checkpoint_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    """Replay CS272, run/replay CS273, then request CS274 only on semantic pass."""
    repo_root = repo_root.resolve()
    checkpoint_path = _inside_repo_file(
        repo_root,
        cs321_checkpoint_path,
        "QWEN_POST_COMPOSITION_CS321_INVALID",
    )
    output_dir = _inside_repo_output(
        repo_root,
        output_dir,
        "QWEN_POST_COMPOSITION_OUTPUT_INVALID",
    )
    cs321 = _read_json(checkpoint_path, "QWEN_POST_COMPOSITION_CS321_INVALID")
    if cs321.get("schema") != CS321_SCHEMA:
        raise ValueError("QWEN_POST_COMPOSITION_CS321_SCHEMA_DRIFT")
    if cs321.get("authoritative") is not False:
        raise ValueError("QWEN_POST_COMPOSITION_CS321_AUTHORITY_DRIFT")
    if (
        cs321.get("composition_executed") is not True
        or cs321.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
    ):
        raise ValueError("QWEN_POST_COMPOSITION_CS321_NOT_ADMITTED")
    _assert_downstream_closed(cs321, "QWEN_POST_COMPOSITION_CS321")

    cs272_path = _resolve_checkpoint_receipt(
        repo_root,
        cs321,
        "cs272_receipt",
        "QWEN_POST_COMPOSITION_CS272_PATH_INVALID",
    )
    cs272 = verify_composed_candidate_byte_admission(cs272_path, repo_root=repo_root)
    if (
        cs272.get("schema") != CS272_SCHEMA
        or cs272.get("composition_executed") is not True
        or cs272.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
    ):
        raise ValueError("QWEN_POST_COMPOSITION_CS272_NOT_ADMITTED")
    _assert_downstream_closed(cs272, "QWEN_POST_COMPOSITION_CS272")
    if cs321.get("story_snapshot_sha256") != cs272.get("story_snapshot_sha256"):
        raise ValueError("QWEN_POST_COMPOSITION_CROSS_STORY")
    if cs321.get("candidate_png") != cs272.get("source_candidate_png"):
        raise ValueError("QWEN_POST_COMPOSITION_SOURCE_CANDIDATE_DRIFT")
    if cs321.get("composed_candidate_png") != cs272.get("composed_candidate_png"):
        raise ValueError("QWEN_POST_COMPOSITION_COMPOSED_BYTES_DRIFT")

    # Semantic verification is local-only. Missing pinned verifier assets must
    # fail closed instead of falling back to a hub/network fetch.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs273_dir = output_dir / "cs273"
    cs274_dir = output_dir / "cs274"
    cs273_run = run_composed_candidate_hybrid_surface_semantic_qa(
        cs272_path,
        cs273_dir,
        repo_root=repo_root,
    )
    cs273 = verify_composed_candidate_hybrid_surface_semantic_qa(
        cs273_run.receipt_path,
        repo_root=repo_root,
    )
    if cs273.get("schema") != CS273_SCHEMA or cs273.get("semantic_inspection_executed") is not True:
        raise ValueError("QWEN_POST_COMPOSITION_CS273_NOT_EXECUTED")
    _assert_downstream_closed(cs273, "QWEN_POST_COMPOSITION_CS273")
    if cs272.get("story_snapshot_sha256") != cs273.get("story_snapshot_sha256"):
        raise ValueError("QWEN_POST_COMPOSITION_CS273_CROSS_STORY")
    if cs272.get("composed_candidate_png") != cs273.get("composed_candidate_png"):
        raise ValueError("QWEN_POST_COMPOSITION_CS273_COMPOSED_BYTES_DRIFT")

    cs274_path: Path | None = None
    cs274: Mapping[str, Any] | None = None
    status = "COMPOSED_CANDIDATE_REJECTED_BY_HYBRID_SURFACE_SEMANTIC_QA"
    if cs273.get("hybrid_surface_semantic_qa_approved") is True:
        cs274_path = build_composed_candidate_visual_quality_review_request(
            cs273_run.receipt_path,
            cs274_dir,
            repo_root=repo_root,
        )
        cs274 = verify_composed_candidate_visual_quality_review_request(
            cs274_path,
            repo_root=repo_root,
        )
        if cs274.get("schema") != CS274_SCHEMA or cs274.get("visual_quality_review_requested") is not True:
            raise ValueError("QWEN_POST_COMPOSITION_CS274_NOT_REQUESTED")
        _assert_downstream_closed(cs274, "QWEN_POST_COMPOSITION_CS274")
        if cs273.get("story_snapshot_sha256") != cs274.get("story_snapshot_sha256"):
            raise ValueError("QWEN_POST_COMPOSITION_CS274_CROSS_STORY")
        if cs273.get("composed_candidate_png") != cs274.get("composed_candidate_png"):
            raise ValueError("QWEN_POST_COMPOSITION_CS274_COMPOSED_BYTES_DRIFT")
        status = "VISUAL_QUALITY_REVIEW_EVIDENCE_REQUIRED"

    final_source = cs274 if cs274 is not None else cs273
    checkpoint = {
        "schema": SCHEMA,
        "status": status,
        "authoritative": False,
        "story_snapshot_sha256": final_source.get("story_snapshot_sha256"),
        "candidate_png": cs272.get("source_candidate_png"),
        "composed_candidate_png": final_source.get("composed_candidate_png"),
        "cs321_checkpoint": checkpoint_path.relative_to(repo_root).as_posix(),
        "cs272_receipt": cs272_path.relative_to(repo_root).as_posix(),
        "cs273_receipt": cs273_run.receipt_path.resolve().relative_to(repo_root).as_posix(),
        "cs274_receipt": (
            cs274_path.resolve().relative_to(repo_root).as_posix()
            if cs274_path is not None
            else None
        ),
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "semantic_inspection_executed": True,
        "hybrid_surface_semantic_qa_approved": cs273.get("hybrid_surface_semantic_qa_approved") is True,
        "visual_quality_review_requested": cs274 is not None,
        "visual_quality_review_executed": False,
        "visual_quality_review_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "exact_cs321_checkpoint_required": True,
            "exact_cs272_receipt_replayed": True,
            "pinned_hybrid_surface_semantic_qa_required": True,
            "semantic_verifier_network_fallback_forbidden": True,
            "cs274_requires_cs273_pass": True,
            "visual_quality_scores_not_fabricated": True,
            "human_review_not_automated": True,
            "global_semantic_authority_not_granted": True,
            "golden_authority_not_granted": True,
            "publication_authority_not_granted": True,
        },
    }
    checkpoint_path_out = output_dir / "post_composition_quality_review_checkpoint.json"
    tmp = output_dir / ".post_composition_quality_review_checkpoint.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(checkpoint, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, checkpoint_path_out)
    return checkpoint_path_out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Continue one exact CS321 admitted composition through CS273 and, only on "
            "semantic pass, build the CS274 visual-quality review request."
        )
    )
    parser.add_argument("--cs321-checkpoint", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    path = continue_admitted_composition_to_quality_review(
        args.cs321_checkpoint,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(path)
    print(f"status={payload['status']}")
    print(f"hybrid_surface_semantic_qa_approved={payload['hybrid_surface_semantic_qa_approved']}")
    print(f"visual_quality_review_requested={payload['visual_quality_review_requested']}")
    return 0 if payload["hybrid_surface_semantic_qa_approved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
