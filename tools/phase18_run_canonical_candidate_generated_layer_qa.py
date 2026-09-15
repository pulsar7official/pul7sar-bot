#!/usr/bin/env python3
"""Run CS268 generated-layer ownership QA on exact repository-bound receipts."""
from __future__ import annotations

import argparse
from pathlib import Path

from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    run_canonical_candidate_generated_layer_qa,
    verify_canonical_candidate_generated_layer_qa,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bind CS264/CS265/(when required) CS267 evidence to the existing HybridLayerQualityGate."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--cs264-receipt", type=Path, required=True)
    parser.add_argument("--cs265-receipt", type=Path, required=True)
    parser.add_argument("--cs267-receipt", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    run = run_canonical_candidate_generated_layer_qa(
        args.cs264_receipt,
        args.cs265_receipt,
        args.output_dir,
        repo_root=args.repo_root,
        cs267_receipt_path=args.cs267_receipt,
    )
    receipt = verify_canonical_candidate_generated_layer_qa(
        run.receipt_path, repo_root=args.repo_root
    )
    print(run.receipt_path)
    print(f"generated_layer_qa_approved={str(receipt['generated_layer_qa_approved']).lower()}")
    print(f"composition_executed={str(receipt['composition_executed']).lower()}")
    print(f"publication_ready={str(receipt['publication_ready']).lower()}")
    return 0 if run.generated_layer_qa_approved else 2


if __name__ == "__main__":
    raise SystemExit(main())
