"""Tamper-evident evidence manifest for the first real Phase 18 Golden PNG.

The manifest is intentionally post-generation and publication-neutral. It proves
which files were produced by the locked GPU smoke path without turning a
successful generation into publication approval. A separate verifier can later
replay every digest from an uploaded/downloaded artifact and fail closed on any
byte, size, path, or manifest mutation.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable, Mapping

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EVIDENCE_SCHEMA = "pul7sar-golden-gpu-evidence-v1"
_HEX = frozenset("0123456789abcdef")


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


def _canonical_manifest_bytes(manifest: Mapping[str, object]) -> bytes:
    payload = dict(manifest)
    payload.pop("manifest_sha256", None)
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(char in _HEX for char in value.casefold())
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

    job_id = payload.get("job_id") or payload.get("job", {}).get("job_id")
    request_id = payload.get("request_id") or payload.get("job", {}).get("request_id")
    payload_sha256 = payload.get("payload_sha256") or payload.get("job", {}).get("payload_sha256")
    if not isinstance(job_id, str) or not job_id.strip():
        raise ValueError("first-PNG result must contain a non-empty job_id")
    if not isinstance(request_id, str) or not request_id.strip():
        raise ValueError("first-PNG result must contain a non-empty request_id")
    if not _is_sha256(payload_sha256):
        raise ValueError("first-PNG result must contain a canonical 64-hex payload_sha256")

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
    manifest: dict[str, object] = {
        "schema": EVIDENCE_SCHEMA,
        "status": payload.get("status"),
        "job_id": job_id,
        "request_id": request_id,
        "payload_sha256": payload_sha256,
        "png": str(png_resolved.relative_to(root)),
        "publication_ready": False,
        "publication_note": "Evidence integrity does not imply semantic or Golden Visual approval.",
        "files": [file.__dict__ for file in files],
    }
    manifest["manifest_sha256"] = sha256(_canonical_manifest_bytes(manifest)).hexdigest()
    return manifest


def verify_golden_evidence_manifest(
    *,
    repository_root: Path,
    manifest: Mapping[str, object],
) -> dict[str, object]:
    """Replay and verify a Golden evidence manifest against repository bytes.

    This function deliberately provides integrity verification only. A verified
    evidence bundle is still not semantically safe, visually approved, or ready
    for publication.
    """

    root = repository_root.resolve()
    if manifest.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("unsupported Golden GPU evidence schema")
    if manifest.get("publication_ready") is not False:
        raise ValueError("evidence manifest must keep publication_ready=false")
    if not isinstance(manifest.get("job_id"), str) or not str(manifest.get("job_id")).strip():
        raise ValueError("evidence manifest is missing job_id")
    if not isinstance(manifest.get("request_id"), str) or not str(manifest.get("request_id")).strip():
        raise ValueError("evidence manifest is missing request_id")
    if not _is_sha256(manifest.get("payload_sha256")):
        raise ValueError("evidence manifest payload_sha256 is invalid")

    recorded_manifest_sha = manifest.get("manifest_sha256")
    if not _is_sha256(recorded_manifest_sha):
        raise ValueError("evidence manifest manifest_sha256 is invalid")
    computed_manifest_sha = sha256(_canonical_manifest_bytes(manifest)).hexdigest()
    if str(recorded_manifest_sha).casefold() != computed_manifest_sha:
        raise ValueError("evidence manifest canonical SHA-256 mismatch")

    raw_files = manifest.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise ValueError("evidence manifest must contain at least one file")

    seen: set[str] = set()
    verified_files: list[dict[str, object]] = []
    for entry in raw_files:
        if not isinstance(entry, Mapping):
            raise ValueError("evidence file entry must be an object")
        relative_value = entry.get("path")
        if not isinstance(relative_value, str) or not relative_value.strip():
            raise ValueError("evidence file entry is missing path")
        if relative_value in seen:
            raise ValueError(f"duplicate evidence path: {relative_value}")
        seen.add(relative_value)

        expected_bytes = entry.get("bytes")
        if not isinstance(expected_bytes, int) or isinstance(expected_bytes, bool) or expected_bytes <= 0:
            raise ValueError(f"invalid evidence size for {relative_value}")
        expected_sha = entry.get("sha256")
        if not _is_sha256(expected_sha):
            raise ValueError(f"invalid evidence SHA-256 for {relative_value}")

        resolved = _inside(root, root / relative_value)
        if not resolved.is_file():
            raise FileNotFoundError(f"evidence file is missing: {resolved}")
        actual_bytes = resolved.stat().st_size
        if actual_bytes != expected_bytes:
            raise ValueError(f"evidence size mismatch for {relative_value}")
        actual_sha = _digest(resolved)
        if actual_sha != str(expected_sha).casefold():
            raise ValueError(f"evidence SHA-256 mismatch for {relative_value}")
        verified_files.append({"path": relative_value, "bytes": actual_bytes, "sha256": actual_sha})

    png_value = manifest.get("png")
    if not isinstance(png_value, str) or png_value not in seen:
        raise ValueError("manifest PNG must be present in the evidence file set")
    png_path = _inside(root, root / png_value)
    if png_path.read_bytes()[:8] != PNG_SIGNATURE:
        raise ValueError("verified PNG evidence no longer has a valid PNG signature")

    return {
        "schema": "pul7sar-golden-gpu-evidence-verification-v1",
        "status": "GOLDEN_GPU_EVIDENCE_VERIFIED",
        "manifest_sha256": computed_manifest_sha,
        "job_id": manifest.get("job_id"),
        "request_id": manifest.get("request_id"),
        "payload_sha256": manifest.get("payload_sha256"),
        "png": png_value,
        "files_verified": len(verified_files),
        "publication_ready": False,
        "publication_note": "Integrity verification does not imply semantic or Golden Visual approval.",
    }
