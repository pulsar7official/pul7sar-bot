import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.phase18_colab_pitch_review as review


class FakeDiagnosticBuilder:
    def build(self, *, base_path: str, output_dir: str):
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)
        variants = []
        for preset in review.FootballCameraPreset:
            path = root / f"pitch-diagnostic-{preset.value}.png"
            path.write_bytes(b"diagnostic")
            variants.append({"camera_preset": preset.value, "png": str(path)})
        manifest = root / "pitch-diagnostics.json"
        manifest.write_text("{}", encoding="utf-8")
        return {
            "status": "FOOTBALL_PITCH_DIAGNOSTICS_READY",
            "publication_ready": False,
            "candidate_pixels_untouched": True,
            "manifest": str(manifest),
            "variants": variants,
        }


class ColabPitchReviewTests(unittest.TestCase):
    def _fixture(self, root: Path, *, candidate: int = 1) -> tuple[Path, Path]:
        base = root / "base.png"
        base.write_bytes(b"real-base-placeholder-for-contract-test")
        summary = root / "latest.json"
        summary.write_text(
            json.dumps(
                {
                    "branch": review.EXPECTED_BRANCH,
                    "manifest_version": review.EXPECTED_MANIFEST_VERSION,
                    "hybrid_surface_replacement_required": True,
                    "publication_ready": False,
                    "candidate": candidate,
                    "request_id": "golden-v5-test",
                    "seed": 7007001,
                    "model_id": "black-forest-labs/FLUX.2-klein-4B",
                    "png": str(base),
                }
            ),
            encoding="utf-8",
        )
        return summary, base

    def test_review_displays_base_and_every_preset_without_auto_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, base = self._fixture(root)
            displayed = []

            def fake_display(path: Path) -> bool:
                displayed.append(Path(path))
                return True

            with patch.object(review, "_branch", return_value=review.EXPECTED_BRANCH):
                payload = review.build_review(
                    summary_path=summary,
                    output_dir=root / "out",
                    candidate=1,
                    root=root,
                    display_fn=fake_display,
                    builder=FakeDiagnosticBuilder(),
                )

            self.assertEqual(payload["status"], "COLAB_PITCH_REVIEW_READY")
            self.assertFalse(payload["publication_ready"])
            self.assertTrue(payload["review_only"])
            self.assertTrue(payload["candidate_pixels_untouched"])
            self.assertIsNone(payload["selected_preset"])
            self.assertIsNone(payload["selected_review_png"])
            self.assertFalse(payload["selection_is_manual"])
            self.assertEqual(len(payload["variants"]), len(tuple(review.FootballCameraPreset)))
            self.assertEqual(displayed[0], base)
            self.assertEqual(len(displayed), 1 + len(tuple(review.FootballCameraPreset)))

    def test_explicit_selection_is_recorded_but_never_publication_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, _ = self._fixture(root)
            selected = review.FootballCameraPreset.SIDELINE_OBLIQUE.value
            with patch.object(review, "_branch", return_value=review.EXPECTED_BRANCH):
                payload = review.build_review(
                    summary_path=summary,
                    output_dir=root / "out",
                    candidate=1,
                    selected_preset=selected,
                    root=root,
                    display_fn=lambda path: False,
                    builder=FakeDiagnosticBuilder(),
                )

            self.assertEqual(payload["selected_preset"], selected)
            self.assertTrue(payload["selection_is_manual"])
            self.assertTrue(str(payload["selected_review_png"]).endswith(f"pitch-diagnostic-{selected}.png"))
            self.assertFalse(payload["publication_ready"])

    def test_stale_or_publication_ready_summary_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, _ = self._fixture(root)
            data = json.loads(summary.read_text(encoding="utf-8"))
            data["manifest_version"] = "pul7sar-golden-batch-v4"
            summary.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "STALE_GOLDEN_CONTRACT"):
                review._load_latest(summary, candidate=1, root=root)

            data["manifest_version"] = review.EXPECTED_MANIFEST_VERSION
            data["publication_ready"] = True
            summary.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "NON_PUBLICATION_SOURCE"):
                review._load_latest(summary, candidate=1, root=root)

    def test_candidate_mismatch_and_wrong_branch_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            summary, _ = self._fixture(root, candidate=1)
            with self.assertRaisesRegex(RuntimeError, "CANDIDATE_MISMATCH"):
                review._load_latest(summary, candidate=2, root=root)

            with patch.object(review, "_branch", return_value="main"):
                with self.assertRaisesRegex(RuntimeError, "COLAB_BRANCH_BLOCKED"):
                    review.build_review(
                        summary_path=summary,
                        output_dir=root / "out",
                        candidate=1,
                        root=root,
                        display_fn=lambda path: False,
                        builder=FakeDiagnosticBuilder(),
                    )


if __name__ == "__main__":
    unittest.main()
