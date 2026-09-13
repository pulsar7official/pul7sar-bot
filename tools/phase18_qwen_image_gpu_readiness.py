#!/usr/bin/env python3
"""Print the local, zero-cost Qwen-Image static preflight as JSON."""
from __future__ import annotations

import argparse
import json

from engine.intelligence.qwen_image_gpu_readiness import inspect_qwen_image_gpu_readiness


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot-path",
        default=None,
        help="Existing local pinned Qwen/Qwen-Image-2512 snapshot path; no download is performed.",
    )
    parser.add_argument(
        "--require-static-ready",
        action="store_true",
        help="Return exit code 2 unless the static preflight is fully satisfied.",
    )
    args = parser.parse_args()

    result = inspect_qwen_image_gpu_readiness(snapshot_path=args.snapshot_path)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    if args.require_static_ready and not result.static_preflight_passed:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
