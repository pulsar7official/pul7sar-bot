from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6-jit.yml"


class FirstGenuineGoldenV6JitOfflineContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_jit_workflow_enforces_offline_huggingface_resolution(self) -> None:
        self.assertIn('HF_HUB_OFFLINE: "1"', self.workflow)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', self.workflow)
        self.assertIn('PUL7SAR_PHASE18_COST_MODE: $0-local', self.workflow)

    def test_cuda_preflight_fails_closed_if_offline_contract_is_missing(self) -> None:
        self.assertIn('os.environ.get("HF_HUB_OFFLINE") != "1"', self.workflow)
        self.assertIn('os.environ.get("TRANSFORMERS_OFFLINE") != "1"', self.workflow)
        self.assertIn('First Genuine Golden v6 JIT requires local-cache-only model resolution', self.workflow)
        self.assertIn('model_cache_mode', self.workflow)
        self.assertIn('offline-local-only', self.workflow)

    def test_jit_workflow_still_requires_exact_phase18_gpu_runner_and_branch(self) -> None:
        self.assertIn('runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]', self.workflow)
        self.assertIn('refs/heads/phase18/story-intelligence', self.workflow)
        self.assertIn('git fetch --no-tags origin main:refs/remotes/origin/main', self.workflow)
        self.assertIn("Unexpected main.py modification detected in Phase 18 diff.", self.workflow)

    def test_jit_workflow_does_not_grant_downstream_authority(self) -> None:
        for field in (
            'human_visual_review_approved',
            'golden_quality_approved',
            'publication_ready',
            'seeds_2_to_4_authorized',
        ):
            self.assertIn(field, self.workflow)
        self.assertNotIn('publication_ready\": true', self.workflow.lower())
        self.assertNotIn('golden_quality_approved\": true', self.workflow.lower())


if __name__ == "__main__":
    unittest.main()
