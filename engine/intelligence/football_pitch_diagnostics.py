"""Build non-publication football pitch integration diagnostics.

This module reuses an existing FLUX base PNG and renders the current deterministic
football composition across the approved camera presets. It never mutates the
base image and never marks any output publication-ready. The purpose is to
compare placement/integration choices before spending GPU time on another seed.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from engine.intelligence.football_hybrid_composer import FootballHybridComposer
from engine.intelligence.football_pitch_placement import FootballCameraPreset
from engine.intelligence.hybrid_artifact_integrity import HybridArtifactIntegrityGate


class FootballPitchDiagnosticBuilder:
    """Render one deterministic integration proof per approved camera preset."""

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def build(self, *, base_path: str, output_dir: str) -> dict[str, object]:
        base = Path(base_path)
        if not base.is_file():
            raise FileNotFoundError(base_path)
        before_sha = self._sha256(base)

        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        composer = FootballHybridComposer()
        integrity_gate = HybridArtifactIntegrityGate()
        variants: list[dict[str, object]] = []

        for preset in FootballCameraPreset:
            output = target_dir / f"pitch-diagnostic-{preset.value}.png"
            receipt = composer.compose_file(
                base_path=str(base),
                output_path=str(output),
                camera_preset=preset,
            )
            integrity = integrity_gate.validate_football(receipt)
            if not integrity.valid:
                raise RuntimeError(
                    "PITCH_DIAGNOSTIC_INTEGRITY_FAILED: " + ", ".join(integrity.failures)
                )
            variants.append(
                {
                    "camera_preset": preset.value,
                    "png": str(output),
                    "output_sha256": receipt.output_sha256,
                    "artifact_integrity": {
                        "valid": integrity.valid,
                        "failures": list(integrity.failures),
                    },
                    "composition_receipt": asdict(receipt),
                }
            )

        after_sha = self._sha256(base)
        if before_sha != after_sha:
            raise RuntimeError("PITCH_DIAGNOSTIC_MUTATED_BASE_IMAGE")

        payload: dict[str, object] = {
            "status": "FOOTBALL_PITCH_DIAGNOSTICS_READY",
            "diagnostic_only": True,
            "publication_ready": False,
            "base_png": str(base),
            "base_sha256": before_sha,
            "candidate_pixels_untouched": True,
            "variant_count": len(variants),
            "variants": variants,
            "review_rule": (
                "Choose a camera preset only from visual evidence on the real base PNG; "
                "diagnostics never waive semantic, factual, identity or Golden-quality gates."
            ),
        }
        manifest = target_dir / "pitch-diagnostics.json"
        manifest.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        payload["manifest"] = str(manifest)
        return payload
