from __future__ import annotations

import struct
import unittest
import zlib

from engine.intelligence.qwen_image_genuine_golden_materialization import (
    PNG_SIGNATURE,
    _require_cs284_authority,
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
            "composed_visual_approved": True,
            "semantic_approved": True,
            "semantic_publication_execution_requested": True,
            "semantic_publication_gate_executed": True,
            "semantic_publication_allowed": True,
            "semantic_publication_failures": [],
            "genuine_golden_png_created": False,
            "publication_ready": False,
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


if __name__ == "__main__":
    unittest.main()
