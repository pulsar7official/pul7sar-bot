import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.provider_prompting import PromptConstraintCompiler
from tools.phase18_build_golden_batch import build_batch
from tools.phase18_build_golden_handoff import GOLDEN_BENCHMARK_ID, build_request
from tools.phase18_verify_golden_batch import verify_batch


class UnifiedScenePolicyTests(unittest.TestCase):
    def test_provider_reframes_legacy_collage_pitch_and_brand_constraints_for_flux_like_models(self):
        compiled = PromptConstraintCompiler().compile(
            (
                "no collage or multi-panel layout",
                "no split-screen, grid, diptych, triptych, or contact-sheet framing",
                "no image-within-image composition",
                "no malformed football pitch geometry",
                "no duplicate, missing, warped, or invented field markings",
                "no generated branding, wordmarks, readable text, or pseudo-text",
            ),
            supports_native_negative=False,
        )
        self.assertTrue(compiled.complete)
        self.assertEqual(compiled.native_negative_constraints, ())
        text = " ".join(compiled.positive_instructions).casefold()
        self.assertIn("one single continuous full-bleed editorial scene", text)
        self.assertIn("clean unbranded photographic base scene", text)
        self.assertIn("no legible words, letters, numerals", text)

    def test_golden_request_is_atmosphere_only_with_deterministic_pitch_replacement(self):
        request = build_request(seed=7007001, request_id="golden-season-opener-hybrid-v5-test")
        prompt = request.prompt.casefold()
        self.assertIn("one single continuous full-bleed editorial image", prompt)
        self.assertIn("never use collage, montage, split-screen, grid, diptych, triptych", prompt)
        self.assertNotIn("five visual zones", prompt)
        self.assertIn("unmarked neutral sport-surface region reserved for deterministic overlay", prompt)
        self.assertIn("no field/court/rink lines", prompt)
        self.assertIn("the exact surface will be replaced by deterministic code after generation", prompt)
        self.assertNotIn("exactly one halfway line", prompt)
        self.assertIn("fully unbranded", prompt)
        self.assertIn("platform names", prompt)
        self.assertNotIn("pul7sar", prompt)
        self.assertNotIn("pulsar", prompt)
        self.assertTrue(request.metadata["brand_name_redacted_from_generation_prompt"])
        self.assertFalse(request.metadata["generated_branding_allowed"])
        self.assertEqual(request.native_negative_constraints, ())

    def test_golden_v5_batch_round_trip_verifies_hybrid_geometry_and_brand_policy(self):
        with tempfile.TemporaryDirectory() as temp:
            manifest = build_batch(temp, seeds=(7007001, 7007002))
            self.assertEqual(manifest["manifest_version"], "pul7sar-golden-batch-v5")
            self.assertEqual(manifest["benchmark"], GOLDEN_BENCHMARK_ID)
            self.assertEqual(manifest["composition_grammar"], "single_continuous_scene")
            self.assertEqual(manifest["sport_geometry"], "deterministic_football_pitch_projective_v1")
            self.assertFalse(manifest["generated_sport_geometry_allowed"])
            self.assertTrue(manifest["hybrid_surface_replacement_required"])
            self.assertFalse(manifest["generated_branding_allowed"])
            self.assertEqual(manifest["brand_composition_policy"], "dynamic_deterministic_after_generation")
            verified = verify_batch(str(Path(temp) / "manifest.json"))
            self.assertEqual(verified["status"], "GOLDEN_BATCH_INTEGRITY_VERIFIED")
            self.assertEqual(verified["sport_geometry"], "deterministic_football_pitch_projective_v1")
            self.assertFalse(verified["generated_sport_geometry_allowed"])
            self.assertTrue(verified["hybrid_surface_replacement_required"])
            self.assertFalse(verified["generated_branding_allowed"])

    def test_v5_verifier_rejects_missing_composition_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, seeds=(7007001,))
            manifest_path = Path(temp) / "manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["composition_grammar"] = "multi_panel"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "single_continuous_scene"):
                verify_batch(str(manifest_path))

    def test_v5_verifier_rejects_generated_pitch_geometry_permission(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, seeds=(7007001,))
            manifest_path = Path(temp) / "manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["generated_sport_geometry_allowed"] = True
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Golden Hybrid v5 contract mismatch"):
                verify_batch(str(manifest_path))

    def test_v5_verifier_rejects_generated_branding_permission(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, seeds=(7007001,))
            manifest_path = Path(temp) / "manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["generated_branding_allowed"] = True
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Golden Hybrid v5 contract mismatch"):
                verify_batch(str(manifest_path))


if __name__ == "__main__":
    unittest.main()
