import unittest

from engine.intelligence.model_cache import GIB, ModelCachePolicy


class Phase18ModelCachePolicyTests(unittest.TestCase):
    def test_cached_snapshot_is_eligible_without_requiring_download_space(self):
        decision = ModelCachePolicy(minimum_free_gib=30.0).evaluate(
            model_id="black-forest-labs/FLUX.2-klein-4B",
            cached_snapshot_path="/cache/models--black-forest-labs--FLUX.2-klein-4B/snapshots/abc",
            free_bytes=2 * GIB,
        )
        self.assertTrue(decision.eligible)
        self.assertTrue(decision.cache_ready)
        self.assertFalse(decision.download_required)
        self.assertEqual(decision.reasons, ())

    def test_uncached_snapshot_requires_proven_disk_headroom(self):
        decision = ModelCachePolicy(minimum_free_gib=30.0).evaluate(
            model_id="black-forest-labs/FLUX.2-klein-4B",
            cached_snapshot_path=None,
            free_bytes=29 * GIB,
        )
        self.assertFalse(decision.eligible)
        self.assertTrue(decision.download_required)
        self.assertIn("at least 30.000 GiB", decision.reasons[0])

    def test_uncached_snapshot_with_sufficient_disk_is_eligible(self):
        decision = ModelCachePolicy(minimum_free_gib=30.0).evaluate(
            model_id="black-forest-labs/FLUX.2-klein-4B",
            cached_snapshot_path=None,
            free_bytes=40 * GIB,
        )
        self.assertTrue(decision.eligible)
        self.assertTrue(decision.download_required)
        self.assertAlmostEqual(decision.free_gib, 40.0)

    def test_unknown_free_space_fails_closed_when_download_is_required(self):
        decision = ModelCachePolicy().evaluate(
            model_id="black-forest-labs/FLUX.2-klein-4B",
            cached_snapshot_path=None,
            free_bytes=None,
        )
        self.assertFalse(decision.eligible)
        self.assertIn("could not be proven", decision.reasons[0])

    def test_invalid_policy_or_free_space_is_rejected(self):
        with self.assertRaises(ValueError):
            ModelCachePolicy(minimum_free_gib=0)
        with self.assertRaises(ValueError):
            ModelCachePolicy().evaluate(
                model_id="black-forest-labs/FLUX.2-klein-4B",
                cached_snapshot_path=None,
                free_bytes=-1,
            )


if __name__ == "__main__":
    unittest.main()
