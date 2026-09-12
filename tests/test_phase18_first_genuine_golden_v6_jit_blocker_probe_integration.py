import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "phase18_colab_first_genuine_jit_replay_locked.py"
PROBE = ROOT / "tools" / "phase18_probe_first_golden_execution_blocker.py"
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6-jit.yml"


class FirstGenuineGoldenV6JitBlockerProbeIntegrationTests(unittest.TestCase):
    def test_jit_cli_binds_probe_before_heavier_candidate_execution(self) -> None:
        text = TOOL.read_text(encoding="utf-8")
        ast.parse(text)

        self.assertIn("phase18_probe_first_golden_execution_blocker", text)
        self.assertIn("inspect_execution_blockers", text)
        self.assertIn("first-genuine-golden-v6-execution-blocker-probe.json", text)
        self.assertIn("ready_for_authoritative_golden_preflight", text)

        probe_index = text.index("probe = _probe_execution_prerequisites()")
        run_index = text.index("payload = run(force=args.force, output=args.output)")
        self.assertLess(probe_index, run_index)

    def test_jit_cli_fails_closed_when_probe_is_not_ready(self) -> None:
        text = TOOL.read_text(encoding="utf-8")
        guard = 'if probe.get("ready_for_authoritative_golden_preflight") is not True:'
        self.assertIn(guard, text)
        guard_index = text.index(guard)
        return_index = text.index("return 2", guard_index)
        run_index = text.index("payload = run(force=args.force, output=args.output)")
        self.assertLess(guard_index, return_index)
        self.assertLess(return_index, run_index)

    def test_probe_remains_non_authoritative_zero_cost_and_offline_only(self) -> None:
        text = PROBE.read_text(encoding="utf-8")
        ast.parse(text)

        self.assertIn('"authoritative_gate": False', text)
        self.assertIn('"network_download_authorized": False', text)
        self.assertIn('"generation_authorized": False', text)
        self.assertIn('"publication_ready": False', text)
        self.assertIn('"seeds_2_to_4_authorized": False', text)
        self.assertIn('values.get("PUL7SAR_PHASE18_COST_MODE") != "$0-local"', text)
        self.assertIn('values.get("HF_HUB_OFFLINE") != "1"', text)
        self.assertIn('values.get("TRANSFORMERS_OFFLINE") != "1"', text)
        self.assertIn("QWEN_APPROVED_SNAPSHOT_MISSING", text)
        self.assertIn("FLUX_APPROVED_SNAPSHOT_MISSING", text)
        self.assertIn("NATIVE_BF16_UNAVAILABLE", text)

    def test_workflow_records_probe_before_native_cuda_preflight_and_uploads_receipt_on_failure(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        probe_step = "Record first-Golden execution blocker probe before CUDA preflight"
        cuda_step = "Prove CUDA-enabled PyTorch native BF16 and offline-only model resolution exist without replacing them"
        self.assertIn(probe_step, text)
        self.assertIn(cuda_step, text)
        self.assertIn("phase18_probe_first_golden_execution_blocker.py", text)
        self.assertIn("first-genuine-golden-v6-execution-blocker-probe.json", text)
        self.assertLess(text.index(probe_step), text.index(cuda_step))
        self.assertIn("if: always()", text)
        self.assertIn("output/phase18_gpu_smoke/**", text)
        self.assertIn("phase18_colab_first_genuine_jit_replay_locked.py", text)

    def test_run_function_remains_separate_from_cli_probe_for_existing_unit_replay(self) -> None:
        source = TOOL.read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        self.assertIn("run", functions)
        self.assertIn("main", functions)

        run_source = ast.get_source_segment(source, functions["run"]) or ""
        main_source = ast.get_source_segment(source, functions["main"]) or ""
        self.assertNotIn("_probe_execution_prerequisites", run_source)
        self.assertIn("_probe_execution_prerequisites", main_source)


if __name__ == "__main__":
    unittest.main()
