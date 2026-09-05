import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import tools.phase18_colab_bootstrap as bootstrap
from engine.intelligence.approved_model_revisions import QWEN25_VL_3B_REVISION
from engine.intelligence.qwen25_vl_inspector import MODEL_ID, MODEL_REVISION


class QwenModelPrefetchTests(unittest.TestCase):
    def test_prefetch_command_is_exact_zero_cost_cache_preparation(self):
        text = Path("tools/phase18_prefetch_qwen.py").read_text(encoding="utf-8")
        self.assertIn('QWEN25_VL_3B_MODEL_ID', text)
        self.assertIn('QWEN25_VL_3B_REVISION', text)
        self.assertIn('"cost_mode": "$0-local"', text)
        self.assertIn('revision=MODEL_REVISION', text)
        self.assertIn('local_files_only=True', text)
        self.assertIn('assert_snapshot_revision(snapshot, MODEL_REVISION)', text)
        self.assertIn('"revision_pinned": True', text)
        self.assertIn('config.json', text)
        self.assertIn('*.safetensors', text)
        self.assertNotIn('pipeline(', text)
        self.assertEqual(MODEL_ID, "Qwen/Qwen2.5-VL-3B-Instruct")
        self.assertEqual(MODEL_REVISION, QWEN25_VL_3B_REVISION)
        self.assertEqual(len(MODEL_REVISION), 40)

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
