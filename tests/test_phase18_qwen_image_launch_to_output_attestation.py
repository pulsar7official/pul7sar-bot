from __future__ import annotations

from pathlib import Path
import unittest

from engine.intelligence.qwen_image_launch_to_output_attestation import (
    _assert_join,
    _snapshot_inventory_evidence,
)


def _records():
    launch = {
        "story_snapshot_sha256": "a" * 64,
        "model_id": "Qwen/Qwen-Image-2512",
        "model_revision": "2ce1c28560fbc62c9f5531e076b237d3575330a9",
        "cost_mode": "$0-local",
        "network_allowed": False,
        "local_files_only": True,
        "snapshot": {
            "resolved_path": "/tmp/snapshots/2ce1",
            "revision": "2ce1c28560fbc62c9f5531e076b237d3575330a9",
            "revision_verified": True,
        },
        "snapshot_byte_inventory": {
            "schema": "pul7sar.phase18.qwen_image_snapshot_inventory.v1",
            "model_revision": "2ce1c28560fbc62c9f5531e076b237d3575330a9",
            "snapshot_inventory_sha256": "c" * 64,
            "snapshot_file_count": 17,
            "snapshot_total_bytes": 123456,
        },
        "inference_settings": {
            "width": 1024,
            "height": 1024,
            "seed": 7,
            "num_inference_steps": 8,
            "guidance_scale": 1.0,
        },
    }
    provenance = {
        "story_snapshot_sha256": launch["story_snapshot_sha256"],
        "model_id": launch["model_id"],
        "model_revision": launch["model_revision"],
        "cost_mode": "$0-local",
        "network_allowed": False,
        "local_files_only": True,
        "snapshot": dict(launch["snapshot"]),
        "genuine_canonical_inference_executed": True,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    canonical = {
        "story_snapshot_sha256": launch["story_snapshot_sha256"],
        "model_id": launch["model_id"],
        "model_revision": launch["model_revision"],
        "cost_mode": "$0-local",
        "width": 1024,
        "height": 1024,
        "seed": 7,
        "num_inference_steps": 8,
        "guidance_scale": 1.0,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    return launch, provenance, canonical


class LaunchToOutputAttestationTests(unittest.TestCase):
    def test_launch_output_join_accepts_exact_attested_execution(self) -> None:
        launch, provenance, canonical = _records()
        _assert_join(launch, provenance, canonical)

    def test_inventory_evidence_accepts_exact_bound_snapshot(self) -> None:
        launch, _, _ = _records()
        evidence = _snapshot_inventory_evidence(launch)
        self.assertEqual(evidence["snapshot_inventory_sha256"], "c" * 64)
        self.assertEqual(evidence["snapshot_file_count"], 17)
        self.assertEqual(evidence["snapshot_total_bytes"], 123456)
        self.assertEqual(evidence["model_revision"], launch["model_revision"])

    def test_inventory_evidence_rejects_missing_inventory(self) -> None:
        launch, _, _ = _records()
        launch.pop("snapshot_byte_inventory")
        with self.assertRaisesRegex(ValueError, "SNAPSHOT_INVENTORY_MISSING"):
            _snapshot_inventory_evidence(launch)

    def test_inventory_evidence_rejects_revision_drift(self) -> None:
        launch, _, _ = _records()
        launch["snapshot_byte_inventory"]["model_revision"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "SNAPSHOT_INVENTORY_REVISION_DRIFT"):
            _snapshot_inventory_evidence(launch)

    def test_launch_output_join_rejects_seed_drift(self) -> None:
        launch, provenance, canonical = _records()
        canonical["seed"] = 8
        with self.assertRaisesRegex(ValueError, "SETTINGS_DRIFT:seed"):
            _assert_join(launch, provenance, canonical)

    def test_launch_output_join_rejects_story_drift(self) -> None:
        launch, provenance, canonical = _records()
        canonical["story_snapshot_sha256"] = "b" * 64
        with self.assertRaisesRegex(ValueError, "JOIN_DRIFT:story_snapshot_sha256"):
            _assert_join(launch, provenance, canonical)

    def test_launch_output_join_rejects_network_enabled_provenance(self) -> None:
        launch, provenance, canonical = _records()
        provenance["network_allowed"] = True
        with self.assertRaisesRegex(ValueError, "NETWORK_DRIFT"):
            _assert_join(launch, provenance, canonical)

    def test_launch_output_join_rejects_snapshot_path_drift(self) -> None:
        launch, provenance, canonical = _records()
        provenance["snapshot"]["resolved_path"] = "/tmp/other"
        with self.assertRaisesRegex(ValueError, "SNAPSHOT_DRIFT:resolved_path"):
            _assert_join(launch, provenance, canonical)

    def test_launch_output_join_rejects_premature_golden_authority(self) -> None:
        launch, provenance, canonical = _records()
        provenance["genuine_golden_png_created"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:genuine_golden_png_created"):
            _assert_join(launch, provenance, canonical)

    def test_attestation_module_requires_inventory_bound_manifest_replay(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (
            root / "engine/intelligence/qwen_image_launch_to_output_attestation.py"
        ).read_text(encoding="utf-8")
        self.assertIn("verify_inventory_bound_gpu_host_launch_manifest", source)
        self.assertNotIn(
            "from .qwen_image_gpu_host_launch_manifest import verify_gpu_host_launch_manifest",
            source,
        )
        self.assertIn('"snapshot_byte_inventory_verified": True', source)
        self.assertIn("QWEN_LAUNCH_OUTPUT_SNAPSHOT_INVENTORY_RECEIPT_DRIFT", source)

    def test_production_cli_materializes_and_replays_postflight_attestation(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / "tools/phase18_run_one_shot_canonical_inference.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("build_launch_to_output_attestation", source)
        self.assertIn("verify_launch_to_output_attestation", source)
        self.assertIn('"launch_to_output_attestation.json"', source)


if __name__ == "__main__":
    unittest.main()