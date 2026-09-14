import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from tools.phase18_verify_first_genuine_golden_v6_snapshot_bound import (
    _sha256_json,
    build_manifest,
)


class FirstGoldenSnapshotBoundManifestTests(unittest.TestCase):
    def _model(self, model_id: str, revision: str, name: str, size: int) -> dict:
        files = [{"path": name, "size_bytes": size, "is_symlink": False}]
        payload = {"model_id": model_id, "revision": revision, "files": files, "total_bytes": size}
        return {
            "model_id": model_id,
            "revision": revision,
            "snapshot_path": f"/cache/{revision}",
            "file_count": 1,
            "total_bytes": size,
            "inventory_sha256": _sha256_json(payload),
            "files": files,
            "ready": True,
            "blockers": [],
        }

    def _inventory(self) -> dict:
        qwen = self._model(QWEN25_VL_3B_MODEL_ID, QWEN25_VL_3B_REVISION, "config.json", 17)
        flux = self._model(FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION, "model.safetensors", 31)
        combined = _sha256_json({
            "qwen_inventory_sha256": qwen["inventory_sha256"],
            "flux_inventory_sha256": flux["inventory_sha256"],
        })
        return {
            "schema": "pul7sar-phase18-approved-snapshot-inventory-v1",
            "branch_required": "phase18/story-intelligence",
            "cost_mode": "$0-local",
            "offline_only": True,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
            "cache_root": "/cache",
            "qwen": qwen,
            "flux": flux,
            "combined_inventory_sha256": combined,
            "ready": True,
            "blockers": [],
        }

    def _runtime(self, digest: str = "c" * 64) -> dict:
        return {
            "runtime_fingerprint_sha256": digest,
            "cost_mode": "$0-local",
            "generation_authorized": False,
            "queue_mutated": False,
            "png_created": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _execution_probe(self, digest: str = "c" * 64) -> dict:
        return {
            "schema": "pul7sar-phase18-first-golden-execution-blocker-probe-v6",
            "ready_for_authoritative_golden_preflight": True,
            "blockers": [],
            "cost_mode_required": "$0-local",
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
            "generation_runtime": {
                "ready": True,
                "runtime_fingerprint_sha256": digest,
                "cost_mode": "$0-local",
                "generation_authorized": False,
                "publication_ready": False,
            },
        }

    def _upstream(self, execution_probe_path: Path) -> dict:
        import hashlib
        execution_sha = hashlib.sha256(execution_probe_path.read_bytes()).hexdigest()
        return {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v3",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "offline_only": True,
            "source_commit_sha": "a" * 40,
            "source_commit_verified": True,
            "execution_environment_verified": True,
            "runner_identity_verified": True,
            "fresh_attempt_evidence": True,
            "source_bound_artifact_verified": True,
            "png_sha256": "b" * 64,
            "evidence": {"execution_blocker_probe": {"path": str(execution_probe_path), "sha256": execution_sha}},
            "eligible_for_human_visual_review": True,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }

    def _write(self, root: Path, name: str, payload: dict) -> Path:
        path = root / name
        path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def test_accepts_identical_preflight_and_post_generation_inventory_and_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = self._inventory()
            execution_path = self._write(root, "execution.json", self._execution_probe())
            upstream_path = self._write(root, "upstream.json", self._upstream(execution_path))
            inventory_path = self._write(root, "inventory.json", inventory)
            manifest = build_manifest(
                upstream_manifest_path=upstream_path,
                recorded_inventory_path=inventory_path,
                execution_probe_path=execution_path,
                current_inventory=inventory,
                current_runtime=self._runtime(),
            )
            self.assertTrue(manifest["approved_snapshot_inventory_verified"])
            self.assertTrue(manifest["approved_snapshot_inventory_replayed_after_generation"])
            self.assertTrue(manifest["generation_runtime_fingerprint_verified_after_generation"])
            self.assertEqual(manifest["generation_runtime_fingerprint_sha256"], "c" * 64)
            self.assertTrue(manifest["eligible_for_human_visual_review"])
            self.assertFalse(manifest["publication_ready"])
            self.assertEqual(manifest["png_sha256"], "b" * 64)

    def test_rejects_cache_drift_after_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            recorded = self._inventory()
            replay = self._inventory()
            replay["flux"] = self._model(FLUX2_KLEIN_4B_MODEL_ID, FLUX2_KLEIN_4B_REVISION, "model.safetensors", 32)
            replay["combined_inventory_sha256"] = _sha256_json({
                "qwen_inventory_sha256": replay["qwen"]["inventory_sha256"],
                "flux_inventory_sha256": replay["flux"]["inventory_sha256"],
            })
            execution_path = self._write(root, "execution.json", self._execution_probe())
            upstream_path = self._write(root, "upstream.json", self._upstream(execution_path))
            inventory_path = self._write(root, "inventory.json", recorded)
            with self.assertRaisesRegex(RuntimeError, "CACHE_DRIFT_AFTER_PREFLIGHT"):
                build_manifest(
                    upstream_manifest_path=upstream_path,
                    recorded_inventory_path=inventory_path,
                    execution_probe_path=execution_path,
                    current_inventory=replay,
                    current_runtime=self._runtime(),
                )

    def test_rejects_generation_runtime_drift_after_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = self._inventory()
            execution_path = self._write(root, "execution.json", self._execution_probe("c" * 64))
            upstream_path = self._write(root, "upstream.json", self._upstream(execution_path))
            inventory_path = self._write(root, "inventory.json", inventory)
            with self.assertRaisesRegex(RuntimeError, "GENERATION_RUNTIME_DRIFT_AFTER_PREFLIGHT"):
                build_manifest(
                    upstream_manifest_path=upstream_path,
                    recorded_inventory_path=inventory_path,
                    execution_probe_path=execution_path,
                    current_inventory=inventory,
                    current_runtime=self._runtime("d" * 64),
                )

    def test_rejects_execution_probe_link_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = self._inventory()
            execution_path = self._write(root, "execution.json", self._execution_probe())
            upstream = self._upstream(execution_path)
            upstream["evidence"]["execution_blocker_probe"]["sha256"] = "e" * 64
            upstream_path = self._write(root, "upstream.json", upstream)
            inventory_path = self._write(root, "inventory.json", inventory)
            with self.assertRaisesRegex(RuntimeError, "EXECUTION_PROBE_LINK_DRIFT"):
                build_manifest(
                    upstream_manifest_path=upstream_path,
                    recorded_inventory_path=inventory_path,
                    execution_probe_path=execution_path,
                    current_inventory=inventory,
                    current_runtime=self._runtime(),
                )

    def test_rejects_authority_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inventory = self._inventory()
            execution_path = self._write(root, "execution.json", self._execution_probe())
            upstream = self._upstream(execution_path)
            upstream["publication_ready"] = True
            upstream_path = self._write(root, "upstream.json", upstream)
            inventory_path = self._write(root, "inventory.json", inventory)
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT"):
                build_manifest(
                    upstream_manifest_path=upstream_path,
                    recorded_inventory_path=inventory_path,
                    execution_probe_path=execution_path,
                    current_inventory=inventory,
                    current_runtime=self._runtime(),
                )


if __name__ == "__main__":
    unittest.main()
