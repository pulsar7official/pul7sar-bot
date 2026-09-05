from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.qwen_image_retrieved_source_byte_binding import bind_retrieved_source_bytes


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Byte-bind already retrieved source documents into a Change Set 253 story manifest."
    )
    parser.add_argument("draft_manifest", type=Path)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    result = bind_retrieved_source_bytes(args.draft_manifest, args.source_root, args.output_dir)
    print(json.dumps({
        "bound_manifest_path": str(result.bound_manifest_path),
        "binding_receipt_path": str(result.binding_receipt_path),
        "source_digests": dict(result.source_digests),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
