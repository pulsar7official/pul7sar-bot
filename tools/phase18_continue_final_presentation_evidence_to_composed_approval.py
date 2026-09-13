#!/usr/bin/env python3
"""Bind one exact CS325 request to external CS280 evidence and CS281 approval.

CS326 never creates or alters presentation-review evidence. It admits an already
written external manual verdict through CS280, replays the exact review lineage
back to CS273, and only then permits deterministic CS281 final-composed approval.
Global semantic approval, Genuine Golden materialization, and publication remain
closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    verify_composed_candidate_visual_quality_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import (
    verify_composed_candidate_visual_quality_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    verify_composed_candidate_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_request import (
    verify_composed_candidate_human_visual_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_human_visual_review_evidence import (
    verify_composed_candidate_human_visual_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_request import (
    SCHEMA as CS279_SCHEMA,
    verify_composed_candidate_final_presentation_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_evidence import (
    SCHEMA as CS280_SCHEMA,
    build_composed_candidate_final_presentation_review_evidence,
    verify_composed_candidate_final_presentation_review_evidence,
)
from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import (
    SCHEMA as CS281_SCHEMA,
    build_composed_candidate_final_composed_visual_approval,
    verify_composed_candidate_final_composed_visual_approval,
)

CS325_SCHEMA = "pul7sar-phase18-human-review-to-final-presentation-request-checkpoint-v1"
SCHEMA = "pul7sar-phase18-final-presentation-evidence-composed-approval-checkpoint-v1"
Verifier = Callable[..., dict[str, Any]]
_DOWNSTREAM_FALSE = (
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


def _reopen_binding(repo_root: Path, binding: Mapping[str, Any], code: str) -> Path:
    relative = binding.get("repository_relative_path")
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or ".." in Path(relative).parts
    ):
        raise ValueError(code)
    path = _inside_repo_file(repo_root, repo_root / relative, code)
    raw = path.read_bytes()
    if binding.get("sha256") != hashlib.sha256(raw).hexdigest():
        raise ValueError(code + "_BYTE_DRIFT")
    if binding.get("byte_size") != len(raw):
        raise ValueError(code + "_BYTE_SIZE_DRIFT")
    return path


def _verified_child(
    repo_root: Path,
    parent: Mapping[str, Any],
    field: str,
    verifier: Verifier,
    code: str,
) -> tuple[Path, dict[str, Any]]:
    binding = parent.get(field)
    if not isinstance(binding, Mapping):
        raise ValueError(code + "_BINDING_MISSING")
    path = _reopen_binding(repo_root, binding, code)
    child = verifier(path, repo_root=repo_root)
    if binding.get("receipt_sha256") != child.get("receipt_sha256"):
        raise ValueError(code + "_RECEIPT_DRIFT")
    return path, child


def _derive_exact_cs273(
    repo_root: Path, cs280: Mapping[str, Any]
) -> tuple[Path, dict[str, Any]]:
    _, cs279 = _verified_child(
        repo_root,
        cs280,
        "source_cs279_request",
        verify_composed_candidate_final_presentation_review_request,
        "QWEN_CS326_CS279_INVALID",
    )
    _, cs278 = _verified_child(
        repo_root,
        cs279,
        "source_cs278_receipt",
        verify_composed_candidate_human_visual_review_evidence,
        "QWEN_CS326_CS278_INVALID",
    )
    _, cs277 = _verified_child(
        repo_root,
        cs278,
        "source_cs277_request",
        verify_composed_candidate_human_visual_review_request,
        "QWEN_CS326_CS277_INVALID",
    )
    _, cs276 = _verified_child(
        repo_root,
        cs277,
        "source_cs276_receipt",
        verify_composed_candidate_golden_quality_adjudication,
        "QWEN_CS326_CS276_INVALID",
    )
    _, cs275 = _verified_child(
        repo_root,
        cs276,
        "source_cs275_receipt",
        verify_composed_candidate_visual_quality_review_evidence,
        "QWEN_CS326_CS275_INVALID",
    )
    _, cs274 = _verified_child(
        repo_root,
        cs275,
        "source_cs274_request",
        verify_composed_candidate_visual_quality_review_request,
        "QWEN_CS326_CS274_INVALID",
    )
    cs273_path, cs273 = _verified_child(
        repo_root,
        cs274,
        "source_cs273_receipt",
        verify_composed_candidate_hybrid_surface_semantic_qa,
        "QWEN_CS326_CS273_INVALID",
    )
    if cs273.get("schema") != CS273_SCHEMA:
        raise ValueError("QWEN_CS326_CS273_SCHEMA_DRIFT")
    return cs273_path, cs273


def _assert_downstream_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def continue_final_presentation_evidence_to_composed_approval(
    cs325_checkpoint_path: Path,
    external_review_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    repo_root = repo_root.resolve()
    checkpoint_path = _inside_repo_file(
        repo_root, cs325_checkpoint_path, "QWEN_CS326_CS325_INVALID"
    )
    review_path = _inside_repo_file(
        repo_root, external_review_path, "QWEN_CS326_EXTERNAL_REVIEW_INVALID"
    )
    output_dir = _inside_repo_output(repo_root, output_dir, "QWEN_CS326_OUTPUT_INVALID")

    cs325 = _read_json(checkpoint_path, "QWEN_CS326_CS325_INVALID")
    if cs325.get("schema") != CS325_SCHEMA:
        raise ValueError("QWEN_CS326_CS325_SCHEMA_DRIFT")
    if cs325.get("authoritative") is not False:
        raise ValueError("QWEN_CS326_CS325_AUTHORITY_DRIFT")
    if cs325.get("status") != "FINAL_PRESENTATION_REVIEW_EVIDENCE_REQUIRED":
        raise ValueError("QWEN_CS326_CS325_STATE_INVALID")
    for field in (
        "golden_quality_approved",
        "human_visual_review_approved",
        "final_presentation_review_requested",
    ):
        if cs325.get(field) is not True:
            raise ValueError(f"QWEN_CS326_CS325_REQUIRED_GATE_MISSING:{field}")
    for field in (
        "final_presentation_review_executed",
        "final_presentation_review_approved",
        "exact_brand_integrity_approved",
        "typography_integrity_approved",
        "composed_visual_approved",
        "semantic_approved",
        "genuine_golden_png_created",
        "publication_ready",
    ):
        if cs325.get(field) is not False:
            raise ValueError(f"QWEN_CS326_CS325_PREMATURE_AUTHORITY:{field}")

    cs279_path = _resolve_checkpoint_receipt(
        repo_root, cs325, "cs279_receipt", "QWEN_CS326_CS279_PATH_INVALID"
    )
    cs279 = verify_composed_candidate_final_presentation_review_request(
        cs279_path, repo_root=repo_root
    )
    if cs279.get("schema") != CS279_SCHEMA:
        raise ValueError("QWEN_CS326_CS279_SCHEMA_DRIFT")
    if (
        cs279.get("final_presentation_review_requested") is not True
        or cs279.get("final_presentation_review_executed") is not False
        or cs279.get("final_presentation_review_approved") is not False
    ):
        raise ValueError("QWEN_CS326_CS279_STATE_INVALID")
    _assert_downstream_closed(cs279, "QWEN_CS326_CS279")

    story = cs325.get("story_snapshot_sha256")
    if story != cs279.get("story_snapshot_sha256"):
        raise ValueError("QWEN_CS326_CS279_CROSS_STORY")
    if cs325.get("composed_candidate_png") != cs279.get("composed_candidate_png"):
        raise ValueError("QWEN_CS326_CS279_COMPOSED_BYTES_DRIFT")

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs280_dir = output_dir / "cs280"
    cs280_path = build_composed_candidate_final_presentation_review_evidence(
        cs279_path, review_path, cs280_dir, repo_root=repo_root
    )
    cs280 = verify_composed_candidate_final_presentation_review_evidence(
        cs280_path, repo_root=repo_root
    )
    if cs280.get("schema") != CS280_SCHEMA:
        raise ValueError("QWEN_CS326_CS280_SCHEMA_DRIFT")
    if cs280.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS326_CS280_CROSS_STORY")
    if cs280.get("composed_candidate_png") != cs279.get("composed_candidate_png"):
        raise ValueError("QWEN_CS326_CS280_COMPOSED_BYTES_DRIFT")
    _assert_downstream_closed(cs280, "QWEN_CS326_CS280")

    checkpoint: dict[str, Any] = {
        "schema": SCHEMA,
        "authoritative": False,
        "story_snapshot_sha256": story,
        "candidate_png": cs325.get("candidate_png"),
        "composed_candidate_png": cs280.get("composed_candidate_png"),
        "cs325_checkpoint": checkpoint_path.relative_to(repo_root).as_posix(),
        "cs279_receipt": cs279_path.relative_to(repo_root).as_posix(),
        "cs280_receipt": cs280_path.relative_to(repo_root).as_posix(),
        "golden_quality_approved": True,
        "human_visual_review_approved": True,
        "final_presentation_review_requested": True,
        "final_presentation_review_executed": True,
        "final_presentation_review_evidence_admitted": True,
        "final_presentation_review_approved": bool(cs280.get("final_presentation_review_approved")),
        "exact_brand_integrity_approved": bool(cs280.get("exact_brand_integrity_approved")),
        "typography_integrity_approved": bool(cs280.get("typography_integrity_approved")),
        "composed_visual_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "presentation_verdict_must_be_preexisting_external_manual_evidence": True,
            "presentation_verdict_not_generated_or_modified_by_orchestrator": True,
            "exact_cs279_request_replayed": True,
            "exact_cs280_evidence_replayed": True,
            "exact_review_lineage_back_to_cs273_required_before_composed_approval": True,
            "final_composed_approval_is_deterministic_aggregation_not_new_review": True,
            "composed_approval_does_not_grant_global_semantic_approval": True,
            "composed_approval_does_not_create_genuine_golden_png": True,
            "composed_approval_does_not_grant_publication_authority": True,
        },
    }

    if cs280.get("final_presentation_review_approved") is not True:
        checkpoint["status"] = "COMPOSED_CANDIDATE_REJECTED_BY_FINAL_PRESENTATION_REVIEW"
        checkpoint["cs281_receipt"] = None
    else:
        for field in ("exact_brand_integrity_approved", "typography_integrity_approved"):
            if cs280.get(field) is not True:
                raise ValueError(f"QWEN_CS326_CS280_REQUIRED_GATE_MISSING:{field}")
        cs273_path, cs273 = _derive_exact_cs273(repo_root, cs280)
        if cs273.get("story_snapshot_sha256") != story:
            raise ValueError("QWEN_CS326_CS273_CROSS_STORY")
        if cs273.get("composed_candidate_png") != cs280.get("composed_candidate_png"):
            raise ValueError("QWEN_CS326_CS273_COMPOSED_BYTES_DRIFT")

        cs281_dir = output_dir / "cs281"
        cs281_path = build_composed_candidate_final_composed_visual_approval(
            cs273_path, cs280_path, cs281_dir, repo_root=repo_root
        )
        cs281 = verify_composed_candidate_final_composed_visual_approval(
            cs281_path, repo_root=repo_root
        )
        if cs281.get("schema") != CS281_SCHEMA:
            raise ValueError("QWEN_CS326_CS281_SCHEMA_DRIFT")
        if cs281.get("story_snapshot_sha256") != story:
            raise ValueError("QWEN_CS326_CS281_CROSS_STORY")
        if cs281.get("composed_candidate_png") != cs280.get("composed_candidate_png"):
            raise ValueError("QWEN_CS326_CS281_COMPOSED_BYTES_DRIFT")
        if cs281.get("composed_visual_approved") is not True:
            raise ValueError("QWEN_CS326_CS281_COMPOSED_APPROVAL_MISSING")
        _assert_downstream_closed(cs281, "QWEN_CS326_CS281")

        checkpoint["status"] = "FINAL_COMPOSED_VISUAL_APPROVED_AWAITING_FINAL_SEMANTIC_APPROVAL"
        checkpoint["cs273_receipt"] = cs273_path.relative_to(repo_root).as_posix()
        checkpoint["cs281_receipt"] = cs281_path.relative_to(repo_root).as_posix()
        checkpoint["composed_visual_approved"] = True

    checkpoint_out = output_dir / "final_presentation_composed_approval_checkpoint.json"
    tmp = output_dir / ".final_presentation_composed_approval_checkpoint.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(checkpoint, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, checkpoint_out)
    return checkpoint_out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs325-checkpoint", required=True, type=Path)
    parser.add_argument("--external-review", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    path = continue_final_presentation_evidence_to_composed_approval(
        args.cs325_checkpoint,
        args.external_review,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))
    print(path)
    print(f"status={payload['status']}")
    print(f"composed_visual_approved={payload['composed_visual_approved']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
