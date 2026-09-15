from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_production_gate_receipt_executor import (
    build_production_gate_receipt_set,
)
from engine.intelligence.qwen_image_source_backed_story_evidence_pack import (
    SOURCE_BACKED_STORY_MANIFEST_SCHEMA,
    compile_source_backed_story_evidence_pack,
)


class SourceBackedStoryEvidencePackTests(unittest.TestCase):
    def _manifest(self) -> dict:
        return {
            "schema": SOURCE_BACKED_STORY_MANIFEST_SCHEMA,
            "source_documents": [
                {
                    "source_id": "source_match_report",
                    "source_url": "https://example.org/match-report",
                    "publisher": "Example Sports Desk",
                    "published_at_utc": "2026-08-29T03:00:00Z",
                    "retrieved_at_utc": "2026-08-29T04:00:00Z",
                    "content_sha256": "a" * 64,
                }
            ],
            "story_source_ids": ["source_match_report"],
            "fact_lock": {
                "minimum_fact_confidence": 0.9,
                "claims": [
                    {
                        "text": "Club A defeated Club B 2-1 in a competitive match.",
                        "kind": "fact",
                        "source": "source_match_report",
                        "confidence": 0.99,
                        "metadata": {},
                    }
                ],
                "required_facts": [
                    "Club A defeated Club B 2-1 in a competitive match."
                ],
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
                    {
                        "field": "headline",
                        "text": "Club A",
                        "expected_entity_id": "club_a",
                    },
                    {
                        "field": "headline",
                        "text": "Club B",
                        "expected_entity_id": "club_b",
                    },
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
                    "generated_elements": [
                        "atmosphere",
                        "lighting",
                        "depth",
                        "environmental texture",
                    ],
                    "forbidden_generated_elements": [
                        "PUL7SAR logo",
                        "brand wordmark",
                        "headline text",
                        "scores",
                        "statistics",
                        "club crests",
                        "competition logos",
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

    def _write_manifest(self, root: Path, payload: dict | None = None) -> Path:
        path = root / "story_manifest.json"
        path.write_text(
            json.dumps(payload or self._manifest(), ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        return path

    def test_compiler_binds_one_story_snapshot_into_all_six_evidence_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._write_manifest(root)
            raw_manifest = manifest_path.read_bytes()
            output = root / "pack"
            pack = compile_source_backed_story_evidence_pack(manifest_path, output)

            expected_sha = hashlib.sha256(raw_manifest).hexdigest()
            self.assertEqual(pack.story_snapshot_sha256, expected_sha)
            self.assertEqual(pack.story_snapshot_byte_size, len(raw_manifest))
            self.assertEqual(tuple(pack.evidence_paths), REQUIRED_FRESH_GATE_EVIDENCE)

            for gate_id, path in pack.evidence_paths.items():
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["gate_id"], gate_id)
                self.assertEqual(payload["story_snapshot_sha256"], expected_sha)

            pack_receipt = json.loads(pack.pack_receipt_path.read_text(encoding="utf-8"))
            self.assertFalse(pack_receipt["production_semantic_replay_executed"])
            self.assertFalse(pack_receipt["fresh_story_gates_passed"])
            self.assertFalse(pack_receipt["canonical_generation_authorized"])
            self.assertFalse(pack_receipt["inference_executed"])
            self.assertFalse(pack_receipt["genuine_golden_png_created"])
            self.assertFalse(pack_receipt["publication_ready"])

    def test_compiled_fixture_can_feed_all_six_real_production_verifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._write_manifest(root)
            pack = compile_source_backed_story_evidence_pack(manifest_path, root / "pack")
            receipts = build_production_gate_receipt_set(
                pack.evidence_paths,
                pack.story_snapshot_sha256,
                evaluated_at_utc="2026-08-29T04:05:00Z",
            )
            self.assertEqual(tuple(item["gate_id"] for item in receipts), REQUIRED_FRESH_GATE_EVIDENCE)
            self.assertTrue(all(item["gate_passed"] is True for item in receipts))

    def test_unknown_fact_source_fails_before_evidence_is_written(self) -> None:
        manifest = self._manifest()
        manifest["fact_lock"]["claims"][0]["source"] = "unknown_source"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_manifest(root, manifest)
            with self.assertRaisesRegex(ValueError, "FACT_SOURCE_UNKNOWN"):
                compile_source_backed_story_evidence_pack(path, root / "pack")

    def test_identity_source_must_resolve_to_manifest_source_document(self) -> None:
        manifest = self._manifest()
        manifest["entity_identity_verification"]["canonical_entities"][0][
            "identity_source_refs"
        ] = ["unknown_source"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_manifest(root, manifest)
            with self.assertRaisesRegex(ValueError, "IDENTITY_SOURCE_UNKNOWN"):
                compile_source_backed_story_evidence_pack(path, root / "pack")

    def test_source_url_must_be_https(self) -> None:
        manifest = self._manifest()
        manifest["source_documents"][0]["source_url"] = "http://example.org/match-report"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_manifest(root, manifest)
            with self.assertRaisesRegex(ValueError, "SOURCE_URL_INVALID"):
                compile_source_backed_story_evidence_pack(path, root / "pack")

    def test_source_content_digest_is_mandatory(self) -> None:
        manifest = self._manifest()
        manifest["source_documents"][0]["content_sha256"] = "not-a-sha"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_manifest(root, manifest)
            with self.assertRaisesRegex(ValueError, "SOURCE_CONTENT_SHA_INVALID"):
                compile_source_backed_story_evidence_pack(path, root / "pack")

    def test_source_backed_emotional_attribution_requires_known_source(self) -> None:
        manifest = self._manifest()
        manifest["sentiment_neutrality"]["emotional_attribution_sources"] = [
            {"attribution": "furious", "source_id": "unknown_source"}
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._write_manifest(root, manifest)
            with self.assertRaisesRegex(ValueError, "EMOTIONAL_SOURCE_UNKNOWN"):
                compile_source_backed_story_evidence_pack(path, root / "pack")

    def test_compiler_refuses_nonempty_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._write_manifest(root)
            output = root / "pack"
            output.mkdir()
            (output / "old.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "OUTPUT_DIR_NOT_EMPTY"):
                compile_source_backed_story_evidence_pack(manifest_path, output)


if __name__ == "__main__":
    unittest.main()
