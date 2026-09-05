import unittest
from pathlib import Path

from engine.intelligence.model_cache_headroom import ModelCacheHeadroomPolicy


ROOT = Path(__file__).resolve().parents[1]
PREFETCH = ROOT / "tools" / "phase18_prefetch_flux2.py"
RESOURCE_LOCK = ROOT / "tools" / "phase18_colab_first_genuine_resources_locked.py"


class ModelCacheHeadroomPolicyTests(unittest.TestCase):
    def test_accepts_working_headroom_at_or_above_floor(self):
        policy = ModelCacheHeadroomPolicy(minimum_working_free_gib=8.0)
        decision = policy.evaluate(free_bytes=8 * 1024 ** 3)
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.reason, "post_cache_working_headroom_ready")
        policy.assert_eligible(decision)

    def test_rejects_working_headroom_below_floor(self):
        policy = ModelCacheHeadroomPolicy(minimum_working_free_gib=8.0)
        decision = policy.evaluate(free_bytes=7 * 1024 ** 3)
        self.assertFalse(decision.eligible)
        self.assertEqual(decision.reason, "post_cache_working_headroom_below_floor")
        with self.assertRaisesRegex(RuntimeError, "PHASE18_MODEL_CACHE_POST_HEADROOM_INSUFFICIENT"):
            policy.assert_eligible(decision)

    def test_rejects_invalid_policy_or_measurement_values(self):
        for value in (0, -1, float("inf"), True, "8"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ModelCacheHeadroomPolicy(minimum_working_free_gib=value)  # type: ignore[arg-type]

        policy = ModelCacheHeadroomPolicy()
        for value in (-1, True, 8.0, "1024"):
            with self.subTest(free_bytes=value):
                with self.assertRaises(ValueError):
                    policy.evaluate(free_bytes=value)  # type: ignore[arg-type]


class FluxPrefetchPostHeadroomContractTests(unittest.TestCase):
    def test_prefetch_rechecks_live_disk_after_pinned_snapshot_is_validated(self):
        text = PREFETCH.read_text(encoding="utf-8")
        revision_check = text.index("resolved_revision = assert_snapshot_revision")
        post_usage = text.index("post_cache_free_bytes = shutil.disk_usage(cache_root).free")
        headroom_assert = text.index("headroom_policy.assert_eligible(after)")
        receipt = text.index('"working_headroom_after_cache": asdict(after)')

        self.assertLess(revision_check, post_usage)
        self.assertLess(post_usage, headroom_assert)
        self.assertLess(headroom_assert, receipt)
        self.assertIn('"--minimum-working-free-gib"', text)
        self.assertIn('"working_headroom_ready": True', text)

    def test_resource_lock_prefetches_flux_before_runtime_fingerprint_and_candidate(self):
        text = RESOURCE_LOCK.read_text(encoding="utf-8")
        prefetch = text.index('"phase18_prefetch_flux2.py"')
        runtime_pre = text.index("runtime_before = capture_generation_runtime_fingerprint()")
        candidate = text.index('"phase18_colab_first_genuine_golden.py"')

        self.assertLess(prefetch, runtime_pre)
        self.assertLess(runtime_pre, candidate)


if __name__ == "__main__":
    unittest.main()
