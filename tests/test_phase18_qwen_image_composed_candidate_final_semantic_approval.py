from __future__ import annotations

import unittest

from engine.intelligence.qwen_image_composed_candidate_final_semantic_approval import (
    _assert_cs273,
    _assert_cs281,
    _assert_same_lineage,
)
from engine.intelligence.qwen_image_composed_candidate_final_composed_visual_approval import SCHEMA as CS281_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import SCHEMA as CS273_SCHEMA


class TestPhase18QwenImageComposedCandidateFinalSemanticApproval(unittest.TestCase):
    def _png(self, sha="c" * 64):
        return {"repository_relative_path": "artifacts/composed_candidate.png", "sha256": sha, "byte_size": 1234}

    def _cs281(self):
        return {
            "schema": CS281_SCHEMA,
            "story_snapshot_sha256": "a" * 64,
            "composed_candidate_png": self._png(),
            "hybrid_surface_semantic_qa_approved": True,
            "human_visual_review_approved": True,
            "final_presentation_review_approved": True,
            "exact_brand_integrity_approved": True,
            "typography_integrity_approved": True,
            "final_composed_visual_approval_executed": True,
            "composed_visual_approved": True,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
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
        }

    def test_final_semantic_authority_requires_both_approved_paths(self):
        a, b = self._cs281(), self._cs273()
        _assert_cs281(a); _assert_cs273(b); _assert_same_lineage(a, b)

    def test_cs281_composed_visual_failure_blocks_semantic_approval(self):
        value = self._cs281(); value["composed_visual_approved"] = False
        with self.assertRaisesRegex(ValueError, "REQUIRED_CS281_GATE_MISSING"):
            _assert_cs281(value)

    def test_cs273_semantic_failure_blocks_semantic_approval(self):
        value = self._cs273(); value["hybrid_surface_semantic_qa_approved"] = False
        with self.assertRaisesRegex(ValueError, "REQUIRED_CS273_GATE_MISSING"):
            _assert_cs273(value)

    def test_story_drift_is_rejected(self):
        a, b = self._cs281(), self._cs273(); b["story_snapshot_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "STORY_LINEAGE_DRIFT"):
            _assert_same_lineage(a, b)

    def test_png_sha_drift_is_rejected(self):
        a, b = self._cs281(), self._cs273(); b["composed_candidate_png"] = self._png("d" * 64)
        with self.assertRaisesRegex(ValueError, "PNG_LINEAGE_DRIFT:sha256"):
            _assert_same_lineage(a, b)

    def test_premature_semantic_authority_in_cs281_is_rejected(self):
        value = self._cs281(); value["semantic_approved"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:semantic_approved"):
            _assert_cs281(value)

    def test_premature_genuine_golden_authority_in_cs281_is_rejected(self):
        value = self._cs281(); value["genuine_golden_png_created"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:genuine_golden_png_created"):
            _assert_cs281(value)


if __name__ == "__main__":
    unittest.main()
