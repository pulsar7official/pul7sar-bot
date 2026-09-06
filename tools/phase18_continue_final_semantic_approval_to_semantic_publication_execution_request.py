#!/usr/bin/env python3
"""Continue one exact CS346 checkpoint into existing CS283 SemanticPublicationGate request."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_final_semantic_approval_to_semantic_publication_execution_request import (
    continue_final_semantic_approval_to_semantic_publication_execution_request,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs346-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    run = continue_final_semantic_approval_to_semantic_publication_execution_request(
        args.cs346_receipt, args.output_dir, repo_root=args.repo_root
    )
    payload = json.loads(run.receipt_path.read_text(encoding="utf-8"))
    print(run.receipt_path)
    print(f"status={payload['status']}")
    print(f"semantic_publication_execution_requested={payload['semantic_publication_execution_requested']}")
    print(f"semantic_publication_gate_executed={payload['semantic_publication_gate_executed']}")
    print(f"semantic_publication_allowed={payload['semantic_publication_allowed']}")
    print(f"genuine_golden_png_created={payload['genuine_golden_png_created']}")
    print(f"publication_ready={payload['publication_ready']}")
    print(f"authoritative={payload['authoritative']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
