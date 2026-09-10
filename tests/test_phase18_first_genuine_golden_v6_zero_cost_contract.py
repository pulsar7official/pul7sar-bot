from pathlib import Path
import unittest


WORKFLOW_PATH = (
    Path(__file__).resolve().parents[1]
    / ".github"
    / "workflows"
    / "phase18-first-genuine-golden-v6.yml"
)


class FirstGenuineGoldenV6ZeroCostContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    def test_offline_model_resolution_is_mandatory(self) -> None:
        self.assertIn('PUL7SAR_PHASE18_COST_MODE: $0-local', self.workflow)
        self.assertIn('HF_HUB_OFFLINE: "1"', self.workflow)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', self.workflow)
        self.assertIn(
            'os.environ.get("HF_HUB_OFFLINE") != "1"',
            self.workflow,
        )
        self.assertIn(
            'os.environ.get("TRANSFORMERS_OFFLINE") != "1"',
            self.workflow,
        )
        self.assertIn(
            "First Genuine Golden v6 requires local-cache-only model resolution",
            self.workflow,
        )

    def test_gpu_cuda_bf16_runner_contract_stays_explicit(self) -> None:
        for label in (
            "self-hosted",
            "linux",
            "x64",
            "gpu",
            "cuda",
            "bf16",
            "pul7sar-phase18",
        ):
            self.assertIn(f"- {label}", self.workflow)
        self.assertIn("torch.cuda.is_available()", self.workflow)
        self.assertIn(
            "CUDA-enabled PyTorch is required; refusing to install or replace PyTorch automatically",
            self.workflow,
        )

    def test_replay_rejects_any_runtime_model_download(self) -> None:
        self.assertIn(
            'semantic.get("model_downloaded_now") is not False',
            self.workflow,
        )
        self.assertIn(
            "semantic preflight attempted a model download instead of using the approved local cache",
            self.workflow,
        )
        self.assertGreaterEqual(
            self.workflow.count('get("downloaded_now") is not False'),
            2,
        )
        self.assertIn(
            "Qwen snapshot was not already present in the approved local cache",
            self.workflow,
        )
        self.assertIn(
            "FLUX snapshot was not already present in the approved local cache",
            self.workflow,
        )

    def test_downstream_authority_remains_fail_closed(self) -> None:
        self.assertIn(
            'for field in ("golden_quality_approved", "publication_ready", "seeds_2_to_4_authorized"):',
            self.workflow,
        )
        self.assertIn("if staging.get(field) is not False:", self.workflow)
        self.assertIn('"publication_ready": False', self.workflow)
        self.assertIn('"seeds_2_to_4_authorized": False', self.workflow)


if __name__ == "__main__":
    unittest.main()
