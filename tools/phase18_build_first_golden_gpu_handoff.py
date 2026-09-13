#!/usr/bin/env python3
"""Build a fail-closed first-Golden GPU handoff from attested host readiness.

This helper performs no downloads, model loading, image generation, queue mutation,
workflow dispatch, publication, or seed expansion. It validates an already-produced
attested pre-GPU summary against the immutable expected commit and emits a
machine-readable handoff that identifies the canonical workflow and runner labels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
_SHA40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_BRANCH = "phase18/story-intelligence"
CANONICAL_WORKFLOW = ".github/workflows/phase18-first-genuine-golden-v6.yml"
HOST_READINESS_WORKFLOW = ".github/workflows/phase18-first-golden-attested-host-readiness.yml"
REQUIRED_RUNNER_LABELS = ["self-hosted", "linux", "x64", "gpu", "cuda", "bf16", "pul7sar-phase18"]
CLOSED_AUTHORITIES = (
    "authoritative_gate",
    "network_download_authorized",
    "generation_authorized",
    "publication_ready",
    "seeds_2_to_4_authorized",
)


def _inside_repository(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GOLDEN_GPU_HANDOFF_OUTPUT_ESCAPES_REPOSITORY")
    return target


def build(*, expected_commit: str, attested_summary_path: Path) -> dict[str, object]:
    blockers: list[str] = []
    if _SHA40.fullmatch(expected_commit) is None:
        blockers.append("EXPECTED_COMMIT_INVALID")

    summary_path = _inside_repository(attested_summary_path)
    summary: dict[str, object] | None = None
    if not summary_path.is_file():
        blockers.append("ATTESTED_PRE_GPU_SUMMARY_MISSING")
    else:
        try:
            loaded = json.loads(summary_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise TypeError("summary must be an object")
            summary = loaded
        except Exception:
            blockers.append("ATTESTED_PRE_GPU_SUMMARY_INVALID_JSON")

    if summary is not None:
        if summary.get("schema") != "pul7sar-phase18-first-golden-attested-pre-gpu-run-v1":
            blockers.append("ATTESTED_PRE_GPU_SCHEMA_DRIFT")
        if summary.get("expected_commit") != expected_commit:
            blockers.append("ATTESTED_PRE_GPU_COMMIT_DRIFT")
        if summary.get("ready_for_authoritative_golden_preflight") is not True:
            blockers.append("ATTESTED_PRE_GPU_NOT_READY")
        if summary.get("receipt_attested") is not True:
            blockers.append("ATTESTED_PRE_GPU_RECEIPT_NOT_ATTESTED")
        if summary.get("blockers") != []:
            blockers.append("ATTESTED_PRE_GPU_BLOCKERS_REMAIN")
        for field in CLOSED_AUTHORITIES:
            if summary.get(field) is not False:
                blockers.append(f"ATTESTED_PRE_GPU_{field.upper()}_DRIFT")

    canonical_path = ROOT / CANONICAL_WORKFLOW
    readiness_path = ROOT / HOST_READINESS_WORKFLOW
    if not canonical_path.is_file():
        blockers.append("CANONICAL_GOLDEN_WORKFLOW_MISSING")
    if not readiness_path.is_file():
        blockers.append("HOST_READINESS_WORKFLOW_MISSING")

    eligible = not blockers
    return {
        "schema": "pul7sar-phase18-first-golden-gpu-handoff-v1",
        "expected_commit": expected_commit,
        "branch_required": EXPECTED_BRANCH,
        "cost_mode_required": "$0-local",
        "offline_required": True,
        "attested_summary_path": str(summary_path),
        "host_readiness_workflow": HOST_READINESS_WORKFLOW,
        "canonical_workflow": CANONICAL_WORKFLOW,
        "required_runner_labels": list(REQUIRED_RUNNER_LABELS),
        "eligible_for_authoritative_golden_preflight": eligible,
        "blockers": blockers,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an immutable first-Golden GPU handoff from attested host readiness")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--attested-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = build(expected_commit=args.expected_commit, attested_summary_path=args.attested_summary)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = _inside_repository(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["eligible_for_authoritative_golden_preflight"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
