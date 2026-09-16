from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication import (
    _assert_exact_lineage,
    build_composed_candidate_golden_quality_adjudication,
    verify_composed_candidate_golden_quality_adjudication,
)
from engine.intelligence.qwen_image_canonical_candidate_byte_admission import CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_byte_admission import SCHEMA as CS272_SCHEMA
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import SCHEMA as CS275_SCHEMA

MODULE = "engine.intelligence.qwen_image_composed_candidate_golden_quality_adjudication"
STORY = "1" * 64
CANONICAL = "2" * 64


def png(path: str, digest: str) -> dict:
    return {"repository_relative_path": path, "sha256": digest, "byte_size": 123, "width": 1024, "height": 1024}


def sources(blocker: bool = False):
    candidate = png("runs/canonical_candidate.png", "3" * 64)
    composed = png("runs/composed_candidate.png", "4" * 64)
    closed = {"semantic_approved": False, "human_visual_review_approved": False, "genuine_golden_png_created": False, "golden_quality_approved": False, "publication_ready": False}
    cs263 = {
        "schema": CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
        "receipt_sha256": "5" * 64,
        "story_snapshot_sha256": STORY,
        "source_canonical_inference_receipt": {"receipt_sha256": CANONICAL},
        "candidate_png": candidate,
        "inference_settings": {"seed": 424242},
        "genuine_canonical_inference_executed": True,
        "handoff_sealed": True,
        "candidate_bytes_admitted_for_post_generation_qa": True,
        "cost_mode": "$0-local",
        "network_allowed": False,
        "local_files_only": True,
        **closed,
    }
    composed_closed = {"composed_visual_approved": False, **closed}
    cs272 = {
        "schema": CS272_SCHEMA, "receipt_sha256": "6" * 64, "story_snapshot_sha256": STORY,
        "source_candidate_png": dict(candidate), "composed_candidate_png": composed,
        "composition_executed": True, "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        **composed_closed,
    }
    blocker_fields = (
        "fantasy_or_monumental_staging", "fake_logo_or_crest", "pseudo_text_or_gibberish",
        "generated_platform_brand_or_wordmark", "invented_result_or_winner", "cluttered_collage",
        "broken_geometry_or_anatomy", "broken_sport_surface_geometry",
    )
    blockers = {name: False for name in blocker_fields}
    blockers["fantasy_or_monumental_staging"] = blocker
    cs275 = {
        "schema": CS275_SCHEMA, "receipt_sha256": "7" * 64, "story_snapshot_sha256": STORY,
        "composed_candidate_png": dict(composed),
        "scores": {name: 9.0 for name in ("editorial_realism", "composition_hierarchy", "stadium_depth", "controlled_lighting", "protected_zone_cleanliness", "platform_crop_strength")},
        "blockers": blockers,
        "visual_quality_review_requested": True, "visual_quality_review_executed": True,
        "visual_quality_evidence_admitted": True, "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "semantic_inspection_executed": True, "hybrid_surface_semantic_qa_approved": True,
        "visual_quality_review_approved": False, **composed_closed,
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

    def patched(self, values):
        return (
            patch(f"{MODULE}.verify_canonical_candidate_byte_admission", return_value=values[0]),
            patch(f"{MODULE}.verify_composed_candidate_byte_admission", return_value=values[1]),
            patch(f"{MODULE}.verify_composed_candidate_visual_quality_review_evidence", return_value=values[2]),
            patch(f"{MODULE}._assert_exact_lineage", return_value=None),
        )

    def build(self, values, name="out"):
        a, b, c, d = self.patched(values)
        with a, b, c, d:
            return build_composed_candidate_golden_quality_adjudication(*self.paths, self.root / name, repo_root=self.root)

    def test_current_sealed_generation_context_is_used(self):
        values = sources()
        receipt_path = self.build(values)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertTrue(receipt["golden_quality_approved"])
        self.assertEqual(receipt["generation_context"]["seed"], 424242)
        self.assertEqual(receipt["generation_context"]["request_id"], f"qwen-canonical-{CANONICAL}")
        self.assertEqual(receipt["generation_context"]["seed_source"], "sealed_cs303_inference_settings")
        self.assertFalse(receipt["human_visual_review_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        a, b, c, d = self.patched(values)
        with a, b, c, d:
            self.assertTrue(verify_composed_candidate_golden_quality_adjudication(receipt_path, repo_root=self.root)["golden_quality_approved"])

    def test_legacy_authority_shape_is_rejected(self):
        values = list(sources())
        values[0] = dict(values[0])
        values[0].pop("handoff_sealed")
        values[0]["inference_executed"] = True
        with self.assertRaisesRegex(ValueError, "handoff_sealed"):
            self.build(tuple(values))

    def test_zero_cost_local_contract_is_required(self):
        values = list(sources())
        values[0] = dict(values[0])
        values[0]["network_allowed"] = True
        with self.assertRaisesRegex(ValueError, "LOCAL_ONLY_DRIFT"):
            self.build(tuple(values))

    def test_quality_blocker_remains_fail_closed(self):
        receipt = json.loads(self.build(sources(True)).read_text(encoding="utf-8"))
        self.assertFalse(receipt["golden_quality_approved"])
        self.assertEqual(receipt["quality_tier"], "below_golden")

    def test_base_candidate_mismatch_is_rejected(self):
        values = list(sources())
        values[1] = dict(values[1])
        values[1]["source_candidate_png"] = dict(values[1]["source_candidate_png"])
        values[1]["source_candidate_png"]["sha256"] = "8" * 64
        with self.assertRaisesRegex(ValueError, "BASE_CANDIDATE_DRIFT"):
            self.build(tuple(values))

    def test_cs263_cross_run_substitution_is_rejected(self):
        cs263, cs272, cs275 = sources()
        supplied = {"repository_relative_path": "cs263.json", "sha256": "a" * 64, "byte_size": 10}
        derived = {"repository_relative_path": "other/cs263.json", "sha256": "b" * 64, "byte_size": 11}
        with patch(f"{MODULE}._derive_candidate_admission_from_cs272", return_value=(derived, cs263)), self.assertRaisesRegex(ValueError, "CS263_CS272_LINEAGE_DRIFT"):
            _assert_exact_lineage(repo_root=self.root, cs263_binding=supplied, cs263=cs263, cs272_binding={"repository_relative_path": "cs272.json", "sha256": "c" * 64, "byte_size": 12}, cs272=cs272, cs275=cs275)

    def test_cs272_cross_run_substitution_is_rejected(self):
        cs263, cs272, cs275 = sources()
        b263 = {"repository_relative_path": "cs263.json", "sha256": "a" * 64, "byte_size": 10}
        b272 = {"repository_relative_path": "cs272.json", "sha256": "c" * 64, "byte_size": 12}
        derived263 = {**b263, "receipt_sha256": cs263["receipt_sha256"]}
        derived272 = {"repository_relative_path": "other/cs272.json", "sha256": "d" * 64, "byte_size": 13, "receipt_sha256": cs272["receipt_sha256"]}
        with patch(f"{MODULE}._derive_candidate_admission_from_cs272", return_value=(derived263, cs263)), patch(f"{MODULE}._derive_cs272_binding_from_cs275", return_value=derived272), self.assertRaisesRegex(ValueError, "CS272_CS275_LINEAGE_DRIFT"):
            _assert_exact_lineage(repo_root=self.root, cs263_binding=b263, cs263=cs263, cs272_binding=b272, cs272=cs272, cs275=cs275)

    def test_existing_output_is_rejected(self):
        output = self.root / "taken"
        output.mkdir()
        values = sources()
        a, b, c, d = self.patched(values)
        with a, b, c, d, self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
            build_composed_candidate_golden_quality_adjudication(*self.paths, output, repo_root=self.root)


if __name__ == "__main__":
    unittest.main()
