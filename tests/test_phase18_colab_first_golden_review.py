import unittest
from pathlib import Path


class Phase18ColabFirstGoldenReviewTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("tools/phase18_colab_first_golden_review.py")
        self.text = self.path.read_text(encoding="utf-8")

    def test_tool_is_phase18_candidate1_only(self):
        self.assertIn('EXPECTED_BRANCH = "phase18/story-intelligence"', self.text)
        self.assertIn('if first_png.get("candidate") != 1', self.text)
        self.assertIn('"--candidate",\n            "1"', self.text)
        self.assertIn('"seeds_2_to_4_authorized": False', self.text)
        self.assertNotIn('"--candidate", str(', self.text)

    def test_runs_original_scene_and_current_trusted_path_in_strict_order(self):
        original_scene = self.text.index("phase18_first_png_original_scene.py")
        handoff = self.text.index("phase18_build_first_png_hybrid_handoff.py")
        continuation = self.text.index("phase18_continue_hybrid_from_first_png.py")
        review_bundle = self.text.index("phase18_prepare_hybrid_human_review.py")
        review_template = self.text.index("phase18_build_hybrid_human_review_template.py")
        self.assertLess(original_scene, handoff)
        self.assertLess(handoff, continuation)
        self.assertLess(continuation, review_bundle)
        self.assertLess(review_bundle, review_template)
        self.assertNotIn('str(ROOT / "tools" / "phase18_first_png.py")', self.text)

    def test_requires_measured_original_scene_runtime_admission(self):
        self.assertIn('original_scene_run.get("status") != "FIRST_GOLDEN_PNG_ORIGINAL_SCENE_PATH_COMPLETE"', self.text)
        self.assertIn('admission.get("status") != "GOLDEN_ORIGINAL_SCENE_RUNTIME_ADMITTED"', self.text)
        self.assertIn('admission.get("candidate") != 1', self.text)
        self.assertIn('admission.get("resolved_dtype") != "bfloat16"', self.text)
        self.assertIn('admission.get("runtime_ready") is not True', self.text)
        self.assertIn('"generated_branding_allowed"', Path("tools/phase18_first_png_original_scene.py").read_text(encoding="utf-8"))

    def test_requires_original_scene_postflight_binding_before_downstream_staging(self):
        helper = self.text.index("def _require_original_scene_receipt_binding")
        original_scene = self.text.index("phase18_first_png_original_scene.py")
        handoff = self.text.index("phase18_build_first_png_hybrid_handoff.py")
        binding_call = self.text.index("_require_original_scene_receipt_binding(original_scene_run, admission_receipt)")
        self.assertLess(helper, original_scene)
        self.assertLess(original_scene, binding_call)
        self.assertLess(binding_call, handoff)
        self.assertIn('original_scene_run.get("original_scene_admission_replayed") is not True', self.text)
        self.assertIn('original_scene_run.get("original_scene_admission_sha256")', self.text)
        self.assertIn('original_scene_run.get("original_scene_admission_bytes")', self.text)
        self.assertIn("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_REPLAY_BINDING_FAILED", self.text)

    def test_requires_semantic_approval_before_human_review_staging(self):
        self.assertIn('continuation.get("semantic_layer_gate_approved") is not True', self.text)
        self.assertIn('continuation.get("hybrid_semantic_review_approved") is not True', self.text)
        self.assertIn('continuation.get("status") != "FIRST_GOLDEN_HYBRID_SEMANTIC_PROOF_READY"', self.text)

    def test_never_records_human_or_golden_approval_automatically(self):
        self.assertIn('template.get("decision") is not None', self.text)
        self.assertIn('"human_visual_review_approved": False', self.text)
        self.assertIn('"golden_quality_approved": False', self.text)
        self.assertIn('"publication_ready": False', self.text)
        self.assertNotIn("phase18_record_hybrid_human_review.py", self.text)
        self.assertNotIn("phase18_apply_human_approved_golden_review.py", self.text)

    def test_review_artifacts_and_original_scene_admission_are_sha_bound(self):
        self.assertIn('"review_base_png_sha256": _sha256(review_base)', self.text)
        self.assertIn('"review_hybrid_png_sha256": _sha256(review_hybrid)', self.text)
        self.assertIn('"original_scene_runtime_admission_sha256": admission_sha256', self.text)
        self.assertIn('"original_scene_runtime_admission_bytes": admission_bytes', self.text)
        self.assertIn('"original_scene_runtime_admission_replayed": True', self.text)
        self.assertIn("FIRST_GOLDEN_REVIEW_ORIGINAL_SCENE_ADMISSION_DRIFT_BEFORE_PACKET", self.text)
        self.assertIn('"schema": "pul7sar-first-golden-human-review-packet-v2"', self.text)
        self.assertIn("FIRST_GOLDEN_REVIEW_PATH_ESCAPES_REPOSITORY", self.text)
        self.assertIn('value.read_bytes()[:8] != b"\\x89PNG\\r\\n\\x1a\\n"', self.text)

    def test_preserves_zero_cost_and_publication_gates(self):
        self.assertIn('first_png.get("cost_mode") != "$0-local"', self.text)
        self.assertIn('admission.get("cost_mode") != "$0-local"', self.text)
        self.assertIn('"cost_mode": "$0-local"', self.text)
        self.assertIn('_require_false(first_png, "publication_ready"', self.text)
        self.assertIn('"generation_authorized",', self.text)
        self.assertIn('"queue_mutated",', self.text)
        self.assertIn('"png_created",', self.text)
        self.assertIn('_require_false(template, "golden_quality_approved", "publication_ready"', self.text)


if __name__ == "__main__":
    unittest.main()
