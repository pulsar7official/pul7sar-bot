import unittest

from engine.intelligence.first_golden_cache_budget import GIB, FirstGoldenCacheBudgetPolicy


class FirstGoldenCacheBudgetPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = FirstGoldenCacheBudgetPolicy(qwen_minimum_free_gib=12.0, flux_minimum_free_gib=30.0)

    def test_both_missing_require_combined_headroom(self):
        decision = self.policy.evaluate(qwen_cached=False, flux_cached=False, free_bytes=41 * GIB)
        self.assertFalse(decision.eligible)
        self.assertEqual(decision.combined_minimum_free_gib, 42.0)
        self.assertIn("42.000 GiB", decision.reasons[0])

    def test_both_missing_pass_with_combined_headroom(self):
        decision = self.policy.evaluate(qwen_cached=False, flux_cached=False, free_bytes=45 * GIB)
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.combined_minimum_free_gib, 42.0)

    def test_qwen_cached_only_requires_flux_budget(self):
        decision = self.policy.evaluate(qwen_cached=True, flux_cached=False, free_bytes=31 * GIB)
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.combined_minimum_free_gib, 30.0)

    def test_flux_cached_only_requires_qwen_budget(self):
        decision = self.policy.evaluate(qwen_cached=False, flux_cached=True, free_bytes=13 * GIB)
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.combined_minimum_free_gib, 12.0)

    def test_both_cached_do_not_require_free_space_proof(self):
        decision = self.policy.evaluate(qwen_cached=True, flux_cached=True, free_bytes=None)
        self.assertTrue(decision.eligible)
        self.assertEqual(decision.combined_minimum_free_gib, 0.0)

    def test_missing_models_without_disk_proof_fail_closed(self):
        decision = self.policy.evaluate(qwen_cached=False, flux_cached=True, free_bytes=None)
        self.assertFalse(decision.eligible)
        with self.assertRaisesRegex(RuntimeError, "cache budget is not eligible"):
            self.policy.assert_eligible(decision)

    def test_negative_free_space_is_rejected(self):
        with self.assertRaises(ValueError):
            self.policy.evaluate(qwen_cached=False, flux_cached=False, free_bytes=-1)


if __name__ == "__main__":
    unittest.main()
