#!/usr/bin/env python3
"""CS329: verify one exact CS328 Genuine Golden checkpoint and execute CS286 readiness.

This continuation performs no image generation, mutation, publication, upload, or network
fallback. It consumes the exact CS285 receipt selected by CS328, independently replays
CS285, proves story and byte identity against the checkpoint, invokes the existing CS286
publication-readiness authority, then independently replays CS286. Publication readiness
therefore remains impossible unless the repository's exact Genuine Golden lineage is valid.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_genuine_golden_materialization import (
    SCHEMA as CS285_SCHEMA,
    verify_genuine_golden_materialization,
)
from engine.intelligence.qwen_image_genuine_golden_publication_readiness import (
    SCHEMA as CS286_SCHEMA,
    finalize_genuine_golden_publication_readiness,
    verify_genuine_golden_publication_readiness,
)

CS328_SCHEMA = "pul7sar-phase18-semantic-publication-evidence-genuine-golden-checkpoint-v1"
CS328_STATUS = "GENUINE_GOLDEN_VISUAL_MATERIALIZED_AWAITING_PUBLICATION_READINESS"
SCHEMA = "pul7sar-phase18-genuine-golden-publication-readiness-checkpoint-v1"
STATUS = "GENUINE_GOLDEN_VISUAL_PUBLICATION_READY"


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


def _assert_same_binding(
    expected: Mapping[str, Any], actual: Mapping[str, Any], code: str
) -> None:
    for field in ("repository_relative_path", "sha256", "byte_size"):
        if expected.get(field) != actual.get(field):
            raise ValueError(f"{code}:{field}")


def _verify_bound_file(repo_root: Path, binding: Mapping[str, Any], code: str) -> Path:
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


def continue_genuine_golden_to_publication_readiness(
    cs328_checkpoint_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
) -> Path:
    repo_root = repo_root.resolve()
    checkpoint_path = _inside_repo_file(
        repo_root, cs328_checkpoint_path, "QWEN_CS329_CS328_INVALID"
    )
    output_dir = _inside_repo_output(repo_root, output_dir, "QWEN_CS329_OUTPUT_INVALID")
    cs328 = _read_json(checkpoint_path, "QWEN_CS329_CS328_INVALID")

    if cs328.get("schema") != CS328_SCHEMA:
        raise ValueError("QWEN_CS329_CS328_SCHEMA_DRIFT")
    if cs328.get("status") != CS328_STATUS:
        raise ValueError("QWEN_CS329_CS328_STATE_INVALID")
    if cs328.get("authoritative") is not False:
        raise ValueError("QWEN_CS329_CS328_AUTHORITY_DRIFT")

    expected_cs328 = {
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": False,
    }
    for field, value in expected_cs328.items():
        if cs328.get(field) is not value:
            raise ValueError(f"QWEN_CS329_CS328_STATE_DRIFT:{field}")

    story = cs328.get("story_snapshot_sha256")
    if not isinstance(story, str) or len(story) != 64:
        raise ValueError("QWEN_CS329_STORY_SHA_INVALID")

    source_png = cs328.get("source_composed_candidate_png")
    golden_png = cs328.get("genuine_golden_visual_png")
    if not isinstance(source_png, Mapping) or not isinstance(golden_png, Mapping):
        raise ValueError("QWEN_CS329_CS328_PNG_BINDING_INVALID")
    source_path = _verify_bound_file(repo_root, source_png, "QWEN_CS329_SOURCE_PNG_INVALID")
    golden_path = _verify_bound_file(repo_root, golden_png, "QWEN_CS329_GOLDEN_PNG_INVALID")
    if source_path.read_bytes() != golden_path.read_bytes():
        raise ValueError("QWEN_CS329_CS328_BYTE_IDENTITY_FAILED")
    if source_png.get("sha256") != golden_png.get("sha256"):
        raise ValueError("QWEN_CS329_CS328_GOLDEN_SHA_DRIFT")
    if source_png.get("byte_size") != golden_png.get("byte_size"):
        raise ValueError("QWEN_CS329_CS328_GOLDEN_SIZE_DRIFT")

    cs285_path = _resolve_checkpoint_receipt(
        repo_root, cs328, "cs285_receipt", "QWEN_CS329_CS285_PATH_INVALID"
    )
    cs285 = verify_genuine_golden_materialization(cs285_path, repo_root=repo_root)
    if cs285.get("schema") != CS285_SCHEMA:
        raise ValueError("QWEN_CS329_CS285_SCHEMA_DRIFT")
    if cs285.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS329_CS285_CROSS_STORY")
    cs285_source = cs285.get("source_composed_candidate_png")
    cs285_golden = cs285.get("genuine_golden_visual_png")
    if not isinstance(cs285_source, Mapping) or not isinstance(cs285_golden, Mapping):
        raise ValueError("QWEN_CS329_CS285_PNG_BINDING_INVALID")
    _assert_same_binding(source_png, cs285_source, "QWEN_CS329_CS285_SOURCE_BYTES_DRIFT")
    _assert_same_binding(golden_png, cs285_golden, "QWEN_CS329_CS285_GOLDEN_BYTES_DRIFT")

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
            raise ValueError(f"QWEN_CS329_CS285_STATE_DRIFT:{field}")

    # Defensive no-network posture. CS286 is deterministic receipt verification only.
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    output_dir.mkdir(mode=0o700)
    cs286_dir = output_dir / "cs286"
    cs286_path = finalize_genuine_golden_publication_readiness(
        cs285_path, cs286_dir, repo_root=repo_root
    )
    cs286 = verify_genuine_golden_publication_readiness(cs286_path, repo_root=repo_root)
    if cs286.get("schema") != CS286_SCHEMA:
        raise ValueError("QWEN_CS329_CS286_SCHEMA_DRIFT")
    if cs286.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_CS329_CS286_CROSS_STORY")

    cs286_source = cs286.get("source_composed_candidate_png")
    cs286_golden = cs286.get("genuine_golden_visual_png")
    if not isinstance(cs286_source, Mapping) or not isinstance(cs286_golden, Mapping):
        raise ValueError("QWEN_CS329_CS286_PNG_BINDING_INVALID")
    _assert_same_binding(source_png, cs286_source, "QWEN_CS329_CS286_SOURCE_BYTES_DRIFT")
    _assert_same_binding(golden_png, cs286_golden, "QWEN_CS329_CS286_GOLDEN_BYTES_DRIFT")

    expected_cs286 = {
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": True,
    }
    for field, value in expected_cs286.items():
        if cs286.get(field) is not value:
            raise ValueError(f"QWEN_CS329_CS286_STATE_DRIFT:{field}")

    checkpoint: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "authoritative": False,
        "story_snapshot_sha256": story,
        "source_composed_candidate_png": dict(source_png),
        "genuine_golden_visual_png": dict(golden_png),
        "cs328_checkpoint": checkpoint_path.relative_to(repo_root).as_posix(),
        "cs285_receipt": cs285_path.relative_to(repo_root).as_posix(),
        "cs286_receipt": cs286_path.relative_to(repo_root).as_posix(),
        "composed_visual_approved": True,
        "semantic_approved": True,
        "semantic_publication_gate_executed": True,
        "semantic_publication_allowed": True,
        "byte_identity_preserved": True,
        "genuine_golden_png_created": True,
        "publication_ready": True,
        "publication_side_effect_executed": False,
        "policy": {
            "exact_cs328_selected_cs285_required": True,
            "cs285_independently_replayed": True,
            "cs286_independently_replayed": True,
            "exact_story_and_png_bytes_preserved": True,
            "pixel_mutation_forbidden": True,
            "publication_readiness_has_no_publish_side_effect": True,
            "no_generation_or_network_fallback": True,
            "checkpoint_is_non_authoritative_wrapper": True,
        },
    }
    checkpoint_out = output_dir / "publication_readiness_checkpoint.json"
    tmp = output_dir / ".publication_readiness_checkpoint.json.tmp"
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
    parser.add_argument("--cs328-checkpoint", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path("."), type=Path)
    args = parser.parse_args()
    path = continue_genuine_golden_to_publication_readiness(
        args.cs328_checkpoint, args.output_dir, repo_root=args.repo_root
    )
    print(path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
