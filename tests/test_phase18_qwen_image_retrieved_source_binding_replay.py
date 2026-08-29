from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_retrieved_source_binding_replay import (
    compile_replayed_source_binding_to_evidence_pack,
    replay_retrieved_source_binding,
)
from engine.intelligence.qwen_image_retrieved_source_byte_binding import (
    RETRIEVED_SOURCE_DRAFT_SCHEMA,
    bind_retrieved_source_bytes,
)


class RetrievedSourceBindingReplayTests(unittest.TestCase):
    def _draft(self) -> dict:
        return {
            "schema": RETRIEVED_SOURCE_DRAFT_SCHEMA,
            "source_documents": [{
                "source_id": "official_report",
                "source_url": "https://example.org/report",
                "publisher": "Example Sports Desk",
                "published_at_utc": "2026-08-29T03:00:00Z",
                "retrieved_at_utc": "2026-08-29T04:00:00Z",
                "content_path": "source.bin",
            }],
            "story_source_ids": ["official_report"],
            "fact_lock": {
                "claims": [{"text": "Team A defeated Team B 2-1.", "kind": "fact", "confidence": 1.0, "source": "official_report"}],
                "required_facts": ["Team A defeated Team B 2-1."],
                "minimum_fact_confidence": 0.95,
            },
            "entity_identity_verification": {
                "canonical_entities": [
                    {
                        "entity_id": "team-a",
                        "canonical_name": "Team A",
                        "aliases": ["Team A"],
                        "identity_source_refs": ["official_report"],
                    },
                    {
                        "entity_id": "team-b",
                        "canonical_name": "Team B",
                        "aliases": ["Team B"],
                        "identity_source_refs": ["official_report"],
                    },
                ],
                "story_entity_references": [
                    {"reference": "Team A", "expected_entity_id": "team-a"},
                    {"reference": "Team B", "expected_entity_id": "team-b"},
                ],
                "exact_identity_assets": [],
            },
            "sentiment_neutrality": {
                "outcome_is_competitive_result": True,
                "opponent_or_loser_present": True,
                "editorial_text_fields": {"headline": "Team A edge Team B 2-1"},
                "emotional_attribution_sources": [],
            },
            "story_semantic_preflight": {
                "story": {
                    "story_id": "story-1",
                    "topic": "football",
                    "headline": "Team A edge Team B 2-1",
                    "summary": "Team A defeated Team B 2-1.",
                    "confidence": 0.99,
                    "story_type": "match_result",
                    "entities": ["Team A", "Team B"],
                    "score": "2-1",
                },
                "declared_visual_family": "result_statement",
                "declared_production_mode": "hybrid_composite",
                "declared_scene_concept": "winner-led result composition",
                "declared_generated_elements": ["atmosphere", "depth", "non_factual_texture"],
                "declared_forbidden_generated_elements": ["text", "numbers", "score", "logos", "identity", "brand", "sport_geometry"],
            },
            "zero_cost_policy": {
                "cost_mode": "$0-local",
                "billing_class": "local_free",
                "payment_method_required": False,
                "external_paid_api_used": False,
                "canonical_execution_local_only": True,
                "provider_economics": {"provider": "local_qwen", "cost_type": "LOCAL_FREE", "estimated_cost_usd": 0.0},
            },
            "semantic_layer_ownership": {
                "layers": [
                    {"layer_id": "background", "owner": "diffusion", "content_kind": "atmosphere", "contains_text": False, "contains_exact_number": False, "contains_brand": False, "contains_entity_mark": False, "contains_identity": False, "contains_deterministic_sport_geometry": False},
                    {"layer_id": "score", "owner": "deterministic", "content_kind": "exact_number", "contains_text": True, "contains_exact_number": True, "contains_brand": False, "contains_entity_mark": False, "contains_identity": False, "contains_deterministic_sport_geometry": False},
                ]
            },
        }

    def _prepare(self, root: Path):
        sources = root / "sources"
        sources.mkdir()
        (sources / "source.bin").write_bytes(b"official captured report bytes")
        draft_path = root / "draft.json"
        draft_path.write_text(json.dumps(self._draft(), separators=(",", ":")) + "\n", encoding="utf-8")
        bound = bind_retrieved_source_bytes(draft_path, sources, root / "bound")
        return sources, bound

    def test_current_bytes_replay_against_receipt_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources, bound = self._prepare(root)
            result = replay_retrieved_source_binding(bound.binding_receipt_path, bound.bound_manifest_path, sources)
            self.assertEqual(result.source_digests, bound.source_digests)

    def test_source_mutation_after_binding_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources, bound = self._prepare(root)
            (sources / "source.bin").write_bytes(b"mutated after original binding")
            with self.assertRaisesRegex(ValueError, "CONTENT_SHA_DRIFT"):
                replay_retrieved_source_binding(bound.binding_receipt_path, bound.bound_manifest_path, sources)

    def test_bound_manifest_mutation_after_binding_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources, bound = self._prepare(root)
            manifest = json.loads(bound.bound_manifest_path.read_text(encoding="utf-8"))
            manifest["story_source_ids"] = []
            bound.bound_manifest_path.write_text(json.dumps(manifest, separators=(",", ":")) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "MANIFEST_SHA_DRIFT"):
                replay_retrieved_source_binding(bound.binding_receipt_path, bound.bound_manifest_path, sources)

    def test_authority_in_binding_receipt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources, bound = self._prepare(root)
            receipt = json.loads(bound.binding_receipt_path.read_text(encoding="utf-8"))
            receipt["canonical_generation_authorized"] = True
            bound.binding_receipt_path.write_text(json.dumps(receipt, separators=(",", ":")) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
                replay_retrieved_source_binding(bound.binding_receipt_path, bound.bound_manifest_path, sources)

    def test_replay_is_required_before_evidence_compilation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources, bound = self._prepare(root)
            pack = compile_replayed_source_binding_to_evidence_pack(
                bound.binding_receipt_path,
                bound.bound_manifest_path,
                sources,
                root / "evidence",
            )
            receipt = json.loads(pack.pack_receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(len(receipt["evidence"]), 6)
            self.assertFalse(receipt["production_semantic_replay_executed"])
            self.assertFalse(receipt["fresh_story_gates_passed"])
            self.assertFalse(receipt["canonical_generation_authorized"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])


if __name__ == "__main__":
    unittest.main()
