import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.provider_prompting import PromptConstraintCompiler
from tools.phase18_build_golden_batch import build_batch
from tools.phase18_build_golden_handoff import GOLDEN_BENCHMARK_ID, build_request
from tools.phase18_verify_golden_batch import verify_batch


class UnifiedScenePolicyTests(unittest.TestCase):
    def test_provider_reframes_collage_and_pitch_geometry_constraints_for_flux_like_models(self):
        compiled = PromptConstraintCompiler().compile(
            (
                "no collage or multi-panel layout",
                "no split-screen, grid, diptych, triptych, or contact-sheet framing",
                "no image-within-image composition",
                "no malformed football pitch geometry",
                "no duplicate, missing, warped, or invented field markings",
            ),
            supports_native_negative=False,
        )
        self.assertTrue(compiled.complete)
        self.assertEqual(compiled.native_negative_constraints, ())
        text = " ".join(compiled.positive_instructions).casefold()
        self.assertIn("one single continuous full-bleed editorial scene", text)
        self.assertIn("one uninterrupted photographic frame", text)
        self.assertIn("same coherent physical scene", text)
        self.assertIn("regulation association-football pitch geometry", text)
        self.assertIn("exactly one halfway line", text)
        self.assertIn("do not duplicate the halfway line or centre circle", text)

    def test_golden_request_is_locked_to_single_scene_and_regulation_pitch(self):
        request = build_request(seed=7007001, request_id="golden-general-season-opener-v3-test")
        prompt = request.prompt.casefold()
        self.assertIn("one single continuous full-bleed editorial image", prompt)
        self.assertIn("never use collage, montage, split-screen, grid, diptych, triptych", prompt)
        self.assertIn("same physical stadium world", prompt)
        self.assertNotIn("five visual zones", prompt)
        self.assertIn("regulation association-football pitch geometry", prompt)
        self.assertIn("exactly one halfway line", prompt)
        self.assertIn("exactly one circular centre circle", prompt)
        self.assertIn("do not duplicate the halfway line or centre circle", prompt)
        self.assertEqual(request.native_negative_constraints, ())

    def test_golden_v3_batch_round_trip_verifies_composition_and_pitch_geometry(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = build_batch(temp, seeds=(7007001, 7007002))
            self.assertEqual(manifest["manifest_version"], "pul7sar-golden-batch-v3")
            self.assertEqual(manifest["benchmark"], GOLDEN_BENCHMARK_ID)
            self.assertEqual(manifest["composition_grammar"], "single_continuous_scene")
            self.assertEqual(manifest["sport_geometry"], "association_football_regulation_pitch")
            verified = verify_batch(str(Path(temp) / "manifest.json"))
            self.assertEqual(verified["status"], "GOLDEN_BATCH_INTEGRITY_VERIFIED")
            self.assertEqual(verified["composition_grammar"], "single_continuous_scene")
            self.assertEqual(verified["sport_geometry"], "association_football_regulation_pitch")

    def test_v3_verifier_rejects_missing_composition_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, seeds=(7007001,))
            manifest_path = Path(temp) / "manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["composition_grammar"] = "multi_panel"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "single_continuous_scene"):
                verify_batch(str(manifest_path))

    def test_v3_verifier_rejects_missing_pitch_geometry_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, seeds=(7007001,))
            manifest_path = Path(temp) / "manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["sport_geometry"] = "decorative_pitch"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "regulation association-football pitch geometry"):
                verify_batch(str(manifest_path))


if __name__ == "__main__":
    unittest.main()
