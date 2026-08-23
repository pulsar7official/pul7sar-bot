import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import tools.phase18_colab_bootstrap as bootstrap
from engine.intelligence.qwen25_vl_inspector import MODEL_ID


class QwenModelPrefetchTests(unittest.TestCase):
    def test_prefetch_command_is_exact_zero_cost_cache_preparation(self):
        text = Path("tools/phase18_prefetch_qwen.py").read_text(encoding="utf-8")
        self.assertIn('from engine.intelligence.qwen25_vl_inspector import MODEL_ID', text)
        self.assertIn('"cost_mode": "$0-local"', text)
        self.assertIn('snapshot_download(repo_id=MODEL_ID)', text)
        self.assertIn('local_files_only=True', text)
        self.assertIn('config.json', text)
        self.assertIn('*.safetensors', text)
        self.assertNotIn('pipeline(', text)
        self.assertEqual(MODEL_ID, "Qwen/Qwen2.5-VL-3B-Instruct")

    def test_bootstrap_prefetches_semantic_weights_before_golden_runner(self):
        text = Path("tools/phase18_colab_bootstrap.py").read_text(encoding="utf-8")
        prefetch = text.index("Proving/caching exact Qwen semantic weights before FLUX GPU generation")
        runner = text.index("Launching protected Golden Hybrid v5 runner")
        self.assertLess(prefetch, runner)
        self.assertIn('semantic_mode = "none"', text)
        self.assertIn("SEMANTIC_MODEL_CACHE_REQUIRED_BY_STRICT_MODE", text)

    def test_prefetch_failure_is_observable_without_exception_in_normal_mode(self):
        completed = SimpleNamespace(returncode=1)
        with patch.object(bootstrap, "_run", return_value=completed):
            self.assertFalse(bootstrap._prefetch_semantic_model())

    def test_prefetch_success_is_observable(self):
        completed = SimpleNamespace(returncode=0)
        with patch.object(bootstrap, "_run", return_value=completed):
            self.assertTrue(bootstrap._prefetch_semantic_model())


if __name__ == "__main__":
    unittest.main()
