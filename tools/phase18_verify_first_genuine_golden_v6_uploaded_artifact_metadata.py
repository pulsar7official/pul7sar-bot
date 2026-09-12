#!/usr/bin/env python3
"""Fail-closed transport-metadata verifier for the first Genuine Golden v6 artifact.

This CPU-safe verifier does not download models, generate images, approve Human
Review, approve Golden quality, or publish anything. It binds GitHub Actions
artifact metadata to the already-created run-bound readiness manifest so a
consumer can prove that the uploaded immutable archive belongs to the expected
workflow run and exact source commit.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


BRANCH = "phase18/story-intelligence"
READY_SCHEMA = "pul7sar-first-genuine-golden-v6-artifact-ready-v2"
READY_STATUS = "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_READY_FOR_HUMAN_VISUAL_REVIEW"
TRANSPORT_STATUS = "FIRST_GENUINE_GOLDEN_V6_UPLOADED_ARTIFACT_METADATA_VERIFIED"
EXPECTED_EVIDENCE_FILES = 10
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool):
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_TRANSPORT_{label}_INVALID")
    try:
        parsed = int(str(value))
    except (TypeError, ValueError) as exc:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_TRANSPORT_{label}_INVALID") from exc
    if parsed <= 0 or str(parsed) != str(value).strip():
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_TRANSPORT_{label}_INVALID")
    return parsed


def _load_object(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_TRANSPORT_{label}_INVALID_JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_TRANSPORT_{label}_INVALID_OBJECT")
    return value


def verify(
    artifact_metadata: dict[str, object],
    readiness: dict[str, object],
    *,
    expected_source_sha: str,
    expected_workflow_run_id: object,
    expected_workflow_run_attempt: object,
    expected_artifact_digest: str | None = None,
) -> dict[str, object]:
    run_id = _positive_int(expected_workflow_run_id, "WORKFLOW_RUN_ID")
    run_attempt = _positive_int(expected_workflow_run_attempt, "WORKFLOW_RUN_ATTEMPT")
    if not _SHA40.fullmatch(expected_source_sha):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_SOURCE_SHA_INVALID")

    if readiness.get("schema") != READY_SCHEMA or readiness.get("status") != READY_STATUS:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_READINESS_CONTRACT_INVALID")
    if readiness.get("branch") != BRANCH or readiness.get("candidate") != 1:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_READINESS_IDENTITY_DRIFT")
    if readiness.get("workflow_run_id") != run_id or readiness.get("workflow_run_attempt") != run_attempt:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_READINESS_RUN_DRIFT")
    if readiness.get("source_commit_sha") != expected_source_sha or readiness.get("source_commit_verified") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_READINESS_SOURCE_DRIFT")
    if readiness.get("artifact_replay_verified") is not True or readiness.get("eligible_for_human_visual_review") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_READINESS_NOT_VERIFIED")
    if readiness.get("evidence_files_verified") != EXPECTED_EVIDENCE_FILES or readiness.get("evidence_semantics_verified") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_READINESS_EVIDENCE_NOT_VERIFIED")
    if readiness.get("cost_mode") != "$0-local":
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_COST_MODE_DRIFT")
    for field in (
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if readiness.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_TRANSPORT_ILLEGAL_AUTHORITY:{field}")

    artifact_id = _positive_int(artifact_metadata.get("id"), "ARTIFACT_ID")
    expected_name = f"phase18-first-genuine-golden-v6-{run_id}"
    if artifact_metadata.get("name") != expected_name:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_ARTIFACT_NAME_DRIFT")
    if artifact_metadata.get("expired") is not False:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_ARTIFACT_EXPIRED")
    size_in_bytes = _positive_int(artifact_metadata.get("size_in_bytes"), "ARTIFACT_SIZE")

    digest = artifact_metadata.get("digest")
    if not isinstance(digest, str) or not digest.startswith("sha256:"):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_ARTIFACT_DIGEST_INVALID")
    digest_hex = digest.removeprefix("sha256:")
    if not _SHA256.fullmatch(digest_hex):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_ARTIFACT_DIGEST_INVALID")
    if expected_artifact_digest is not None:
        normalized_expected = expected_artifact_digest.removeprefix("sha256:")
        if not _SHA256.fullmatch(normalized_expected) or normalized_expected != digest_hex:
            raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_ARTIFACT_DIGEST_MISMATCH")

    workflow_run = artifact_metadata.get("workflow_run")
    if not isinstance(workflow_run, dict):
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_WORKFLOW_RUN_MISSING")
    if workflow_run.get("id") != run_id:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_WORKFLOW_RUN_ID_DRIFT")
    if workflow_run.get("head_branch") != BRANCH:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_WORKFLOW_BRANCH_DRIFT")
    if workflow_run.get("head_sha") != expected_source_sha:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_TRANSPORT_WORKFLOW_SOURCE_DRIFT")

    return {
        "status": TRANSPORT_STATUS,
        "branch": BRANCH,
        "candidate": 1,
        "cost_mode": "$0-local",
        "workflow_run_id": run_id,
        "workflow_run_attempt": run_attempt,
        "source_commit_sha": expected_source_sha,
        "source_commit_verified": True,
        "artifact_id": artifact_id,
        "artifact_name": expected_name,
        "artifact_digest": f"sha256:{digest_hex}",
        "artifact_size_in_bytes": size_in_bytes,
        "uploaded_artifact_metadata_verified": True,
        "eligible_for_human_visual_review": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_metadata", type=Path)
    parser.add_argument("readiness_manifest", type=Path)
    parser.add_argument("--expected-source-sha", required=True)
    parser.add_argument("--expected-workflow-run-id", required=True)
    parser.add_argument("--expected-workflow-run-attempt", required=True)
    parser.add_argument("--expected-artifact-digest", default=None)
    args = parser.parse_args()

    result = verify(
        _load_object(args.artifact_metadata, "ARTIFACT_METADATA"),
        _load_object(args.readiness_manifest, "READINESS"),
        expected_source_sha=args.expected_source_sha,
        expected_workflow_run_id=args.expected_workflow_run_id,
        expected_workflow_run_attempt=args.expected_workflow_run_attempt,
        expected_artifact_digest=args.expected_artifact_digest,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
