#!/usr/bin/env python3
"""Continue one exact CS326 composed approval through CS282 and CS283.

This checkpoint is intentionally non-authoritative. It replays the exact CS281
receipt selected by CS326, grants final semantic authority only through the
existing CS282 contract, then creates the existing CS283 request that binds the
repository SemanticPublicationGate policy bytes. It never executes CS284, never
manufactures publication evidence, never creates a Genuine Golden PNG, and never
sets publication_ready.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import (
    SCHEMA as CS281_SCHEMA,
    verify_composed_candidate_final_composed_visual_approval,
)
from engine.intelligence.qwen_image_composed_candidate_final_semantic_approval import (
    SCHEMA as CS282_SCHEMA,
    build_composed_candidate_final_semantic_approval,
    verify_composed_candidate_final_semantic_approval,
)
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    SCHEMA as CS283_SCHEMA,
    build_semantic_publication_execution_request,
    verify_semantic_publication_execution_request,
)

CS326_SCHEMA = "pul7sar-phase18-final-presentation-evidence-composed-approval-checkpoint-v1"
SCHEMA = "pul7sar-phase18-composed-approval-semantic-publication-request-checkpoint-v1"
STATUS = "SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_REQUIRED"


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


def _assert_same_composed_png(
    expected: Mapping[str, Any], actual: Mapping[str, Any], code: str
) -> None:
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if expected.get(field) != actual.get(field):
            raise ValueError(f"{code}:{field}")


def _verify_bound_png(repo_root: Path, binding: Mapping[str, Any], code: str) -> None:
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


def continue_composed_approval_to_semantic_publication_request(
    cs326_checkpoint_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    repo_root = repo_root.resolve()
    checkpoint_path = _inside_repo_file(
        repo_root, cs326_checkpoint_path, "QWEN_CS327_CS326_INVALID"
    )
    output_dir = _inside_repo_output(repo_root, output_dir, "QWEN_CS327_OUTPUT_INVALID")
    cs326 = _read_json(checkpoint_path, "QWEN_CS327_CS326_INVALID")

    if cs326.get("schema") != CS326_SCHEMA:
        raise ValueError("QWEN_CS327_CS326_SCHEMA_DRIFT")
    if cs326.get("authoritative") is not False:
        raise ValueError("QWEN_CS327_CS326_AUTHORITY_DRIFT")
    if cs326.get("status") != "FINAL_COMPOSED_VISUAL_APPROVED_AWAITING_FINAL_SEMANTIC_APPROVAL":
        raise ValueError("QWEN_CS327_CS326_STATE_INVALID")
    for field in (
        "golden_quality_approved",
        "human_visual_review_approved",
        "final_presentation_review_approved",
        "exact_brand_integrity_approved",
        "typography_integrity_approved",
        "composed_visual_approved",
    ):
        if cs326.get(field) is not True:
            raise ValueError(f"QWEN_CS327_CS326_REQUIRED_GATE_MISSING:{field}")
    for field in ("semantic_approved", "genuine_golden_png_created", "publication_ready"):
        if cs326.get(field) is not False:
            raise ValueError(f"QWEN_CS327_CS326_PREMATURE_AUTHORITY:{field}")

    story = cs326.get("story_snapshot_sha256")
    if not isinstance(story, str) or len(story) != 64:
        raise ValueError("QWEN_CS327_STORY_SHA_INVALID")
    composed = cs326.get("composed_candidate_png")
    if not isinstance(composed, Mapping):
        raise ValueError("QWEN_CS327_COMPOSED_BINDING_INVALID")
    _verify_bound_png(repo_root, composed, "QWEN_CS327_COMPOSED_PNG_INVALID")

    cs281_path = _resolve_checkpoint_receipt(
        repo_root, cs326, "cs281_receipt", "QWEN_CS327_CS281_PATH_INVALID"
    )
    cs281 = verify_composed_candidate_final_composed_visual_approval(
        cs281_path, repo_root=repo_root
    )
    if cs281.get("schema") != CS281_SCHEMA:
        raise ValueError("QWEN_CS327_CS281_SCHEMA_DRIFT")
    if cs281.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS327_CS281_CROSS_STORY")
    if cs281.get("composed_visual_approved") is not True:
        raise ValueError("QWEN_CS327_CS281_COMPOSED_APPROVAL_MISSING")
    for field in ("semantic_approved", "genuine_golden_png_created", "publication_ready"):
        if cs281.get(field) is not False:
            raise ValueError(f"QWEN_CS327_CS281_PREMATURE_AUTHORITY:{field}")
    cs281_png = cs281.get("composed_candidate_png")
    if not isinstance(cs281_png, Mapping):
        raise ValueError("QWEN_CS327_CS281_COMPOSED_BINDING_INVALID")
    _assert_same_composed_png(composed, cs281_png, "QWEN_CS327_CS281_COMPOSED_BYTES_DRIFT")

    # Defensive network-off posture. CS282/CS283 are deterministic receipt stages,
    # but no library import in this continuation may silently fetch verifier/model data.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs282_dir = output_dir / "cs282"
    cs282_path = build_composed_candidate_final_semantic_approval(
        cs281_path, cs282_dir, repo_root=repo_root
    )
    cs282 = verify_composed_candidate_final_semantic_approval(
        cs282_path, repo_root=repo_root
    )
    if cs282.get("schema") != CS282_SCHEMA:
        raise ValueError("QWEN_CS327_CS282_SCHEMA_DRIFT")
    if cs282.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS327_CS282_CROSS_STORY")
    cs282_png = cs282.get("composed_candidate_png")
    if not isinstance(cs282_png, Mapping):
        raise ValueError("QWEN_CS327_CS282_COMPOSED_BINDING_INVALID")
    _assert_same_composed_png(composed, cs282_png, "QWEN_CS327_CS282_COMPOSED_BYTES_DRIFT")
    if cs282.get("composed_visual_approved") is not True or cs282.get("semantic_approved") is not True:
        raise ValueError("QWEN_CS327_CS282_FINAL_SEMANTIC_APPROVAL_MISSING")
    for field in ("genuine_golden_png_created", "publication_ready"):
        if cs282.get(field) is not False:
            raise ValueError(f"QWEN_CS327_CS282_PREMATURE_AUTHORITY:{field}")

    cs283_dir = output_dir / "cs283"
    cs283_path = build_semantic_publication_execution_request(
        cs282_path, cs283_dir, repo_root=repo_root
    )
    cs283 = verify_semantic_publication_execution_request(
        cs283_path, repo_root=repo_root
    )
    if cs283.get("schema") != CS283_SCHEMA:
        raise ValueError("QWEN_CS327_CS283_SCHEMA_DRIFT")
    if cs283.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS327_CS283_CROSS_STORY")
    cs283_png = cs283.get("composed_candidate_png")
    if not isinstance(cs283_png, Mapping):
        raise ValueError("QWEN_CS327_CS283_COMPOSED_BINDING_INVALID")
    _assert_same_composed_png(composed, cs283_png, "QWEN_CS327_CS283_COMPOSED_BYTES_DRIFT")
    expected_cs283 = {
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    for field, value in expected_cs283.items():
        if cs283.get(field) is not value:
            raise ValueError(f"QWEN_CS327_CS283_STATE_DRIFT:{field}")

    checkpoint: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "authoritative": False,
        "story_snapshot_sha256": story,
        "candidate_png": cs326.get("candidate_png"),
        "composed_candidate_png": dict(composed),
        "cs326_checkpoint": checkpoint_path.relative_to(repo_root).as_posix(),
        "cs281_receipt": cs281_path.relative_to(repo_root).as_posix(),
        "cs282_receipt": cs282_path.relative_to(repo_root).as_posix(),
        "cs283_receipt": cs283_path.relative_to(repo_root).as_posix(),
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "exact_cs326_selected_cs281_replayed": True,
            "exact_composed_png_bytes_preserved_through_cs281_cs282_cs283": True,
            "final_semantic_authority_granted_only_by_existing_cs282": True,
            "semantic_publication_request_granted_only_by_existing_cs283": True,
            "semantic_publication_gate_not_executed_by_this_checkpoint": True,
            "cs284_requires_real_external_execution_evidence": True,
            "no_publication_verdict_is_manufactured": True,
            "no_genuine_golden_png_is_created": True,
            "publication_ready_remains_closed": True,
            "offline_local_only_posture_preserved": True,
        },
    }
    checkpoint_out = output_dir / "semantic_publication_request_checkpoint.json"
    tmp = output_dir / ".semantic_publication_request_checkpoint.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(checkpoint, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, checkpoint_out)
    return checkpoint_out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs326-checkpoint", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path("."), type=Path)
    args = parser.parse_args()
    path = continue_composed_approval_to_semantic_publication_request(
        args.cs326_checkpoint,
        args.output_dir,
        repo_root=args.repo_root,
    )
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
