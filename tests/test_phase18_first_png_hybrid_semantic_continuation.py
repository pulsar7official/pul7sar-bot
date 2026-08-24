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


class FirstPngHybridSemanticContinuationTests(unittest.TestCase):
    def _fixture(self, root: Path):
        base = root / "base.png"
        hybrid = root / "hybrid.png"
        base.write_bytes(PNG + b"-base")
        hybrid.write_bytes(PNG + b"-hybrid")
        handoff = root / "latest.json"
        handoff.write_text(json.dumps({
            "status": continuation.EXPECTED_HANDOFF_STATUS,
            "branch": continuation.EXPECTED_BRANCH,
            "manifest_version": continuation.EXPECTED_MANIFEST,
            "candidate": 1,
            "cost_mode": "$0-local",
            "resolved_dtype": "bfloat16",
            "hybrid_surface_replacement_required": True,
            "generated_sport_geometry_allowed": False,
            "generated_branding_allowed": False,
            "semantic_layer_gate_approved": False,
            "hybrid_semantic_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "png": str(base.resolve()),
            "base_png_sha256": sha256(base),
        }), encoding="utf-8")
        result = {
            "status": "GOLDEN_HYBRID_SURFACE_READY",
            "candidate": 1,
            "base_png": str(base.resolve()),
            "hybrid_png": str(hybrid.resolve()),
            "artifact_integrity": {"valid": True, "failures": []},
            "base_scene_layer_gate": {"allowed": True, "inspection_complete": True, "blockers": []},
            "semantic_visual_inspection": {
                "base_scene": {"approved": True, "status": "SEMANTIC_VISUAL_INSPECTION_COMPLETE"},
                "hybrid_surface": {"approved": True, "status": "SEMANTIC_VISUAL_INSPECTION_COMPLETE"},
            },
            "deterministic_geometry_applied": True,
            "generated_pitch_markings_replaced": True,
            "dynamic_brand_applied": False,
            "typography_applied": False,
            "publication_ready": False,
        }
        return handoff, result

    def test_success_requires_both_semantic_stages_and_keeps_publication_closed(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            output = root / "receipt.json"
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_compose_hybrid", return_value=result),
            ):
                receipt = continuation.run(candidate=1, handoff_path=handoff, output_path=output)
            self.assertEqual(receipt["status"], "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY")
            self.assertTrue(receipt["semantic_layer_gate_approved"])
            self.assertTrue(receipt["hybrid_semantic_review_approved"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["publication_ready"])
            self.assertTrue(output.is_file())

    def test_hybrid_semantic_failure_is_fail_closed(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            result["semantic_visual_inspection"]["hybrid_surface"]["approved"] = False
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_compose_hybrid", return_value=result),
            ):
                with self.assertRaisesRegex(RuntimeError, "HYBRID_CONTINUATION_HYBRID_SURFACE_SEMANTIC_FAILED"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")

    def test_publication_authority_drift_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            result["publication_ready"] = True
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_compose_hybrid", return_value=result),
            ):
                with self.assertRaisesRegex(RuntimeError, "HYBRID_CONTINUATION_PUBLICATION_AUTHORITY_DRIFT"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")

    def test_handoff_tampering_is_rejected_before_qwen_or_composition(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            payload = json.loads(handoff.read_text(encoding="utf-8"))
            payload["base_png_sha256"] = "0" * 64
            handoff.write_text(json.dumps(payload), encoding="utf-8")
            with (
                patch.object(continuation, "LATEST", handoff),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_compose_hybrid", return_value=result) as compose,
            ):
                with self.assertRaisesRegex(RuntimeError, "HYBRID_CONTINUATION_BASE_PNG_SHA256_MISMATCH"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")
                compose.assert_not_called()

    def test_noncanonical_handoff_is_rejected_before_qwen_or_composition(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, result = self._fixture(root)
            canonical = root / "canonical-latest.json"
            canonical.write_bytes(handoff.read_bytes())
            with (
                patch.object(continuation, "LATEST", canonical),
                patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH),
                patch.object(continuation, "_compose_hybrid", return_value=result) as compose,
            ):
                with self.assertRaisesRegex(RuntimeError, "HYBRID_CONTINUATION_CANONICAL_HANDOFF_REQUIRED"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")
                compose.assert_not_called()

    def test_branch_and_candidate_remain_locked(self):
        with tempfile.TemporaryDirectory(dir=".") as temp:
            root = Path(temp)
            handoff, _ = self._fixture(root)
            with patch.object(continuation, "LATEST", handoff), patch.object(continuation, "_branch", return_value="main"):
                with self.assertRaisesRegex(RuntimeError, "HYBRID_CONTINUATION_BRANCH_BLOCKED"):
                    continuation.run(candidate=1, handoff_path=handoff, output_path=root / "receipt.json")
            with patch.object(continuation, "LATEST", handoff), patch.object(continuation, "_branch", return_value=continuation.EXPECTED_BRANCH):
                with self.assertRaisesRegex(RuntimeError, "HYBRID_CONTINUATION_REQUIRES_CANDIDATE_1"):
                    continuation.run(candidate=2, handoff_path=handoff, output_path=root / "receipt.json")


if __name__ == "__main__":
    unittest.main()
