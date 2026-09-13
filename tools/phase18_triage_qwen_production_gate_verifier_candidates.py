#!/usr/bin/env python3
"""CPU-only CLI for Change Set 243 production verifier candidate triage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_production_gate_verifier_candidate_triage import (
    build_production_gate_verifier_candidate_triage,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()
    receipt = build_production_gate_verifier_candidate_triage(
        repo_root=Path(args.repo_root)
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
