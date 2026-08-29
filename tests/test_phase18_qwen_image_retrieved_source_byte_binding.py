from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_retrieved_source_byte_binding import (
    RETRIEVED_SOURCE_DRAFT_SCHEMA,
    bind_retrieved_source_bytes,
)
from engine.intelligence.qwen_image_source_backed_story_evidence_pack import (
    SOURCE_BACKED_STORY_MANIFEST_SCHEMA,
)


class RetrievedSourceByteBindingTests(unittest.TestCase):
    def _draft(self, content_path: str = "source.bin") -> dict:
        return {
            "schema": RETRIEVED_SOURCE_DRAFT_SCHEMA,
            "source_documents": [{
                "source_id": "official_report",
                "source_url": "https://example.org/report",
                "publisher": "Example Sports Desk",
                "published_at_utc": "2026-08-29T03:00:00Z",
                "retrieved_at_utc": "2026-08-29T04:00:00Z",
                "content_path": content_path,
            }],
            "story_source_ids": ["official_report"],
            "fact_lock": {},
            "entity_identity_verification": {},
            "sentiment_neutrality": {},
            "story_semantic_preflight": {},
            "zero_cost_policy": {},
            "semantic_layer_ownership": {},
        }

    def _write_draft(self, root: Path, payload: dict) -> Path:
        path = root / "draft.json"
        path.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
        return path

    def test_exact_source_bytes_are_hashed_into_bound_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources"
            sources.mkdir()
            raw = b"captured source bytes\x00preserved exactly"
            (sources / "source.bin").write_bytes(raw)
            draft = self._write_draft(root, self._draft())
            result = bind_retrieved_source_bytes(draft, sources, root / "bound")

            expected = hashlib.sha256(raw).hexdigest()
            manifest = json.loads(result.bound_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema"], SOURCE_BACKED_STORY_MANIFEST_SCHEMA)
            self.assertEqual(manifest["source_documents"][0]["content_sha256"], expected)
            self.assertEqual(result.source_digests["official_report"], expected)

            receipt = json.loads(result.binding_receipt_path.read_text(encoding="utf-8"))
            self.assertTrue(receipt["source_bytes_verified"])
            self.assertEqual(receipt["source_bindings"][0]["content_byte_size"], len(raw))
            self.assertEqual(receipt["source_bindings"][0]["content_sha256"], expected)
            self.assertFalse(receipt["production_semantic_replay_executed"])
            self.assertFalse(receipt["fresh_story_gates_passed"])
            self.assertFalse(receipt["canonical_generation_authorized"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])

    def test_content_change_changes_bound_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources"
            sources.mkdir()
            source = sources / "source.bin"
            source.write_bytes(b"version one")
            first_draft = self._write_draft(root, self._draft())
            first = bind_retrieved_source_bytes(first_draft, sources, root / "bound1")
            first_digest = first.source_digests["official_report"]
            source.write_bytes(b"version two")
            second = bind_retrieved_source_bytes(first_draft, sources, root / "bound2")
            self.assertNotEqual(first_digest, second.source_digests["official_report"])

    def test_capture_path_cannot_escape_source_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources"
            sources.mkdir()
            (root / "outside.bin").write_bytes(b"outside")
            draft = self._write_draft(root, self._draft("../outside.bin"))
            with self.assertRaisesRegex(ValueError, "CONTENT_PATH_ESCAPE"):
                bind_retrieved_source_bytes(draft, sources, root / "bound")

    def test_empty_capture_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources"
            sources.mkdir()
            (sources / "source.bin").write_bytes(b"")
            draft = self._write_draft(root, self._draft())
            with self.assertRaisesRegex(ValueError, "CONTENT_FILE_EMPTY"):
                bind_retrieved_source_bytes(draft, sources, root / "bound")

    def test_duplicate_capture_path_is_rejected(self) -> None:
        draft = self._draft()
        duplicate = dict(draft["source_documents"][0])
        duplicate["source_id"] = "second_source"
        draft["source_documents"].append(duplicate)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = root / "sources"
            sources.mkdir()
            (sources / "source.bin").write_bytes(b"same captured bytes")
            path = self._write_draft(root, draft)
            with self.assertRaisesRegex(ValueError, "CONTENT_PATH_DUPLICATE"):
                bind_retrieved_source_bytes(path, sources, root / "bound")


if __name__ == "__main__":
    unittest.main()
