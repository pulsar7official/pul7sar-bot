"""Visual-proof artifact contract for the first real $0 PUL7SAR generation.

This module never fabricates an image. It validates a real generated PNG and
writes deterministic JSON provenance next to it so GitHub Actions can expose the
result as a visual proof artifact.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.image_evidence_extraction import GeneratedImageObservation
from engine.intelligence.local_vision_inspectors import PngFileObserver


@dataclass(frozen=True)
class VisualProofArtifact:
    png_path: str
    metadata_path: str
    observation: GeneratedImageObservation
    provenance: LocalGenerationProvenance


class VisualProofArtifactWriter:
    """Validate and register a real PNG without inventing visual output."""

    def __init__(self, output_dir: str = "output/phase18_visual_proof") -> None:
        self.output_dir = Path(output_dir)
        self._observer = PngFileObserver()

    def register(
        self,
        *,
        png_path: str,
        provenance: LocalGenerationProvenance,
    ) -> VisualProofArtifact:
        source = Path(png_path)
        if not source.exists() or not source.is_file():
            raise FileNotFoundError(f"visual proof PNG does not exist: {source}")
        observation = self._observer.observe(str(source))
        if (observation.width, observation.height) != (provenance.width, provenance.height):
            raise ValueError("visual proof dimensions do not match generation provenance")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        target_png = self.output_dir / f"{provenance.request_id}.png"
        if source.resolve() != target_png.resolve():
            target_png.write_bytes(source.read_bytes())

        metadata_path = self.output_dir / f"{provenance.request_id}.json"
        metadata = provenance.as_provider_metadata()
        metadata.update({
            "output_ref": str(target_png),
            "aspect_ratio": observation.aspect_ratio,
            "visual_proof": True,
            "cost_mode": "$0-local",
        })
        metadata_path.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return VisualProofArtifact(
            png_path=str(target_png),
            metadata_path=str(metadata_path),
            observation=GeneratedImageObservation(
                str(target_png), observation.width, observation.height, observation.aspect_ratio
            ),
            provenance=provenance,
        )
