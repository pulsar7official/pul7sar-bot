from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_preload_host_diagnostic import (
    compare_preload_identity,
    inspect_preload_host,
    non_authority_fields,
)


class QwenImagePreloadHostDiagnosticTests(unittest.TestCase):
    def test_reports_all_identity_drift(self) -> None:
        observed = {
            "gpu_name": "GPU-B",
            "gpu_total_vram_gb": 23.0,
            "torch_version": "2.9.0",
            "cuda_version": "12.8",
        }
        expected = {
            "gpu_name": "GPU-A",
            "gpu_total_vram_gb": 24.0,
            "torch_version": "2.8.0",
            "cuda_version": "12.6",
        }
        self.assertEqual(
            compare_preload_identity(observed, expected),
            [
                "identity_drift:cuda_version",
                "identity_drift:gpu_name",
                "identity_drift:gpu_total_vram_gb",
                "identity_drift:torch_version",
            ],
        )

    def test_accepts_equivalent_vram_observation(self) -> None:
        self.assertEqual(
            compare_preload_identity(
                {"gpu_total_vram_gb": 23.98}, {"gpu_total_vram_gb": 24.0}
            ),
            [],
        )

    def test_diagnostic_never_grants_downstream_authority(self) -> None:
        fields = non_authority_fields()
        self.assertTrue(fields)
        self.assertTrue(all(value is False for value in fields.values()))
        self.assertIn("genuine_golden_png_created", fields)
        self.assertIn("publication_ready", fields)

    def test_preload_replays_inventory_bound_manifest_before_host_probe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "launch.json"
            manifest_path.write_text("{}\n", encoding="utf-8")
            cs260 = root / "runs/cs260.json"
            cs260.parent.mkdir(parents=True)
            cs260.write_text("{}\n", encoding="utf-8")
            snapshot = root / "cache/snapshots/revision"
            snapshot.mkdir(parents=True)

            manifest = {
                "story_snapshot_sha256": "a" * 64,
                "manifest_sha256": "b" * 64,
                "authorization": {"repository_relative_path": "runs/auth.json"},
                "snapshot": {"resolved_path": str(snapshot)},
            }
            authorization = {
                "source_live_pipeline_recheck": {
                    "repository_relative_path": "runs/cs260.json"
                }
            }
            readiness = type(
                "Readiness",
                (),
                {"blockers": ("cuda_unavailable",), "static_preflight_passed": False},
            )()

            with patch(
                "engine.intelligence.qwen_image_preload_host_diagnostic.verify_gpu_host_launch_manifest",
                return_value=manifest,
            ) as verify_manifest, patch(
                "engine.intelligence.qwen_image_preload_host_diagnostic.verify_story_bound_generation_authorization",
                return_value=authorization,
            ), patch(
                "engine.intelligence.qwen_image_preload_host_diagnostic.verify_live_pipeline_receipt",
                return_value={},
            ), patch(
                "engine.intelligence.qwen_image_preload_host_diagnostic._expected_identity",
                return_value={},
            ), patch(
                "engine.intelligence.qwen_image_preload_host_diagnostic.inspect_qwen_image_gpu_readiness",
                return_value=readiness,
            ):
                report = inspect_preload_host(manifest_path, repo_root=root)

            verify_manifest.assert_called_once_with(manifest_path, repo_root=root.resolve())
            self.assertTrue(report["snapshot_inventory_bound"])
            self.assertFalse(report["ready_for_model_load_attempt"])
            self.assertIn("cuda_unavailable", report["blockers"])
            self.assertFalse(report["model_load_attempted"])
            self.assertFalse(report["genuine_golden_png_created"])
            self.assertFalse(report["publication_ready"])

    def test_preload_stops_before_host_probe_when_inventory_manifest_replay_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "launch.json"
            manifest_path.write_text("{}\n", encoding="utf-8")
            with patch(
                "engine.intelligence.qwen_image_preload_host_diagnostic.verify_gpu_host_launch_manifest",
                side_effect=ValueError("QWEN_INVENTORY_BOUND_MANIFEST_SNAPSHOT_BYTE_DRIFT"),
            ), patch(
                "engine.intelligence.qwen_image_preload_host_diagnostic.inspect_qwen_image_gpu_readiness"
            ) as readiness:
                with self.assertRaisesRegex(ValueError, "SNAPSHOT_BYTE_DRIFT"):
                    inspect_preload_host(manifest_path, repo_root=root)
            readiness.assert_not_called()


if __name__ == "__main__":
    unittest.main()
