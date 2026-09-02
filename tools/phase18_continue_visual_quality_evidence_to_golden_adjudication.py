#!/usr/bin/env python3
"""Continue one exact CS322 checkpoint through CS275 and CS276.

Change Set 323 removes the operator-wiring gap between the byte-bound CS274
visual-quality review request, genuine external manual review evidence (CS275),
and deterministic Golden-quality adjudication (CS276).

This tool never invents visual-quality scores, never performs Human Visual
Review, never creates or modifies pixels, and never grants final semantic or
publication authority. The external review document must already exist inside
the repository and satisfy the exact CS275 manual-review contract.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_byte_admission import (
    CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
    verify_canonical_candidate_byte_admission,
)
from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    SCHEMA as CS272_SCHEMA,
    verify_composed_candidate_byte_admission,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    SCHEMA as CS274_SCHEMA,
    verify_composed_candidate_visual_quality_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import (
    SCHEMA as CS275_SCHEMA,
    build_composed_candidate_visual_quality_review_evidence,
    verify_composed_candidate_visual_quality_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    SCHEMA as CS276_SCHEMA,
    build_composed_candidate_golden_quality_adjudication,
    verify_composed_candidate_golden_quality_adjudication,
)

CS322_SCHEMA = "pul7sar-phase18-admitted-composition-quality-review-checkpoint-v1"
SCHEMA = "pul7sar-phase18-visual-quality-evidence-golden-adjudication-checkpoint-v1"
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


def continue_visual_quality_evidence_to_golden_adjudication(
    cs322_checkpoint_path: Path,
    external_review_path: Path,
    candidate_admission_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    """Admit exact manual quality evidence, then execute/replay CS276."""
    repo_root = repo_root.resolve()
    checkpoint_path = _inside_repo_file(
        repo_root,
        cs322_checkpoint_path,
        "QWEN_CS323_CS322_INVALID",
    )
    external_review_path = _inside_repo_file(
        repo_root,
        external_review_path,
        "QWEN_CS323_EXTERNAL_REVIEW_INVALID",
    )
    candidate_admission_path = _inside_repo_file(
        repo_root,
        candidate_admission_path,
        "QWEN_CS323_CANDIDATE_ADMISSION_INVALID",
    )
    output_dir = _inside_repo_output(repo_root, output_dir, "QWEN_CS323_OUTPUT_INVALID")

    cs322 = _read_json(checkpoint_path, "QWEN_CS323_CS322_INVALID")
    if cs322.get("schema") != CS322_SCHEMA:
        raise ValueError("QWEN_CS323_CS322_SCHEMA_DRIFT")
    if cs322.get("authoritative") is not False:
        raise ValueError("QWEN_CS323_CS322_AUTHORITY_DRIFT")
    if cs322.get("status") != "VISUAL_QUALITY_REVIEW_EVIDENCE_REQUIRED":
        raise ValueError("QWEN_CS323_CS322_NOT_READY_FOR_REVIEW_EVIDENCE")
    if (
        cs322.get("hybrid_surface_semantic_qa_approved") is not True
        or cs322.get("visual_quality_review_requested") is not True
        or cs322.get("visual_quality_review_executed") is not False
        or cs322.get("golden_quality_approved") is not False
    ):
        raise ValueError("QWEN_CS323_CS322_GATE_DRIFT")
    _assert_final_authority_closed(cs322, "QWEN_CS323_CS322")

    cs272_path = _resolve_checkpoint_receipt(
        repo_root, cs322, "cs272_receipt", "QWEN_CS323_CS272_PATH_INVALID"
    )
    cs274_path = _resolve_checkpoint_receipt(
        repo_root, cs322, "cs274_receipt", "QWEN_CS323_CS274_PATH_INVALID"
    )
    cs272 = verify_composed_candidate_byte_admission(cs272_path, repo_root=repo_root)
    cs274 = verify_composed_candidate_visual_quality_review_request(cs274_path, repo_root=repo_root)
    if cs272.get("schema") != CS272_SCHEMA:
        raise ValueError("QWEN_CS323_CS272_SCHEMA_DRIFT")
    if cs274.get("schema") != CS274_SCHEMA:
        raise ValueError("QWEN_CS323_CS274_SCHEMA_DRIFT")
    if cs274.get("visual_quality_review_requested") is not True:
        raise ValueError("QWEN_CS323_CS274_NOT_REQUESTED")
    _assert_final_authority_closed(cs272, "QWEN_CS323_CS272")
    _assert_final_authority_closed(cs274, "QWEN_CS323_CS274")

    candidate_admission = verify_canonical_candidate_byte_admission(
        candidate_admission_path, repo_root=repo_root
    )
    if candidate_admission.get("schema") != CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA:
        raise ValueError("QWEN_CS323_CANDIDATE_ADMISSION_SCHEMA_DRIFT")
    if (
        candidate_admission.get("cost_mode") != "$0-local"
        or candidate_admission.get("network_allowed") is not False
        or candidate_admission.get("local_files_only") is not True
    ):
        raise ValueError("QWEN_CS323_ZERO_COST_LOCAL_ONLY_DRIFT")
    _assert_final_authority_closed(candidate_admission, "QWEN_CS323_CANDIDATE_ADMISSION")

    story = cs322.get("story_snapshot_sha256")
    if (
        story != cs272.get("story_snapshot_sha256")
        or story != cs274.get("story_snapshot_sha256")
        or story != candidate_admission.get("story_snapshot_sha256")
    ):
        raise ValueError("QWEN_CS323_CROSS_STORY")
    if cs322.get("candidate_png") != cs272.get("source_candidate_png"):
        raise ValueError("QWEN_CS323_SOURCE_CANDIDATE_DRIFT")
    if candidate_admission.get("candidate_png") != cs272.get("source_candidate_png"):
        raise ValueError("QWEN_CS323_CANDIDATE_ADMISSION_DRIFT")
    if cs322.get("composed_candidate_png") != cs272.get("composed_candidate_png"):
        raise ValueError("QWEN_CS323_COMPOSED_BYTES_DRIFT")
    if cs274.get("composed_candidate_png") != cs272.get("composed_candidate_png"):
        raise ValueError("QWEN_CS323_CS274_COMPOSED_BYTES_DRIFT")

    # This continuation must never fetch models or use the network. CS275 is
    # external-manual evidence admission and CS276 is deterministic adjudication.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs275_dir = output_dir / "cs275"
    cs276_dir = output_dir / "cs276"

    cs275_path = build_composed_candidate_visual_quality_review_evidence(
        cs274_path,
        external_review_path,
        cs275_dir,
        repo_root=repo_root,
    )
    cs275 = verify_composed_candidate_visual_quality_review_evidence(
        cs275_path, repo_root=repo_root
    )
    if (
        cs275.get("schema") != CS275_SCHEMA
        or cs275.get("visual_quality_review_executed") is not True
        or cs275.get("visual_quality_evidence_admitted") is not True
    ):
        raise ValueError("QWEN_CS323_CS275_NOT_ADMITTED")
    _assert_final_authority_closed(cs275, "QWEN_CS323_CS275")
    if cs275.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS323_CS275_CROSS_STORY")
    if cs275.get("composed_candidate_png") != cs272.get("composed_candidate_png"):
        raise ValueError("QWEN_CS323_CS275_COMPOSED_BYTES_DRIFT")

    cs276_path = build_composed_candidate_golden_quality_adjudication(
        candidate_admission_path,
        cs272_path,
        cs275_path,
        cs276_dir,
        repo_root=repo_root,
    )
    cs276 = verify_composed_candidate_golden_quality_adjudication(
        cs276_path, repo_root=repo_root
    )
    if cs276.get("schema") != CS276_SCHEMA:
        raise ValueError("QWEN_CS323_CS276_SCHEMA_DRIFT")
    _assert_final_authority_closed(cs276, "QWEN_CS323_CS276")
    if cs276.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS323_CS276_CROSS_STORY")
    if cs276.get("source_candidate_png") != cs272.get("source_candidate_png"):
        raise ValueError("QWEN_CS323_CS276_SOURCE_CANDIDATE_DRIFT")
    if cs276.get("composed_candidate_png") != cs272.get("composed_candidate_png"):
        raise ValueError("QWEN_CS323_CS276_COMPOSED_BYTES_DRIFT")

    golden_pass = cs276.get("golden_quality_approved") is True
    checkpoint = {
        "schema": SCHEMA,
        "status": (
            "GOLDEN_QUALITY_PASSED_AWAITING_DOWNSTREAM_HUMAN_REVIEW"
            if golden_pass
            else "COMPOSED_CANDIDATE_REJECTED_BY_GOLDEN_QUALITY"
        ),
        "authoritative": False,
        "story_snapshot_sha256": story,
        "candidate_png": cs272.get("source_candidate_png"),
        "composed_candidate_png": cs272.get("composed_candidate_png"),
        "cs322_checkpoint": checkpoint_path.relative_to(repo_root).as_posix(),
        "candidate_admission_receipt": candidate_admission_path.relative_to(repo_root).as_posix(),
        "cs272_receipt": cs272_path.relative_to(repo_root).as_posix(),
        "cs274_receipt": cs274_path.relative_to(repo_root).as_posix(),
        "external_review_evidence": external_review_path.relative_to(repo_root).as_posix(),
        "cs275_receipt": cs275_path.relative_to(repo_root).as_posix(),
        "cs276_receipt": cs276_path.relative_to(repo_root).as_posix(),
        "visual_quality_review_requested": True,
        "visual_quality_review_executed": True,
        "visual_quality_evidence_admitted": True,
        "visual_quality_review_approved": cs276.get("visual_quality_review_approved") is True,
        "golden_quality_approved": golden_pass,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "external_manual_review_required": True,
            "visual_quality_scores_not_generated_by_orchestrator": True,
            "exact_cs274_request_replayed": True,
            "exact_cs272_receipt_replayed": True,
            "candidate_admission_replayed": True,
            "cs275_independently_replayed": True,
            "cs276_independently_replayed": True,
            "golden_selector_result_not_overridden": True,
            "human_visual_review_remains_separate": True,
            "final_semantic_authority_not_granted": True,
            "publication_authority_not_granted": True,
        },
    }
    checkpoint_path_out = output_dir / "visual_quality_golden_adjudication_checkpoint.json"
    tmp = output_dir / ".visual_quality_golden_adjudication_checkpoint.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(checkpoint, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, checkpoint_path_out)
    return checkpoint_path_out


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Admit genuine external manual visual-quality evidence for the exact CS274 "
            "request referenced by CS322, then execute/replay CS276 Golden adjudication."
        )
    )
    parser.add_argument("--cs322-checkpoint", required=True, type=Path)
    parser.add_argument("--external-review", required=True, type=Path)
    parser.add_argument("--candidate-admission", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    path = continue_visual_quality_evidence_to_golden_adjudication(
        args.cs322_checkpoint,
        args.external_review,
        args.candidate_admission,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(path)
    print(f"status={payload['status']}")
    print(f"golden_quality_approved={payload['golden_quality_approved']}")
    return 0 if payload["golden_quality_approved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
