"""Derive the only production inference invocation from a verified launch manifest.

CS295 removes manual duplication between the CS291/292 launch manifest and the
canonical inference command. Operators provide only the verified manifest and a new
repository-local output directory. Authorization, CS257 evidence, immutable snapshot,
and all inference settings are recovered from the manifest after full replay.

CS298 makes the CS297 aggregate preload host diagnostic mandatory at this launcher
edge. The canonical subprocess is never started while any observable static-readiness
or CS260 host-identity blocker remains. This is still a pre-model-load control: it does
not load Qwen, execute inference, create pixels, or grant semantic, visual-quality,
Golden, or publication authority.

CS299 additionally constrains the child process to the library-level offline envelope
used by the local-only Qwen path. The launcher still does not claim to provide an OS
network sandbox; instead it fail-closes the cost mode and forces Hugging Face Hub and
Transformers offline flags before the canonical subprocess starts, while the canonical
runtime continues to require ``local_files_only=True`` for the actual model load.

CS300 closes the successful-child trust gap. A zero subprocess return code is no longer
sufficient for launcher success: the launcher independently requires the exact canonical
candidate/receipt/provenance/postflight files and replays the CS293 launch-to-output
attestation before returning zero. The replay recursively revalidates the launch manifest,
local inference provenance, canonical inference receipt, and exact PNG bytes. No semantic,
visual-quality, Golden, human-review, or publication authority is granted here.

CS354 upgrades the launcher edge to require the inventory-bound launch verifier. The
exact already-local Qwen snapshot bytes are therefore replayed before the canonical
subprocess can start, while CS352/353 continue to recheck the same snapshot around
``from_pretrained`` itself.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

from .qwen_image_inventory_bound_launch_manifest import (
    verify_inventory_bound_gpu_host_launch_manifest,
)
from .qwen_image_preload_host_diagnostic import inspect_preload_host

REQUIRED_COST_MODE = "$0-local"
CANONICAL_TOOL = "tools/phase18_run_one_shot_canonical_inference.py"
OFFLINE_CHILD_ENVIRONMENT = {
    "HF_HUB_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
}
SUCCESS_OUTPUT_FILES = (
    "canonical_candidate.png",
    "canonical_inference_receipt.json",
    "local_inference_provenance.json",
    "launch_to_output_attestation.json",
)


class QwenPreloadHostNotReadyError(RuntimeError):
    """Raised before the canonical subprocess when the aggregate preload check blocks."""

    def __init__(self, blockers: Sequence[str]) -> None:
        normalized = tuple(sorted(set(str(item) for item in blockers if str(item))))
        self.blockers = normalized
        detail = ",".join(normalized) if normalized else "unspecified"
        super().__init__(f"QWEN_MANIFEST_EXECUTION_PRELOAD_HOST_NOT_READY:{detail}")


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


def _existing_repo_output(path: Path, root: Path) -> Path:
    candidate = path if path.is_absolute() else root / path
    if candidate.is_symlink():
        raise ValueError("QWEN_MANIFEST_EXECUTION_POSTFLIGHT_OUTPUT_SYMLINK")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("QWEN_MANIFEST_EXECUTION_POSTFLIGHT_OUTPUT_OUTSIDE_REPOSITORY") from exc
    if not resolved.is_dir():
        raise ValueError("QWEN_MANIFEST_EXECUTION_POSTFLIGHT_OUTPUT_MISSING")
    return resolved


def build_manifest_bound_execution_argv(
    launch_manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    python_executable: str | None = None,
) -> tuple[str, ...]:
    """Return a shell-free argv derived entirely from a replayed launch manifest."""
    root = repo_root.resolve()
    manifest = verify_inventory_bound_gpu_host_launch_manifest(
        launch_manifest_path, repo_root=root
    )
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


def build_offline_subprocess_environment(
    base_environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return the canonical child environment with zero-cost/offline flags fail-closed.

    This is intentionally a library-level offline envelope, not an operating-system
    network sandbox. The downstream model loader remains responsible for enforcing
    the stronger local artifact contract via ``local_files_only=True`` and the pinned
    immutable snapshot path.
    """
    source = os.environ if base_environment is None else base_environment
    environment = {str(key): str(value) for key, value in source.items()}
    if environment.get("PUL7SAR_PHASE18_COST_MODE", "") != REQUIRED_COST_MODE:
        raise ValueError("QWEN_MANIFEST_EXECUTION_ZERO_COST_MODE_NOT_LOCKED")
    environment["PUL7SAR_PHASE18_COST_MODE"] = REQUIRED_COST_MODE
    environment.update(OFFLINE_CHILD_ENVIRONMENT)
    return environment


def require_preload_host_ready(
    launch_manifest_path: Path,
    *,
    repo_root: Path,
) -> Mapping[str, Any]:
    """Replay CS297 and fail closed before any canonical subprocess is started."""
    report = inspect_preload_host(launch_manifest_path, repo_root=repo_root.resolve())
    blockers = report.get("blockers")
    if not isinstance(blockers, list) or not all(isinstance(item, str) for item in blockers):
        raise ValueError("QWEN_MANIFEST_EXECUTION_PRELOAD_DIAGNOSTIC_INVALID")
    ready = report.get("ready_for_model_load_attempt")
    if ready is not True or blockers:
        raise QwenPreloadHostNotReadyError(blockers)

    forbidden_true = (
        "model_load_attempted",
        "inference_executed",
        "semantic_approved",
        "human_visual_review_approved",
        "golden_quality_approved",
        "genuine_golden_png_created",
        "publication_ready",
    )
    if any(report.get(field) is not False for field in forbidden_true):
        raise ValueError("QWEN_MANIFEST_EXECUTION_PRELOAD_DIAGNOSTIC_AUTHORITY_INVALID")
    return report


def verify_successful_canonical_output(
    output_dir: Path,
    *,
    repo_root: Path,
) -> Mapping[str, Any]:
    """Independently replay the exact successful canonical postflight bundle.

    This function is intentionally called only after a child process returns zero. It
    converts the child return code from a claim into a locally replayed fact by checking
    the expected files and invoking the CS293 verifier, which recursively revalidates the
    launch manifest, provenance, canonical receipt, and exact candidate PNG bytes.
    """
    root = repo_root.resolve()
    output = _existing_repo_output(output_dir, root)
    for filename in SUCCESS_OUTPUT_FILES:
        path = output / filename
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"QWEN_MANIFEST_EXECUTION_POSTFLIGHT_FILE_MISSING:{filename}")

    from .qwen_image_launch_to_output_attestation import verify_launch_to_output_attestation

    verified = verify_launch_to_output_attestation(
        output / "launch_to_output_attestation.json",
        repo_root=root,
    )
    forbidden_true = (
        "semantic_approved",
        "human_visual_review_approved",
        "golden_quality_approved",
        "genuine_golden_png_created",
        "publication_ready",
    )
    if any(verified.get(field) is not False for field in forbidden_true):
        raise ValueError("QWEN_MANIFEST_EXECUTION_POSTFLIGHT_AUTHORITY_INVALID")
    if verified.get("genuine_canonical_inference_executed") is not True:
        raise ValueError("QWEN_MANIFEST_EXECUTION_POSTFLIGHT_GENUINE_INFERENCE_MISSING")
    return verified


def execute_manifest_bound_inference(
    launch_manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    python_executable: str | None = None,
) -> int:
    """Run the preload/offline controls and independently replay successful output."""
    import subprocess

    argv: Sequence[str] = build_manifest_bound_execution_argv(
        launch_manifest_path,
        output_dir,
        repo_root=repo_root,
        python_executable=python_executable,
    )
    require_preload_host_ready(launch_manifest_path, repo_root=repo_root)
    child_environment = build_offline_subprocess_environment()
    completed = subprocess.run(
        tuple(argv),
        cwd=str(repo_root.resolve()),
        check=False,
        env=child_environment,
    )
    code = int(completed.returncode)
    if code != 0:
        return code
    verify_successful_canonical_output(output_dir, repo_root=repo_root)
    return 0
