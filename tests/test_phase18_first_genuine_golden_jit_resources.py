import json
import tempfile
import unittest
from pathlib import Path

import tools.phase18_colab_first_genuine_golden as golden


class FirstGenuineGoldenJitResourceTests(unittest.TestCase):
    def _gpu(self) -> dict[str, object]:
        return {
            "eligible": True,
            "model_id": golden.FLUX2_KLEIN_4B_MODEL_ID,
            "runtime_kind": "local_cuda",
            "cuda_available": True,
            "bf16_supported": True,
            "cost_mode": golden.EXPECTED_COST_MODE,
            "gpu_free_vram_gb": 15.0,
            "required_vram_gb": 13.0,
            "policy": {
                "queue_mutation": False,
                "downloads_model_weights": False,
                "installs_dependencies": False,
                "uses_paid_api": False,
                "requires_live_free_vram": True,
                "required_dtype": golden.EXPECTED_DTYPE,
                "required_model": golden.FLUX2_KLEIN_4B_MODEL_ID,
            },
        }

    def _memory(self) -> dict[str, object]:
        return {
            "schema": "pul7sar-first-golden-host-memory-preflight-v1",
            "branch": golden.EXPECTED_BRANCH,
            "ready": True,
            "cost_mode": golden.EXPECTED_COST_MODE,
            "available_ram_gb": 12.0,
            "minimum_available_ram_gb": 10.0,
            "model_downloads_performed": False,
            "model_loaded": False,
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def test_jit_gpu_accepts_live_bf16_zero_cost_host(self):
        free_vram, required_vram = golden._validate_jit_gpu(self._gpu())
        self.assertEqual(free_vram, 15.0)
        self.assertEqual(required_vram, 13.0)

    def test_jit_gpu_rejects_live_vram_or_authority_drift(self):
        payload = self._gpu()
        payload["gpu_free_vram_gb"] = 8.0
        with self.assertRaisesRegex(RuntimeError, "LIVE_FREE_VRAM_BELOW_FLOOR"):
            golden._validate_jit_gpu(payload)

        payload = self._gpu()
        payload["policy"]["uses_paid_api"] = True
        with self.assertRaisesRegex(RuntimeError, "ILLEGAL_AUTHORITY"):
            golden._validate_jit_gpu(payload)

    def test_jit_host_memory_accepts_live_floor_and_rejects_drift(self):
        available, minimum = golden._validate_jit_host_memory(self._memory())
        self.assertEqual(available, 12.0)
        self.assertEqual(minimum, 10.0)

        payload = self._memory()
        payload["available_ram_gb"] = 9.0
        with self.assertRaisesRegex(RuntimeError, "BELOW_FLOOR"):
            golden._validate_jit_host_memory(payload)

        payload = self._memory()
        payload["generation_authorized"] = True
        with self.assertRaisesRegex(RuntimeError, "ILLEGAL_AUTHORITY"):
            golden._validate_jit_host_memory(payload)

    def test_jit_evidence_replay_detects_byte_drift(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            path = Path(temp) / "jit-resource.json"
            path.write_text(json.dumps({"ready": True}), encoding="utf-8")
            record = golden._evidence_record(path)
            golden._assert_evidence_unchanged(record)
            path.write_text(json.dumps({"ready": False}), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "EVIDENCE_DRIFT_DURING_GENERATION"):
                golden._assert_evidence_unchanged(record)

    def test_cli_orders_jit_resource_guard_immediately_before_candidate(self):
        source = Path(golden.__file__).read_text(encoding="utf-8")
        guard_call = source.index("pre_execution_resources = _run_pre_execution_resource_guard()")
        candidate_call = source.index("completed = subprocess.run(command, cwd=ROOT)")
        replay_gpu = source.index('_assert_evidence_unchanged(pre_execution_resources["gpu"])')
        replay_memory = source.index('_assert_evidence_unchanged(pre_execution_resources["host_memory"])')
        verify = source.index("payload = verify_genuine_candidate()")
        self.assertLess(guard_call, candidate_call)
        self.assertLess(candidate_call, replay_gpu)
        self.assertLess(replay_gpu, replay_memory)
        self.assertLess(replay_memory, verify)
        self.assertIn('"--candidate", "1"', source)
        self.assertIn('"--strict-semantic"', source)
        self.assertIn('"--skip-update"', source)


if __name__ == "__main__":
    unittest.main()
