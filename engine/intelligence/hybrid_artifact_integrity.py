"""Integrity checks for deterministic hybrid composition artifacts.

Prevents stale/tampered PNGs or receipts from being reused as evidence for a
newer visual candidate. The receipt must still match the actual files on disk.
The current football contract is texture-preserving: exact geometry is owned by
code without painting an opaque tactical-board surface over the source image.
The surface colour normalization must also use an inward feather so the final
pitch does not present a hard-edged pasted quadrilateral.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from engine.intelligence.football_hybrid_composer import (
    FOOTBALL_GEOMETRY_RENDERER_ID,
    FootballHybridCompositionReceipt,
    TEXTURE_PRESERVING_COMPOSITION_MODE,
)


@dataclass(frozen=True)
class HybridArtifactIntegrityDecision:
    valid: bool
    failures: tuple[str, ...]


class HybridArtifactIntegrityGate:
    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _validate_geometry_snapshot(receipt: FootballHybridCompositionReceipt, failures: list[str]) -> None:
        if receipt.geometry_renderer_id != FOOTBALL_GEOMETRY_RENDERER_ID:
            failures.append("unexpected_football_geometry_renderer")

        snapshot = receipt.geometry_integrity
        if not isinstance(snapshot, dict):
            failures.append("football_geometry_integrity_missing")
            return
        if snapshot.get("status") != "REGULATION_FOOTBALL_GEOMETRY_READY":
            failures.append("football_geometry_integrity_not_ready")
        if snapshot.get("length_m") != 105.0 or snapshot.get("width_m") != 68.0:
            failures.append("football_geometry_dimensions_mismatch")
        expected_counts = {
            "halfway_line_count": 1,
            "centre_circle_count": 1,
            "centre_mark_count": 1,
            "penalty_mark_count": 2,
            "penalty_arc_count": 2,
            "corner_arc_count": 4,
            "penalty_area_count": 2,
            "goal_area_count": 2,
        }
        for key, expected in expected_counts.items():
            if snapshot.get(key) != expected:
                failures.append(f"football_geometry_{key}_mismatch")
        if snapshot.get("symmetric_penalty_areas") is not True:
            failures.append("football_geometry_penalty_areas_not_symmetric")

    def validate_football(self, receipt: FootballHybridCompositionReceipt) -> HybridArtifactIntegrityDecision:
        if not isinstance(receipt, FootballHybridCompositionReceipt):
            raise TypeError("receipt must be FootballHybridCompositionReceipt")
        failures: list[str] = []
        source = Path(receipt.input_path)
        output = Path(receipt.output_path)

        if receipt.status != "FOOTBALL_HYBRID_SURFACE_COMPOSED":
            failures.append("unexpected_composition_status")
        if not source.is_file():
            failures.append("base_artifact_missing")
        if not output.is_file():
            failures.append("hybrid_artifact_missing")
        if not receipt.deterministic_geometry_applied:
            failures.append("deterministic_geometry_not_applied")
        if not receipt.generated_pitch_markings_replaced:
            failures.append("deterministic_markings_not_authoritative")
        if receipt.composition_mode != TEXTURE_PRESERVING_COMPOSITION_MODE:
            failures.append("unexpected_football_composition_mode")
        if not receipt.source_texture_preserved:
            failures.append("source_pitch_texture_not_preserved")
        if not 24 <= receipt.surface_opacity <= 96:
            failures.append("surface_normalization_opacity_out_of_range")
        if not 8 <= receipt.surface_feather_px <= 48:
            failures.append("surface_boundary_feather_out_of_range")

        self._validate_geometry_snapshot(receipt, failures)

        if source.is_file():
            actual = self._sha256(source)
            if len(receipt.input_sha256) != 64 or actual != receipt.input_sha256:
                failures.append("base_artifact_sha256_mismatch")
        if output.is_file():
            actual = self._sha256(output)
            if len(receipt.output_sha256) != 64 or actual != receipt.output_sha256:
                failures.append("hybrid_artifact_sha256_mismatch")
        if receipt.input_sha256 and receipt.output_sha256 and receipt.input_sha256 == receipt.output_sha256:
            failures.append("hybrid_output_identical_to_base")

        return HybridArtifactIntegrityDecision(not failures, tuple(dict.fromkeys(failures)))
