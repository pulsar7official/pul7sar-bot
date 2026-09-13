from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase18-first-golden-attested-host-readiness.yml"


class FirstGoldenAttestedHostReadinessWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_self_hosted_zero_cost_offline_contract(self) -> None:
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", self.text)
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        self.assertIn('HF_HUB_OFFLINE: "1"', self.text)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', self.text)

    def test_exact_branch_and_dispatch_sha_are_required(self) -> None:
        self.assertIn('test "$DISPATCH_REF" = "refs/heads/phase18/story-intelligence"', self.text)
        self.assertIn('ref: ${{ github.sha }}', self.text)
        self.assertIn('test "$(git rev-parse HEAD)" = "$DISPATCH_SHA"', self.text)
        self.assertIn("git checkout -B phase18/story-intelligence", self.text)

    def test_attested_pre_gpu_runner_uses_immutable_sha(self) -> None:
        runner = "python tools/phase18_run_first_golden_pre_gpu_attested.py"
        self.assertIn(runner, self.text)
        self.assertIn('--expected-commit "$DISPATCH_SHA"', self.text)
        self.assertIn("first-golden-attested-pre-gpu-receipt.json", self.text)
        self.assertIn("first-golden-attested-pre-gpu-attestation.json", self.text)
        self.assertIn("first-golden-attested-pre-gpu-summary.json", self.text)

    def test_main_isolation_and_authority_closure_are_preserved(self) -> None:
        self.assertIn("git diff --name-only", self.text)
        self.assertIn("grep -qx 'main.py'", self.text)
        for field in (
            "authoritative_gate",
            "network_download_authorized",
            "generation_authorized",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(field, self.text)
        self.assertIn('if data.get(field) is not False:', self.text)

    def test_workflow_is_diagnostic_only_and_does_not_invoke_generation(self) -> None:
        forbidden = (
            "phase18_colab_first_genuine_golden.py",
            "phase18_colab_first_genuine_resources_locked.py",
            "phase18_colab_first_genuine_jit_replay_locked.py",
            "phase18_colab_first_genuine_offload_locked.py",
        )
        for token in forbidden:
            self.assertNotIn(token, self.text)


if __name__ == "__main__":
    unittest.main()
