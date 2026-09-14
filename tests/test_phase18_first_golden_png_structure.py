from __future__ import annotations

import hashlib
import json
import struct
import zlib
from pathlib import Path

import pytest

from tools.phase18_verify_first_genuine_golden_png_structure import verify


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def _png(*, trailing: bytes = b"", corrupt_crc: bool = False) -> bytes:
    # 1x1 RGB, filter byte + black pixel.
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00\x00\x00")
    data = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")
    if corrupt_crc:
        data = data[:-5] + bytes([data[-5] ^ 1]) + data[-4:]
    return data + trailing


def _manifest(root: Path, png: Path) -> Path:
    digest = hashlib.sha256(png.read_bytes()).hexdigest()
    payload = {
        "schema": "pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v3",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "cost_mode": "$0-local",
        "offline_only": True,
        "source_commit_sha": "a" * 40,
        "png_sha256": digest,
        "eligible_for_human_visual_review": True,
        "evidence": {"png": {"path": str(png), "sha256": digest, "bytes": png.stat().st_size}},
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
    path = root / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_valid_png_structure_is_verified(tmp_path: Path) -> None:
    png = tmp_path / "candidate.png"
    png.write_bytes(_png())
    result = verify(manifest_path=_manifest(tmp_path, png), repo_root=tmp_path)
    assert result["png_structure_verified"] is True
    assert result["width"] == 1 and result["height"] == 1
    assert result["crc_verified_for_all_chunks"] is True
    assert result["idat_zlib_stream_verified"] is True
    assert result["no_trailing_bytes"] is True
    assert result["human_visual_review_approved"] is False
    assert result["publication_ready"] is False


def test_trailing_bytes_are_rejected(tmp_path: Path) -> None:
    png = tmp_path / "candidate.png"
    png.write_bytes(_png(trailing=b"unexpected"))
    with pytest.raises(RuntimeError, match="TRAILING_BYTES"):
        verify(manifest_path=_manifest(tmp_path, png), repo_root=tmp_path)


def test_crc_drift_is_rejected(tmp_path: Path) -> None:
    png = tmp_path / "candidate.png"
    png.write_bytes(_png(corrupt_crc=True))
    with pytest.raises(RuntimeError, match="CRC_INVALID"):
        verify(manifest_path=_manifest(tmp_path, png), repo_root=tmp_path)


def test_manifest_authority_drift_is_rejected(tmp_path: Path) -> None:
    png = tmp_path / "candidate.png"
    png.write_bytes(_png())
    path = _manifest(tmp_path, png)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["publication_ready"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(RuntimeError, match="AUTHORITY_DRIFT:publication_ready"):
        verify(manifest_path=path, repo_root=tmp_path)
