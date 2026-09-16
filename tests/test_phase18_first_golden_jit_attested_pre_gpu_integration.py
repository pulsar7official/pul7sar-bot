from pathlib import Path
import unittest


class FirstGoldenJitAttestedPreGpuIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = Path(
            ".github/workflows/phase18-first-genuine-golden-v6-jit.yml"
        ).read_text(encoding="utf-8")

    def test_attested_runner_is_bound_to_exact_dispatch_sha(self) -> None:
        self.assertIn("tools/phase18_run_first_golden_pre_gpu_attested.py", self.workflow)
        self.assertIn('--expected-commit "$DISPATCH_SHA"', self.workflow)
        self.assertIn("${{ github.sha }}", self.workflow)

    def test_attested_pre_gpu_runs_before_existing_execution_blocker(self) -> None:
        attested = self.workflow.index(
            "Attest immutable source and zero-cost host before JIT Golden execution"
        )
        blocker = self.workflow.index(
            "Record first-Golden execution blocker probe before CUDA preflight"
        )
        cuda = self.workflow.index(
            "Prove CUDA-enabled PyTorch native BF16 and offline-only model resolution exist without replacing them"
        )
        generation = self.workflow.index(
            "Run JIT-resource replay locked strict Golden Editorial v6 Candidate 1"
        )
        self.assertLess(attested, blocker)
        self.assertLess(blocker, cuda)
        self.assertLess(cuda, generation)

    def test_zero_cost_offline_and_closed_authorities_remain_explicit(self) -> None:
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.workflow)
        self.assertIn('HF_HUB_OFFLINE: "1"', self.workflow)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', self.workflow)
        for field in (
            "authoritative_gate",
            "network_download_authorized",
            "generation_authorized",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(field, self.workflow)

    def test_main_isolation_and_bf16_refusal_remain(self) -> None:
        self.assertIn("git diff --name-only", self.workflow)
        self.assertIn("'main.py'", self.workflow)
        self.assertIn("Native CUDA BF16 support is required; refusing FP16/FP32 substitution", self.workflow)


if __name__ == "__main__":
    unittest.main()
