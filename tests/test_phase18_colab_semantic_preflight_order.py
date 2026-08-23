import unittest
from pathlib import Path


class ColabSemanticPreflightOrderTests(unittest.TestCase):
    def test_semantic_runtime_is_proven_before_gpu_runner(self):
        text = Path("tools/phase18_colab_one_command.py").read_text(encoding="utf-8")
        preflight = text.index("Proving Qwen/Pillow semantic runtime compatibility before GPU generation")
        runner = text.index("Entering locked atmosphere-only Golden runner")
        self.assertLess(preflight, runner)

    def test_full_execution_keeps_qwen_as_publication_gate_but_can_degrade_to_engineering_proof(self):
        text = Path("tools/phase18_colab_one_command.py").read_text(encoding="utf-8")
        self.assertIn('_require_semantic_runtime_ready()', text)
        self.assertIn('SEMANTIC_QA_BLOCKED', text)
        self.assertIn('GOLDEN_HYBRID_ENGINEERING_PROOF', text)
        self.assertIn('"publication_ready": False', text)
        self.assertIn('--strict-semantic', text)

    def test_semantic_readiness_is_rechecked_before_inspection(self):
        text = Path("tools/phase18_colab_one_command.py").read_text(encoding="utf-8")
        self.assertIn("Rechecking semantic runtime immediately before visual inspection", text)
        self.assertIn('semantic_report["runtime_readiness"] = _require_semantic_runtime_ready()', text)


if __name__ == "__main__":
    unittest.main()
