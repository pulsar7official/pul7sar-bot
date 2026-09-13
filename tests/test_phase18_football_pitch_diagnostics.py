import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_pitch_diagnostics import FootballPitchDiagnosticBuilder
from engine.intelligence.football_pitch_placement import FootballCameraPreset


class FootballPitchDiagnosticTests(unittest.TestCase):
    def test_builds_one_integrity_checked_variant_per_preset_without_mutating_base(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.png"
            out = root / "diagnostics"
            Image.new("RGB", (640, 800), (34, 88, 47)).save(base)
            before = base.read_bytes()

            payload = FootballPitchDiagnosticBuilder().build(
                base_path=str(base),
                output_dir=str(out),
            )

            self.assertEqual(payload["status"], "FOOTBALL_PITCH_DIAGNOSTICS_READY")
            self.assertTrue(payload["diagnostic_only"])
            self.assertFalse(payload["publication_ready"])
            self.assertTrue(payload["candidate_pixels_untouched"])
            self.assertEqual(payload["variant_count"], len(FootballCameraPreset))
            self.assertEqual(base.read_bytes(), before)

            variants = payload["variants"]
            self.assertEqual(
                {item["camera_preset"] for item in variants},
                {preset.value for preset in FootballCameraPreset},
            )
            for item in variants:
                self.assertTrue(Path(item["png"]).is_file())
                self.assertTrue(item["artifact_integrity"]["valid"])
                self.assertEqual(len(item["output_sha256"]), 64)

            manifest = Path(payload["manifest"])
            self.assertTrue(manifest.is_file())
            stored = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(stored["publication_ready"])
            self.assertNotIn("manifest", stored)

    def test_missing_base_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(FileNotFoundError):
                FootballPitchDiagnosticBuilder().build(
                    base_path=str(Path(temp) / "missing.png"),
                    output_dir=str(Path(temp) / "out"),
                )


if __name__ == "__main__":
    unittest.main()
