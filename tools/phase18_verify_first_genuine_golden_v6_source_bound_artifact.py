#!/usr/bin/env python3
"""Fail-closed source-bound replay verifier for First Genuine Golden v6 artifacts.

This CPU-safe wrapper composes the existing byte/semantic artifact replay with the
exact source-commit envelope produced by the Golden v6 workflow. It performs no
model loading, generation, network access, Human Review, Golden approval, or
publication action.

When invoked from the CLI, it also writes an atomic artifact-readiness manifest
next to the resource-lock receipt. The readiness filename and payload are bound
to the immutable GitHub Actions run id and run attempt. This makes a marker from
a previous self-hosted-runner workspace distinguishable from the current run,
even when ``if: always()`` uploads diagnostic output after an early failure.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from phase18_bind_first_genuine_golden_source_commit import verify as verify_source_binding
from phase18_verify_first_genuine_golden_v6_artifact import verify as verify_artifact

SOURCE_BINDING_RECORDED_PATH = "output/phase18_gpu_smoke/first-genuine-golden-v6-source-binding.json"
ARTIFACT_READY_FILENAME_PREFIX = "first-genuine-golden-v6-artifact-ready"
LEGACY_ARTIFACT_READY_FILENAME = "first-genuine-golden-v6-artifact-ready.json"


def _resolve_source_binding(root: Path) -> Path:
    root = root.resolve()
    relative = Path("phase18_gpu_smoke/first-genuine-golden-v6-source-binding.json")
    candidates = (root / relative, root / "output" / relative)
    existing = [candidate.resolve() for candidate in candidates if candidate.is_file()]
    if not existing:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_ARTIFACT_MISSING")
    if len(existing) > 1 and existing[0] != existing[1]:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_ARTIFACT_AMBIGUOUS")
    binding = existing[0]
    if binding != root and root not in binding.parents:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_ESCAPES_ARTIFACT_ROOT")
    return binding


def _positive_int(value: object, *, label: str) -> int:
    if isinstance(value, bool):
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_{label}_INVALID")
    try:
        parsed = int(str(value))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_{label}_INVALID") from exc
    if parsed <= 0 or str(parsed) != str(value).strip():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_{label}_INVALID")
    return parsed


def artifact_ready_filename(workflow_run_id: object, workflow_run_attempt: object) -> str:
    run_id = _positive_int(workflow_run_id, label="WORKFLOW_RUN_ID")
    attempt = _positive_int(workflow_run_attempt, label="WORKFLOW_RUN_ATTEMPT")
    return f"{ARTIFACT_READY_FILENAME_PREFIX}-run-{run_id}-attempt-{attempt}.json"


def verify(
    receipt_path: Path,
    *,
    artifact_root: Path | None = None,
    expected_source_sha: str,
) -> dict[str, object]:
    receipt_path = receipt_path.resolve()
    root = (artifact_root or receipt_path.parent).resolve()

    replay = verify_artifact(receipt_path, artifact_root=root)
    binding_path = _resolve_source_binding(root)
    source = verify_source_binding(
        binding_path,
        receipt_path,
        expected_source_sha=expected_source_sha,
    )

    if replay.get("branch") != source.get("branch") or replay.get("candidate") != source.get("candidate"):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_IDENTITY_DRIFT")
    for field in (
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if replay.get(field) is not False or source.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ILLEGAL_AUTHORITY:{field}")

    result = dict(replay)
    result.update(
        {
            "status": "FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_REPLAY_VERIFIED",
            "source_commit_sha": expected_source_sha,
            "source_commit_verified": True,
            "source_binding": str(binding_path),
            "resource_lock_sha256": source.get("resource_lock_sha256"),
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
    )
    return result


def build_artifact_ready_manifest(
    result: dict[str, object],
    *,
    workflow_run_id: object,
    workflow_run_attempt: object,
) -> dict[str, object]:
    if result.get("status") != "FIRST_GENUINE_GOLDEN_V6_SOURCE_BOUND_ARTIFACT_REPLAY_VERIFIED":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_REPLAY_NOT_VERIFIED")
    if result.get("source_commit_verified") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_SOURCE_NOT_VERIFIED")
    if result.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_COST_MODE_DRIFT")
    if result.get("evidence_semantics_verified") is not True or result.get("evidence_files_verified") != 9:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_EVIDENCE_NOT_VERIFIED")

    run_id = _positive_int(workflow_run_id, label="WORKFLOW_RUN_ID")
    run_attempt = _positive_int(workflow_run_attempt, label="WORKFLOW_RUN_ATTEMPT")
    source_sha = result.get("source_commit_sha")
    resource_lock_sha256 = result.get("resource_lock_sha256")
    png_sha256 = result.get("png_sha256")
    png_bytes = result.get("png_bytes")
    if not isinstance(source_sha, str) or len(source_sha) != 40:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_SOURCE_SHA_INVALID")
    for label, value in (("resource_lock_sha256", resource_lock_sha256), ("png_sha256", png_sha256)):
        if not isinstance(value, str) or len(value) != 64:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_{label.upper()}_INVALID")
    if not isinstance(png_bytes, int) or png_bytes <= 0:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_PNG_BYTES_INVALID")

    for field in (
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if result.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_ILLEGAL_AUTHORITY:{field}")

    return {
        "schema": "pul7sar-first-genuine-golden-v6-artifact-ready-v2",
        "status": "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_FOR_HUMAN_VISUAL_REVIEW",
        "branch": result.get("branch"),
        "candidate": result.get("candidate"),
        "cost_mode": "$0-local",
        "workflow_run_id": run_id,
        "workflow_run_attempt": run_attempt,
        "artifact_replay_verified": True,
        "source_commit_verified": True,
        "source_commit_sha": source_sha,
        "resource_lock_sha256": resource_lock_sha256,
        "png_sha256": png_sha256,
        "png_bytes": png_bytes,
        "evidence_files_verified": 9,
        "evidence_semantics_verified": True,
        "eligible_for_human_visual_review": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def verify_artifact_ready_manifest(
    manifest: dict[str, object],
    result: dict[str, object],
    *,
    expected_workflow_run_id: object,
    expected_workflow_run_attempt: object,
) -> None:
    expected = build_artifact_ready_manifest(
        result,
        workflow_run_id=expected_workflow_run_id,
        workflow_run_attempt=expected_workflow_run_attempt,
    )
    if manifest != expected:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_MANIFEST_REPLAY_MISMATCH")


def write_artifact_ready_manifest(
    path: Path,
    result: dict[str, object],
    *,
    workflow_run_id: object,
    workflow_run_attempt: object,
) -> dict[str, object]:
    manifest = build_artifact_ready_manifest(
        result,
        workflow_run_id=workflow_run_id,
        workflow_run_attempt=workflow_run_attempt,
    )
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--expected-source-sha", required=True)
    parser.add_argument("--workflow-run-id", default=os.environ.get("GITHUB_RUN_ID"))
    parser.add_argument("--workflow-run-attempt", default=os.environ.get("GITHUB_RUN_ATTEMPT"))
    args = parser.parse_args()

    run_id = _positive_int(args.workflow_run_id, label="WORKFLOW_RUN_ID")
    run_attempt = _positive_int(args.workflow_run_attempt, label="WORKFLOW_RUN_ATTEMPT")
    ready_dir = args.receipt.resolve().parent
    ready_path = ready_dir / artifact_ready_filename(run_id, run_attempt)

    # Remove only a same-run partial marker plus the obsolete v1 canonical name.
    # Markers from other run ids are deliberately not trusted; their distinct
    # filenames make stale self-hosted-runner output externally detectable.
    ready_path.unlink(missing_ok=True)
    (ready_dir / LEGACY_ARTIFACT_READY_FILENAME).unlink(missing_ok=True)

    result = verify(
        args.receipt,
        artifact_root=args.artifact_root,
        expected_source_sha=args.expected_source_sha,
    )
    manifest = write_artifact_ready_manifest(
        ready_path,
        result,
        workflow_run_id=run_id,
        workflow_run_attempt=run_attempt,
    )
    verify_artifact_ready_manifest(
        manifest,
        result,
        expected_workflow_run_id=run_id,
        expected_workflow_run_attempt=run_attempt,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
