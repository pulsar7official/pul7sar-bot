from __future__ import annotations

import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from tools.phase18_verify_first_genuine_golden_png_structure import verify


ROOT = Path(__file__).resolve().parents[1]


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def _png(
    *,
    trailing: bytes = b"",
    corrupt_crc: bool = False,
    decoded: bytes = b"\x00\x00\x00\x00",
    interlace: int = 0,
) -> bytes:
    # 1x1 RGB8: one filter byte followed by exactly three pixel bytes.
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, interlace)
    idat = zlib.compress(decoded)
    data = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")
    if corrupt_crc:
        # Corrupt an actual CRC byte while preserving the IEND chunk type.
        data = data[:-1] + bytes([data[-1] ^ 1])
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


class FirstGoldenPngStructureTests(unittest.TestCase):
    def _with_root(self):
        return tempfile.TemporaryDirectory()

    def test_valid_png_structure_is_verified(self) -> None:
        with self._with_root() as tmp:
            root = Path(tmp)
            png = root / "candidate.png"
            png.write_bytes(_png())
            result = verify(manifest_path=_manifest(root, png), repo_root=root)
            self.assertTrue(result["png_structure_verified"])
            self.assertEqual((result["width"], result["height"]), (1, 1))
            self.assertTrue(result["crc_verified_for_all_chunks"])
            self.assertTrue(result["idat_zlib_stream_verified"])
            self.assertTrue(result["zlib_stream_terminated_exactly"])
            self.assertTrue(result["decoded_scanline_layout_verified"])
            self.assertTrue(result["scanline_filter_bytes_verified"])
            self.assertEqual(result["expected_decoded_scanline_bytes"], 4)
            self.assertEqual(result["scanline_filter_types_seen"], [0])
            self.assertTrue(result["no_trailing_bytes"])
            self.assertFalse(result["human_visual_review_approved"])
            self.assertFalse(result["publication_ready"])

    def test_trailing_bytes_are_rejected(self) -> None:
        with self._with_root() as tmp:
            root = Path(tmp)
            png = root / "candidate.png"
            png.write_bytes(_png(trailing=b"unexpected"))
            with self.assertRaisesRegex(RuntimeError, "TRAILING_BYTES"):
                verify(manifest_path=_manifest(root, png), repo_root=root)

    def test_crc_drift_is_rejected(self) -> None:
        with self._with_root() as tmp:
            root = Path(tmp)
            png = root / "candidate.png"
            png.write_bytes(_png(corrupt_crc=True))
            with self.assertRaisesRegex(RuntimeError, "CRC_INVALID"):
                verify(manifest_path=_manifest(root, png), repo_root=root)

    def test_short_decoded_scanline_is_rejected(self) -> None:
        with self._with_root() as tmp:
            root = Path(tmp)
            png = root / "candidate.png"
            png.write_bytes(_png(decoded=b"\x00\x00\x00"))
            with self.assertRaisesRegex(RuntimeError, "SCANLINE_SIZE_INVALID"):
                verify(manifest_path=_manifest(root, png), repo_root=root)

    def test_invalid_scanline_filter_byte_is_rejected(self) -> None:
        with self._with_root() as tmp:
            root = Path(tmp)
            png = root / "candidate.png"
            png.write_bytes(_png(decoded=b"\x05\x00\x00\x00"))
            with self.assertRaisesRegex(RuntimeError, "FILTER_BYTE_INVALID"):
                verify(manifest_path=_manifest(root, png), repo_root=root)

    def test_interlaced_candidate_is_fail_closed_until_adam7_is_fully_verified(self) -> None:
        with self._with_root() as tmp:
            root = Path(tmp)
            png = root / "candidate.png"
            png.write_bytes(_png(interlace=1))
            with self.assertRaisesRegex(RuntimeError, "INTERLACE_UNSUPPORTED_FOR_GOLDEN"):
                verify(manifest_path=_manifest(root, png), repo_root=root)

    def test_manifest_authority_drift_is_rejected(self) -> None:
        with self._with_root() as tmp:
            root = Path(tmp)
            png = root / "candidate.png"
            png.write_bytes(_png())
            path = _manifest(root, png)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:publication_ready"):
                verify(manifest_path=path, repo_root=root)

    def test_workflow_runs_png_structure_gate_before_snapshot_replay_and_packaging(self) -> None:
        workflow = (ROOT / ".github/workflows/phase18-first-genuine-golden-v6-fresh.yml").read_text(encoding="utf-8")
        tool = "tools/phase18_verify_first_genuine_golden_png_structure.py"
        self.assertIn(f"test -f {tool}", workflow)
        gate = workflow.index("Prove complete Candidate 1 PNG structure before review packaging")
        snapshot = workflow.index("Replay and bind approved model snapshots and runtime after generation")
        package = workflow.index("Package exact Golden v6 Candidate 1 review bundle")
        upload = workflow.index("Upload exact Golden v6 Candidate 1 review bundle")
        self.assertLess(gate, snapshot)
        self.assertLess(snapshot, package)
        self.assertLess(package, upload)
        self.assertIn("first-genuine-golden-v6-png-structure.json", workflow)


if __name__ == "__main__":
    unittest.main()
