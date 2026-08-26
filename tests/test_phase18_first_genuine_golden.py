import json
import tempfile
import unittest
from pathlib import Path

import tools.phase18_colab_first_genuine_golden as golden


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"pul7sar-golden"


class FirstGenuineGoldenTests(unittest.TestCase):
    def _fixtures(self, root: Path):
        png = root / "candidate-01.png"
        latest = root / "latest.json"
        semantic = root / "semantic.json"
        png.write_bytes(PNG_BYTES)
        latest.write_text(json.dumps({
            "manifest_version": golden.EXPECTED_MANIFEST_VERSION,
            "benchmark": golden.EXPECTED_BENCHMARK,
            "candidate": 1,
            "publication_ready": False,
            "visual_grammar_surface_visibility": "context_only",
            "hybrid_surface_replacement_required": False,
            "focal_anchor": golden.EXPECTED_FOCAL_ANCHOR,
            "copy_negative_space": golden.EXPECTED_COPY_NEGATIVE_SPACE,
            "brand_quiet_zone": golden.EXPECTED_BRAND_QUIET_ZONE,
            "png": str(png),
        }), encoding="utf-8")
        semantic.write_text(json.dumps({
            "status": golden.EXPECTED_RECEIPT_STATUS,
            "candidate": 1,
            "publication_ready": False,
            "deterministic_pitch_applied": False,
            "pitch_replacement_required": False,
            "editorial_png": str(png),
            "semantic_visual_inspection": {"approved": True},
            "base_scene_layer_gate": {"allowed": True, "inspection_complete": True},
        }), encoding="utf-8")
        return png, latest, semantic

    def test_verified_candidate_stays_review_only(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            png, latest, semantic = self._fixtures(Path(temp))
            expected_sha = golden._sha256(png)
            payload = golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)
        self.assertEqual(payload["status"], "FIRST_GENUINE_GOLDEN_EDITORIAL_CANDIDATE_READY_FOR_HUMAN_REVIEW")
        self.assertEqual(payload["png_sha256"], expected_sha)
        self.assertTrue(payload["semantic_approved"])
        self.assertTrue(payload["layer_ownership_approved"])
        self.assertTrue(payload["human_visual_review_required"])
        self.assertFalse(payload["golden_quality_approved"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])
        self.assertFalse(payload["deterministic_pitch_applied"])

    def test_engineering_or_failed_semantic_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic = self._fixtures(Path(temp))
            payload = json.loads(semantic.read_text(encoding="utf-8"))
            payload["status"] = "GOLDEN_EDITORIAL_ENGINEERING_PROOF"
            payload["semantic_visual_inspection"] = {"approved": False}
            semantic.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_RECEIPT_NOT_APPROVED"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_composition_map_drift_is_rejected_before_review(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic = self._fixtures(Path(temp))
            payload = json.loads(latest.read_text(encoding="utf-8"))
            payload["focal_anchor"] = "center_pitch"
            latest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "COMPOSITION_MAP_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_pitch_replacement_regression_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic = self._fixtures(Path(temp))
            payload = json.loads(latest.read_text(encoding="utf-8"))
            payload["hybrid_surface_replacement_required"] = True
            latest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "MUST_NOT_REQUIRE_PITCH_REPLACEMENT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_png_path_drift_between_generation_and_semantic_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            root = Path(temp)
            _, latest, semantic = self._fixtures(root)
            other = root / "other.png"
            other.write_bytes(PNG_BYTES + b"other")
            payload = json.loads(semantic.read_text(encoding="utf-8"))
            payload["editorial_png"] = str(other)
            semantic.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "PNG_PATH_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_cli_source_forces_candidate_one_and_strict_semantic(self):
        source = Path(golden.__file__).read_text(encoding="utf-8")
        self.assertIn('"--candidate", "1"', source)
        self.assertIn('"--semantic-inspection", "qwen"', source)
        self.assertIn('"--strict-semantic"', source)
        self.assertNotIn('"--candidate", str(args.candidate)', source)


if __name__ == "__main__":
    unittest.main()
