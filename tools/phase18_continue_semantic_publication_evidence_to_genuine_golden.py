#!/usr/bin/env python3
"""CS328: admit one exact CS284 decision and materialize the exact Genuine Golden PNG.

This checkpoint never executes or emulates SemanticPublicationGate. It consumes the
exact CS283 selected by CS327 plus a pre-existing CS284 receipt, independently replays
both contracts, proves that CS284 is bound to that exact CS283/story/composed PNG, and
only when the repository gate itself returned allowed=True invokes the existing CS285
byte-identical materializer. It never mutates pixels and never grants publication
readiness; CS286 remains a separate downstream authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution import (
    SCHEMA as CS284_SCHEMA,
    verify_semantic_publication_execution,
)
from engine.intelligence.qwen_image_composed_candidate_semantic_publication_execution_request import (
    SCHEMA as CS283_SCHEMA,
    verify_semantic_publication_execution_request,
)
from engine.intelligence.qwen_image_genuine_golden_materialization import (
    SCHEMA as CS285_SCHEMA,
    materialize_genuine_golden_visual,
    verify_genuine_golden_materialization,
)

CS327_SCHEMA = "pul7sar-phase18-composed-approval-semantic-publication-request-checkpoint-v1"
CS327_STATUS = "SEMANTIC_PUBLICATION_EXECUTION_EVIDENCE_REQUIRED"
SCHEMA = "pul7sar-phase18-semantic-publication-evidence-genuine-golden-checkpoint-v1"
STATUS = "GENUINE_GOLDEN_VISUAL_MATERIALIZED_AWAITING_PUBLICATION_READINESS"


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


def _bind(repo_root: Path, path: Path, code: str) -> dict[str, Any]:
    resolved = _inside_repo_file(repo_root, path, code)
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {
        "repository_relative_path": resolved.relative_to(repo_root.resolve()).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


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


def _assert_same_binding(
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


def continue_semantic_publication_evidence_to_genuine_golden(
    cs327_checkpoint_path: Path,
    cs284_receipt_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    repo_root = repo_root.resolve()
    checkpoint_path = _inside_repo_file(
        repo_root, cs327_checkpoint_path, "QWEN_CS328_CS327_INVALID"
    )
    cs284_path = _inside_repo_file(
        repo_root, cs284_receipt_path, "QWEN_CS328_CS284_INVALID"
    )
    output_dir = _inside_repo_output(repo_root, output_dir, "QWEN_CS328_OUTPUT_INVALID")
    cs327 = _read_json(checkpoint_path, "QWEN_CS328_CS327_INVALID")

    if cs327.get("schema") != CS327_SCHEMA:
        raise ValueError("QWEN_CS328_CS327_SCHEMA_DRIFT")
    if cs327.get("status") != CS327_STATUS:
        raise ValueError("QWEN_CS328_CS327_STATE_INVALID")
    if cs327.get("authoritative") is not False:
        raise ValueError("QWEN_CS328_CS327_AUTHORITY_DRIFT")
    expected_cs327 = {
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_execution_requested": True,
        "semantic_publication_gate_executed": False,
        "semantic_publication_allowed": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    for field, value in expected_cs327.items():
        if cs327.get(field) is not value:
            raise ValueError(f"QWEN_CS328_CS327_STATE_DRIFT:{field}")

    story = cs327.get("story_snapshot_sha256")
    if not isinstance(story, str) or len(story) != 64:
        raise ValueError("QWEN_CS328_STORY_SHA_INVALID")
    composed = cs327.get("composed_candidate_png")
    if not isinstance(composed, Mapping):
        raise ValueError("QWEN_CS328_COMPOSED_BINDING_INVALID")
    _verify_bound_png(repo_root, composed, "QWEN_CS328_COMPOSED_PNG_INVALID")

    cs283_path = _resolve_checkpoint_receipt(
        repo_root, cs327, "cs283_receipt", "QWEN_CS328_CS283_PATH_INVALID"
    )
    cs283 = verify_semantic_publication_execution_request(cs283_path, repo_root=repo_root)
    if cs283.get("schema") != CS283_SCHEMA:
        raise ValueError("QWEN_CS328_CS283_SCHEMA_DRIFT")
    if cs283.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS328_CS283_CROSS_STORY")
    cs283_png = cs283.get("composed_candidate_png")
    if not isinstance(cs283_png, Mapping):
        raise ValueError("QWEN_CS328_CS283_COMPOSED_BINDING_INVALID")
    _assert_same_binding(composed, cs283_png, "QWEN_CS328_CS283_COMPOSED_BYTES_DRIFT")

    # Verification replays the repository SemanticPublicationGate from the bound
    # evidence. No external `allowed` flag is trusted by this continuation.
    cs284 = verify_semantic_publication_execution(cs284_path, repo_root=repo_root)
    if cs284.get("schema") != CS284_SCHEMA:
        raise ValueError("QWEN_CS328_CS284_SCHEMA_DRIFT")
    if cs284.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS328_CS284_CROSS_STORY")
    cs284_png = cs284.get("composed_candidate_png")
    if not isinstance(cs284_png, Mapping):
        raise ValueError("QWEN_CS328_CS284_COMPOSED_BINDING_INVALID")
    _assert_same_binding(composed, cs284_png, "QWEN_CS328_CS284_COMPOSED_BYTES_DRIFT")

    source_cs283 = cs284.get("source_cs283_semantic_publication_request")
    if not isinstance(source_cs283, Mapping):
        raise ValueError("QWEN_CS328_CS284_CS283_BINDING_INVALID")
    exact_cs283_binding = _bind(repo_root, cs283_path, "QWEN_CS328_CS283_INVALID")
    _assert_same_binding(
        exact_cs283_binding,
        source_cs283,
        "QWEN_CS328_CS284_NOT_BOUND_TO_EXACT_CS283",
    )
    if source_cs283.get("receipt_sha256") != cs283.get("receipt_sha256"):
        raise ValueError("QWEN_CS328_CS284_CS283_RECEIPT_DRIFT")

    if cs284.get("semantic_publication_gate_executed") is not True:
        raise ValueError("QWEN_CS328_SEMANTIC_PUBLICATION_GATE_NOT_EXECUTED")
    if cs284.get("semantic_publication_allowed") is not True:
        raise ValueError("QWEN_CS328_SEMANTIC_PUBLICATION_REJECTED")
    failures = cs284.get("semantic_publication_failures")
    if not isinstance(failures, list) or failures:
        raise ValueError("QWEN_CS328_SEMANTIC_PUBLICATION_FAILURE_STATE_INVALID")
    for field in ("genuine_golden_png_created", "publication_ready"):
        if cs284.get(field) is not False:
            raise ValueError(f"QWEN_CS328_CS284_PREMATURE_AUTHORITY:{field}")

    # Defensive no-network posture. CS285 is a deterministic exact-byte operation.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs285_dir = output_dir / "cs285"
    cs285_path = materialize_genuine_golden_visual(
        cs284_path, cs285_dir, repo_root=repo_root
    )
    cs285 = verify_genuine_golden_materialization(cs285_path, repo_root=repo_root)
    if cs285.get("schema") != CS285_SCHEMA:
        raise ValueError("QWEN_CS328_CS285_SCHEMA_DRIFT")
    if cs285.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS328_CS285_CROSS_STORY")
    source_png = cs285.get("source_composed_candidate_png")
    golden_png = cs285.get("genuine_golden_visual_png")
    if not isinstance(source_png, Mapping) or not isinstance(golden_png, Mapping):
        raise ValueError("QWEN_CS328_CS285_PNG_BINDING_INVALID")
    _assert_same_binding(composed, source_png, "QWEN_CS328_CS285_SOURCE_BYTES_DRIFT")
    if golden_png.get("sha256") != composed.get("sha256"):
        raise ValueError("QWEN_CS328_CS285_GOLDEN_SHA_DRIFT")
    if golden_png.get("byte_size") != composed.get("byte_size"):
        raise ValueError("QWEN_CS328_CS285_GOLDEN_SIZE_DRIFT")
    _verify_bound_png(repo_root, golden_png, "QWEN_CS328_GOLDEN_PNG_INVALID")

    expected_cs285 = {
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": False,
    }
    for field, value in expected_cs285.items():
        if cs285.get(field) is not value:
            raise ValueError(f"QWEN_CS328_CS285_STATE_DRIFT:{field}")

    checkpoint: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "authoritative": False,
        "story_snapshot_sha256": story,
        "candidate_png": cs327.get("candidate_png"),
        "source_composed_candidate_png": dict(composed),
        "genuine_golden_visual_png": dict(golden_png),
        "cs327_checkpoint": checkpoint_path.relative_to(repo_root).as_posix(),
        "cs283_receipt": cs283_path.relative_to(repo_root).as_posix(),
        "cs284_receipt": cs284_path.relative_to(repo_root).as_posix(),
        "cs285_receipt": cs285_path.relative_to(repo_root).as_posix(),
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": False,
        "policy": {
            "preexisting_cs284_required": True,
            "cs284_replayed_through_repository_semantic_publication_gate": True,
            "exact_cs327_selected_cs283_required": True,
            "exact_story_and_composed_png_bytes_preserved": True,
            "cs284_rejection_cannot_materialize_golden": True,
            "cs285_materialization_is_exact_byte_copy_only": True,
            "no_pixel_generation_or_mutation_by_this_checkpoint": True,
            "cs286_publication_readiness_not_executed": True,
            "publication_ready_remains_closed": True,
            "offline_local_only_posture_preserved": True,
        },
    }
    checkpoint_out = output_dir / "genuine_golden_checkpoint.json"
    tmp = output_dir / ".genuine_golden_checkpoint.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(checkpoint, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, checkpoint_out)
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise
    return checkpoint_out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs327-checkpoint", required=True, type=Path)
    parser.add_argument("--cs284-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path("."), type=Path)
    args = parser.parse_args()
    path = continue_semantic_publication_evidence_to_genuine_golden(
        args.cs327_checkpoint,
        args.cs284_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
