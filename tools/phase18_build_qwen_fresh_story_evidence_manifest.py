#!/usr/bin/env python3
"""Build Change Set 235's CPU-only byte-bound fresh-story evidence manifest."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_fresh_story_evidence_manifest import (
    build_fresh_story_evidence_manifest,
    verify_fresh_story_evidence_manifest,
)


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def _parse_evidence(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        gate, separator, path = value.partition("=")
        if not separator or not gate or not path:
            raise ValueError("Evidence must use GATE_ID=REPOSITORY_RELATIVE_PATH")
        if gate in parsed:
            raise ValueError(f"Duplicate evidence gate: {gate}")
        parsed[gate] = path
    if tuple(parsed.keys()) != REQUIRED_FRESH_GATE_EVIDENCE:
        expected = ", ".join(REQUIRED_FRESH_GATE_EVIDENCE)
        raise ValueError(f"Evidence gates must be supplied once and in canonical order: {expected}")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Bind exact bytes for all Change Set 233 fresh-story evidence requirements. "
            "This does not approve any story gate and cannot authorize generation."
        )
    )
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument(
        "--evidence",
        required=True,
        action="append",
        metavar="GATE_ID=PATH",
        help="Repeat once per required gate in the canonical order printed by --help.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    contract_path = args.contract
    if not contract_path.is_absolute():
        contract_path = repo_root / contract_path
    contract = _load_json(contract_path)
    evidence = _parse_evidence(args.evidence)

    manifest = build_fresh_story_evidence_manifest(
        contract,
        evidence,
        repo_root=repo_root,
    )
    verify_fresh_story_evidence_manifest(manifest, contract, repo_root=repo_root)

    output = args.output
    if not output.is_absolute():
        output = repo_root / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
