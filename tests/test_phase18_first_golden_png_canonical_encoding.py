from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.phase18_verify_first_genuine_golden_png_canonical_encoding import verify


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = "a" * 40
PNG_SHA = "b" * 64


def _structure(root: Path, **overrides) -> Path:
    payload = {
        "schema": "pul7sar-phase18-first-genuine-golden-png-structure-v3",
        "status": "FIRST_GENUINE_GOLDEN_PNG_STRUCTURE_VERIFIED",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "cost_mode": "$0-local",
        "offline_only": True,
        "source_commit_sha": SOURCE_SHA,
        "png_path": str(root / "candidate.png"),
        "png_sha256": PNG_SHA,
        "png_bytes": 123,
        "width": 1080,
        "height": 1350,
        "bit_depth": 8,
        "color_type": 2,
        "channels": 3,
        "bits_per_pixel": 24,
        "interlace_method": 0,
        "png_structure_verified": True,
        "crc_verified_for_all_chunks": True,
        "idat_zlib_stream_verified": True,
        "zlib_stream_terminated_exactly": True,
        "decoded_scanline_layout_verified": True,
        "scanline_filter_bytes_verified": True,
        "iend_terminal": True,
        "no_trailing_bytes": True,
        "canonical_encoding_verified": True,
        "canonical_encoding": "RGB8_TRUECOLOUR_NON_INTERLACED",
        "eligible_for_human_visual_review": True,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
    payload.update(overrides)
    path = root / "structure.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class FirstGoldenPngCanonicalEncodingTests(unittest.TestCase):
    def test_rgb8_non_interlaced_structure_v3_is_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = verify(structure_path=_structure(Path(tmp)))
            self.assertTrue(result["canonical_platform_encoding_verified"])
            self.assertEqual(result["canonical_color_mode"], "RGB8")
            self.assertEqual(result["bit_depth"], 8)
            self.assertEqual(result["color_type"], 2)
            self.assertEqual(result["channels"], 3)
            self.assertEqual(result["bits_per_pixel"], 24)
            self.assertFalse(result["human_visual_review_approved"])
            self.assertFalse(result["publication_ready"])

    def test_stale_structure_v2_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "STRUCTURE_SCHEMA_DRIFT"):
                verify(structure_path=_structure(Path(tmp), schema="pul7sar-phase18-first-genuine-golden-png-structure-v2"))

    def test_missing_cs481_canonical_proof_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "STRUCTURE_FLAG_DRIFT:canonical_encoding_verified"):
                verify(structure_path=_structure(Path(tmp), canonical_encoding_verified=False))

    def test_canonical_contract_label_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "CONTRACT_DRIFT"):
                verify(structure_path=_structure(Path(tmp), canonical_encoding="RGB8"))

    def test_rgba_structure_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "PIXEL_FORMAT_DRIFT:color_type"):
                verify(structure_path=_structure(Path(tmp), color_type=6, channels=4, bits_per_pixel=32))

    def test_16_bit_rgb_structure_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "PIXEL_FORMAT_DRIFT:bit_depth"):
                verify(structure_path=_structure(Path(tmp), bit_depth=16, bits_per_pixel=48))

    def test_interlaced_structure_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "PIXEL_FORMAT_DRIFT:interlace_method"):
                verify(structure_path=_structure(Path(tmp), interlace_method=1))

    def test_incomplete_structural_proof_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "STRUCTURE_FLAG_DRIFT:crc_verified_for_all_chunks"):
                verify(structure_path=_structure(Path(tmp), crc_verified_for_all_chunks=False))

    def test_authority_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:publication_ready"):
                verify(structure_path=_structure(Path(tmp), publication_ready=True))

    def test_platform_normalizer_contract_remains_rgb_png(self) -> None:
        source = (ROOT / "engine/intelligence/canvas_normalization.py").read_text(encoding="utf-8")
        self.assertIn('image = image.convert("RGB")', source)
        self.assertIn('image.save(destination, format="PNG", optimize=True)', source)


if __name__ == "__main__":
    unittest.main()
