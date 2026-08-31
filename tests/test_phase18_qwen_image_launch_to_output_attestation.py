from __future__ import annotations

import pytest

from engine.intelligence.qwen_image_launch_to_output_attestation import _assert_join


def _records():
    launch = {
        "story_snapshot_sha256": "a" * 64,
        "model_id": "Qwen/Qwen-Image-2512",
        "model_revision": "2ce1c28560fbc62c9f5531e076b237d3575330a9",
        "cost_mode": "$0-local",
        "network_allowed": False,
        "local_files_only": True,
        "snapshot": {"resolved_path": "/tmp/snapshots/2ce1", "revision": "2ce1c28560fbc62c9f5531e076b237d3575330a9", "revision_verified": True},
        "inference_settings": {"width": 1024, "height": 1024, "seed": 7, "num_inference_steps": 8, "guidance_scale": 1.0},
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
        "width": 1024, "height": 1024, "seed": 7,
        "num_inference_steps": 8, "guidance_scale": 1.0,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    return launch, provenance, canonical


def test_launch_output_join_accepts_exact_attested_execution():
    launch, provenance, canonical = _records()
    _assert_join(launch, provenance, canonical)


def test_launch_output_join_rejects_seed_drift():
    launch, provenance, canonical = _records()
    canonical["seed"] = 8
    with pytest.raises(ValueError, match="SETTINGS_DRIFT:seed"):
        _assert_join(launch, provenance, canonical)


def test_launch_output_join_rejects_story_drift():
    launch, provenance, canonical = _records()
    canonical["story_snapshot_sha256"] = "b" * 64
    with pytest.raises(ValueError, match="JOIN_DRIFT:story_snapshot_sha256"):
        _assert_join(launch, provenance, canonical)


def test_launch_output_join_rejects_network_enabled_provenance():
    launch, provenance, canonical = _records()
    provenance["network_allowed"] = True
    with pytest.raises(ValueError, match="NETWORK_DRIFT"):
        _assert_join(launch, provenance, canonical)


def test_launch_output_join_rejects_snapshot_path_drift():
    launch, provenance, canonical = _records()
    provenance["snapshot"]["resolved_path"] = "/tmp/other"
    with pytest.raises(ValueError, match="SNAPSHOT_DRIFT:resolved_path"):
        _assert_join(launch, provenance, canonical)


def test_launch_output_join_rejects_premature_golden_authority():
    launch, provenance, canonical = _records()
    provenance["genuine_golden_png_created"] = True
    with pytest.raises(ValueError, match="PREMATURE_AUTHORITY:genuine_golden_png_created"):
        _assert_join(launch, provenance, canonical)
