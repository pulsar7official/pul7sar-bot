import unittest
from pathlib import Path


class FirstGenuineGoldenV6JitLockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.wrapper = Path("tools/phase18_colab_first_genuine_jit_replay_locked.py").read_text(encoding="utf-8")

    def test_jit_replay_occurs_after_offload_lock_and_before_final_receipt(self):
        inner = self.wrapper.index("phase18_colab_first_genuine_offload_locked.py")
        load_outer = self.wrapper.index("outer = _load(OFFLOAD_LOCK)")
        # Measure the runtime call site rather than the import statement near the
        # top of the file.
        replay = self.wrapper.index("jit = verify_golden_jit_resource_replay(repository_root=ROOT, staging=staging)")
        final_payload = self.wrapper.index('"schema": "pul7sar-first-genuine-golden-v6-jit-lock-v1"')
        self.assertLess(inner, load_outer)
        self.assertLess(load_outer, replay)
        self.assertLess(replay, final_payload)

    def test_wrapper_requires_nested_staging_and_jit_resource_binding(self):
        self.assertIn('outer_evidence.get("inner_resource_lock")', self.wrapper)
        self.assertIn('inner_evidence.get("strict_golden_staging")', self.wrapper)
        self.assertIn("FIRST_GENUINE_GOLDEN_JIT_STAGING_PATH_DRIFT", self.wrapper)
        self.assertIn('"jit_pre_execution_resource_replay_bound": True', self.wrapper)
        self.assertIn('"jit_resource_replay": _record(JIT_REPLAY)', self.wrapper)
        self.assertIn("resource_fingerprint_sha256", self.wrapper)

    def test_wrapper_keeps_human_golden_publication_and_extra_seeds_closed(self):
        self.assertIn('"human_visual_review_approved": False', self.wrapper)
        self.assertIn('"golden_quality_approved": False', self.wrapper)
        self.assertIn('"publication_ready": False', self.wrapper)
        self.assertIn('"seeds_2_to_4_authorized": False', self.wrapper)

    def test_wrapper_requires_actual_offload_binding_before_jit_replay(self):
        self.assertIn('outer.get("safe_offload_preflight_bound") is not True', self.wrapper)
        self.assertIn('outer.get("actual_offload_mode_bound") is not True', self.wrapper)
        self.assertIn('outer.get("selected_safe_offload_mode") != outer.get("actual_offload_mode")', self.wrapper)


if __name__ == "__main__":
    unittest.main()
