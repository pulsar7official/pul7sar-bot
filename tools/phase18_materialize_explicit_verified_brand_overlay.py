from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_explicit_verified_brand_overlay_materializer import (
    materialize_explicit_verified_brand_overlay,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize an exact, explicitly placed verified PUL7SAR brand tile into a full-canvas RGBA overlay."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt = materialize_explicit_verified_brand_overlay(
        manifest=manifest,
        output_path=args.output,
        repo_root=args.repo_root,
    )
    receipt_path = Path(args.receipt)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt.to_dict(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
