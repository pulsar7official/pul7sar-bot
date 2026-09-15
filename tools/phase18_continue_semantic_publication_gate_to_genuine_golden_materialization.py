#!/usr/bin/env python3
"""Continue exact allowed CS348 result through existing CS285 Golden materialization."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_semantic_publication_gate_to_genuine_golden_materialization import (
    continue_semantic_publication_gate_to_genuine_golden_materialization,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs348-receipt", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    args = parser.parse_args()
    run = continue_semantic_publication_gate_to_genuine_golden_materialization(
        args.cs348_receipt,
        args.output_dir,
        repo_root=args.repo_root,
    )
    payload = json.loads(run.receipt_path.read_text(encoding="utf-8"))
    print(run.receipt_path)
    print(run.genuine_golden_visual_path)
    print(f"status={payload['status']}")
    print(f"semantic_publication_allowed={payload['semantic_publication_allowed']}")
    print(f"byte_identity_preserved={payload['byte_identity_preserved']}")
    print(f"genuine_golden_png_created={payload['genuine_golden_png_created']}")
    print(f"publication_ready={payload['publication_ready']}")
    print(f"authoritative={payload['authoritative']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
