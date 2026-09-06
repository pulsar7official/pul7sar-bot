import tempfile
import unittest
from pathlib import Path

from engine.intelligence.hybrid_human_review_bundle import HybridHumanReviewBundleBuilder


PNG = b"\x89PNG\r\n\x1a\nphase18-review"


class HybridHumanReviewBundleTests(unittest.TestCase):
    def _fixture(self, root: Path):
        base = root / "base.png"
        hybrid = root / "hybrid.png"
        base.write_bytes(PNG + b"-base")
        hybrid.write_bytes(PNG + b"-hybrid")
        builder = HybridHumanReviewBundleBuilder(root=root)
        base_sha = builder._sha256(base)
        hybrid_sha = builder._sha256(hybrid)
        continuation = {
            "status": "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY",
            "candidate": 1,
            "base_png": str(base),
            "hybrid_png": str(hybrid),
            "hybrid_png_sha256": hybrid_sha,
            "artifact_integrity": {
                "valid": True,
                "input_sha256": base_sha,
                "output_sha256": hybrid_sha,
            },
            "semantic_layer_gate_approved": True,
            "hybrid_semantic_review_approved": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        return builder, base, hybrid, continuation

    def test_builds_byte_identical_non_publication_review_bundle(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            builder, base, hybrid, continuation = self._fixture(root)
            receipt = builder.build(continuation=continuation, output_dir=root / "review")
            self.assertEqual(receipt.status, "HYBRID_HUMAN_REVIEW_BUNDLE_READY")
            self.assertTrue(receipt.human_visual_review_required)
            self.assertFalse(receipt.automatic_selection_performed)
            self.assertFalse(receipt.golden_quality_approved)
            self.assertFalse(receipt.publication_ready)
            self.assertEqual(Path(receipt.review_base_png).read_bytes(), base.read_bytes())
            self.assertEqual(Path(receipt.review_hybrid_png).read_bytes(), hybrid.read_bytes())

    def test_rejects_hybrid_tampering_after_semantic_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            builder, _, hybrid, continuation = self._fixture(root)
            hybrid.write_bytes(PNG + b"-tampered")
            with self.assertRaisesRegex(RuntimeError, "HYBRID_SHA256_MISMATCH"):
                builder.build(continuation=continuation, output_dir=root / "review")

    def test_rejects_missing_semantic_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            builder, _, _, continuation = self._fixture(root)
            continuation["hybrid_semantic_review_approved"] = False
            with self.assertRaisesRegex(RuntimeError, "HYBRID_SEMANTIC_GATE_NOT_APPROVED"):
                builder.build(continuation=continuation, output_dir=root / "review")

    def test_rejects_publication_authority_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            builder, _, _, continuation = self._fixture(root)
            continuation["publication_ready"] = True
            with self.assertRaisesRegex(RuntimeError, "PUBLICATION_AUTHORITY_DRIFT"):
                builder.build(continuation=continuation, output_dir=root / "review")

    def test_rejects_output_escape(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            builder, _, _, continuation = self._fixture(root)
            with self.assertRaisesRegex(RuntimeError, "OUTPUT_DIR_ESCAPES_REPOSITORY"):
                builder.build(continuation=continuation, output_dir=Path(outside))


if __name__ == "__main__":
    unittest.main()
