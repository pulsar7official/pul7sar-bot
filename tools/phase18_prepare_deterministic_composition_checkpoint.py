#!/usr/bin/env python3
"""Prepare deterministic composition inputs after an approved CS268 candidate.

Change Set 319 deliberately stops before composition execution.  It binds an
explicit operator/repository composition manifest through CS269 and, when an
explicit deterministic payload manifest is supplied, binds those payload files
through CS270.  It never invents editorial copy, brand assets, sport geometry,
renderer payloads, or any downstream approval.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    SCHEMA as CS270_SCHEMA,
    build_composition_execution_preflight,
    verify_composition_execution_preflight,
)
from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    SCHEMA as CS269_SCHEMA,
    build_deterministic_composition_request,
    verify_deterministic_composition_request,
)
from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    SCHEMA as CS268_SCHEMA,
    verify_canonical_candidate_generated_layer_qa,
)

SCHEMA = "pul7sar-phase18-deterministic-composition-preparation-checkpoint-v1"
_DOWNSTREAM_FALSE = (
    "composition_executed",
    "composed_visual_approved",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _assert_downstream_closed(receipt: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _inside_repo(repo_root: Path, path: Path, code: str) -> Path:
    root = repo_root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(code) from exc
    return resolved


def _relative(repo_root: Path, path: Path, code: str) -> str:
    resolved = _inside_repo(repo_root, path, code)
    if not resolved.is_file() or resolved.is_symlink():
        raise ValueError(code)
    return resolved.relative_to(repo_root.resolve()).as_posix()


def _write_checkpoint(path: Path, payload: Mapping[str, Any]) -> None:
    tmp = path.with_name(f".{path.name}.tmp")
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(payload), ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def prepare_deterministic_composition_checkpoint(
    cs268_receipt_path: Path,
    composition_manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    payload_manifest_path: Path | None = None,
) -> Path:
    repo_root = repo_root.resolve()
    output_dir = _inside_repo(repo_root, output_dir, "QWEN_COMPOSITION_PREPARATION_OUTPUT_OUTSIDE_REPOSITORY")
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_COMPOSITION_PREPARATION_OUTPUT_INVALID")

    cs268 = verify_canonical_candidate_generated_layer_qa(cs268_receipt_path, repo_root=repo_root)
    if cs268.get("schema") != CS268_SCHEMA or cs268.get("generated_layer_qa_approved") is not True:
        raise ValueError("QWEN_COMPOSITION_PREPARATION_CS268_NOT_APPROVED")
    _assert_downstream_closed(cs268, "QWEN_COMPOSITION_PREPARATION_CS268")

    # These inputs must already exist inside the repository.  This checkpoint
    # never synthesizes editorial text, marks, geometry, or renderer payloads.
    _relative(repo_root, composition_manifest_path, "QWEN_COMPOSITION_PREPARATION_MANIFEST_INVALID")
    if payload_manifest_path is not None:
        _relative(repo_root, payload_manifest_path, "QWEN_COMPOSITION_PREPARATION_PAYLOAD_MANIFEST_INVALID")

    output_dir.mkdir(mode=0o700)
    cs269_dir = output_dir / "cs269"
    cs269_run = build_deterministic_composition_request(
        cs268_receipt_path,
        composition_manifest_path,
        cs269_dir,
        repo_root=repo_root,
    )
    cs269 = verify_deterministic_composition_request(cs269_run.receipt_path, repo_root=repo_root)
    if cs269.get("schema") != CS269_SCHEMA:
        raise ValueError("QWEN_COMPOSITION_PREPARATION_CS269_SCHEMA_DRIFT")
    _assert_downstream_closed(cs269, "QWEN_COMPOSITION_PREPARATION_CS269")

    cs270_receipt_path: Path | None = None
    cs270: dict[str, Any] | None = None
    if cs269.get("composition_request_ready") is True and payload_manifest_path is not None:
        cs270_dir = output_dir / "cs270"
        cs270_run = build_composition_execution_preflight(
            cs269_run.receipt_path,
            payload_manifest_path,
            cs270_dir,
            repo_root=repo_root,
        )
        cs270_receipt_path = cs270_run.receipt_path
        cs270 = verify_composition_execution_preflight(cs270_receipt_path, repo_root=repo_root)
        if cs270.get("schema") != CS270_SCHEMA:
            raise ValueError("QWEN_COMPOSITION_PREPARATION_CS270_SCHEMA_DRIFT")
        _assert_downstream_closed(cs270, "QWEN_COMPOSITION_PREPARATION_CS270")

    cs269_ready = cs269.get("composition_request_ready") is True
    cs270_ready = bool(cs270 is not None and cs270.get("composition_execution_ready") is True)
    if not cs269_ready:
        status = "COMPOSITION_INPUT_MANIFEST_BLOCKED"
        blockers = list(cs269.get("blockers") or [])
    elif payload_manifest_path is None:
        status = "DETERMINISTIC_PAYLOAD_MANIFEST_REQUIRED"
        blockers = ["deterministic_payload_manifest_not_supplied"]
    elif not cs270_ready:
        status = "DETERMINISTIC_PAYLOAD_BINDING_BLOCKED"
        blockers = list((cs270 or {}).get("blockers") or [])
    else:
        status = "COMPOSITION_EXECUTION_PREFLIGHT_READY"
        blockers = []

    story_sha = cs268.get("story_snapshot_sha256")
    candidate = cs268.get("candidate_png")
    if cs269.get("story_snapshot_sha256") != story_sha or cs269.get("candidate_png") != candidate:
        raise ValueError("QWEN_COMPOSITION_PREPARATION_CS269_LINEAGE_DRIFT")
    if cs270 is not None and (
        cs270.get("story_snapshot_sha256") != story_sha or cs270.get("candidate_png") != candidate
    ):
        raise ValueError("QWEN_COMPOSITION_PREPARATION_CS270_LINEAGE_DRIFT")

    checkpoint = {
        "schema": SCHEMA,
        "status": status,
        "authoritative": False,
        "story_snapshot_sha256": story_sha,
        "candidate_png": candidate,
        "source_cs268_receipt": _relative(repo_root, cs268_receipt_path, "QWEN_COMPOSITION_PREPARATION_CS268_INVALID"),
        "source_composition_manifest": _relative(repo_root, composition_manifest_path, "QWEN_COMPOSITION_PREPARATION_MANIFEST_INVALID"),
        "source_payload_manifest": (
            _relative(repo_root, payload_manifest_path, "QWEN_COMPOSITION_PREPARATION_PAYLOAD_MANIFEST_INVALID")
            if payload_manifest_path is not None
            else None
        ),
        "cs269_receipt": _relative(repo_root, cs269_run.receipt_path, "QWEN_COMPOSITION_PREPARATION_CS269_INVALID"),
        "cs270_receipt": (
            _relative(repo_root, cs270_receipt_path, "QWEN_COMPOSITION_PREPARATION_CS270_INVALID")
            if cs270_receipt_path is not None
            else None
        ),
        "composition_request_ready": cs269_ready,
        "composition_execution_ready": cs270_ready,
        "blockers": blockers,
        "composition_executed": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "explicit_repository_composition_manifest_required": True,
            "explicit_repository_payload_manifest_required_for_cs270": True,
            "missing_or_drifting_inputs_fail_closed": True,
            "checkpoint_is_non_authoritative": True,
            "checkpoint_never_executes_composition": True,
            "checkpoint_never_synthesizes_layer_inputs": True,
        },
    }
    checkpoint_path = output_dir / "composition_preparation_checkpoint.json"
    _write_checkpoint(checkpoint_path, checkpoint)
    return checkpoint_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare and replay Phase 18 CS269/CS270 without executing composition."
    )
    parser.add_argument("--cs268-receipt", required=True, type=Path)
    parser.add_argument("--composition-manifest", required=True, type=Path)
    parser.add_argument("--payload-manifest", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    checkpoint_path = prepare_deterministic_composition_checkpoint(
        args.cs268_receipt,
        args.composition_manifest,
        args.output_dir,
        repo_root=args.repo_root,
        payload_manifest_path=args.payload_manifest,
    )
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    print(checkpoint_path)
    print(f"status={payload['status']}")
    print(f"composition_request_ready={payload['composition_request_ready']}")
    print(f"composition_execution_ready={payload['composition_execution_ready']}")
    for blocker in payload["blockers"]:
        print(f"blocker={blocker}")
    return 0 if payload["composition_execution_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
