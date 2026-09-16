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

    def test_workflow_continues_admitted_bytes_through_cs304_and_cs305(self):
        self.assertIn("tools/phase18_run_admitted_candidate_semantic_checkpoint.py", self.workflow)
        self.assertIn('admission_receipt="$(python -c', self.workflow)
        self.assertIn("admitted-candidate-semantic-checkpoint-${GITHUB_RUN_ID}", self.workflow)
        self.assertIn('result.get("semantic_inspection_executed") is not True', self.workflow)
        self.assertIn('result.get("semantic_base_scene_approved") is not True', self.workflow)
        self.assertIn('result.get("identity_requirement_classified") is not True', self.workflow)
        self.assertIn('isinstance(result.get("pixel_identity_review_required"), bool)', self.workflow)
        self.assertIn('test "$checkpoint_rc" -eq 0', self.workflow)

    def test_workflow_routes_cs304_cs305_through_cs317_exactly_once(self):
        self.assertIn("tools/phase18_route_semantic_checkpoint_after_identity_requirement.py", self.workflow)
        self.assertIn("post-semantic-identity-route-${GITHUB_RUN_ID}", self.workflow)
        self.assertIn("post-semantic-identity-route-result.json", self.workflow)
        self.assertIn("--cs304-receipt \"$CS304_RECEIPT\"", self.workflow)
        self.assertIn("--cs305-receipt \"$CS305_RECEIPT\"", self.workflow)
        self.assertIn("missing exact semantic checkpoint lineage: {key}", self.workflow)
        self.assertEqual(
            self.workflow.count("python tools/phase18_route_semantic_checkpoint_after_identity_requirement.py"),
            1,
        )

    def test_required_identity_route_stops_at_cs266_before_generated_layer_qa(self):
        self.assertIn('result.get("route") != "CS266_PIXEL_IDENTITY_REVIEW_REQUIRED"', self.workflow)
        self.assertIn('result.get("pixel_identity_review_request_created") is not True', self.workflow)
        self.assertIn('result.get("generated_layer_qa_executed") is not False', self.workflow)
        self.assertIn("CS268 must not run before required human identity review", self.workflow)

    def test_no_review_route_requires_cs268_generated_layer_approval(self):
        self.assertIn(
            'result.get("route") != "CS268_GENERATED_LAYER_QA_NO_PIXEL_IDENTITY_REVIEW_REQUIRED"',
            self.workflow,
        )
        self.assertIn('result.get("generated_layer_qa_executed") is not True', self.workflow)
        self.assertIn('result.get("generated_layer_qa_approved") is not True', self.workflow)
        self.assertIn("candidate rejected at CS268 Generated-Layer QA", self.workflow)
        self.assertIn('test "$route_rc" -eq 0', self.workflow)

    def test_identity_aware_route_keeps_all_later_authorities_closed(self):
        for field in (
            "identity_approved",
            "semantic_approved",
            "human_visual_review_approved",
            "golden_quality_approved",
            "genuine_golden_png_created",
            "publication_ready",
        ):
            self.assertIn(f'"{field}",', self.workflow)
        self.assertIn("identity-aware routing created premature authority: {field}", self.workflow)

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
