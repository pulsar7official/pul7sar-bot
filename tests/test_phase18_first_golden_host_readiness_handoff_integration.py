from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-golden-attested-host-readiness.yml"


class Phase18FirstGoldenHostReadinessHandoffIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_handoff_is_built_after_attested_summary_replay(self):
        replay = self.text.index("Replay readiness summary and keep all authorities closed")
        build = self.text.index("Build immutable first-Golden GPU handoff")
        handoff_replay = self.text.index("Replay GPU handoff and keep generation authority closed")
        upload = self.text.index("Upload attested host-readiness evidence")
        self.assertLess(replay, build)
        self.assertLess(build, handoff_replay)
        self.assertLess(handoff_replay, upload)

    def test_handoff_is_bound_to_exact_dispatch_sha(self):
        self.assertIn("python tools/phase18_build_first_golden_gpu_handoff.py", self.text)
        self.assertIn('--expected-commit "$DISPATCH_SHA"', self.text)
        self.assertIn("--attested-summary output/phase18_gpu_smoke/first-golden-attested-pre-gpu-summary.json", self.text)
        self.assertIn("--output output/phase18_gpu_smoke/first-golden-gpu-handoff.json", self.text)

    def test_handoff_artifact_is_uploaded_with_host_evidence(self):
        self.assertIn("output/phase18_gpu_smoke/first-golden-gpu-handoff.json", self.text)
        self.assertIn("output/phase18_gpu_smoke/first-golden-attested-pre-gpu-receipt.json", self.text)
        self.assertIn("output/phase18_gpu_smoke/first-golden-attested-pre-gpu-attestation.json", self.text)
        self.assertIn("output/phase18_gpu_smoke/first-golden-attested-pre-gpu-summary.json", self.text)

    def test_zero_cost_offline_and_runner_constraints_remain(self):
        self.assertIn("runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]", self.text)
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", self.text)
        self.assertIn('HF_HUB_OFFLINE: "1"', self.text)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', self.text)

    def test_all_authorities_remain_closed_after_handoff(self):
        for field in (
            "authoritative_gate",
            "network_download_authorized",
            "generation_authorized",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(field, self.text)
        self.assertIn('data.get(field) is not False', self.text)
        self.assertIn('data.get("eligible_for_authoritative_golden_preflight") is not True', self.text)

    def test_main_isolation_guard_remains(self):
        self.assertIn("git fetch --no-tags origin main:refs/remotes/origin/main", self.text)
        self.assertIn("git diff --name-only", self.text)
        self.assertIn("Unexpected main.py modification detected in Phase 18 diff.", self.text)


if __name__ == "__main__":
    unittest.main()
