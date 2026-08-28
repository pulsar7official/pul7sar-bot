#!/usr/bin/env python3
"""Audit the canonical Change Set 238 production verifier registry without inference."""
from __future__ import annotations

import argparse
import json

from engine.intelligence.qwen_image_production_gate_verifier_readiness import (
    audit_production_gate_verifier_readiness,
)
from engine.intelligence.qwen_image_production_gate_verifier_registry import (
    GATE_REPLAY_VERIFIERS,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit whether all six production fresh-story replay verifiers are bound. "
            "This command never loads model weights, executes Qwen inference, or grants "
            "canonical-generation/publication authority."
        )
    )
    parser.parse_args()

    receipt = audit_production_gate_verifier_readiness(GATE_REPLAY_VERIFIERS)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["all_production_verifiers_bound"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
