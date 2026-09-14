from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.phase18_bind_png_structure_to_review_bundle import bind, verify


SOURCE_SHA = "a" * 40
PNG_SHA = "b" * 64


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _bundle(root: Path) -> Path:
    bundle = root / "bundle"
    bundle.mkdir()
    candidate = bundle / "candidate-1.png"
    candidate.write_bytes(b"not-used-by-this-binding-test")
    manifest = {
        "schema": "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "cost_mode": "$0-local",
        "offline_only": True,
        "source_commit_sha": SOURCE_SHA,
        "png_sha256": PNG_SHA,
        "exact_evidence_only": True,
        "eligible_for_human_visual_review": True,
        "entries": {
            "candidate_png": {
                "path": "candidate-1.png",
                "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
                "bytes": candidate.stat().st_size,
            }
        },
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
    _write_json(bundle / "review-bundle-manifest.json", manifest)
    return bundle


def _structure(root: Path, **overrides) -> Path:
    payload = {
        "schema": "pul7sar-phase18-first-genuine-golden-png-structure-v2",
        "status": "FIRST_GENUINE_GOLDEN_PNG_STRUCTURE_VERIFIED",
        "branch": "phase18/story-intelligence",
        "candidate": 1,
        "cost_mode": "$0-local",
        "offline_only": True,
        "source_commit_sha": SOURCE_SHA,
        "png_sha256": PNG_SHA,
        "png_bytes": 123,
        "png_structure_verified": True,
        "crc_verified_for_all_chunks": True,
        "idat_zlib_stream_verified": True,
        "zlib_stream_terminated_exactly": True,
        "decoded_scanline_layout_verified": True,
        "scanline_filter_bytes_verified": True,
        "iend_terminal": True,
        "no_trailing_bytes": True,
        "interlace_method": 0,
        "eligible_for_human_visual_review": True,
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
    payload.update(overrides)
    path = root / "structure.json"
    _write_json(path, payload)
    return path


class PngStructureReviewBindingTests(unittest.TestCase):
    def test_binds_and_replays_exact_structure_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _bundle(root)
            result = bind(bundle_dir=bundle, structure_path=_structure(root))
            self.assertTrue(result["png_structure_verified"])
            manifest = json.loads((bundle / "review-bundle-manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["png_structure_verified"])
            self.assertIn("evidence_png_structure", manifest["entries"])
            self.assertEqual(manifest["entries"]["evidence_png_structure"]["path"], "evidence/png_structure.json")
            replay = verify(bundle_dir=bundle)
            self.assertEqual(replay["png_sha256"], PNG_SHA)
            self.assertFalse(replay["publication_ready"])

    def test_rejects_png_identity_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, "UPSTREAM_IDENTITY_DRIFT"):
                bind(bundle_dir=_bundle(root), structure_path=_structure(root, png_sha256="c" * 64))

    def test_rejects_incomplete_structure_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, "STRUCTURE_FLAG_DRIFT:crc_verified_for_all_chunks"):
                bind(bundle_dir=_bundle(root), structure_path=_structure(root, crc_verified_for_all_chunks=False))

    def test_rejects_authority_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:structure:publication_ready"):
                bind(bundle_dir=_bundle(root), structure_path=_structure(root, publication_ready=True))

    def test_rejects_evidence_byte_drift_after_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = _bundle(root)
            bind(bundle_dir=bundle, structure_path=_structure(root))
            bound = bundle / "evidence/png_structure.json"
            bound.write_text(bound.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "EVIDENCE_DRIFT"):
                verify(bundle_dir=bundle)


if __name__ == "__main__":
    unittest.main()
