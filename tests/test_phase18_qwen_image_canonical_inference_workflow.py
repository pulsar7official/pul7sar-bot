import unittest
from pathlib import Path


WORKFLOW = Path(".github/workflows/phase18-qwen-image-canonical-inference.yml")


class Phase18QwenImageCanonicalInferenceWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_workflow_is_manual_branch_bound_and_zero_cost(self):
        self.assertIn("workflow_dispatch:", self.workflow)
        self.assertIn("RUN_PHASE18_QWEN_CANONICAL_INFERENCE", self.workflow)
        self.assertIn('test "$DISPATCH_REF" = "refs/heads/phase18/story-intelligence"', self.workflow)
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.workflow)
        self.assertIn('HF_HUB_OFFLINE: "1"', self.workflow)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', self.workflow)
        self.assertIn('HF_DATASETS_OFFLINE: "1"', self.workflow)
        self.assertIn('HF_HUB_DISABLE_TELEMETRY: "1"', self.workflow)
        self.assertIn(
            "runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]",
            self.workflow,
        )

    def test_workflow_uses_manifest_bound_canonical_qwen_path(self):
        for tool in (
            "tools/phase18_qwen_image_gpu_readiness.py",
            "tools/phase18_qwen_image_gpu_host_launch_manifest.py",
            "tools/phase18_run_manifest_bound_canonical_inference.py",
            "tools/phase18_qwen_image_launch_to_output_attestation.py",
        ):
            self.assertIn(tool, self.workflow)
        self.assertIn("--require-static-ready", self.workflow)
        self.assertIn("canonical_candidate.png", self.workflow)
        self.assertIn("launch_to_output_attestation.json", self.workflow)

    def test_workflow_seals_and_byte_admits_exact_attested_candidate(self):
        self.assertIn(
            "tools/phase18_qwen_image_canonical_candidate_handoff.py build",
            self.workflow,
        )
        self.assertIn(
            "tools/phase18_qwen_image_canonical_candidate_handoff.py verify",
            self.workflow,
        )
        self.assertIn("tools/phase18_admit_canonical_candidate_bytes.py", self.workflow)
        self.assertIn("canonical-candidate-handoff-${GITHUB_RUN_ID}.json", self.workflow)
        self.assertIn("canonical-candidate-admission-${GITHUB_RUN_ID}", self.workflow)
        self.assertIn('result.get("handoff_sealed") is not True', self.workflow)
        self.assertIn(
            'result.get("candidate_bytes_admitted_for_post_generation_qa") is not True',
            self.workflow,
        )
        self.assertIn('result.get("genuine_golden_png_created") is not False', self.workflow)
        self.assertIn('result.get("publication_ready") is not False', self.workflow)

    def test_workflow_continues_admitted_bytes_through_cs304_and_cs305_only(self):
        self.assertIn("tools/phase18_run_admitted_candidate_semantic_checkpoint.py", self.workflow)
        self.assertIn('admission_receipt="$(python -c', self.workflow)
        self.assertIn("admitted-candidate-semantic-checkpoint-${GITHUB_RUN_ID}", self.workflow)
        self.assertIn('result.get("semantic_inspection_executed") is not True', self.workflow)
        self.assertIn('result.get("semantic_base_scene_approved") is not True', self.workflow)
        self.assertIn('result.get("identity_requirement_classified") is not True', self.workflow)
        self.assertIn('isinstance(result.get("pixel_identity_review_required"), bool)', self.workflow)
        self.assertIn('test "$checkpoint_rc" -eq 0', self.workflow)

    def test_semantic_checkpoint_keeps_identity_and_all_later_authorities_closed(self):
        for field in (
            "identity_approved",
            "semantic_approved",
            "human_visual_review_approved",
            "golden_quality_approved",
            "genuine_golden_png_created",
            "publication_ready",
        ):
            self.assertIn(f'"{field}",', self.workflow)
        self.assertIn('semantic checkpoint created premature authority: {field}', self.workflow)

    def test_workflow_keeps_all_downstream_authorities_closed(self):
        self.assertIn('if verified.get("genuine_canonical_inference_executed") is not True:', self.workflow)
        for field in (
            "semantic_approved",
            "human_visual_review_approved",
            "golden_quality_approved",
            "genuine_golden_png_created",
            "publication_ready",
        ):
            self.assertIn(f'"{field}",', self.workflow)
        self.assertIn('if verified.get(field) is not False:', self.workflow)

    def test_workflow_does_not_use_legacy_flux_generation(self):
        self.assertNotIn("phase18_first_png.py", self.workflow)
        self.assertNotIn("phase18_prefetch_flux2.py", self.workflow)
        self.assertNotIn("Flux2KleinPipeline", self.workflow)
        self.assertNotIn("FLUX2_KLEIN_4B_MODEL_ID", self.workflow)


if __name__ == "__main__":
    unittest.main()
