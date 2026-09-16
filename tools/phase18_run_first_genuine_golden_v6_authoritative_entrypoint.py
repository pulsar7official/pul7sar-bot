#!/usr/bin/env python3
"""Single fail-closed authoritative entrypoint for the first genuine Golden v6 attempt.

Captures and binds the exact pre-generation evidence first, then delegates to the
canonical-fresh launcher. This module is intentionally a thin composition layer:
it does not weaken or replace factual, identity, sentiment, zero-cost,
semantic-publication, PNG, Human Review, or Golden-quality gates.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_capture_authoritative_pre_generation_evidence import capture
from tools.phase18_run_first_genuine_golden_v6_canonical_fresh import run as run_fresh

BRANCH = "phase18/story-intelligence"
SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-authoritative-entrypoint-v1"
_SHA40 = re.compile(r"^[0-9a-f]{40}$")


def run(*, expected_commit: str, output_path: Path, evidence_dir: Path = Path("output/phase18_gpu_smoke")) -> dict[str, object]:
    if _SHA40.fullmatch(expected_commit) is None:
        raise RuntimeError("FIRST_GOLDEN_AUTHORITATIVE_ENTRYPOINT_SOURCE_SHA_INVALID")
    if os.environ.get("PUL7SAR_PHASE18_COST_MODE") != "$0-local":
        raise RuntimeError("FIRST_GOLDEN_AUTHORITATIVE_ENTRYPOINT_REQUIRES_ZERO_COST_MODE")
    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        raise RuntimeError("FIRST_GOLDEN_AUTHORITATIVE_ENTRYPOINT_REQUIRES_OFFLINE_MODEL_RESOLUTION")

    capture_result = capture(source_sha=expected_commit, output_dir=evidence_dir)
    if capture_result.get("ready") is not True:
        raise RuntimeError("FIRST_GOLDEN_AUTHORITATIVE_PRE_GENERATION_CAPTURE_NOT_READY")

    fresh_result = run_fresh(
        expected_commit=expected_commit,
        output_path=output_path,
        receipt_path=evidence_dir / "first-genuine-golden-v6-canonical-attested-pre-gpu-receipt.json",
        attestation_path=evidence_dir / "first-genuine-golden-v6-canonical-attested-pre-gpu-attestation.json",
        summary_path=evidence_dir / "first-genuine-golden-v6-canonical-attested-pre-gpu-summary.json",
        handoff_path=evidence_dir / "first-genuine-golden-v6-canonical-gpu-handoff.json",
        attempt_contract_path=evidence_dir / "first-genuine-golden-v6-gpu-attempt-contract.json",
        freshness_baseline_path=evidence_dir / "first-genuine-golden-v6-freshness-baseline.json",
        freshness_verification_path=evidence_dir / "first-genuine-golden-v6-freshness-verification.json",
        pre_generation_binding_path=evidence_dir / "first-genuine-golden-v6-authoritative-pre-generation-binding.json",
        network_evidence_path=evidence_dir / "first-genuine-golden-v6-zero-cost-network-guard.json",
        runner_identity_path=evidence_dir / "first-genuine-golden-v6-runner-identity.json",
        snapshot_inventory_path=evidence_dir / "first-genuine-golden-v6-approved-snapshot-inventory.json",
        execution_blocker_path=evidence_dir / "first-genuine-golden-v6-execution-blocker-probe.json",
    )
    return {
        "schema": SCHEMA,
        "branch": BRANCH,
        "expected_commit": expected_commit,
        "pre_generation_capture": capture_result,
        "fresh_canonical_result": fresh_result,
        "ready": fresh_result.get("ready") is True,
        "blockers": list(fresh_result.get("blockers") or []),
        "canonical_png": fresh_result.get("canonical_png"),
        "canonical_png_sha256": fresh_result.get("canonical_png_sha256"),
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the fail-closed authoritative first-Golden v6 entrypoint")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, default=Path("output/phase18_gpu_smoke"))
    args = parser.parse_args()
    payload = run(expected_commit=args.expected_commit, output_path=args.output, evidence_dir=args.evidence_dir)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
