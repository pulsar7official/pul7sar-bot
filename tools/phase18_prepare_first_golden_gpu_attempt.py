#!/usr/bin/env python3
"""Prepare a fail-closed canonical first-Golden GPU attempt contract.

This helper performs no workflow dispatch, downloads, model loading, image generation,
queue mutation, publication, or seed expansion. It consumes the already-attested GPU
handoff for one immutable Phase 18 commit and emits the exact canonical launcher
invocation plus evidence paths needed for a genuine Candidate 1 attempt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_BRANCH = "phase18/story-intelligence"
HANDOFF_SCHEMA = "pul7sar-phase18-first-golden-gpu-handoff-v1"
CANONICAL_WORKFLOW = ".github/workflows/phase18-first-genuine-golden-v6.yml"
CANONICAL_LAUNCHER = "tools/phase18_run_first_genuine_golden_v6_canonical_attested.py"
REQUIRED_RUNNER_LABELS = ["self-hosted", "linux", "x64", "gpu", "cuda", "bf16", "pul7sar-phase18"]
CLOSED_AUTHORITIES = (
    "authoritative_gate",
    "network_download_authorized",
    "generation_authorized",
    "publication_ready",
    "seeds_2_to_4_authorized",
)

DEFAULT_PATHS = {
    "canonical_output": "output/phase18_gpu_smoke/first-genuine-golden-v6-resource-lock.json",
    "pre_gpu_receipt": "output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-receipt.json",
    "pre_gpu_attestation": "output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-attestation.json",
    "pre_gpu_summary": "output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-summary.json",
    "gpu_handoff": "output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-gpu-handoff.json",
}


def _inside_repository(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GOLDEN_GPU_ATTEMPT_PATH_ESCAPES_REPOSITORY")
    return target


def _load_json(path: Path) -> dict[str, object] | None:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return loaded if isinstance(loaded, dict) else None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(*, expected_commit: str, handoff_path: Path) -> dict[str, object]:
    blockers: list[str] = []
    if _SHA40.fullmatch(expected_commit) is None:
        blockers.append("EXPECTED_COMMIT_INVALID")

    handoff_target = _inside_repository(handoff_path)
    handoff: dict[str, object] | None = None
    handoff_sha256: str | None = None
    if not handoff_target.is_file():
        blockers.append("GPU_HANDOFF_MISSING")
    else:
        handoff_sha256 = _sha256(handoff_target)
        handoff = _load_json(handoff_target)
        if handoff is None:
            blockers.append("GPU_HANDOFF_INVALID_JSON")

    if handoff is not None:
        if handoff.get("schema") != HANDOFF_SCHEMA:
            blockers.append("GPU_HANDOFF_SCHEMA_DRIFT")
        if handoff.get("expected_commit") != expected_commit:
            blockers.append("GPU_HANDOFF_COMMIT_DRIFT")
        if handoff.get("branch_required") != EXPECTED_BRANCH:
            blockers.append("GPU_HANDOFF_BRANCH_DRIFT")
        if handoff.get("cost_mode_required") != "$0-local":
            blockers.append("GPU_HANDOFF_COST_MODE_DRIFT")
        if handoff.get("offline_required") is not True:
            blockers.append("GPU_HANDOFF_OFFLINE_POLICY_DRIFT")
        if handoff.get("canonical_workflow") != CANONICAL_WORKFLOW:
            blockers.append("GPU_HANDOFF_CANONICAL_WORKFLOW_DRIFT")
        if handoff.get("required_runner_labels") != REQUIRED_RUNNER_LABELS:
            blockers.append("GPU_HANDOFF_RUNNER_LABEL_DRIFT")
        if handoff.get("eligible_for_authoritative_golden_preflight") is not True:
            blockers.append("GPU_HANDOFF_NOT_ELIGIBLE")
        if handoff.get("blockers") != []:
            blockers.append("GPU_HANDOFF_BLOCKERS_REMAIN")
        for field in CLOSED_AUTHORITIES:
            if handoff.get(field) is not False:
                blockers.append(f"GPU_HANDOFF_AUTHORITY_DRIFT_{field.upper()}")

    workflow_target = ROOT / CANONICAL_WORKFLOW
    launcher_target = ROOT / CANONICAL_LAUNCHER
    workflow_sha256: str | None = None
    launcher_sha256: str | None = None
    if not workflow_target.is_file():
        blockers.append("CANONICAL_WORKFLOW_MISSING")
    else:
        workflow_sha256 = _sha256(workflow_target)
    if not launcher_target.is_file():
        blockers.append("CANONICAL_LAUNCHER_MISSING")
    else:
        launcher_sha256 = _sha256(launcher_target)

    command = [
        "python",
        CANONICAL_LAUNCHER,
        "--expected-commit",
        expected_commit,
        "--output",
        DEFAULT_PATHS["canonical_output"],
        "--receipt",
        DEFAULT_PATHS["pre_gpu_receipt"],
        "--attestation",
        DEFAULT_PATHS["pre_gpu_attestation"],
        "--summary",
        DEFAULT_PATHS["pre_gpu_summary"],
        "--handoff",
        DEFAULT_PATHS["gpu_handoff"],
    ]

    ready = not blockers
    return {
        "schema": "pul7sar-phase18-first-golden-gpu-attempt-contract-v1",
        "expected_commit": expected_commit,
        "branch_required": EXPECTED_BRANCH,
        "canonical_workflow": CANONICAL_WORKFLOW,
        "canonical_launcher": CANONICAL_LAUNCHER,
        "required_runner_labels": list(REQUIRED_RUNNER_LABELS),
        "cost_mode_required": "$0-local",
        "offline_required": True,
        "source_handoff": str(handoff_target),
        "source_handoff_sha256": handoff_sha256,
        "canonical_workflow_sha256": workflow_sha256,
        "canonical_launcher_sha256": launcher_sha256,
        "evidence_paths": dict(DEFAULT_PATHS),
        "canonical_command": command,
        "attempt_contract_ready": ready,
        "blockers": blockers,
        "workflow_dispatch_performed": False,
        "png_created": False,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a no-dispatch first-Golden GPU attempt contract")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--handoff", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = build(expected_commit=args.expected_commit, handoff_path=args.handoff)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = _inside_repository(args.output)
        if target == _inside_repository(args.handoff):
            raise RuntimeError("FIRST_GOLDEN_GPU_ATTEMPT_OUTPUT_COLLIDES_WITH_HANDOFF")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["attempt_contract_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
