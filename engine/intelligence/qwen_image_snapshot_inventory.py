"""Deterministic, local-only byte inventory for the approved Qwen Image snapshot.

CS352 closes a pre-model-load asset-drift gap. Structural readiness proves that
an approved local snapshot exists; this module additionally binds every local
snapshot file to a deterministic SHA-256 inventory so the inference edge can
fail closed if any model/config/tokenizer byte changes between preflight and
``from_pretrained``.

No network access, model loading, inference, pixel creation, or publication
authority exists in this module.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from .approved_model_revisions import QWEN_IMAGE_2512_REVISION, assert_snapshot_revision

SCHEMA = "pul7sar.phase18.qwen_image_snapshot_inventory.v1"
PIPELINE_CLASS = "QwenImagePipeline"


@dataclass(frozen=True)
class QwenImageSnapshotInventory:
    schema: str
    model_revision: str
    snapshot_inventory_sha256: str
    snapshot_file_count: int
    snapshot_total_bytes: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _model_root(snapshot: Path) -> Path:
    if snapshot.parent.name != "snapshots":
        raise ValueError("QWEN_SNAPSHOT_INVENTORY_CACHE_LAYOUT_INVALID")
    return snapshot.parent.parent.resolve()


def build_qwen_image_snapshot_inventory(snapshot_path: str | Path) -> QwenImageSnapshotInventory:
    """Return an exact byte inventory of one approved already-local snapshot.

    Hugging Face cache file symlinks are supported only when their resolved
    targets remain inside the same model cache root. Broken/external links,
    directory symlinks, empty inventories, revision drift, malformed
    ``model_index.json``, and non-Qwen pipeline declarations all fail closed.
    """
    snapshot = Path(snapshot_path).expanduser().resolve()
    assert_snapshot_revision(snapshot, QWEN_IMAGE_2512_REVISION)
    if not snapshot.is_dir():
        raise ValueError("QWEN_SNAPSHOT_INVENTORY_DIRECTORY_MISSING")
    model_root = _model_root(snapshot)

    model_index = snapshot / "model_index.json"
    if not model_index.is_file():
        raise ValueError("QWEN_SNAPSHOT_INVENTORY_MODEL_INDEX_MISSING")
    try:
        payload = json.loads(model_index.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_SNAPSHOT_INVENTORY_MODEL_INDEX_INVALID") from exc
    if not isinstance(payload, dict) or payload.get("_class_name") != PIPELINE_CLASS:
        raise ValueError("QWEN_SNAPSHOT_INVENTORY_PIPELINE_CLASS_INVALID")

    records: list[dict[str, Any]] = []
    declared_components = {
        key
        for key, value in payload.items()
        if isinstance(key, str)
        and not key.startswith("_")
        and isinstance(value, (list, tuple))
        and len(value) == 2
    }
    if not declared_components:
        raise ValueError("QWEN_SNAPSHOT_INVENTORY_COMPONENTS_UNDECLARED")

    component_files = {name: 0 for name in declared_components}
    for item in sorted(snapshot.rglob("*"), key=lambda value: value.relative_to(snapshot).as_posix()):
        if item.is_symlink() and item.is_dir():
            raise ValueError("QWEN_SNAPSHOT_INVENTORY_DIRECTORY_SYMLINK_FORBIDDEN")
        if not item.is_file():
            continue
        try:
            resolved = item.resolve(strict=True)
            resolved.relative_to(model_root)
        except (OSError, ValueError) as exc:
            raise ValueError("QWEN_SNAPSHOT_INVENTORY_FILE_TARGET_OUTSIDE_MODEL_ROOT") from exc
        relative = item.relative_to(snapshot).as_posix()
        sha256, byte_size = _sha256_file(resolved)
        records.append({"path": relative, "sha256": sha256, "byte_size": byte_size})
        top = relative.split("/", 1)[0]
        if top in component_files:
            component_files[top] += 1

    if not records:
        raise ValueError("QWEN_SNAPSHOT_INVENTORY_EMPTY")
    missing = sorted(name for name, count in component_files.items() if count < 1)
    if missing:
        raise ValueError("QWEN_SNAPSHOT_INVENTORY_COMPONENT_FILE_MISSING:" + ",".join(missing))

    canonical = json.dumps(records, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return QwenImageSnapshotInventory(
        schema=SCHEMA,
        model_revision=QWEN_IMAGE_2512_REVISION,
        snapshot_inventory_sha256=hashlib.sha256(canonical).hexdigest(),
        snapshot_file_count=len(records),
        snapshot_total_bytes=sum(record["byte_size"] for record in records),
    )


def assert_snapshot_inventory_unchanged(
    before: QwenImageSnapshotInventory,
    after: QwenImageSnapshotInventory,
) -> None:
    if before != after:
        raise RuntimeError("QWEN_LOCAL_INFERENCE_SNAPSHOT_BYTE_INVENTORY_DRIFT")
