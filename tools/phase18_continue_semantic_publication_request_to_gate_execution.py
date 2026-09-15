#!/usr/bin/env python3
"""Continue exact CS347 request through existing CS284 SemanticPublicationGate execution."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_semantic_publication_request_to_gate_execution import (
    continue_semantic_publication_request_to_gate_execution,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs347-receipt", required=True, type=Path)
    parser.add_argument("--execution-evidence", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    run = continue_semantic_publication_request_to_gate_execution(
        args.cs347_receipt,
        args.execution_evidence,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(run.receipt_path.read_text(encoding="utf-8"))
    print(run.receipt_path)
    print(f"status={payload['status']}")
    print(f"semantic_publication_gate_executed={payload['semantic_publication_gate_executed']}")
    print(f"semantic_publication_allowed={payload['semantic_publication_allowed']}")
    print(f"base_scene_accepted={payload['base_scene_accepted']}")
    print(f"semantic_verifier_eligible={payload['semantic_verifier_eligible']}")
    print(f"genuine_golden_png_created={payload['genuine_golden_png_created']}")
    print(f"publication_ready={payload['publication_ready']}")
    print(f"authoritative={payload['authoritative']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
