from __future__ import annotations

import hashlib
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from tools.phase18_verify_first_genuine_golden_png_chunk_semantics import verify


def chunk(name: bytes, data: bytes = b"") -> bytes:
    crc = zlib.crc32(data, zlib.crc32(name)) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)


def png(extra_between_idat: bytes = b"", *, extra_before_idat: bytes = b"") -> bytes:
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    raw = b"\x00\x00\x00\x00"
    compressed = zlib.compress(raw)
    split = max(1, len(compressed) // 2)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + extra_before_idat +
            chunk(b"IDAT", compressed[:split]) + extra_between_idat +
            chunk(b"IDAT", compressed[split:]) + chunk(b"IEND"))


def evidence(path: Path, data: bytes) -> dict[str, object]:
    return {
        "schema": "pul7sar-phase18-first-genuine-golden-png-structure-v3",
        "branch": "phase18/story-intelligence", "candidate": 1,
        "cost_mode": "$0-local", "offline_only": True,
        "source_commit_sha": "a" * 40, "png_path": str(path),
        "png_sha256": hashlib.sha256(data).hexdigest(), "png_bytes": len(data),
        "png_structure_verified": True, "canonical_encoding_verified": True,
        "eligible_for_human_visual_review": True,
        "authoritative_gate": False, "network_download_authorized": False,
        "generation_authorized": False, "human_visual_review_approved": False,
        "golden_quality_approved": False, "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


class GoldenPngChunkSemanticsTests(unittest.TestCase):
    def run_case(self, data: bytes, expected_error: str | None = None) -> dict[str, object] | None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "candidate.png"
            target.write_bytes(data)
            proof = root / "structure.json"
            proof.write_text(json.dumps(evidence(target, data)), encoding="utf-8")
            if expected_error:
                with self.assertRaisesRegex(RuntimeError, expected_error):
                    verify(structure_path=proof, repo_root=root)
                return None
            return verify(structure_path=proof, repo_root=root)

    def test_accepts_consecutive_idat_and_ancillary_before_idat(self) -> None:
        result = self.run_case(png(extra_before_idat=chunk(b"tEXt", b"k\x00v")))
        self.assertIsNotNone(result)
        self.assertTrue(result["known_critical_chunks_only"])
        self.assertTrue(result["idat_consecutive"])
        self.assertFalse(result["publication_ready"])

    def test_rejects_unknown_critical_chunk(self) -> None:
        self.run_case(png(extra_before_idat=chunk(b"ABCD")), "UNKNOWN_CRITICAL")

    def test_rejects_reserved_bit_violation(self) -> None:
        self.run_case(png(extra_before_idat=chunk(b"teXt")), "RESERVED_BIT_INVALID")

    def test_rejects_non_consecutive_idat(self) -> None:
        self.run_case(png(extra_between_idat=chunk(b"tEXt", b"k\x00v")), "IDAT_NOT_CONSECUTIVE")

    def test_rejects_plte_after_idat(self) -> None:
        self.run_case(png(extra_between_idat=chunk(b"PLTE", b"\x00\x00\x00")), "PLTE_ORDER_INVALID")

    def test_rejects_authority_drift(self) -> None:
        data = png()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "candidate.png"
            target.write_bytes(data)
            payload = evidence(target, data)
            payload["publication_ready"] = True
            proof = root / "structure.json"
            proof.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT"):
                verify(structure_path=proof, repo_root=root)


if __name__ == "__main__":
    unittest.main()
