"""Derive the only production inference invocation from a verified launch manifest.

CS295 removes manual duplication between the CS291/292 launch manifest and the
canonical inference command. Operators provide only the verified manifest and a new
repository-local output directory. Authorization, CS257 evidence, immutable snapshot,
and all inference settings are recovered from the manifest after full replay.

This module does not import or load Qwen, execute inference, create pixels, or grant any
semantic, visual-quality, Golden, or publication authority.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

from .qwen_image_gpu_host_launch_manifest import verify_gpu_host_launch_manifest

REQUIRED_COST_MODE = "$0-local"
CANONICAL_TOOL = "tools/phase18_run_one_shot_canonical_inference.py"


def _mapping(value: Any, code: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(code)
    return value


def _relative(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError(code)
    return value


def _new_repo_output(path: Path, root: Path) -> Path:
    candidate = path if path.is_absolute() else root / path
    if candidate.exists() or candidate.is_symlink():
        raise ValueError("QWEN_MANIFEST_EXECUTION_OUTPUT_ALREADY_EXISTS")
    parent = candidate.parent.resolve()
    try:
        parent.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("QWEN_MANIFEST_EXECUTION_OUTPUT_OUTSIDE_REPOSITORY") from exc
    if not parent.is_dir():
        raise ValueError("QWEN_MANIFEST_EXECUTION_OUTPUT_PARENT_INVALID")
    return parent / candidate.name


def build_manifest_bound_execution_argv(
    launch_manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    python_executable: str | None = None,
) -> tuple[str, ...]:
    """Return a shell-free argv derived entirely from a replayed launch manifest."""
    root = repo_root.resolve()
    manifest = verify_gpu_host_launch_manifest(launch_manifest_path, repo_root=root)
    if os.environ.get("PUL7SAR_PHASE18_COST_MODE", "") != REQUIRED_COST_MODE:
        raise ValueError("QWEN_MANIFEST_EXECUTION_ZERO_COST_MODE_NOT_LOCKED")

    authorization = _mapping(
        manifest.get("authorization"), "QWEN_MANIFEST_EXECUTION_AUTHORIZATION_INVALID"
    )
    cs257 = _mapping(
        manifest.get("cs257_evidence"), "QWEN_MANIFEST_EXECUTION_CS257_INVALID"
    )
    snapshot = _mapping(
        manifest.get("snapshot"), "QWEN_MANIFEST_EXECUTION_SNAPSHOT_INVALID"
    )
    settings = _mapping(
        manifest.get("inference_settings"), "QWEN_MANIFEST_EXECUTION_SETTINGS_INVALID"
    )

    auth_relative = _relative(
        authorization.get("repository_relative_path"),
        "QWEN_MANIFEST_EXECUTION_AUTHORIZATION_PATH_INVALID",
    )
    cs257_relative = _relative(
        cs257.get("repository_relative_directory"),
        "QWEN_MANIFEST_EXECUTION_CS257_PATH_INVALID",
    )
    snapshot_path = snapshot.get("resolved_path")
    if not isinstance(snapshot_path, str) or not snapshot_path:
        raise ValueError("QWEN_MANIFEST_EXECUTION_SNAPSHOT_PATH_INVALID")

    output = _new_repo_output(output_dir, root)
    tool = root / CANONICAL_TOOL
    if not tool.is_file() or tool.is_symlink():
        raise ValueError("QWEN_MANIFEST_EXECUTION_CANONICAL_TOOL_INVALID")

    width = settings.get("width")
    height = settings.get("height")
    seed = settings.get("seed")
    steps = settings.get("num_inference_steps")
    guidance = settings.get("guidance_scale")
    if not isinstance(width, int) or not isinstance(height, int) or not isinstance(seed, int):
        raise ValueError("QWEN_MANIFEST_EXECUTION_SETTINGS_INVALID")
    if not isinstance(steps, int) or not isinstance(guidance, (int, float)):
        raise ValueError("QWEN_MANIFEST_EXECUTION_SETTINGS_INVALID")

    manifest_file = launch_manifest_path if launch_manifest_path.is_absolute() else root / launch_manifest_path
    executable = python_executable or sys.executable
    return (
        executable,
        str(tool),
        "--launch-manifest", str(manifest_file.resolve()),
        "--authorization", str((root / auth_relative).resolve()),
        "--cs257-run-dir", str((root / cs257_relative).resolve()),
        "--snapshot-path", str(Path(snapshot_path).expanduser().resolve()),
        "--output-dir", str(output),
        "--repo-root", str(root),
        "--width", str(width),
        "--height", str(height),
        "--steps", str(steps),
        "--guidance-scale", str(float(guidance)),
        "--seed", str(seed),
    )


def execute_manifest_bound_inference(
    launch_manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    python_executable: str | None = None,
) -> int:
    """Execute the canonical CLI with a shell-free argv produced by the manifest."""
    import subprocess

    argv: Sequence[str] = build_manifest_bound_execution_argv(
        launch_manifest_path,
        output_dir,
        repo_root=repo_root,
        python_executable=python_executable,
    )
    completed = subprocess.run(tuple(argv), cwd=str(repo_root.resolve()), check=False)
    return int(completed.returncode)
