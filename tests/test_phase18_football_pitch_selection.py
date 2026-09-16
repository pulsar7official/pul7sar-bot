import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_pitch_selection import FootballPitchSelectionLock


class FootballPitchSelectionLockTests(unittest.TestCase):
    @staticmethod
    def _sha(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def _fixture(self, root: Path, *, manual: bool = True, publication_ready: bool = False):
        base = root / "base.png"
        variant = root / "pitch-diagnostic-high_wide_central.png"
        base.write_bytes(b"genuine-base-bytes")
        variant.write_bytes(b"selected-diagnostic-bytes")

        manifest = root / "pitch-diagnostics.json"
        manifest.write_text(json.dumps({
            "status": "FOOTBALL_PITCH_DIAGNOSTICS_READY",
            "diagnostic_only": True,
            "publication_ready": False,
            "base_png": str(base),
            "base_sha256": self._sha(base),
            "candidate_pixels_untouched": True,
            "variants": [{
                "camera_preset": "high_wide_central",
                "png": str(variant),
                "output_sha256": self._sha(variant),
                "artifact_integrity": {"valid": True, "failures": []},
            }],
        }), encoding="utf-8")

        review = root / "colab-pitch-review.json"
        review.write_text(json.dumps({
            "status": "COLAB_PITCH_REVIEW_READY",
            "review_only": True,
            "publication_ready": publication_ready,
            "candidate": 1,
            "request_id": "golden-v5-test",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "base_png": str(base),
            "diagnostic_manifest": str(manifest),
            "selected_preset": "high_wide_central" if manual else None,
            "selected_review_png": str(variant) if manual else None,
            "selection_is_manual": manual,
        }), encoding="utf-8")
        return base, variant, manifest, review

    def test_manual_selection_locks_exact_variant_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, variant, _, review = self._fixture(root)
            before = base.read_bytes()
            payload = FootballPitchSelectionLock().lock(
                review_path=str(review),
                output_dir=str(root / "locked"),
            )
            locked = Path(payload["locked_png"])
            self.assertTrue(locked.is_file())
            self.assertEqual(locked.read_bytes(), variant.read_bytes())
            self.assertEqual(payload["locked_png_sha256"], self._sha(variant))
            self.assertEqual(base.read_bytes(), before)
            self.assertTrue(payload["selection_is_manual"])
            self.assertFalse(payload["publication_ready"])
            self.assertTrue(payload["artifact_integrity_proven"])
            self.assertIn("semantic_publication", payload["gates_not_waived"])

    def test_auto_or_missing_selection_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, _, _, review = self._fixture(root, manual=False)
            with self.assertRaisesRegex(RuntimeError, "EXPLICIT_MANUAL_SELECTION"):
                FootballPitchSelectionLock().lock(
                    review_path=str(review), output_dir=str(root / "locked")
                )

    def test_publication_ready_review_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, _, _, review = self._fixture(root, publication_ready=True)
            with self.assertRaisesRegex(RuntimeError, "MUST_BE_NON_PUBLICATION"):
                FootballPitchSelectionLock().lock(
                    review_path=str(review), output_dir=str(root / "locked")
                )

    def test_tampered_selected_variant_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _, variant, _, review = self._fixture(root)
            variant.write_bytes(b"tampered-after-review")
            with self.assertRaisesRegex(RuntimeError, "VARIANT_SHA256_MISMATCH"):
                FootballPitchSelectionLock().lock(
                    review_path=str(review), output_dir=str(root / "locked")
                )

    def test_tampered_base_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base, _, _, review = self._fixture(root)
            base.write_bytes(b"changed-base-after-diagnostics")
            with self.assertRaisesRegex(RuntimeError, "BASE_SHA256_MISMATCH"):
                FootballPitchSelectionLock().lock(
                    review_path=str(review), output_dir=str(root / "locked")
                )


if __name__ == "__main__":
    unittest.main()
