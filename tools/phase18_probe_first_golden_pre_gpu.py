#!/usr/bin/env python3
"""Unified fail-closed pre-GPU probe for the first genuine Golden v6.

This probe performs no downloads, model loading, generation, queue mutation, or
publication. It first proves immutable Phase 18 source identity. Only when that
source proof is ready does it evaluate the existing zero-cost execution blocker
probe. The resulting receipt gives one decision point before any authoritative
Golden preflight or GPU-heavy work is attempted.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.phase18_probe_first_golden_source_identity import inspect as inspect_source_identity

_SHA40 = re.compile(r"^[0-9a-f]{40}$")
SourceInspector = Callable[..., dict[str, object]]
ExecutionInspector = Callable[..., dict[str, object]]


def inspect(
    *,
    expected_commit: str,
    source_inspector: SourceInspector | None = None,
    execution_inspector: ExecutionInspector | None = None,
) -> dict[str, object]:
    blockers: list[str] = []

    if _SHA40.fullmatch(expected_commit) is None:
        blockers.append("EXPECTED_COMMIT_INVALID")

    source_fn = inspect_source_identity if source_inspector is None else source_inspector
    source = source_fn(expected_commit=expected_commit)
    source_ready = source.get("source_identity_ready") is True
    if not source_ready:
        blockers.append("FIRST_GOLDEN_SOURCE_IDENTITY_NOT_READY")

    execution: dict[str, object] | None = None
    if source_ready and not blockers:
        if execution_inspector is None:
            from tools.phase18_probe_first_golden_execution_blocker import inspect as inspect_execution

            execution_fn = inspect_execution
        else:
            execution_fn = execution_inspector
        execution = execution_fn()
        if execution.get("ready_for_authoritative_golden_preflight") is not True:
            blockers.append("FIRST_GOLDEN_EXECUTION_ENVIRONMENT_NOT_READY")

    for report_name, report in (("source", source), ("execution", execution)):
        if report is None:
            continue
        if report.get("network_download_authorized") is not False:
            blockers.append(f"{report_name.upper()}_NETWORK_AUTHORITY_DRIFT")
        if report.get("generation_authorized") is not False:
            blockers.append(f"{report_name.upper()}_GENERATION_AUTHORITY_DRIFT")
        if report.get("publication_ready") is not False:
            blockers.append(f"{report_name.upper()}_PUBLICATION_AUTHORITY_DRIFT")
        if report.get("seeds_2_to_4_authorized") is not False:
            blockers.append(f"{report_name.upper()}_SEED_AUTHORITY_DRIFT")

    ready = source_ready and execution is not None and execution.get("ready_for_authoritative_golden_preflight") is True and not blockers

    return {
        "schema": "pul7sar-phase18-first-golden-pre-gpu-probe-v1",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "expected_commit": expected_commit,
        "cost_mode_required": "$0-local",
        "source_identity": source,
        "execution_environment": execution,
        "source_identity_ready": source_ready,
        "execution_environment_evaluated": execution is not None,
        "ready_for_authoritative_golden_preflight": ready,
        "blockers": blockers,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prove source identity and local execution readiness before first-Golden GPU work")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = inspect(expected_commit=args.expected_commit)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = args.output if args.output.is_absolute() else ROOT / args.output
        target = target.resolve()
        root = ROOT.resolve()
        if target != root and root not in target.parents:
            raise RuntimeError("FIRST_GOLDEN_PRE_GPU_OUTPUT_ESCAPES_REPOSITORY")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if payload["ready_for_authoritative_golden_preflight"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
