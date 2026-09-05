#!/usr/bin/env python3
"""Build/verify CS276 without accepting request_id, seed, scores or blockers as CLI inputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    build_composed_candidate_golden_quality_adjudication,
    verify_composed_candidate_golden_quality_adjudication,
)


def _repo_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO_ROOT.resolve())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("path must remain inside repository") from exc
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cs263-receipt", type=_repo_path)
    parser.add_argument("--cs272-receipt", type=_repo_path)
    parser.add_argument("--cs275-receipt", type=_repo_path)
    parser.add_argument("--output-dir", type=_repo_path)
    parser.add_argument("--verify-receipt", type=_repo_path)
    args = parser.parse_args()

    if args.verify_receipt:
        if any((args.cs263_receipt, args.cs272_receipt, args.cs275_receipt, args.output_dir)):
            parser.error("--verify-receipt cannot be combined with build arguments")
        receipt = verify_composed_candidate_golden_quality_adjudication(
            args.verify_receipt, repo_root=REPO_ROOT
        )
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0

    if not all((args.cs263_receipt, args.cs272_receipt, args.cs275_receipt, args.output_dir)):
        parser.error("build mode requires --cs263-receipt --cs272-receipt --cs275-receipt --output-dir")
    path = build_composed_candidate_golden_quality_adjudication(
        args.cs263_receipt,
        args.cs272_receipt,
        args.cs275_receipt,
        args.output_dir,
        repo_root=REPO_ROOT,
    )
    receipt = verify_composed_candidate_golden_quality_adjudication(path, repo_root=REPO_ROOT)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
