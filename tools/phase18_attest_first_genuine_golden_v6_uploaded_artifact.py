#!/usr/bin/env python3
"""Create a fail-closed transport attestation for the first Genuine Golden v6 upload.

This helper is CPU-safe and network-free. It consumes GitHub artifact metadata
that was fetched by the workflow plus the immutable outputs from
``actions/upload-artifact`` and delegates semantic verification to the CS404
transport verifier. It never grants Human Review, Golden-quality, publication,
or Seeds 2-4 authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from tools.phase18_verify_first_genuine_golden_v6_uploaded_artifact_metadata import verify


SCHEMA = "pul7sar-first-genuine-golden-v6-upload-transport-attestation-v1"
STATUS = "FIRST_GENUINE_GOLDEN_V6_UPLOAD_TRANSPORT_ATTESTED"
_SHA256 = re.compile(r"^(?:sha256:)?([0-9a-f]{64})$")


def _load_object(path: Path, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ATTEST_{label}_INVALID_JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ATTEST_{label}_INVALID_OBJECT")
    return value


def _canonical_digest(value: str) -> str:
    match = _SHA256.fullmatch(value.strip())
    if match is None:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ATTEST_UPLOAD_DIGEST_INVALID")
    return f"sha256:{match.group(1)}"


def _positive_int(value: object, label: str) -> int:
    if isinstance(value, bool):
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ATTEST_{label}_INVALID")
    text = str(value).strip()
    if not text.isdigit() or text.startswith("0"):
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ATTEST_{label}_INVALID")
    parsed = int(text)
    if parsed <= 0:
        raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ATTEST_{label}_INVALID")
    return parsed


def build_attestation(
    artifact_metadata: dict[str, object],
    readiness: dict[str, object],
    *,
    expected_source_sha: str,
    workflow_run_id: object,
    workflow_run_attempt: object,
    upload_artifact_id: object,
    upload_artifact_digest: str,
) -> dict[str, object]:
    run_id = _positive_int(workflow_run_id, "WORKFLOW_RUN_ID")
    run_attempt = _positive_int(workflow_run_attempt, "WORKFLOW_RUN_ATTEMPT")
    upload_id = _positive_int(upload_artifact_id, "UPLOAD_ARTIFACT_ID")
    digest = _canonical_digest(upload_artifact_digest)

    verified = verify(
        artifact_metadata,
        readiness,
        expected_source_sha=expected_source_sha,
        expected_workflow_run_id=run_id,
        expected_workflow_run_attempt=run_attempt,
        expected_artifact_digest=digest,
    )
    if verified.get("artifact_id") != upload_id:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ATTEST_UPLOAD_ARTIFACT_ID_MISMATCH")
    if verified.get("artifact_digest") != digest:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ATTEST_UPLOAD_ARTIFACT_DIGEST_MISMATCH")
    if verified.get("uploaded_artifact_metadata_verified") is not True:
        raise RuntimeError("FIRST_GENUINE_GOLDEN_V6_ATTEST_TRANSPORT_NOT_VERIFIED")

    for field in (
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if verified.get(field) is not False:
            raise RuntimeError(f"FIRST_GENUINE_GOLDEN_V6_ATTEST_ILLEGAL_AUTHORITY:{field}")

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "branch": verified["branch"],
        "candidate": verified["candidate"],
        "cost_mode": verified["cost_mode"],
        "workflow_run_id": run_id,
        "workflow_run_attempt": run_attempt,
        "source_commit_sha": expected_source_sha,
        "source_commit_verified": True,
        "upload_action_artifact_id": upload_id,
        "upload_action_artifact_digest": digest,
        "rest_artifact_id": verified["artifact_id"],
        "rest_artifact_name": verified["artifact_name"],
        "rest_artifact_digest": verified["artifact_digest"],
        "rest_artifact_size_in_bytes": verified["artifact_size_in_bytes"],
        "uploaded_artifact_metadata_verified": True,
        "eligible_for_human_visual_review": True,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def write_atomic(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_metadata", type=Path)
    parser.add_argument("readiness_manifest", type=Path)
    parser.add_argument("--expected-source-sha", required=True)
    parser.add_argument("--workflow-run-id", required=True)
    parser.add_argument("--workflow-run-attempt", required=True)
    parser.add_argument("--upload-artifact-id", required=True)
    parser.add_argument("--upload-artifact-digest", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = build_attestation(
        _load_object(args.artifact_metadata, "ARTIFACT_METADATA"),
        _load_object(args.readiness_manifest, "READINESS"),
        expected_source_sha=args.expected_source_sha,
        workflow_run_id=args.workflow_run_id,
        workflow_run_attempt=args.workflow_run_attempt,
        upload_artifact_id=args.upload_artifact_id,
        upload_artifact_digest=args.upload_artifact_digest,
    )
    write_atomic(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
