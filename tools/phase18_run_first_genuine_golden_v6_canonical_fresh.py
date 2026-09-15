#!/usr/bin/env python3
"""Freshness-bound wrapper for the canonical first-Golden v6 launcher.

This wrapper cryptographically and semantically binds the authoritative
pre-generation evidence, captures mutable Candidate 1 evidence before the
canonical attempt, runs the existing attested/content-bound/output-replayed
canonical launcher, then replays freshness after the attempt. It never grants
generation, network, publication, Golden-quality, or Seeds 2-4 authority; it
only refuses readiness when evidence is stale, incomplete, or contract-drifted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_bind_authoritative_first_golden_pre_generation_evidence import bind as bind_pre_generation_evidence
from tools.phase18_first_golden_freshness_guard import capture as capture_freshness
from tools.phase18_first_golden_freshness_guard import verify as verify_freshness
from tools.phase18_run_first_genuine_golden_v6_canonical_attested import run as run_canonical

SCHEMA = "pul7sar-phase18-first-genuine-golden-v6-canonical-fresh-launch-v1"
EXPECTED_BRANCH = "phase18/story-intelligence"
PRE_GENERATION_BINDER = "tools/phase18_bind_authoritative_first_golden_pre_generation_evidence.py"


def _inside_repository(path: Path) -> Path:
    target = path if path.is_absolute() else ROOT / path
    target = target.resolve()
    root = ROOT.resolve()
    if target != root and root not in target.parents:
        raise RuntimeError("FIRST_GOLDEN_FRESH_WRAPPER_PATH_ESCAPES_REPOSITORY")
    return target


def _write_json(path: Path, payload: dict[str, object]) -> None:
    target = _inside_repository(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _closed_authorities() -> dict[str, bool]:
    return {
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _prove_binding_implementation_is_immutable(expected_commit: str) -> None:
    """Fail closed unless the binder executed now is exactly the tracked source."""
    if len(expected_commit) != 40 or any(ch not in "0123456789abcdef" for ch in expected_commit):
        raise RuntimeError("FIRST_GOLDEN_PRE_GENERATION_BINDER_SOURCE_SHA_INVALID")
    binder_path = _inside_repository(Path(PRE_GENERATION_BINDER))
    if not binder_path.is_file():
        raise RuntimeError("FIRST_GOLDEN_PRE_GENERATION_BINDER_MISSING")
    try:
        tracked = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", expected_commit, "--", PRE_GENERATION_BINDER],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if tracked != PRE_GENERATION_BINDER:
            raise RuntimeError("FIRST_GOLDEN_PRE_GENERATION_BINDER_NOT_TRACKED_AT_SOURCE_SHA")
        committed = subprocess.run(
            ["git", "show", f"{expected_commit}:{PRE_GENERATION_BINDER}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("FIRST_GOLDEN_PRE_GENERATION_BINDER_GIT_PROOF_FAILED") from exc
    if binder_path.read_bytes() != committed:
        raise RuntimeError("FIRST_GOLDEN_PRE_GENERATION_BINDER_WORKTREE_DRIFT")


def run(
    *,
    expected_commit: str,
    output_path: Path,
    receipt_path: Path,
    attestation_path: Path,
    summary_path: Path,
    handoff_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-gpu-handoff.json"),
    attempt_contract_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-gpu-attempt-contract.json"),
    freshness_baseline_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-freshness-baseline.json"),
    freshness_verification_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-freshness-verification.json"),
    pre_generation_binding_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-authoritative-pre-generation-binding.json"),
    network_evidence_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-zero-cost-network-guard.json"),
    runner_identity_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-runner-identity.json"),
    snapshot_inventory_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-approved-snapshot-inventory.json"),
    execution_blocker_path: Path = Path("output/phase18_gpu_smoke/first-genuine-golden-v6-execution-blocker-probe.json"),
) -> dict[str, object]:
    paths = {
        _inside_repository(output_path),
        _inside_repository(receipt_path),
        _inside_repository(attestation_path),
        _inside_repository(summary_path),
        _inside_repository(handoff_path),
        _inside_repository(attempt_contract_path),
        _inside_repository(freshness_baseline_path),
        _inside_repository(freshness_verification_path),
        _inside_repository(pre_generation_binding_path),
    }
    if len(paths) != 9:
        raise RuntimeError("FIRST_GOLDEN_FRESH_WRAPPER_OUTPUT_PATH_COLLISION")

    # Prove the binder implementation itself is the immutable source-tree copy
    # before trusting it to validate any pre-generation evidence.
    _prove_binding_implementation_is_immutable(expected_commit)

    # This is the last fail-closed evidence gate immediately before any
    # canonical Candidate-1 attempt can begin. The binder validates the exact
    # source SHA, zero-cost/network isolation, CUDA/native-BF16 runner identity,
    # approved local model snapshots, and execution-blocker readiness.
    pre_generation_binding = bind_pre_generation_evidence(
        source_sha=expected_commit,
        branch=EXPECTED_BRANCH,
        network=_inside_repository(network_evidence_path),
        runner=_inside_repository(runner_identity_path),
        snapshots=_inside_repository(snapshot_inventory_path),
        blocker=_inside_repository(execution_blocker_path),
    )
    _write_json(pre_generation_binding_path, pre_generation_binding)

    baseline = capture_freshness()
    _write_json(freshness_baseline_path, baseline)

    canonical = run_canonical(
        expected_commit=expected_commit,
        output_path=output_path,
        receipt_path=receipt_path,
        attestation_path=attestation_path,
        summary_path=summary_path,
        handoff_path=handoff_path,
        attempt_contract_path=attempt_contract_path,
    )

    freshness = verify_freshness(baseline)
    _write_json(freshness_verification_path, freshness)

    blockers: list[str] = []
    canonical_blockers = canonical.get("blockers")
    if isinstance(canonical_blockers, list):
        blockers.extend(str(item) for item in canonical_blockers)
    elif canonical.get("ready") is not True:
        blockers.append("CANONICAL_ATTEMPT_NOT_READY")

    if canonical.get("ready") is not True:
        blockers.append("CANONICAL_READY_FALSE")
    if freshness.get("fresh_attempt_evidence") is not True:
        blockers.append("FRESHNESS_EVIDENCE_NOT_PROVEN")
        freshness_blockers = freshness.get("blockers")
        if isinstance(freshness_blockers, list):
            blockers.extend(f"FRESHNESS::{item}" for item in freshness_blockers)

    # The wrapper is a verifier, never an authority escalator.
    for field in (
        "authoritative_gate",
        "network_download_authorized",
        "generation_authorized",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        if canonical.get(field) is not False:
            blockers.append(f"CANONICAL_AUTHORITY_DRIFT_{field.upper()}")

    blockers = list(dict.fromkeys(blockers))
    return {
        "schema": SCHEMA,
        "expected_commit": expected_commit,
        "pre_generation_binding_implementation_immutable": True,
        "pre_generation_evidence_binding": str(_inside_repository(pre_generation_binding_path)),
        "pre_generation_evidence_binding_schema": pre_generation_binding.get("schema"),
        "pre_generation_evidence_bound": True,
        "canonical_result": canonical,
        "freshness_baseline": str(_inside_repository(freshness_baseline_path)),
        "freshness_verification": str(_inside_repository(freshness_verification_path)),
        "fresh_attempt_evidence": freshness.get("fresh_attempt_evidence") is True,
        "canonical_generation_started": canonical.get("canonical_generation_started") is True,
        "canonical_png": canonical.get("canonical_png"),
        "canonical_png_sha256": canonical.get("canonical_png_sha256"),
        "ready": canonical.get("ready") is True and freshness.get("fresh_attempt_evidence") is True and not blockers,
        "blockers": blockers,
        **_closed_authorities(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the canonical first-Golden v6 attempt with authoritative pre-generation evidence binding and pre/post stale-artifact freshness replay"
    )
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-receipt.json"),
    )
    parser.add_argument(
        "--attestation",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-attestation.json"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-attested-pre-gpu-summary.json"),
    )
    parser.add_argument(
        "--handoff",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-canonical-gpu-handoff.json"),
    )
    parser.add_argument(
        "--attempt-contract",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-gpu-attempt-contract.json"),
    )
    parser.add_argument(
        "--freshness-baseline",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-freshness-baseline.json"),
    )
    parser.add_argument(
        "--freshness-verification",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-freshness-verification.json"),
    )
    parser.add_argument(
        "--pre-generation-binding",
        type=Path,
        default=Path("output/phase18_gpu_smoke/first-genuine-golden-v6-authoritative-pre-generation-binding.json"),
    )
    args = parser.parse_args()

    payload = run(
        expected_commit=args.expected_commit,
        output_path=args.output,
        receipt_path=args.receipt,
        attestation_path=args.attestation,
        summary_path=args.summary,
        handoff_path=args.handoff,
        attempt_contract_path=args.attempt_contract,
        freshness_baseline_path=args.freshness_baseline,
        freshness_verification_path=args.freshness_verification,
        pre_generation_binding_path=args.pre_generation_binding,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload.get("ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
