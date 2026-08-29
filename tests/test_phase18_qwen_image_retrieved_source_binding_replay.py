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
                "source_id": "source_match_report",
                "source_url": "https://example.org/match-report",
                "publisher": "Example Sports Desk",
                "published_at_utc": "2026-08-29T03:00:00Z",
                "retrieved_at_utc": "2026-08-29T04:00:00Z",
                "content_path": "source.bin",
            }],
            "story_source_ids": ["source_match_report"],
            "fact_lock": {
                "minimum_fact_confidence": 0.9,
                "claims": [{
                    "text": "Club A defeated Club B 2-1 in a competitive match.",
                    "kind": "fact",
                    "source": "source_match_report",
                    "confidence": 0.99,
                    "metadata": {},
                }],
                "required_facts": ["Club A defeated Club B 2-1 in a competitive match."],
            },
            "entity_identity_verification": {
                "canonical_entities": [
                    {
                        "entity_id": "club_a",
                        "kind": "club",
                        "display_name": "Club A",
                        "aliases": [],
                        "identity_source_refs": ["source_match_report"],
                    },
                    {
                        "entity_id": "club_b",
                        "kind": "club",
                        "display_name": "Club B",
                        "aliases": [],
                        "identity_source_refs": ["source_match_report"],
                    },
                ],
                "story_entity_references": [
                    {"field": "headline", "text": "Club A", "expected_entity_id": "club_a"},
                    {"field": "headline", "text": "Club B", "expected_entity_id": "club_b"},
                ],
                "exact_entity_assets": [],
            },
            "sentiment_neutrality": {
                "outcome_is_competitive_result": True,
                "opponent_or_loser_present": True,
                "editorial_text_fields": {
                    "headline": "Club A win 2-1",
                    "caption": "Club A defeated Club B 2-1 in a competitive match.",
                },
                "emotional_attribution_sources": [],
            },
            "story_semantic_preflight": {
                "qwen_generation_requested": True,
                "editorial_request": {
                    "event": "result",
                    "sport": "football",
                    "story_core": "Club A defeated Club B 2-1 in a competitive match.",
                    "editorial_angle": "A composed victory presented without degrading the opponent.",
                    "headline_short": "Club A win 2-1",
                    "primary_subject": "Club A",
                    "secondary_subjects": ["Club B"],
                    "stakes": "normal",
                    "sentiment": "neutral",
                    "exact_assets": ["club_a_crest", "club_b_crest"],
                    "geometry_requirements": [],
                    "confidence": 0.95,
                },
                "proposed_visual_plan": {
                    "visual_family": "score_monument",
                    "production_mode": "hybrid",
                    "scene_concept": "A composed victory presented without degrading the opponent.",
                    "generated_elements": ["atmosphere", "lighting", "depth", "environmental texture"],
                    "forbidden_generated_elements": [
                        "PUL7SAR logo", "brand wordmark", "headline text", "scores",
                        "statistics", "club crests", "competition logos",
                    ],
                },
            },
            "zero_cost_policy": {
                "cost_mode": "$0-local",
                "provider_id": "local_qwen_image_2512",
                "billing_class": "local_free",
                "requires_payment_method": False,
                "external_paid_api_used": False,
                "canonical_execution_local_only": True,
            },
            "semantic_layer_ownership": {
                "identity_sensitive_subject_present": False,
                "exact_sport_geometry_required": False,
                "layer_plan": [
                    {"name": "atmosphere_base", "source": "generative", "required": True},
                    {"name": "sport_surface_geometry", "source": "optional", "required": False},
                    {"name": "exact_entity_marks", "source": "verified_asset", "required": False},
                    {"name": "data_and_score", "source": "deterministic", "required": False},
                    {"name": "editorial_typography", "source": "deterministic", "required": True},
                    {"name": "pul7sar_brand", "source": "verified_asset", "required": True},
                ],
                "leakage_evidence": {
                    "generated_text_detected": False,
                    "generated_platform_brand_detected": False,
                    "generated_exact_numbers_detected": False,
                    "generated_entity_mark_detected": False,
                    "generated_unverified_identity_detected": False,
                    "generated_sport_geometry_detected": False,
                    "notes": [],
                },
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
