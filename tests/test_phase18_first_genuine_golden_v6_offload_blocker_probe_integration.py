import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6-offload.yml"


class FirstGenuineGoldenV6OffloadBlockerProbeIntegrationTests(unittest.TestCase):
    def test_offload_workflow_records_probe_before_cuda_preflight(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        probe_step = "Record first-Golden execution blocker probe before offload CUDA preflight"
        cuda_step = "Prove CUDA-enabled PyTorch native BF16 and offline-only model resolution exist without replacing them"

        self.assertIn(probe_step, text)
        self.assertIn(cuda_step, text)
        self.assertIn("phase18_probe_first_golden_execution_blocker.py", text)
        self.assertIn("first-genuine-golden-v6-offload-execution-blocker-probe.json", text)
        self.assertLess(text.index(probe_step), text.index(cuda_step))

    def test_offload_cuda_preflight_is_native_bf16_zero_cost_and_offline_only(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('PUL7SAR_PHASE18_COST_MODE: $0-local', text)
        self.assertIn('HF_HUB_OFFLINE: "1"', text)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', text)
        self.assertIn('os.environ.get("PUL7SAR_PHASE18_COST_MODE") != "$0-local"', text)
        self.assertIn('torch.version.cuda is None', text)
        self.assertIn('torch.cuda.device_count() < 1', text)
        self.assertIn('torch.cuda.is_bf16_supported()', text)
        self.assertIn('refusing FP16/FP32 substitution', text)

    def test_blocker_receipt_is_in_always_uploaded_offload_evidence_tree(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        upload_step = "Upload offload-locked genuine Golden v6 Candidate 1 evidence"

        self.assertIn(upload_step, text)
        tail = text[text.index(upload_step):]
        self.assertIn("if: always()", tail)
        self.assertIn("output/phase18_gpu_smoke/**", tail)

    def test_main_isolation_and_authority_gates_remain_present(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('git fetch --no-tags origin main:refs/remotes/origin/main', text)
        self.assertIn("Unexpected main.py modification detected in Phase 18 diff.", text)
        for field in (
            "human_visual_review_approved",
            "golden_quality_approved",
            "publication_ready",
            "seeds_2_to_4_authorized",
        ):
            self.assertIn(field, text)


if __name__ == "__main__":
    unittest.main()
