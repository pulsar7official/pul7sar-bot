import unittest
from pathlib import Path


TOOL = Path("tools/phase18_run_admitted_candidate_semantic_checkpoint.py")


class Phase18AdmittedCandidateSemanticCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = TOOL.read_text(encoding="utf-8")

    def test_checkpoint_runs_exact_existing_cs304_and_cs305_authorities(self):
        self.assertIn("run_canonical_candidate_semantic_base_qa(", self.source)
        self.assertIn("verify_canonical_candidate_semantic_base_qa(", self.source)
        self.assertIn("run_identity_requirement(", self.source)
        self.assertIn("verify_identity_requirement(", self.source)
        self.assertLess(
            self.source.index("run_canonical_candidate_semantic_base_qa("),
            self.source.index("run_identity_requirement("),
        )

    def test_identity_classification_is_blocked_when_semantic_base_qa_rejects(self):
        self.assertIn('semantic.get("semantic_base_scene_approved") is not True', self.source)
        self.assertIn("QWEN_IMAGE_ADMITTED_CANDIDATE_REJECTED_AT_SEMANTIC_BASE_QA", self.source)
        self.assertIn("return summary_path, False", self.source)

    def test_checkpoint_keeps_downstream_authorities_closed(self):
        for field in (
            "identity_approved",
            "semantic_approved",
            "human_visual_review_approved",
            "golden_quality_approved",
            "genuine_golden_png_created",
            "publication_ready",
        ):
            self.assertIn(f'"{field}"', self.source)
        self.assertIn("_assert_authorities_closed(semantic", self.source)
        self.assertIn("_assert_authorities_closed(identity", self.source)

    def test_checkpoint_rechecks_story_and_candidate_lineage(self):
        self.assertIn("QWEN_SEMANTIC_CHECKPOINT_STORY_LINEAGE_DRIFT", self.source)
        self.assertIn("QWEN_SEMANTIC_CHECKPOINT_CANDIDATE_LINEAGE_DRIFT", self.source)
        self.assertIn('identity.get("candidate_png") != semantic.get("candidate_png")', self.source)

    def test_checkpoint_forces_huggingface_semantic_runtime_offline(self):
        self.assertIn('os.environ["HF_HUB_OFFLINE"] = "1"', self.source)
        self.assertIn('os.environ["TRANSFORMERS_OFFLINE"] = "1"', self.source)
        self.assertIn('os.environ["HF_DATASETS_OFFLINE"] = "1"', self.source)
        self.assertIn('os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"', self.source)
        self.assertIn("_force_local_semantic_runtime()", self.source)
        self.assertLess(
            self.source.index("_force_local_semantic_runtime()", self.source.index("def run_checkpoint")),
            self.source.index("run_canonical_candidate_semantic_base_qa(", self.source.index("def run_checkpoint")),
        )

    def test_checkpoint_does_not_generate_or_publish(self):
        self.assertNotIn("QwenImagePipeline", self.source)
        self.assertNotIn("Flux2KleinPipeline", self.source)
        self.assertNotIn("publish(", self.source)
        self.assertNotIn("requests.", self.source)


if __name__ == "__main__":
    unittest.main()
