#!/usr/bin/env python3
"""Continue one exact approved CS278 receipt to a CS279 presentation-review request.

CS325 accepts an already-admitted, genuinely external Human Visual Review verdict.
It does not create, infer, or alter that verdict. It proves that CS278 belongs to
the exact CS277 request selected by CS324, then opens CS279 request authority only.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    SCHEMA as CS277_SCHEMA,
    verify_composed_candidate_human_visual_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    SCHEMA as CS278_SCHEMA,
    verify_composed_candidate_human_visual_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import (
    SCHEMA as CS279_SCHEMA,
    build_composed_candidate_final_presentation_review_request,
    verify_composed_candidate_final_presentation_review_request,
)

CS324_SCHEMA = "pul7sar-phase18-golden-quality-human-visual-review-request-checkpoint-v1"
SCHEMA = "pul7sar-phase18-human-review-to-final-presentation-request-checkpoint-v1"
_FINAL_FALSE = (
    "composed_visual_approved",
    "semantic_approved",
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


def _assert_final_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _FINAL_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _source_cs277_matches(
    repo_root: Path,
    cs278: Mapping[str, Any],
    cs277_path: Path,
    cs277: Mapping[str, Any],
) -> None:
    source = cs278.get("source_cs277_request")
    if not isinstance(source, Mapping):
        raise ValueError("QWEN_CS325_CS278_CS277_BINDING_MISSING")
    rel = source.get("repository_relative_path")
    if rel != cs277_path.relative_to(repo_root).as_posix():
        raise ValueError("QWEN_CS325_CS278_CS277_PATH_DRIFT")
    if source.get("receipt_sha256") != cs277.get("receipt_sha256"):
        raise ValueError("QWEN_CS325_CS278_CS277_RECEIPT_DRIFT")


def continue_human_review_to_final_presentation_request(
    cs324_checkpoint_path: Path,
    cs278_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    repo_root = repo_root.resolve()
    checkpoint_path = _inside_repo_file(
        repo_root, cs324_checkpoint_path, "QWEN_CS325_CS324_INVALID"
    )
    cs278_path = _inside_repo_file(
        repo_root, cs278_receipt_path, "QWEN_CS325_CS278_INVALID"
    )
    output_dir = _inside_repo_output(repo_root, output_dir, "QWEN_CS325_OUTPUT_INVALID")

    cs324 = _read_json(checkpoint_path, "QWEN_CS325_CS324_INVALID")
    if cs324.get("schema") != CS324_SCHEMA:
        raise ValueError("QWEN_CS325_CS324_SCHEMA_DRIFT")
    if cs324.get("authoritative") is not False:
        raise ValueError("QWEN_CS325_CS324_AUTHORITY_DRIFT")
    if cs324.get("status") != "HUMAN_VISUAL_REVIEW_EVIDENCE_REQUIRED":
        raise ValueError("QWEN_CS325_CS324_STATE_INVALID")
    if (
        cs324.get("golden_quality_approved") is not True
        or cs324.get("human_visual_review_requested") is not True
        or cs324.get("human_visual_review_executed") is not False
        or cs324.get("human_visual_review_approved") is not False
    ):
        raise ValueError("QWEN_CS325_CS324_GATE_DRIFT")
    _assert_final_closed(cs324, "QWEN_CS325_CS324")

    cs277_path = _resolve_checkpoint_receipt(
        repo_root, cs324, "cs277_receipt", "QWEN_CS325_CS277_PATH_INVALID"
    )
    cs277 = verify_composed_candidate_human_visual_review_request(
        cs277_path, repo_root=repo_root
    )
    if cs277.get("schema") != CS277_SCHEMA:
        raise ValueError("QWEN_CS325_CS277_SCHEMA_DRIFT")
    if (
        cs277.get("human_visual_review_requested") is not True
        or cs277.get("human_visual_review_executed") is not False
        or cs277.get("human_visual_review_approved") is not False
    ):
        raise ValueError("QWEN_CS325_CS277_STATE_INVALID")
    _assert_final_closed(cs277, "QWEN_CS325_CS277")

    cs278 = verify_composed_candidate_human_visual_review_evidence(
        cs278_path, repo_root=repo_root
    )
    if cs278.get("schema") != CS278_SCHEMA:
        raise ValueError("QWEN_CS325_CS278_SCHEMA_DRIFT")
    if (
        cs278.get("human_visual_review_requested") is not True
        or cs278.get("human_visual_review_executed") is not True
        or cs278.get("human_visual_review_evidence_admitted") is not True
        or cs278.get("human_visual_review_approved") is not True
    ):
        raise ValueError("QWEN_CS325_HUMAN_REVIEW_NOT_APPROVED")
    _assert_final_closed(cs278, "QWEN_CS325_CS278")
    _source_cs277_matches(repo_root, cs278, cs277_path, cs277)

    story = cs324.get("story_snapshot_sha256")
    if story != cs277.get("story_snapshot_sha256") or story != cs278.get("story_snapshot_sha256"):
        raise ValueError("QWEN_CS325_CROSS_STORY")
    if cs324.get("composed_candidate_png") != cs277.get("composed_candidate_png"):
        raise ValueError("QWEN_CS325_CS277_COMPOSED_BYTES_DRIFT")
    if cs324.get("composed_candidate_png") != cs278.get("composed_candidate_png"):
        raise ValueError("QWEN_CS325_CS278_COMPOSED_BYTES_DRIFT")

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs279_dir = output_dir / "cs279"
    cs279_path = build_composed_candidate_final_presentation_review_request(
        cs278_path, cs279_dir, repo_root=repo_root
    )
    cs279 = verify_composed_candidate_final_presentation_review_request(
        cs279_path, repo_root=repo_root
    )
    if cs279.get("schema") != CS279_SCHEMA:
        raise ValueError("QWEN_CS325_CS279_SCHEMA_DRIFT")
    if (
        cs279.get("human_visual_review_approved") is not True
        or cs279.get("final_presentation_review_requested") is not True
        or cs279.get("final_presentation_review_executed") is not False
        or cs279.get("final_presentation_review_approved") is not False
        or cs279.get("exact_brand_integrity_approved") is not False
        or cs279.get("typography_integrity_approved") is not False
    ):
        raise ValueError("QWEN_CS325_CS279_REQUEST_STATE_INVALID")
    _assert_final_closed(cs279, "QWEN_CS325_CS279")
    if cs279.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS325_CS279_CROSS_STORY")
    if cs279.get("composed_candidate_png") != cs278.get("composed_candidate_png"):
        raise ValueError("QWEN_CS325_CS279_COMPOSED_BYTES_DRIFT")

    checkpoint = {
        "schema": SCHEMA,
        "status": "FINAL_PRESENTATION_REVIEW_EVIDENCE_REQUIRED",
        "authoritative": False,
        "story_snapshot_sha256": story,
        "candidate_png": cs324.get("candidate_png"),
        "composed_candidate_png": cs278.get("composed_candidate_png"),
        "cs324_checkpoint": checkpoint_path.relative_to(repo_root).as_posix(),
        "cs277_receipt": cs277_path.relative_to(repo_root).as_posix(),
        "cs278_receipt": cs278_path.relative_to(repo_root).as_posix(),
        "cs279_receipt": cs279_path.relative_to(repo_root).as_posix(),
        "golden_quality_approved": True,
        "human_visual_review_requested": True,
        "human_visual_review_executed": True,
        "human_visual_review_evidence_admitted": True,
        "human_visual_review_approved": True,
        "final_presentation_review_requested": True,
        "final_presentation_review_executed": False,
        "final_presentation_review_approved": False,
        "exact_brand_integrity_approved": False,
        "typography_integrity_approved": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "cs278_must_be_preexisting_external_human_evidence": True,
            "human_verdict_not_generated_or_modified_by_orchestrator": True,
            "exact_cs277_lineage_replayed": True,
            "exact_cs278_receipt_replayed": True,
            "cs279_independently_replayed": True,
            "presentation_verdict_must_be_external_and_independent": True,
            "presentation_evidence_not_generated_by_orchestrator": True,
            "presentation_request_does_not_grant_brand_or_typography_approval": True,
            "presentation_request_does_not_grant_composed_approval": True,
            "presentation_request_does_not_grant_semantic_or_publication_authority": True,
        },
    }
    checkpoint_out = output_dir / "human_review_final_presentation_request_checkpoint.json"
    tmp = output_dir / ".human_review_final_presentation_request_checkpoint.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(checkpoint, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, checkpoint_out)
    return checkpoint_out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs324-checkpoint", required=True, type=Path)
    parser.add_argument("--cs278-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    path = continue_human_review_to_final_presentation_request(
        args.cs324_checkpoint,
        args.cs278_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(path)
    print(f"status={payload['status']}")
    print(f"final_presentation_review_requested={payload['final_presentation_review_requested']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
