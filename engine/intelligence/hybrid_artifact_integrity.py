"""Integrity checks for deterministic hybrid composition artifacts.

Prevents stale/tampered PNGs or receipts from being reused as evidence for a
newer visual candidate. The receipt must still match the actual files on disk.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

from engine.intelligence.football_hybrid_composer import FootballHybridCompositionReceipt


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
            failures.append("generated_pitch_markings_not_replaced")
        if receipt.surface_opacity != 255:
            failures.append("surface_replacement_not_opaque")
        if not receipt.mowing_stripes_applied:
            failures.append("deterministic_surface_texture_missing")

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
