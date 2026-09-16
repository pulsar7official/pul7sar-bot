from __future__ import annotations

import ast
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


def argparse_flags(source: str) -> set[str]:
    """Return literal long-form flags declared through ``*.add_argument`` calls.

    AST inspection makes the contract independent of whitespace, line wrapping,
    quote style, and formatter choices while remaining standard-library only.
    """
    flags: set[str] = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if not isinstance(function, ast.Attribute) or function.attr != "add_argument":
            continue
        for argument in node.args:
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                if argument.value.startswith("--"):
                    flags.add(argument.value)
    return flags


class FirstGoldenAttestedCliContractTests(unittest.TestCase):
    def test_pre_gpu_runner_exposes_current_evidence_flag_names(self) -> None:
        flags = argparse_flags(read(PRE_GPU_RUNNER))
        self.assertTrue({"--expected-commit", "--receipt", "--attestation", "--summary"}.issubset(flags))
        self.assertTrue({"--receipt-out", "--attestation-out", "--summary-out"}.isdisjoint(flags))

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
                self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", text)
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

        flags = argparse_flags(launcher)
        self.assertTrue({"--expected-commit", "--output", "--receipt", "--attestation", "--summary"}.issubset(flags))
        self.assertTrue({"--receipt-out", "--attestation-out", "--summary-out"}.isdisjoint(flags))
        for stale_flag in ("--receipt-out", "--attestation-out", "--summary-out"):
            self.assertNotIn(stale_flag, workflow)

    def test_contract_does_not_open_generation_or_publication_authority(self) -> None:
        pre_gpu = read(PRE_GPU_RUNNER)
        canonical = read(CANONICAL_LAUNCHER)
        for source in (pre_gpu, canonical):
            self.assertIn('"network_download_authorized": False', source)
            self.assertIn('"publication_ready": False', source)
            self.assertIn('"seeds_2_to_4_authorized": False', source)


if __name__ == "__main__":
    unittest.main()
