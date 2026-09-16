#!/usr/bin/env python3
"""Execute one exact CS270 composition runner and immediately byte-admit its output.

Change Set 321 closes the operator wiring gap between CS270, CS271, and CS272.
It requires an explicit repository-local Python runner source and top-level
entrypoint, loads that exact source, delegates composition to the existing
CS271 one-shot boundary, independently re-verifies CS271, then admits the exact
resulting composed PNG through CS272 and independently re-verifies CS272.

It does not invent composition inputs, approve the visual, grant semantic or
human authority, create a Golden visual, or publish anything.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Callable, Mapping

from engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution import (
    SCHEMA as CS271_SCHEMA,
    execute_one_shot_composition,
    verify_one_shot_composition_execution,
)
from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    SCHEMA as CS272_SCHEMA,
    admit_composed_candidate_bytes,
    verify_composed_candidate_byte_admission,
)

SCHEMA = "pul7sar-phase18-bound-composition-execution-and-admission-checkpoint-v1"
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


def _assert_downstream_closed(value: Mapping[str, Any], prefix: str) -> None:
    for field in _DOWNSTREAM_FALSE:
        if value.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _load_exact_runner(
    repo_root: Path,
    runner_source_path: Path,
    runner_entrypoint: str,
) -> tuple[ModuleType, Callable[[Mapping[str, Any], Path, Path], None]]:
    runner_path = _inside_repo_file(
        repo_root,
        runner_source_path,
        "QWEN_BOUND_COMPOSITION_RUNNER_SOURCE_INVALID",
    )
    if runner_path.suffix != ".py":
        raise ValueError("QWEN_BOUND_COMPOSITION_RUNNER_SOURCE_NOT_PYTHON")
    if (
        not isinstance(runner_entrypoint, str)
        or not runner_entrypoint
        or runner_entrypoint == "<lambda>"
        or "." in runner_entrypoint
    ):
        raise ValueError("QWEN_BOUND_COMPOSITION_RUNNER_ENTRYPOINT_INVALID")

    module_name = (
        "_pul7sar_phase18_bound_renderer_"
        + runner_path.stem.replace("-", "_")
        + "_"
        + str(abs(hash(runner_path.as_posix())))
    )
    spec = importlib.util.spec_from_file_location(module_name, runner_path)
    if spec is None or spec.loader is None:
        raise ValueError("QWEN_BOUND_COMPOSITION_RUNNER_IMPORT_SPEC_INVALID")
    module = importlib.util.module_from_spec(spec)

    # Keep model/data hubs offline during import as well as execution.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise

    compose_fn = getattr(module, runner_entrypoint, None)
    if not callable(compose_fn):
        raise ValueError("QWEN_BOUND_COMPOSITION_RUNNER_ENTRYPOINT_MISSING")
    return module, compose_fn


def execute_bound_composition_and_admit(
    cs270_receipt_path: Path,
    runner_source_path: Path,
    runner_entrypoint: str,
    runner_id: str,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    """Execute CS271 once, replay it, then admit the exact bytes through CS272."""
    repo_root = repo_root.resolve()
    cs270_receipt_path = _inside_repo_file(
        repo_root,
        cs270_receipt_path,
        "QWEN_BOUND_COMPOSITION_CS270_INVALID",
    )
    runner_source_path = _inside_repo_file(
        repo_root,
        runner_source_path,
        "QWEN_BOUND_COMPOSITION_RUNNER_SOURCE_INVALID",
    )
    output_dir = _inside_repo_output(
        repo_root,
        output_dir,
        "QWEN_BOUND_COMPOSITION_OUTPUT_INVALID",
    )
    if not isinstance(runner_id, str) or not runner_id.strip():
        raise ValueError("QWEN_BOUND_COMPOSITION_RUNNER_ID_INVALID")

    _, compose_fn = _load_exact_runner(
        repo_root,
        runner_source_path,
        runner_entrypoint,
    )

    output_dir.mkdir(mode=0o700)
    cs271_dir = output_dir / "cs271"
    cs272_dir = output_dir / "cs272"

    cs271_run = execute_one_shot_composition(
        cs270_receipt_path,
        cs271_dir,
        repo_root=repo_root,
        runner_source_path=runner_source_path,
        runner_id=runner_id.strip(),
        compose_fn=compose_fn,
    )
    cs271 = verify_one_shot_composition_execution(
        cs271_run.receipt_path,
        repo_root=repo_root,
    )
    if cs271.get("schema") != CS271_SCHEMA or cs271.get("composition_executed") is not True:
        raise ValueError("QWEN_BOUND_COMPOSITION_CS271_NOT_EXECUTED")
    _assert_downstream_closed(cs271, "QWEN_BOUND_COMPOSITION_CS271")
    if cs271.get("runner_entrypoint") != runner_entrypoint:
        raise ValueError("QWEN_BOUND_COMPOSITION_RUNNER_ENTRYPOINT_DRIFT")

    cs272_run = admit_composed_candidate_bytes(
        cs271_run.receipt_path,
        cs272_dir,
        repo_root=repo_root,
    )
    cs272 = verify_composed_candidate_byte_admission(
        cs272_run.receipt_path,
        repo_root=repo_root,
    )
    if (
        cs272.get("schema") != CS272_SCHEMA
        or cs272.get("composition_executed") is not True
        or cs272.get("composed_candidate_bytes_admitted_for_post_composition_qa") is not True
    ):
        raise ValueError("QWEN_BOUND_COMPOSITION_CS272_NOT_ADMITTED")
    _assert_downstream_closed(cs272, "QWEN_BOUND_COMPOSITION_CS272")

    if cs271.get("story_snapshot_sha256") != cs272.get("story_snapshot_sha256"):
        raise ValueError("QWEN_BOUND_COMPOSITION_CROSS_STORY")
    if cs271.get("candidate_png") != cs272.get("source_candidate_png"):
        raise ValueError("QWEN_BOUND_COMPOSITION_SOURCE_CANDIDATE_DRIFT")
    if cs271.get("composed_candidate_png") != cs272.get("composed_candidate_png"):
        raise ValueError("QWEN_BOUND_COMPOSITION_COMPOSED_BYTES_DRIFT")

    checkpoint = {
        "schema": SCHEMA,
        "status": "COMPOSED_CANDIDATE_BYTES_ADMITTED_FOR_POST_COMPOSITION_QA",
        "authoritative": False,
        "story_snapshot_sha256": cs272.get("story_snapshot_sha256"),
        "runner_id": cs271.get("runner_id"),
        "runner_entrypoint": cs271.get("runner_entrypoint"),
        "candidate_png": cs272.get("source_candidate_png"),
        "composed_candidate_png": cs272.get("composed_candidate_png"),
        "cs271_receipt": cs271_run.receipt_path.resolve().relative_to(repo_root).as_posix(),
        "cs272_receipt": cs272_run.receipt_path.resolve().relative_to(repo_root).as_posix(),
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "explicit_repository_runner_required": True,
            "exact_top_level_entrypoint_required": True,
            "cs271_must_reverify": True,
            "cs272_must_reverify": True,
            "exact_cs271_output_must_feed_cs272": True,
            "checkpoint_is_non_authoritative": True,
            "byte_admission_is_not_visual_approval": True,
            "no_layer_input_synthesis": True,
        },
    }
    checkpoint_path = output_dir / "bound_composition_execution_checkpoint.json"
    tmp = output_dir / ".bound_composition_execution_checkpoint.json.tmp"
    with tmp.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(checkpoint, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, checkpoint_path)
    return checkpoint_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Execute one exact repository-bound CS270 composition runner, replay CS271, "
            "and byte-admit the exact result through CS272."
        )
    )
    parser.add_argument("--cs270-receipt", required=True, type=Path)
    parser.add_argument("--runner-source", required=True, type=Path)
    parser.add_argument("--runner-entrypoint", required=True)
    parser.add_argument("--runner-id", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    checkpoint_path = execute_bound_composition_and_admit(
        args.cs270_receipt,
        args.runner_source,
        args.runner_entrypoint,
        args.runner_id,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    print(checkpoint_path)
    print(f"status={payload['status']}")
    print(f"composition_executed={payload['composition_executed']}")
    print(
        "composed_candidate_bytes_admitted_for_post_composition_qa="
        f"{payload['composed_candidate_bytes_admitted_for_post_composition_qa']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
