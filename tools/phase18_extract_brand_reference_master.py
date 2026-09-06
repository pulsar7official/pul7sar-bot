#!/usr/bin/env python3
"""Reproduce the exact Phase 18 PUL7SAR brand reference crop from the approved board.

The approved identity board itself is user-owned reference evidence and is not
committed here as a publication asset. Given the exact source board bytes, this
command verifies SHA-256 and dimensions before extracting the locked crop.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

from PIL import Image

from engine.intelligence.brand_reference_master import APPROVED_BRAND_REFERENCE_MASTER


def extract(source_path: str, output_path: str) -> str:
    ref = APPROVED_BRAND_REFERENCE_MASTER
    ref.assert_safe()
    source = Path(source_path)
    payload = source.read_bytes()
    actual = sha256(payload).hexdigest()
    if actual != ref.source_sha256:
        raise ValueError("approved brand reference source checksum mismatch")
    with Image.open(source) as image:
        if image.size != (ref.source_width, ref.source_height):
            raise ValueError("approved brand reference source dimensions mismatch")
        crop = image.convert("RGBA").crop((ref.crop_left, ref.crop_top, ref.crop_right, ref.crop_bottom))
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        crop.save(target, format="PNG")
    digest = sha256(Path(output_path).read_bytes()).hexdigest()
    if digest != ref.crop_sha256:
        raise ValueError("extracted brand reference crop checksum mismatch")
    return digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("output")
    args = parser.parse_args()
    print(extract(args.source, args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
