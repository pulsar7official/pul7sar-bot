from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase18-first-genuine-golden-v6.yml"


class CanonicalAttestedWorkflowIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_canonical_launcher_is_present_and_dispatch_sha_bound(self) -> None:
        self.assertIn(
            "test -f tools/phase18_run_first_genuine_golden_v6_canonical_attested.py",
            self.text,
        )
        self.assertIn(
            "python tools/phase18_run_first_genuine_golden_v6_canonical_attested.py",
            self.text,
        )
        self.assertIn('--expected-commit "$DISPATCH_SHA"', self.text)
        self.assertIn("DISPATCH_SHA: ${{ github.sha }}", self.text)

    def test_attested_launcher_owns_canonical_generation_entrypoint(self) -> None:
        self.assertNotIn(
            "python tools/phase18_colab_first_genuine_resources_locked.py",
            self.text,
        )
        self.assertIn(
            "--output output/phase18_gpu_smoke/first-genuine-golden-v6-resource-lock.json",
            self.text,
        )

    def test_defense_in_depth_order_is_preserved(self) -> None:
        blocker = self.text.index("python tools/phase18_probe_first_golden_execution_blocker.py")
        cuda = self.text.index("if not torch.cuda.is_available():")
        attested = self.text.index(
            "python tools/phase18_run_first_genuine_golden_v6_canonical_attested.py"
        )
        replay = self.text.index(
            "Replay exact model-cache semantic resource runtime and staging evidence"
        )
        self.assertLess(blocker, cuda)
        self.assertLess(cuda, attested)
        self.assertLess(attested, replay)

    def test_zero_cost_offline_native_bf16_contract_remains(self) -> None:
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        self.assertIn('HF_HUB_OFFLINE: "1"', self.text)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', self.text)
        self.assertIn("torch.cuda.is_bf16_supported()", self.text)
        self.assertIn("refusing FP16/FP32 substitution", self.text)

    def test_attested_evidence_paths_are_distinct_and_preserved_for_upload(self) -> None:
        expected = (
            "first-genuine-golden-v6-canonical-attested-pre-gpu-receipt.json",
            "first-genuine-golden-v6-canonical-attested-pre-gpu-attestation.json",
            "first-genuine-golden-v6-canonical-attested-pre-gpu-summary.json",
        )
        for name in expected:
            self.assertIn(name, self.text)
        self.assertIn("output/phase18_gpu_smoke/**", self.text)

    def test_main_isolation_and_post_generation_provenance_remain(self) -> None:
        self.assertIn("refs/heads/phase18/story-intelligence", self.text)
        self.assertIn("grep -qx 'main.py'", self.text)
        self.assertIn("phase18_bind_first_genuine_golden_source_commit.py bind", self.text)
        self.assertIn("phase18_verify_first_genuine_golden_v6_source_bound_artifact.py", self.text)
        self.assertIn("phase18_attest_first_genuine_golden_v6_uploaded_artifact.py", self.text)


if __name__ == "__main__":
    unittest.main()
