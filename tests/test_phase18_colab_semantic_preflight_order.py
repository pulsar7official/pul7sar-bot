import unittest
from pathlib import Path


class ColabSemanticPreflightOrderTests(unittest.TestCase):
    def test_semantic_runtime_is_proven_before_any_full_flow_gpu_generation(self):
        text = Path("tools/phase18_colab_one_command.py").read_text(encoding="utf-8")
        preflight = text.index('print(f"3/9 Proving semantic runtime compatibility {stage_text}...")')
        runner = text.index('print("4/9 Entering story-first Golden editorial runner...")')
        self.assertLess(preflight, runner)
        self.assertIn('"before semantic-only reuse" if args.semantic_only_existing else "before GPU generation"', text)
        self.assertIn("_require_existing_generation_for_semantic(args.candidate)", text)

    def test_full_execution_keeps_qwen_as_publication_gate_but_can_degrade_to_engineering_proof(self):
        text = Path("tools/phase18_colab_one_command.py").read_text(encoding="utf-8")
        self.assertIn('_require_semantic_runtime_ready()', text)
        self.assertIn('SEMANTIC_QA_BLOCKED', text)
        self.assertIn('GOLDEN_EDITORIAL_ENGINEERING_PROOF', text)
        self.assertIn('"publication_ready": False', text)
        self.assertIn('--strict-semantic', text)
        self.assertIn('"deterministic_pitch_applied": False', text)
        self.assertIn('"pitch_replacement_required": False', text)

    def test_semantic_readiness_is_rechecked_inside_editorial_review(self):
        text = Path("tools/phase18_colab_one_command.py").read_text(encoding="utf-8")
        review = text.index("def _review_editorial_base")
        readiness = text.index("readiness = _require_semantic_runtime_ready()", review)
        inspection = text.index("inspector.inspect_file", review)
        self.assertLess(readiness, inspection)
        self.assertGreaterEqual(text.count("_require_semantic_runtime_ready()"), 2)


if __name__ == "__main__":
    unittest.main()
