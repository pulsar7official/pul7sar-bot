#!/usr/bin/env python3
"""Continue one exact CS344 checkpoint into CS281 final composed visual approval."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_final_presentation_evidence_to_final_composed_visual_approval import (
    continue_final_presentation_evidence_to_final_composed_visual_approval,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs344-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    run = continue_final_presentation_evidence_to_final_composed_visual_approval(
        args.cs344_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(run.receipt_path.read_text(encoding="utf-8"))
    print(run.receipt_path)
    print(f"status={payload['status']}")
    print(f"composed_visual_approved={payload['composed_visual_approved']}")
    print(f"semantic_approved={payload['semantic_approved']}")
    print(f"genuine_golden_png_created={payload['genuine_golden_png_created']}")
    print(f"publication_ready={payload['publication_ready']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
