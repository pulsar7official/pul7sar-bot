import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import tools.phase18_continue_hybrid_from_first_png as continuation


PNG = b"\x89PNG\r\n\x1a\nsemantic-test-payload"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FirstPngEditorialSemanticContinuationTests(unittest.TestCase):
    def _fixture(self, root: Path):
        base = root / "base.png"
        base.write_bytes(PNG + b"-base")
        handoff = root / "latest.json"
        handoff.write_text(json.dumps({
            "status": continuation.EXPECTED_HANDOFF_STATUS,
            "branch": continuation.EXPECTED_BRANCH,
            "manifest_version": continuation.EXPECTED_MANIFEST,
            "candidate": 1,
            "cost_mode": "$0-local",
            "resolved_dtype": "bfloat16",
            "hybrid_surface_replacement_required": False,
            "generated_sport_geometry_allowed": False,
            "generated_branding_allowed": False,
            "visual_grammar_surface_visibility": "context_only",
            "football_camera_preset": "editorial_environmental_oblique",
            "visual_priority": continuation.EXPECTED_VISUAL_PRIORITY,
            "focal_anchor": continuation.EXPECTED_FOCAL_ANCHOR,
            "copy_negative_space": continuation.EXPECTED_COPY_NEGATIVE_SPACE,
            "brand_quiet_zone": continuation.EXPECTED_BRAND_QUIET_ZONE,
            "publication_ready": False,
            "png": str(base.resolve()),
            "base_png_sha256": sha256(base),
        }), encoding="utf-8")
        result = {
            "status": "GOLDEN_EDITORIAL_BASE_SEMANTICALLY_CLEAN",
            "candidate": 1,
            "editorial_png": str(base.resolve()),
            "visual_grammar_surface_visibility": "context_only",
            "visual_priority": continuation.EXPECTED_VISUAL_PRIORITY,
            "focal_anchor": continuation.EXPECTED_FOCAL_ANCHOR,
            "copy_negative_space": continuation.EXPECTED_COPY_NEGATIVE_SPACE,
            "brand_quiet_zone": continuation.EXPECTED_BRAND_QUIET_ZONE,
            "deterministic_pitch_applied": False,
            "pitch_replacement_required": False,
            "base_scene_layer_gate": {"allowed": True, "inspection_complete": True, "blockers": []},
            "semantic_visual_inspection": {
                "status": "SEMANTIC_VISUAL_INSPECTION_COMPLETE",
                "approved": True,
                "failures": [],
            },
            "dynamic_brand_applied": False,
            "typography_applied": False,
            "publication_ready": False,
        }
        return handoff, result

    def test_success_preserves_first_png_pixels_and_keeps_publication_closed(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            output = root / "receipt.json"
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_review_editorial_base", return_value=result),
            ):
                receipt = continuation.run(candidate=1, handoff_path=handoff, output_path=output)
            self.assertEqual(receipt["schema"], "pul7sar-first-png-editorial-semantic-continuation-v3")
            self.assertEqual(receipt["status"], "FIRST_GOLDEN_EDITORIAL_SEMANTIC_PROOF_READY")
            self.assertTrue(receipt["pixel_identity_preserved"])
            self.assertTrue(receipt["semantic_layer_gate_approved"])
            self.assertTrue(receipt["composition_map_locked"])
            self.assertEqual(receipt["visual_priority"], continuation.EXPECTED_VISUAL_PRIORITY)
            self.assertEqual(receipt["focal_anchor"], continuation.EXPECTED_FOCAL_ANCHOR)
            self.assertEqual(receipt["copy_negative_space"], continuation.EXPECTED_COPY_NEGATIVE_SPACE)
            self.assertEqual(receipt["brand_quiet_zone"], continuation.EXPECTED_BRAND_QUIET_ZONE)
            self.assertFalse(receipt["deterministic_pitch_applied"])
            self.assertFalse(receipt["pitch_replacement_required"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["publication_ready"])
            self.assertTrue(output.is_file())

    def test_handoff_composition_map_drift_is_rejected_before_semantic_review(self):
        for key, bad in (
            ("visual_priority", "sport_surface_before_story"),
            ("focal_anchor", "center_pitch"),
            ("copy_negative_space", "none"),
            ("brand_quiet_zone", "lower_right"),
        ):
            with self.subTest(key=key), tempfile.TemporaryDirectory(dir=".") as temp:
                root = Path(temp)
                handoff, result = self._fixture(root)
                payload = json.loads(handoff.read_text(encoding="utf-8"))
                payload[key] = bad
                handoff.write_text(json.dumps(payload), encoding="utf-8")
                with (
                    patch.object(continuation, "LATEST", handoff),
                    patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                    patch.object(continuation, "_review_editorial_base", return_value=result) as review,
                ):
                    with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_HANDOFF_COMPOSITION_MAP_DRIFT"):
                        continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")
                    review.assert_not_called()

    def test_semantic_result_composition_map_drift_is_rejected(self):
        for key, bad in (
            ("visual_priority", "sport_surface_before_story"),
            ("focal_anchor", "center_pitch"),
            ("copy_negative_space", "none"),
            ("brand_quiet_zone", "lower_right"),
        ):
            with self.subTest(key=key), tempfile.TemporaryDirectory(dir=".") as temp:
                root = Path(temp)
                handoff, result = self._fixture(root)
                result[key] = bad
                with (
                    patch.object(continuation, "LATEST", handoff),
                    patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                    patch.object(continuation, "_review_editorial_base", return_value=result),
                ):
                    with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_SEMANTIC_RESULT_COMPOSITION_MAP_DRIFT"):
                        continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")

    def test_base_semantic_failure_is_fail_closed(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            result["semantic_visual_inspection"]["approved"] = False
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_review_editorial_base", return_value=result),
            ):
                with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_BASE_SEMANTIC_FAILED"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")

    def test_pitch_reintroduction_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            result["deterministic_pitch_applied"] = True
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_review_editorial_base", return_value=result),
            ):
                with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_PITCH_MUST_NOT_BE_APPLIED"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")

    def test_publication_authority_drift_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            result["publication_ready"] = True
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_review_editorial_base", return_value=result),
            ):
                with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_PUBLICATION_AUTHORITY_DRIFT"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")

    def test_handoff_tampering_is_rejected_before_semantic_review(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            payload = json.loads(handoff.read_text(encoding="utf-8"))
            payload["base_png_sha256"] = "0" * 64
            handoff.write_text(json.dumps(payload), encoding="utf-8")
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_review_editorial_base", return_value=result) as review,
            ):
                with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_BASE_PNG_SHA256_MISMATCH"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")
                review.assert_not_called()

    def test_noncanonical_handoff_is_rejected_before_semantic_review(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            canonical = root / "canonical-latest.json"
            canonical.write_bytes(handoff.read_bytes())
            with (
                patch.object(continuation, "LATEST", canonical),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_review_editorial_base", return_value=result) as review,
            ):
                with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_CANONICAL_HANDOFF_REQUIRED"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")
                review.assert_not_called()

    def test_branch_and_candidate_remain_locked(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, _ = self._fixture(root)
            with patch.object(continuation, "LATEST", handoff), patch.object(continuation, "_branch", return_value="main"):
                with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_BRANCH_BLOCKED"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")
            with patch.object(continuation, "LATEST", handoff), patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH):
                with self.assertRaisesRegex(RuntimeError, "EDITORIAL_CONTINUATION_REQUIRES_CANDIDATE_1"):
                    continuation.run(candidate=2, handoff_path=handoff, output_path=root / "receipt.json")


if __name__ == "__main__":
    unittest.main()