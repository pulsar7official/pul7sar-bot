from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_materialized_overlay_composition_manifest_bundle import (
    build_materialized_overlay_composition_manifest_bundle,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build exact CS269/CS270 manifests from verified CS332/CS333 materialized overlays."
    )
    parser.add_argument("--cs268-receipt", required=True)
    parser.add_argument("--typography-receipt", required=True)
    parser.add_argument("--brand-manifest", required=True)
    parser.add_argument("--brand-receipt", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    receipt_path = build_materialized_overlay_composition_manifest_bundle(
        Path(args.cs268_receipt),
        Path(args.typography_receipt),
        Path(args.brand_manifest),
        Path(args.brand_receipt),
        Path(args.output_dir),
        repo_root=Path(args.repo_root),
    )
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    print(json.dumps(receipt, ensure_ascii=False, sort_keys=True))
    return 0 if receipt.get("composition_input_binding_ready") is True else 2


if __name__ == "__main__":
    raise SystemExit(main())
