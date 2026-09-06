from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.intelligence.approved_model_revisions import QWEN_IMAGE_2512_REVISION
from engine.intelligence.qwen_image_snapshot_inventory import (
    assert_snapshot_inventory_unchanged,
    build_qwen_image_snapshot_inventory,
)


def _snapshot(tmp_path: Path) -> Path:
    model_root = tmp_path / "models--Qwen--Qwen-Image-2512"
    snapshot = model_root / "snapshots" / QWEN_IMAGE_2512_REVISION
    snapshot.mkdir(parents=True)
    (snapshot / "model_index.json").write_text(
        json.dumps(
            {
                "_class_name": "QwenImagePipeline",
                "scheduler": ["diffusers", "FlowMatchEulerDiscreteScheduler"],
                "transformer": ["diffusers", "QwenImageTransformer2DModel"],
                "vae": ["diffusers", "AutoencoderKLQwenImage"],
            }
        ),
        encoding="utf-8",
    )
    for name in ("scheduler", "transformer", "vae"):
        component = snapshot / name
        component.mkdir()
        (component / "config.json").write_text(f'{{"component":"{name}"}}', encoding="utf-8")
    return snapshot


def test_inventory_is_deterministic_and_byte_bound(tmp_path: Path):
    snapshot = _snapshot(tmp_path)
    first = build_qwen_image_snapshot_inventory(snapshot)
    second = build_qwen_image_snapshot_inventory(snapshot)

    assert first == second
    assert first.snapshot_file_count == 4
    assert first.snapshot_total_bytes > 0
    assert len(first.snapshot_inventory_sha256) == 64
    assert_snapshot_inventory_unchanged(first, second)

    (snapshot / "transformer" / "config.json").write_text('{"component":"changed"}', encoding="utf-8")
    changed = build_qwen_image_snapshot_inventory(snapshot)
    assert changed.snapshot_inventory_sha256 != first.snapshot_inventory_sha256
    with pytest.raises(RuntimeError, match="SNAPSHOT_BYTE_INVENTORY_DRIFT"):
        assert_snapshot_inventory_unchanged(first, changed)


def test_huggingface_blob_symlink_inside_same_model_root_is_allowed(tmp_path: Path):
    snapshot = _snapshot(tmp_path)
    model_root = snapshot.parent.parent
    blob = model_root / "blobs" / "abc123"
    blob.parent.mkdir()
    blob.write_bytes(b"local-weight-bytes")
    target = snapshot / "transformer" / "weights.safetensors"
    target.symlink_to(blob)

    inventory = build_qwen_image_snapshot_inventory(snapshot)

    assert inventory.snapshot_file_count == 5
    assert inventory.snapshot_total_bytes >= len(b"local-weight-bytes")


def test_symlink_target_outside_same_model_root_fails_closed(tmp_path: Path):
    snapshot = _snapshot(tmp_path)
    external = tmp_path / "external.bin"
    external.write_bytes(b"not-part-of-approved-model-cache")
    target = snapshot / "transformer" / "weights.safetensors"
    target.symlink_to(external)

    with pytest.raises(ValueError, match="FILE_TARGET_OUTSIDE_MODEL_ROOT"):
        build_qwen_image_snapshot_inventory(snapshot)


def test_missing_declared_component_file_fails_closed(tmp_path: Path):
    snapshot = _snapshot(tmp_path)
    (snapshot / "vae" / "config.json").unlink()

    with pytest.raises(ValueError, match="COMPONENT_FILE_MISSING:vae"):
        build_qwen_image_snapshot_inventory(snapshot)


def test_wrong_pipeline_class_fails_closed(tmp_path: Path):
    snapshot = _snapshot(tmp_path)
    payload = json.loads((snapshot / "model_index.json").read_text(encoding="utf-8"))
    payload["_class_name"] = "OtherPipeline"
    (snapshot / "model_index.json").write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="PIPELINE_CLASS_INVALID"):
        build_qwen_image_snapshot_inventory(snapshot)
