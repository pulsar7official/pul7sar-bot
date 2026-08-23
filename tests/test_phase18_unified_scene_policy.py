import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.provider_prompting import PromptConstraintCompiler
from tools.phase18_build_golden_batch import build_batch
from tools.phase18_build_golden_handoff import GOLDEN_BENCHMARK_ID, build_request
from tools.phase18_verify_golden_batch import verify_batch


class UnifiedScenePolicyTests(unittest.TestCase):
    def test_provider_reframes_collage_constraints_for_flux_like_models(self):
        compiled = PromptConstraintCompiler().compile(
            (
                "no collage or multi-panel layout",
                "no split-screen, grid, diptych, triptych, or contact-sheet framing",
                "no image-within-image composition",
            ),
            supports_native_negative=False,
        )
        self.assertTrue(compiled.complete)
        self.assertEqual(compiled.native_negative_constraints, ())
        text = " ".join(compiled.positive_instructions).casefold()
        self.assertIn("one single continuous full-bleed editorial scene", text)
        self.assertIn("one uninterrupted photographic frame", text)
        self.assertIn("same coherent physical scene", text)

    def test_golden_request_is_locked_to_single_continuous_scene(self):
        request = build_request(seed=7007001, request_id="golden-general-season-opener-v2-test")
        prompt = request.prompt.casefold()
        self.assertIn("one single continuous full-bleed editorial image", prompt)
        self.assertIn("never use collage, montage, split-screen, grid, diptych, triptych", prompt)
        self.assertIn("same physical stadium world", prompt)
        self.assertNotIn("five visual zones", prompt)
        self.assertEqual(request.native_negative_constraints, ())

    def test_golden_v2_batch_round_trip_verifies_composition_grammar(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = build_batch(temp, seeds=(7007001, 7007002))
            self.assertEqual(manifest["manifest_version"], "pul7sar-golden-batch-v2")
            self.assertEqual(manifest["benchmark"], GOLDEN_BENCHMARK_ID)
            self.assertEqual(manifest["composition_grammar"], "single_continuous_scene")
            verified = verify_batch(str(Path(temp) / "manifest.json"))
            self.assertEqual(verified["status"], "GOLDEN_BATCH_INTEGRITY_VERIFIED")
            self.assertEqual(verified["composition_grammar"], "single_continuous_scene")

    def test_v2_verifier_rejects_missing_composition_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, seeds=(7007001,))
            manifest_path = Path(temp) / "manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["composition_grammar"] = "multi_panel"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "single_continuous_scene"):
                verify_batch(str(manifest_path))


if __name__ == "__main__":
    unittest.main()
