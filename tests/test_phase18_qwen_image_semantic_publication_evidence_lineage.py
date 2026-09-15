from __future__ import annotations

import unittest

from engine.intelligence.qwen_image_semantic_publication_evidence_lineage import (
    EVIDENCE_SCHEMA,
    assert_lineage_bound_semantic_publication_evidence,
)


class TestPhase18QwenImageSemanticPublicationEvidenceLineage(unittest.TestCase):
    def _fixture(self):
        story = "a" * 64
        png_sha = "b" * 64
        cs282_sha = "c" * 64
        cs283_sha = "d" * 64
        cs283_binding = {
            "repository_relative_path": "runs/cs283/request.json",
            "sha256": "e" * 64,
            "byte_size": 123,
        }
        cs282_binding = {
            "repository_relative_path": "runs/cs282/approval.json",
            "sha256": "f" * 64,
            "byte_size": 111,
            "receipt_sha256": cs282_sha,
        }
        png = {
            "repository_relative_path": "runs/cs272/composed_candidate.png",
            "sha256": png_sha,
            "byte_size": 4096,
            "width": 1080,
            "height": 1350,
        }
        generation_context = {"request_id": "qwen-canonical-test", "seed": 7}
        cs283 = {
            "receipt_sha256": cs283_sha,
            "story_snapshot_sha256": story,
            "source_cs282_final_semantic_approval": cs282_binding,
            "composed_candidate_png": png,
            "generation_context": generation_context,
        }
        raw = {
            "schema": EVIDENCE_SCHEMA,
            "source_cs283_semantic_publication_request": {
                **cs283_binding,
                "receipt_sha256": cs283_sha,
            },
            "source_cs282_final_semantic_approval": dict(cs282_binding),
            "story_snapshot_sha256": story,
            "composed_candidate_png": dict(png),
            "generation_context": dict(generation_context),
            "generation_package": {
                "metadata": {
                    "story_snapshot_sha256": story,
                    "composed_candidate_png_sha256": png_sha,
                    "source_cs282_receipt_sha256": cs282_sha,
                }
            },
            "base_scene_evidence": {
                "output_ref": png["repository_relative_path"],
                "provenance": {
                    "story_snapshot_sha256": story,
                    "composed_candidate_png_sha256": png_sha,
                    "source_cs282_receipt_sha256": cs282_sha,
                },
            },
            "vision_verifier_profile": {
                "local_zero_cost": True,
                "requires_network": False,
            },
            "vision_verifier_lineage": {
                "source_cs282_receipt_sha256": cs282_sha,
                "composed_candidate_png_sha256": png_sha,
                "cost_mode": "$0-local",
                "network_allowed": False,
                "local_files_only": True,
            },
        }
        return raw, cs283, cs283_binding

    def test_exact_lineage_is_accepted(self):
        raw, cs283, binding = self._fixture()
        assert_lineage_bound_semantic_publication_evidence(raw, cs283=cs283, cs283_binding=binding)

    def test_same_story_png_cannot_substitute_different_cs283_run(self):
        raw, cs283, binding = self._fixture()
        raw["source_cs283_semantic_publication_request"]["receipt_sha256"] = "1" * 64
        with self.assertRaisesRegex(ValueError, "CS283_LINEAGE_DRIFT"):
            assert_lineage_bound_semantic_publication_evidence(raw, cs283=cs283, cs283_binding=binding)

    def test_cs282_parent_substitution_is_rejected(self):
        raw, cs283, binding = self._fixture()
        raw["source_cs282_final_semantic_approval"]["receipt_sha256"] = "2" * 64
        with self.assertRaisesRegex(ValueError, "CS282_LINEAGE_DRIFT"):
            assert_lineage_bound_semantic_publication_evidence(raw, cs283=cs283, cs283_binding=binding)

    def test_png_path_substitution_is_rejected_even_with_same_png_sha(self):
        raw, cs283, binding = self._fixture()
        raw["composed_candidate_png"]["repository_relative_path"] = "runs/other/composed_candidate.png"
        with self.assertRaisesRegex(ValueError, "PNG_LINEAGE_DRIFT"):
            assert_lineage_bound_semantic_publication_evidence(raw, cs283=cs283, cs283_binding=binding)

    def test_paid_or_network_verifier_is_rejected_before_gate(self):
        raw, cs283, binding = self._fixture()
        raw["vision_verifier_profile"]["local_zero_cost"] = False
        with self.assertRaisesRegex(ValueError, "ZERO_COST_OFFLINE_REQUIRED"):
            assert_lineage_bound_semantic_publication_evidence(raw, cs283=cs283, cs283_binding=binding)
        raw, cs283, binding = self._fixture()
        raw["vision_verifier_profile"]["requires_network"] = True
        with self.assertRaisesRegex(ValueError, "ZERO_COST_OFFLINE_REQUIRED"):
            assert_lineage_bound_semantic_publication_evidence(raw, cs283=cs283, cs283_binding=binding)

    def test_package_and_base_provenance_must_bind_exact_parent(self):
        raw, cs283, binding = self._fixture()
        raw["generation_package"]["metadata"]["source_cs282_receipt_sha256"] = "3" * 64
        with self.assertRaisesRegex(ValueError, "PACKAGE_LINEAGE_DRIFT"):
            assert_lineage_bound_semantic_publication_evidence(raw, cs283=cs283, cs283_binding=binding)
        raw, cs283, binding = self._fixture()
        raw["base_scene_evidence"]["provenance"]["composed_candidate_png_sha256"] = "4" * 64
        with self.assertRaisesRegex(ValueError, "BASE_LINEAGE_DRIFT"):
            assert_lineage_bound_semantic_publication_evidence(raw, cs283=cs283, cs283_binding=binding)


if __name__ == "__main__":
    unittest.main()
