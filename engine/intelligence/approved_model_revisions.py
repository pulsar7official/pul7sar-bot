"""Immutable upstream model revisions approved for Phase 18 local execution.

Repository names alone are mutable. Golden evidence must identify the exact
upstream model bytes intended for execution, so the local GPU path pins approved
Hugging Face repositories to full commit SHAs and rejects snapshot drift.
"""
from __future__ import annotations

from pathlib import Path


FLUX2_KLEIN_4B_MODEL_ID = "black-forest-labs/FLUX.2-klein-4B"
FLUX2_KLEIN_4B_REVISION = "e7b7dc27f91deacad38e78976d1f2b499d76a294"
QWEN_IMAGE_2512_MODEL_ID = "Qwen/Qwen-Image-2512"
QWEN_IMAGE_2512_REVISION = "2ce1c28560fbc62c9f5531e076b237d3575330a9"
QWEN25_VL_3B_MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
QWEN25_VL_3B_REVISION = "66285546d2b821cf421d4f5eb2576359d3770cd3"


def assert_full_commit_sha(value: str, *, label: str = "model revision") -> str:
    """Return a normalized full Git SHA or fail closed."""
    candidate = value.strip().lower() if isinstance(value, str) else ""
    if len(candidate) != 40 or any(ch not in "0123456789abcdef" for ch in candidate):
        raise ValueError(f"{label} must be a full 40-character hexadecimal commit SHA")
    return candidate


def snapshot_revision_from_path(snapshot_path: str | Path) -> str:
    """Extract the Hugging Face snapshot revision from a canonical cache path.

    Standard Hub snapshots resolve to ``.../snapshots/<commit-sha>``. Phase 18
    deliberately refuses paths that do not expose a full immutable revision,
    rather than guessing that a mutable ref such as ``main`` is equivalent.
    """
    path = Path(snapshot_path).expanduser().resolve()
    if path.parent.name != "snapshots":
        raise RuntimeError("model snapshot path is not a canonical Hugging Face snapshots/<revision> path")
    return assert_full_commit_sha(path.name, label="resolved snapshot revision")


def assert_snapshot_revision(snapshot_path: str | Path, expected_revision: str) -> str:
    """Prove that a cached snapshot is the exact approved upstream revision."""
    expected = assert_full_commit_sha(expected_revision, label="expected model revision")
    actual = snapshot_revision_from_path(snapshot_path)
    if actual != expected:
        raise RuntimeError(
            f"model snapshot revision drift: expected {expected}, resolved {actual}"
        )
    return actual
