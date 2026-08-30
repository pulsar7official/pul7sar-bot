from __future__ import annotations

import unittest

from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import (
    _assert_cs273,
    _assert_cs280,
    _assert_same_lineage,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    SCHEMA as CS273_SCHEMA,
)
from engine.intelligence.qwen_image_composed_candidate_final_presentation_review_evidence import (
    SCHEMA as CS280_SCHEMA,
)


class TestPhase18QwenImageComposedCandidateFinalComposedVisualApproval(unittest.TestCase):
    def _png(self, sha="c" * 64):
        return {
            "repository_relative_path": "artifacts/composed_candidate.png",
            "sha256": sha,
            "byte_size": 1234,
        }

    def _cs273(self):
        return {
            "schema": CS273_SCHEMA,
            "story_snapshot_sha256": "a" * 64,
            "composed_candidate_png": self._png(),
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "semantic_inspection_executed": True,
            "hybrid_surface_semantic_qa_approved": True,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _cs280(self):
        return {
            "schema": CS280_SCHEMA,
            "story_snapshot_sha256": "a" * 64,
            "composed_candidate_png": self._png(),
            "human_visual_review_approved": True,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": True,
            "final_presentation_review_evidence_admitted": True,
            "final_presentation_review_approved": True,
            "exact_brand_integrity_approved": True,
            "typography_integrity_approved": True,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def test_independent_paths_may_aggregate_only_when_both_are_approved(self):
        cs273, cs280 = self._cs273(), self._cs280()
        _assert_cs273(cs273)
        _assert_cs280(cs280)
        _assert_same_lineage(cs273, cs280)

    def test_cs273_semantic_failure_blocks_final_composed_approval(self):
        source = self._cs273()
        source["hybrid_surface_semantic_qa_approved"] = False
        with self.assertRaisesRegex(ValueError, "REQUIRED_CS273_GATE_MISSING"):
            _assert_cs273(source)

    def test_cs280_final_presentation_failure_blocks_final_composed_approval(self):
        source = self._cs280()
        source["final_presentation_review_approved"] = False
        source["exact_brand_integrity_approved"] = False
        with self.assertRaisesRegex(ValueError, "REQUIRED_CS280_GATE_MISSING"):
            _assert_cs280(source)

    def test_story_lineage_drift_is_rejected(self):
        cs273, cs280 = self._cs273(), self._cs280()
        cs280["story_snapshot_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "STORY_LINEAGE_DRIFT"):
            _assert_same_lineage(cs273, cs280)

    def test_exact_composed_png_sha_drift_is_rejected(self):
        cs273, cs280 = self._cs273(), self._cs280()
        cs280["composed_candidate_png"] = self._png("d" * 64)
        with self.assertRaisesRegex(ValueError, "PNG_LINEAGE_DRIFT:sha256"):
            _assert_same_lineage(cs273, cs280)

    def test_exact_composed_png_path_drift_is_rejected(self):
        cs273, cs280 = self._cs273(), self._cs280()
        cs280["composed_candidate_png"]["repository_relative_path"] = "artifacts/other.png"
        with self.assertRaisesRegex(ValueError, "PNG_LINEAGE_DRIFT:repository_relative_path"):
            _assert_same_lineage(cs273, cs280)

    def test_premature_semantic_authority_in_cs280_is_rejected(self):
        source = self._cs280()
        source["semantic_approved"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:semantic_approved"):
            _assert_cs280(source)

    def test_premature_composed_authority_in_cs280_is_rejected(self):
        source = self._cs280()
        source["composed_visual_approved"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:composed_visual_approved"):
            _assert_cs280(source)


if __name__ == "__main__":
    unittest.main()
