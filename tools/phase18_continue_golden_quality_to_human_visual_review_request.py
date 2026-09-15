#!/usr/bin/env python3
"""Continue one exact CS323 Golden-quality pass to a CS277 Human Visual Review request.

Change Set 324 removes only the operator-wiring gap between the exact CS276
Golden-quality receipt already selected by CS323 and the byte-bound CS277 Human
Visual Review request. It never performs Human Visual Review, never admits a
human verdict, never changes pixels, and never grants composed, semantic,
Genuine-Golden, or publication authority.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    SCHEMA as CS276_SCHEMA,
    verify_composed_candidate_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    SCHEMA as CS277_SCHEMA,
    build_composed_candidate_human_visual_review_request,
    verify_composed_candidate_human_visual_review_request,
)

CS323_SCHEMA = "pul7sar-phase18-visual-quality-evidence-golden-adjudication-checkpoint-v1"
SCHEMA = "pul7sar-phase18-golden-quality-human-visual-review-request-checkpoint-v1"
_FINAL_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
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
        value = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(value, dict):
        raise ValueError(code)
    return value


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


def _assert_final_authority_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _FINAL_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def continue_golden_quality_to_human_visual_review_request(
    cs323_checkpoint_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    """Replay the exact CS276 selected by CS323 and create/replay CS277 only."""
    repo_root = repo_root.resolve()
    checkpoint_path = _inside_repo_file(
        repo_root,
        cs323_checkpoint_path,
        "QWEN_CS324_CS323_INVALID",
    )
    output_dir = _inside_repo_output(repo_root, output_dir, "QWEN_CS324_OUTPUT_INVALID")

    cs323 = _read_json(checkpoint_path, "QWEN_CS324_CS323_INVALID")
    if cs323.get("schema") != CS323_SCHEMA:
        raise ValueError("QWEN_CS324_CS323_SCHEMA_DRIFT")
    if cs323.get("authoritative") is not False:
        raise ValueError("QWEN_CS324_CS323_AUTHORITY_DRIFT")
    if cs323.get("status") != "GOLDEN_QUALITY_PASSED_AWAITING_DOWNSTREAM_HUMAN_REVIEW":
        raise ValueError("QWEN_CS324_CS323_NOT_GOLDEN_QUALITY_PASSED")
    if (
        cs323.get("visual_quality_review_requested") is not True
        or cs323.get("visual_quality_review_executed") is not True
        or cs323.get("visual_quality_evidence_admitted") is not True
        or cs323.get("visual_quality_review_approved") is not True
        or cs323.get("golden_quality_approved") is not True
    ):
        raise ValueError("QWEN_CS324_CS323_GATE_DRIFT")
    _assert_final_authority_closed(cs323, "QWEN_CS324_CS323")

    cs276_path = _resolve_checkpoint_receipt(
        repo_root,
        cs323,
        "cs276_receipt",
        "QWEN_CS324_CS276_PATH_INVALID",
    )
    cs276 = verify_composed_candidate_golden_quality_adjudication(
        cs276_path,
        repo_root=repo_root,
    )
    if cs276.get("schema") != CS276_SCHEMA:
        raise ValueError("QWEN_CS324_CS276_SCHEMA_DRIFT")
    if (
        cs276.get("golden_quality_selector_executed") is not True
        or cs276.get("golden_quality_approved") is not True
    ):
        raise ValueError("QWEN_CS324_CS276_NOT_GOLDEN_QUALITY_PASSED")
    _assert_final_authority_closed(cs276, "QWEN_CS324_CS276")

    story = cs323.get("story_snapshot_sha256")
    if story != cs276.get("story_snapshot_sha256"):
        raise ValueError("QWEN_CS324_CROSS_STORY")
    if cs323.get("candidate_png") != cs276.get("source_candidate_png"):
        raise ValueError("QWEN_CS324_SOURCE_CANDIDATE_DRIFT")
    if cs323.get("composed_candidate_png") != cs276.get("composed_candidate_png"):
        raise ValueError("QWEN_CS324_COMPOSED_BYTES_DRIFT")

    # CS277 is deterministic receipt construction. Keep the environment closed
    # anyway so this orchestration cannot become a model/network-fetch surface.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs277_dir = output_dir / "cs277"
    cs277_path = build_composed_candidate_human_visual_review_request(
        cs276_path,
        cs277_dir,
        repo_root=repo_root,
    )
    cs277 = verify_composed_candidate_human_visual_review_request(
        cs277_path,
        repo_root=repo_root,
    )
    if cs277.get("schema") != CS277_SCHEMA:
        raise ValueError("QWEN_CS324_CS277_SCHEMA_DRIFT")
    if (
        cs277.get("golden_quality_approved") is not True
        or cs277.get("human_visual_review_requested") is not True
        or cs277.get("human_visual_review_executed") is not False
        or cs277.get("human_visual_review_approved") is not False
    ):
        raise ValueError("QWEN_CS324_CS277_REQUEST_STATE_INVALID")
    _assert_final_authority_closed(cs277, "QWEN_CS324_CS277")
    if cs277.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS324_CS277_CROSS_STORY")
    if cs277.get("composed_candidate_png") != cs276.get("composed_candidate_png"):
        raise ValueError("QWEN_CS324_CS277_COMPOSED_BYTES_DRIFT")

    checkpoint = {
        "schema": SCHEMA,
        "status": "HUMAN_VISUAL_REVIEW_EVIDENCE_REQUIRED",
        "authoritative": False,
        "story_snapshot_sha256": story,
        "candidate_png": cs276.get("source_candidate_png"),
        "composed_candidate_png": cs276.get("composed_candidate_png"),
        "cs323_checkpoint": checkpoint_path.relative_to(repo_root).as_posix(),
        "cs276_receipt": cs276_path.relative_to(repo_root).as_posix(),
        "cs277_receipt": cs277_path.relative_to(repo_root).as_posix(),
        "golden_quality_approved": True,
        "human_visual_review_requested": True,
        "human_visual_review_executed": False,
        "human_visual_review_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "exact_cs276_receipt_replayed": True,
            "cs277_independently_replayed": True,
            "human_review_must_be_external_and_independent": True,
            "human_review_evidence_not_generated_by_orchestrator": True,
            "human_review_verdict_not_generated_by_orchestrator": True,
            "exact_bound_composed_png_must_be_inspected": True,
            "golden_quality_does_not_replace_human_review": True,
            "human_review_request_does_not_grant_composed_approval": True,
            "human_review_request_does_not_grant_final_semantic_authority": True,
            "human_review_request_does_not_grant_publication_authority": True,
        },
    }
    checkpoint_path_out = output_dir / "golden_quality_human_visual_review_request_checkpoint.json"
    tmp = output_dir / ".golden_quality_human_visual_review_request_checkpoint.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(checkpoint, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, checkpoint_path_out)
    return checkpoint_path_out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Replay the exact CS276 Golden-quality pass referenced by CS323 and "
            "create/replay its CS277 Human Visual Review request."
        )
    )
    parser.add_argument("--cs323-checkpoint", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    path = continue_golden_quality_to_human_visual_review_request(
        args.cs323_checkpoint,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(path)
    print(f"status={payload['status']}")
    print(f"human_visual_review_requested={payload['human_visual_review_requested']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
