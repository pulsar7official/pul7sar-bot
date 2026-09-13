from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]

PRE_GPU_RUNNER = ROOT / "tools/phase18_run_first_golden_pre_gpu_attested.py"
CANONICAL_LAUNCHER = ROOT / "tools/phase18_run_first_genuine_golden_v6_canonical_attested.py"

DIRECT_PRE_GPU_WORKFLOWS = (
    ROOT / ".github/workflows/phase18-first-golden-attested-host-readiness.yml",
    ROOT / ".github/workflows/phase18-first-genuine-golden-v6-jit.yml",
    ROOT / ".github/workflows/phase18-first-genuine-golden-v6-offload.yml",
)
CANONICAL_WORKFLOW = ROOT / ".github/workflows/phase18-first-genuine-golden-v6.yml"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class FirstGoldenAttestedCliContractTests(unittest.TestCase):
    def test_pre_gpu_runner_exposes_only_the_current_evidence_flag_names(self) -> None:
        source = read(PRE_GPU_RUNNER)
        for flag in ("--expected-commit", "--receipt", "--attestation", "--summary"):
            self.assertIn(f'parser.add_argument("{flag}"', source)
        for stale_flag in ("--receipt-out", "--attestation-out", "--summary-out"):
            self.assertNotIn(stale_flag, source)

    def test_direct_pre_gpu_workflows_match_runner_cli_exactly(self) -> None:
        for workflow in DIRECT_PRE_GPU_WORKFLOWS:
            with self.subTest(workflow=workflow.name):
                text = read(workflow)
                self.assertIn("tools/phase18_run_first_golden_pre_gpu_attested.py", text)
                self.assertIn('--expected-commit "$DISPATCH_SHA"', text)
                self.assertIn("--receipt ", text)
                self.assertIn("--attestation ", text)
                self.assertIn("--summary ", text)
                for stale_flag in ("--receipt-out", "--attestation-out", "--summary-out"):
                    self.assertNotIn(stale_flag, text)
                self.assertIn('PUL7SAR_PHASE18_COST_MODE: $0-local', text)
                self.assertIn('HF_HUB_OFFLINE: "1"', text)
                self.assertIn('TRANSFORMERS_OFFLINE: "1"', text)

    def test_canonical_workflow_and_launcher_share_the_attested_evidence_contract(self) -> None:
        workflow = read(CANONICAL_WORKFLOW)
        launcher = read(CANONICAL_LAUNCHER)

        self.assertIn("tools/phase18_run_first_genuine_golden_v6_canonical_attested.py", workflow)
        self.assertIn('--expected-commit "$DISPATCH_SHA"', workflow)
        self.assertIn("--output ", workflow)
        self.assertIn("--receipt ", workflow)
        self.assertIn("--attestation ", workflow)
        self.assertIn("--summary ", workflow)

        for flag in ("--expected-commit", "--output", "--receipt", "--attestation", "--summary"):
            self.assertIn(f'parser.add_argument("{flag}"', launcher)
        for stale_flag in ("--receipt-out", "--attestation-out", "--summary-out"):
            self.assertNotIn(stale_flag, workflow)
            self.assertNotIn(stale_flag, launcher)

    def test_contract_does_not_open_generation_or_publication_authority(self) -> None:
        pre_gpu = read(PRE_GPU_RUNNER)
        canonical = read(CANONICAL_LAUNCHER)
        for source in (pre_gpu, canonical):
            self.assertIn('"network_download_authorized": False', source)
            self.assertIn('"publication_ready": False', source)
            self.assertIn('"seeds_2_to_4_authorized": False', source)


if __name__ == "__main__":
    unittest.main()
