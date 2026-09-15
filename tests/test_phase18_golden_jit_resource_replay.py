import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_MODEL_ID
from engine.intelligence.golden_jit_resource_replay import verify_golden_jit_resource_replay


def _sha(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


class GoldenJitResourceReplayTests(unittest.TestCase):
    def _fixture(self, root: Path):
        gpu_path = root / "output" / "gpu.json"
        ram_path = root / "output" / "ram.json"
        gpu_path.parent.mkdir(parents=True, exist_ok=True)

        gpu = {
            "eligible": True,
            "model_id": FLUX2_KLEIN_4B_MODEL_ID,
            "runtime_kind": "local_cuda",
            "cuda_available": True,
            "bf16_supported": True,
            "cost_mode": "$0-local",
            "gpu_free_vram_gb": 15.25,
            "required_vram_gb": 13.0,
            "policy": {
                "requires_live_free_vram": True,
                "required_dtype": "bfloat16",
                "required_model": FLUX2_KLEIN_4B_MODEL_ID,
                "queue_mutation": False,
                "downloads_model_weights": False,
                "installs_dependencies": False,
                "uses_paid_api": False,
            },
        }
        ram = {
            "schema": "pul7sar-first-golden-host-memory-preflight-v1",
            "branch": "phase18/story-intelligence",
            "ready": True,
            "cost_mode": "$0-local",
            "available_ram_gb": 18.5,
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
        gpu_path.write_text(json.dumps(gpu, sort_keys=True), encoding="utf-8")
        ram_path.write_text(json.dumps(ram, sort_keys=True), encoding="utf-8")

        staging = {
            "schema": "pul7sar-first-genuine-golden-staging-v3",
            "status": "FIRST_GENUINE_GOLDEN_EDITORIAL_CANDIDATE_READY_FOR_HUMAN_REVIEW",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "resolved_dtype": "bfloat16",
            "pre_execution_resource_guard_bound": True,
            "pre_execution_gpu_host_qualification": {
                "path": str(gpu_path),
                "sha256": _sha(gpu_path),
                "bytes": gpu_path.stat().st_size,
            },
            "pre_execution_host_memory": {
                "path": str(ram_path),
                "sha256": _sha(ram_path),
                "bytes": ram_path.stat().st_size,
            },
            "pre_execution_live_free_vram_gb": 15.25,
            "pre_execution_required_vram_gb": 13.0,
            "pre_execution_available_host_ram_gb": 18.5,
            "pre_execution_required_host_ram_gb": 10.0,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        return staging, gpu_path, ram_path

    def test_replay_accepts_bound_live_gpu_and_ram_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging, _, _ = self._fixture(root)
            result = verify_golden_jit_resource_replay(repository_root=root, staging=staging)
            self.assertEqual(result["status"], "GOLDEN_JIT_PREEXECUTION_RESOURCE_REPLAY_VERIFIED")
            self.assertEqual(result["candidate"], 1)
            self.assertFalse(result["publication_ready"])
            self.assertFalse(result["seeds_2_to_4_authorized"])
            self.assertEqual(len(result["resource_fingerprint_sha256"]), 64)

    def test_replay_rejects_gpu_evidence_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging, gpu_path, _ = self._fixture(root)
            gpu_path.write_text(gpu_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "GPU_EVIDENCE_DRIFT"):
                verify_golden_jit_resource_replay(repository_root=root, staging=staging)

    def test_replay_rejects_live_vram_below_floor_even_if_record_hash_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging, gpu_path, _ = self._fixture(root)
            gpu = json.loads(gpu_path.read_text(encoding="utf-8"))
            gpu["gpu_free_vram_gb"] = 8.0
            gpu_path.write_text(json.dumps(gpu, sort_keys=True), encoding="utf-8")
            staging["pre_execution_gpu_host_qualification"]["sha256"] = _sha(gpu_path)
            staging["pre_execution_gpu_host_qualification"]["bytes"] = gpu_path.stat().st_size
            staging["pre_execution_live_free_vram_gb"] = 8.0
            with self.assertRaisesRegex(RuntimeError, "GPU_FREE_VRAM_BELOW_FLOOR"):
                verify_golden_jit_resource_replay(repository_root=root, staging=staging)

    def test_replay_rejects_host_ram_below_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging, _, ram_path = self._fixture(root)
            ram = json.loads(ram_path.read_text(encoding="utf-8"))
            ram["available_ram_gb"] = 6.0
            ram_path.write_text(json.dumps(ram, sort_keys=True), encoding="utf-8")
            staging["pre_execution_host_memory"]["sha256"] = _sha(ram_path)
            staging["pre_execution_host_memory"]["bytes"] = ram_path.stat().st_size
            staging["pre_execution_available_host_ram_gb"] = 6.0
            with self.assertRaisesRegex(RuntimeError, "HOST_RAM_BELOW_FLOOR"):
                verify_golden_jit_resource_replay(repository_root=root, staging=staging)

    def test_replay_rejects_staging_authority_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            staging, _, _ = self._fixture(root)
            staging["publication_ready"] = True
            with self.assertRaisesRegex(RuntimeError, "STAGING_AUTHORITY_DRIFT"):
                verify_golden_jit_resource_replay(repository_root=root, staging=staging)

    def test_replay_rejects_path_escape(self):
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            staging, _, _ = self._fixture(root)
            outside_path = Path(outside) / "gpu.json"
            outside_path.write_text("{}", encoding="utf-8")
            staging["pre_execution_gpu_host_qualification"] = {
                "path": str(outside_path),
                "sha256": _sha(outside_path),
                "bytes": outside_path.stat().st_size,
            }
            with self.assertRaisesRegex(RuntimeError, "PATH_ESCAPES_REPOSITORY"):
                verify_golden_jit_resource_replay(repository_root=root, staging=staging)


if __name__ == "__main__":
    unittest.main()
