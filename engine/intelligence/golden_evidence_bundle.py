"""Tamper-evident evidence manifest for the first real Phase 18 Golden PNG.

The manifest is intentionally post-generation and publication-neutral. It proves
which files were produced by the locked GPU smoke path without turning a
successful generation into publication approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class EvidenceFile:
    path: str
    bytes: int
    sha256: str


def _inside(root: Path, path: Path) -> Path:
    root = root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"evidence path escapes repository root: {path}") from exc
    return resolved


def _digest(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _evidence_file(root: Path, path: Path) -> EvidenceFile:
    resolved = _inside(root, path)
    if not resolved.is_file():
        raise FileNotFoundError(f"evidence file is missing: {resolved}")
    return EvidenceFile(
        path=str(resolved.relative_to(root.resolve())),
        bytes=resolved.stat().st_size,
        sha256=_digest(resolved),
    )


def build_golden_evidence_manifest(
    *,
    repository_root: Path,
    result_path: Path,
    additional_paths: Iterable[Path] = (),
) -> dict[str, object]:
    """Build a deterministic evidence manifest from a genuine smoke result.

    Requirements remain fail-closed:
    - result JSON must stay inside the repository;
    - generation must explicitly leave publication gated;
    - referenced PNG must exist, be non-empty and have a real PNG signature;
    - all listed evidence files must exist inside the repository;
    - no visual score or publication approval is inferred here.
    """

    root = repository_root.resolve()
    result_resolved = _inside(root, result_path)
    if not result_resolved.is_file():
        raise FileNotFoundError(f"first-PNG result is missing: {result_resolved}")

    payload = json.loads(result_resolved.read_text(encoding="utf-8"))
    if payload.get("publication_ready") is not False:
        raise ValueError("first-PNG result must keep publication_ready=false")

    png_value = payload.get("png")
    if not isinstance(png_value, str) or not png_value.strip():
        raise ValueError("first-PNG result does not contain a PNG path")
    png_path = Path(png_value)
    if not png_path.is_absolute():
        png_path = root / png_path
    png_resolved = _inside(root, png_path)
    if not png_resolved.is_file() or png_resolved.stat().st_size <= 8:
        raise FileNotFoundError("first-PNG result does not point to a non-empty PNG")
    if png_resolved.read_bytes()[:8] != PNG_SIGNATURE:
        raise ValueError("first-PNG evidence does not have a valid PNG signature")

    requested_paths = [result_resolved, png_resolved]
    requested_paths.extend(Path(path) for path in additional_paths)

    seen: set[str] = set()
    files: list[EvidenceFile] = []
    for path in requested_paths:
        evidence = _evidence_file(root, path if path.is_absolute() else root / path)
        if evidence.path in seen:
            continue
        seen.add(evidence.path)
        files.append(evidence)

    files.sort(key=lambda item: item.path)
    manifest = {
        "schema": "pul7sar-golden-gpu-evidence-v1",
        "status": payload.get("status"),
        "job_id": payload.get("job_id") or payload.get("job", {}).get("job_id"),
        "request_id": payload.get("request_id") or payload.get("job", {}).get("request_id"),
        "payload_sha256": payload.get("payload_sha256") or payload.get("job", {}).get("payload_sha256"),
        "png": str(png_resolved.relative_to(root)),
        "publication_ready": False,
        "publication_note": "Evidence integrity does not imply semantic or Golden Visual approval.",
        "files": [file.__dict__ for file in files],
    }

    canonical = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest["manifest_sha256"] = sha256(canonical).hexdigest()
    return manifest
