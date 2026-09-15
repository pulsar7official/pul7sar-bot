"""CS302: execute the canonical Qwen path and seal its downstream candidate handoff.

This module composes the already fail-closed manifest-bound launcher (CS295-CS300)
with the canonical candidate handoff seal (CS301). A zero inference exit code is not
considered a complete downstream handoff until the handoff artifact is built and
independently replay-verified. This layer grants no semantic, visual-quality, human,
Golden, or publication authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .qwen_image_canonical_candidate_handoff import (
    build_canonical_candidate_handoff,
    verify_canonical_candidate_handoff,
)
from .qwen_image_manifest_bound_execution import execute_manifest_bound_inference

CANONICAL_HANDOFF_FILENAME = "canonical_candidate_handoff.json"
DOWNSTREAM_FALSE = (
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "genuine_golden_png_created",
    "publication_ready",
)


def _assert_handoff_authority_closed(payload: Mapping[str, Any]) -> None:
    if payload.get("genuine_canonical_inference_executed") is not True:
        raise ValueError("QWEN_SEALED_EXECUTION_GENUINE_INFERENCE_MISSING")
    if payload.get("handoff_sealed") is not True:
        raise ValueError("QWEN_SEALED_EXECUTION_HANDOFF_NOT_SEALED")
    for field in DOWNSTREAM_FALSE:
        if payload.get(field) is not False:
            raise ValueError(f"QWEN_SEALED_EXECUTION_PREMATURE_AUTHORITY:{field}")


def execute_and_seal_canonical_candidate(
    launch_manifest_path: Path,
    output_dir: Path,
    *,
    repo_root: Path,
    python_executable: str | None = None,
) -> int:
    """Execute the canonical run, then build and replay-verify the CS301 handoff.

    A non-zero canonical execution result is propagated unchanged and no handoff is
    attempted. After zero, the canonical launcher has already replayed the exact PNG,
    inference receipt, local provenance, and launch-to-output attestation. This wrapper
    then creates one repository-local handoff beside those files and independently
    verifies it before returning success.
    """
    root = repo_root.resolve()
    code = execute_manifest_bound_inference(
        launch_manifest_path,
        output_dir,
        repo_root=root,
        python_executable=python_executable,
    )
    if code != 0:
        return int(code)

    output = output_dir if output_dir.is_absolute() else root / output_dir
    output = output.resolve()
    try:
        output.relative_to(root)
    except ValueError as exc:
        raise ValueError("QWEN_SEALED_EXECUTION_OUTPUT_OUTSIDE_REPOSITORY") from exc
    if output.is_symlink() or not output.is_dir():
        raise ValueError("QWEN_SEALED_EXECUTION_OUTPUT_INVALID")

    handoff_path = output / CANONICAL_HANDOFF_FILENAME
    if handoff_path.exists() or handoff_path.is_symlink():
        raise ValueError("QWEN_SEALED_EXECUTION_HANDOFF_ALREADY_EXISTS")

    built = build_canonical_candidate_handoff(
        output,
        handoff_path,
        repo_root=root,
    )
    _assert_handoff_authority_closed(built)

    verified = verify_canonical_candidate_handoff(handoff_path, repo_root=root)
    _assert_handoff_authority_closed(verified)
    return 0
