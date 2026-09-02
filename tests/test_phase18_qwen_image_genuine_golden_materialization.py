from __future__ import annotations

import struct
import unittest
import zlib

from engine.intelligence.qwen_image_genuine_golden_materialization import (
    MATERIALIZATION_POLICY,
    PNG_SIGNATURE,
    _require_cs284_authority,
    _require_materialization_receipt_matches_cs284,
    _validate_png_bytes,
)


def _chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type)
    crc = zlib.crc32(data, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def _valid_png(width: int = 2, height: int = 3) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw_scanlines = b"".join(b"\x00" + (b"\x00\x00\x00" * width) for _ in range(height))
    return PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(raw_scanlines)) + _chunk(b"IEND", b"")


class TestPhase18QwenImageGenuineGoldenMaterialization(unittest.TestCase):
    def _allowed_cs284(self):
        return {
            "story_snapshot_sha256": "story-sha",
            "composed_candidate_png": {
                "repository_relative_path": "artifacts/composed.png",
                "sha256": "png-sha",
                "byte_size": 123,
            },
            "generation_context": {
                "cost_mode": "$0-local",
                "network_allowed": False,
                "local_files_only": True,
            },
            "weighted_score": 0.97,
            "quality_tier": "golden",
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "semantic_publication_failures": [],
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def _matching_cs285_receipt(self):
        cs284 = self._allowed_cs284()
        return {
            "story_snapshot_sha256": cs284["story_snapshot_sha256"],
            "source_composed_candidate_png": dict(cs284["composed_candidate_png"]),
            "generation_context": dict(cs284["generation_context"]),
            "weighted_score": cs284["weighted_score"],
            "quality_tier": cs284["quality_tier"],
            "policy": dict(MATERIALIZATION_POLICY),
        }

    def test_valid_png_container_returns_dimensions(self):
        self.assertEqual(_validate_png_bytes(_valid_png(7, 11)), (7, 11))

    def test_corrupted_png_crc_is_rejected(self):
        raw = bytearray(_valid_png())
        raw[-5] ^= 0x01
        with self.assertRaisesRegex(ValueError, "CRC_INVALID"):
            _validate_png_bytes(bytes(raw))

    def test_non_png_payload_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "SIGNATURE_INVALID"):
            _validate_png_bytes(b"synthetic fixture")

    def test_cs284_must_have_real_publication_allowance(self):
        state = self._allowed_cs284()
        state["semantic_publication_allowed"] = False
        with self.assertRaisesRegex(ValueError, "semantic_publication_allowed"):
            _require_cs284_authority(state)

    def test_cs284_with_failures_cannot_materialize_golden(self):
        state = self._allowed_cs284()
        state["semantic_publication_failures"] = ["identity mismatch"]
        with self.assertRaisesRegex(ValueError, "FAILURE_STATE_INVALID"):
            _require_cs284_authority(state)

    def test_premature_golden_or_publication_state_is_rejected(self):
        state = self._allowed_cs284()
        state["genuine_golden_png_created"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_GOLDEN_STATE"):
            _require_cs284_authority(state)

        state = self._allowed_cs284()
        state["publication_ready"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_PUBLICATION_STATE"):
            _require_cs284_authority(state)

    def test_exact_cs284_metadata_lineage_is_accepted(self):
        _require_materialization_receipt_matches_cs284(
            self._matching_cs285_receipt(),
            self._allowed_cs284(),
        )

    def test_generation_context_drift_is_rejected(self):
        receipt = self._matching_cs285_receipt()
        receipt["generation_context"]["network_allowed"] = True
        with self.assertRaisesRegex(ValueError, "generation_context"):
            _require_materialization_receipt_matches_cs284(receipt, self._allowed_cs284())

    def test_weighted_score_drift_is_rejected(self):
        receipt = self._matching_cs285_receipt()
        receipt["weighted_score"] = 0.01
        with self.assertRaisesRegex(ValueError, "weighted_score"):
            _require_materialization_receipt_matches_cs284(receipt, self._allowed_cs284())

    def test_quality_tier_drift_is_rejected(self):
        receipt = self._matching_cs285_receipt()
        receipt["quality_tier"] = "unreviewed"
        with self.assertRaisesRegex(ValueError, "quality_tier"):
            _require_materialization_receipt_matches_cs284(receipt, self._allowed_cs284())

    def test_materialization_policy_drift_is_rejected(self):
        receipt = self._matching_cs285_receipt()
        receipt["policy"]["pixel_mutation_forbidden"] = False
        with self.assertRaisesRegex(ValueError, "POLICY_DRIFT"):
            _require_materialization_receipt_matches_cs284(receipt, self._allowed_cs284())


if __name__ == "__main__":
    unittest.main()