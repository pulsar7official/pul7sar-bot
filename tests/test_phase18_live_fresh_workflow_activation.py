from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase18-first-genuine-golden-v6-fresh.yml"


class LiveFreshWorkflowActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_exact_branch_and_gpu_labels_remain_locked(self):
        self.assertIn('test "$DISPATCH_REF" = "refs/heads/phase18/story-intelligence"', self.text)
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", self.text)

    def test_zero_cost_offline_contract_remains_locked(self):
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        self.assertIn('HF_HUB_OFFLINE: "1"', self.text)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', self.text)
        self.assertIn("Native BF16 support is required; refusing FP16/FP32 substitution", self.text)

    def test_four_authoritative_evidence_files_are_captured_before_candidate(self):
        required = [
            "first-genuine-golden-v6-zero-cost-network-guard.json",
            "first-genuine-golden-v6-execution-blocker-probe.json",
            "first-genuine-golden-v6-approved-snapshot-inventory.json",
            "first-genuine-golden-v6-runner-identity.json",
        ]
        candidate = self.text.index("python tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py")
        for name in required:
            self.assertLess(self.text.index(name), candidate, name)

    def test_live_candidate_path_is_freshness_bound(self):
        fresh = self.text.index("python tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py")
        self.assertNotIn(
            "python tools/phase18_run_first_genuine_golden_v6_canonical_attested.py",
            self.text[:fresh],
        )
        self.assertIn("phase18_first_golden_freshness_guard.py", self.text)

    def test_source_png_review_and_publication_gates_remain_present(self):
        for token in (
            "phase18_verify_first_genuine_golden_v6_source_bound_artifact.py",
            "phase18_verify_first_genuine_golden_png_structure.py",
            "phase18_verify_first_genuine_golden_png_chunk_semantics.py",
            "phase18_verify_first_genuine_golden_png_canonical_encoding.py",
            "phase18_package_first_genuine_golden_v6_review_bundle.py",
            "phase18_verify_first_genuine_golden_v6_review_bundle.py",
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(token, self.text)


if __name__ == "__main__":
    unittest.main()
