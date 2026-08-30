from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    build_composed_candidate_golden_quality_adjudication,
    verify_composed_candidate_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_canonical_candidate_byte_admission import (
    CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
)
from engine.intelligence.qwen_image_composed_candidate_byte_admission import SCHEMA as CS272_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import SCHEMA as CS275_SCHEMA

MODULE = "engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication"
STORY = "1" * 64
CS262 = "2" * 64


def _png(path: str, sha: str) -> dict:
    return {
        "repository_relative_path": path,
        "sha256": sha,
        "byte_size": 123,
        "width": 1024,
        "height": 1024,
    }


def _sources(*, blocker: bool = False):
    candidate = _png("runs/canonical_candidate.png", "3" * 64)
    composed = _png("runs/composed_candidate.png", "4" * 64)
    false = {
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "golden_quality_approved": False,
    }
    cs263 = {
        "schema": CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
        "receipt_sha256": "5" * 64,
        "story_snapshot_sha256": STORY,
        "source_cs262_receipt": {"receipt_sha256": CS262},
        "candidate_png": candidate,
        "seed": 424242,
        "inference_executed": True,
        "genuine_canonical_inference_executed": True,
        "candidate_bytes_admitted_for_post_generation_qa": True,
        **false,
    }
    cs272 = {
        "schema": CS272_SCHEMA,
        "receipt_sha256": "6" * 64,
        "story_snapshot_sha256": STORY,
        "source_candidate_png": dict(candidate),
        "composed_candidate_png": composed,
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        **false,
    }
    blockers = {
        "fantasy_or_monumental_staging": blocker,
        "fake_logo_or_crest": False,
        "pseudo_text_or_gibberish": False,
        "generated_platform_brand_or_wordmark": False,
        "invented_result_or_winner": False,
        "cluttered_collage": False,
        "broken_geometry_or_anatomy": False,
        "broken_sport_surface_geometry": False,
    }
    cs275 = {
        "schema": CS275_SCHEMA,
        "receipt_sha256": "7" * 64,
        "story_snapshot_sha256": STORY,
        "composed_candidate_png": dict(composed),
        "scores": {
            "editorial_realism": 9.0,
            "composition_hierarchy": 9.0,
            "stadium_depth": 9.0,
            "controlled_lighting": 9.0,
            "protected_zone_cleanliness": 9.0,
            "platform_crop_strength": 9.0,
        },
        "blockers": blockers,
        "visual_quality_review_requested": True,
        "visual_quality_review_executed": True,
        "visual_quality_evidence_admitted": True,
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "semantic_inspection_executed": True,
        "hybrid_surface_semantic_qa_approved": True,
        **false,
    }
    return cs263, cs272, cs275


class GoldenQualityAdjudicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.paths = []
        for name in ("cs263.json", "cs272.json", "cs275.json"):
            path = self.root / name
            path.write_text("{}\n", encoding="utf-8")
            self.paths.append(path)

    def tearDown(self):
        self.tmp.cleanup()

    def _patches(self, values):
        return (
            patch(f"{MODULE}.verify_canonical_candidate_byte_admission", return_value=values[0]),
            patch(f"{MODULE}.verify_composed_candidate_byte_admission", return_value=values[1]),
            patch(f"{MODULE}.verify_composed_candidate_visual_quality_review_evidence", return_value=values[2]),
        )

    def _build(self, values, name="out"):
        patches = self._patches(values)
        with patches[0], patches[1], patches[2]:
            return build_composed_candidate_golden_quality_adjudication(
                self.paths[0], self.paths[1], self.paths[2], self.root / name, repo_root=self.root
            )

    def test_approved_selector_uses_only_proven_cs262_context(self):
        values = _sources()
        receipt_path = self._build(values)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertTrue(receipt["golden_quality_selector_executed"])
        self.assertTrue(receipt["golden_quality_approved"])
        self.assertEqual(receipt["quality_tier"], "elite")
        self.assertEqual(receipt["generation_context"]["seed"], 424242)
        self.assertEqual(receipt["generation_context"]["request_id"], f"qwen-cs262-{CS262}")
        self.assertFalse(receipt["human_visual_review_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        patches = self._patches(values)
        with patches[0], patches[1], patches[2]:
            verified = verify_composed_candidate_golden_quality_adjudication(receipt_path, repo_root=self.root)
        self.assertTrue(verified["golden_quality_approved"])

    def test_blocker_is_not_rescued_by_high_scores(self):
        receipt_path = self._build(_sources(blocker=True))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertFalse(receipt["golden_quality_approved"])
        self.assertEqual(receipt["quality_tier"], "below_golden")
        self.assertIsNone(receipt["selected_request_id"])

    def test_base_candidate_lineage_drift_fails_closed(self):
        values = list(_sources())
        values[1] = dict(values[1])
        values[1]["source_candidate_png"] = dict(values[1]["source_candidate_png"])
        values[1]["source_candidate_png"]["sha256"] = "8" * 64
        with self.assertRaisesRegex(ValueError, "BASE_CANDIDATE_DRIFT"):
            self._build(tuple(values))

    def test_composed_candidate_lineage_drift_fails_closed(self):
        values = list(_sources())
        values[2] = dict(values[2])
        values[2]["composed_candidate_png"] = dict(values[2]["composed_candidate_png"])
        values[2]["composed_candidate_png"]["sha256"] = "9" * 64
        with self.assertRaisesRegex(ValueError, "COMPOSED_CANDIDATE_DRIFT"):
            self._build(tuple(values))

    def test_bound_source_receipt_byte_tamper_invalidates_verification(self):
        values = _sources()
        receipt_path = self._build(values)
        self.paths[0].write_text('{"tampered":true}\n', encoding="utf-8")
        patches = self._patches(values)
        with patches[0], patches[1], patches[2], self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
            verify_composed_candidate_golden_quality_adjudication(receipt_path, repo_root=self.root)

    def test_receipt_cannot_forge_golden_verdict_even_with_rehashed_digest(self):
        values = _sources(blocker=True)
        receipt_path = self._build(values)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt["golden_quality_approved"] = True
        receipt.pop("receipt_sha256")
        receipt["receipt_sha256"] = sha256_json(receipt)
        receipt_path.write_text(json.dumps(receipt, separators=(",", ":")) + "\n", encoding="utf-8")
        patches = self._patches(values)
        with patches[0], patches[1], patches[2], self.assertRaisesRegex(ValueError, "VERDICT_DRIFT"):
            verify_composed_candidate_golden_quality_adjudication(receipt_path, repo_root=self.root)

    def test_existing_output_is_rejected(self):
        values = _sources()
        output = self.root / "taken"
        output.mkdir()
        patches = self._patches(values)
        with patches[0], patches[1], patches[2], self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
            build_composed_candidate_golden_quality_adjudication(
                self.paths[0], self.paths[1], self.paths[2], output, repo_root=self.root
            )


if __name__ == "__main__":
    unittest.main()
