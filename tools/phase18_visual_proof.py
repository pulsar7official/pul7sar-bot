#!/usr/bin/env python3
"""Register a real locally generated PNG as a PUL7SAR Phase 18 visual proof.

This command never installs a model, downloads weights, calls a paid API, or
creates a placeholder image. A real PNG and exact provenance must already exist.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.visual_proof import VisualProofArtifactWriter


def _load_provenance(path: str) -> LocalGenerationProvenance:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    required = ("provider_id", "model_id", "backend", "seed", "request_id", "width", "height")
    missing = [name for name in required if name not in data]
    if missing:
        raise ValueError("missing provenance fields: " + ", ".join(missing))
    metadata = {key: value for key, value in data.items() if key not in required}
    return LocalGenerationProvenance(
        provider_id=data["provider_id"],
        model_id=data["model_id"],
        backend=data["backend"],
        seed=data["seed"],
        request_id=data["request_id"],
        width=data["width"],
        height=data["height"],
        metadata=metadata,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a real $0-local Phase 18 visual proof PNG")
    parser.add_argument("--png", required=True, help="Path to a real generated PNG")
    parser.add_argument("--provenance", required=True, help="JSON provenance file")
    parser.add_argument("--output-dir", default="output/phase18_visual_proof")
    args = parser.parse_args()

    provenance = _load_provenance(args.provenance)
    artifact = VisualProofArtifactWriter(args.output_dir).register(
        png_path=args.png,
        provenance=provenance,
    )
    print(json.dumps({
        "status": "VISUAL_PROOF_REGISTERED",
        "png": artifact.png_path,
        "metadata": artifact.metadata_path,
        "width": artifact.observation.width,
        "height": artifact.observation.height,
        "aspect_ratio": artifact.observation.aspect_ratio,
        "cost_mode": "$0-local",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
