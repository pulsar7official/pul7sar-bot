from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.remote_renderer_research_ledger import (
    COST_MODE,
    LEDGER_SCHEMA,
    RemoteRendererResearchLedgerBuilder,
)


PNG = b"\x89PNG\r\n\x1a\n" + b"remote-renderer-study"


class RemoteRendererResearchLedgerTests(unittest.TestCase):
    def _fixtures(self, root: Path):
        output = root / "output" / "qwen.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(PNG)
        import hashlib
        output_sha = hashlib.sha256(PNG).hexdigest()
        prompt_sha = "a" * 64
        report = {
            "schema": "pul7sar-phase18-remote-renderer-benchmark-v3",
            "prompt_sha256": prompt_sha,
            "successful": [{
                "renderer": "qwen-image-2512",
                "space": "Qwen/Qwen-Image-2512",
                "output": str(output),
                "output_sha256": output_sha,
                "output_bytes": len(PNG),
                "seed": 1902001,
                "prompt_sha256": prompt_sha,
                "cost_mode": COST_MODE,
                "entity_neutral_benchmark": True,
                "canonical_golden_eligible": False,
                "publication_ready": False,
            }],
            "cost_mode": COST_MODE,
            "entity_neutral_benchmark": True,
            "verified_identity_asset_used": False,
            "verified_venue_asset_used": False,
            "engineering_benchmark_only": True,
            "canonical_golden_eligible": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "human_visual_review_required": True,
        }
        review = {
            "schema": "pul7sar-phase18-remote-renderer-human-review-v1",
            "prompt_sha256": prompt_sha,
            "renderers": {
                "qwen-image-2512": {
                    "output_sha256": output_sha,
                    "scores": {
                        "editorial_composition": 8.6,
                        "photorealism": 8.4,
                        "geometry_integrity": 8.8,
                        "scene_continuity": 8.5,
                        "entity_neutrality": 9.0,
                        "text_and_brand_cleanliness": 9.2,
                    },
                    "hard_blockers": {
                        "broken_geometry": False,
                        "pseudo_text": False,
                        "identifiable_entity_cue": False,
                        "multi_scene_or_collage": False,
                        "generated_brand_or_crest": False,
                    },
                }
            },
        }
        report_path = root / "benchmark.json"
        review_path = root / "review.json"
        report_path.write_text(json.dumps(report), encoding="utf-8")
        review_path.write_text(json.dumps(review), encoding="utf-8")
        return output, report_path, review_path, report, review

    def test_builds_byte_bound_noncanonical_research_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, report_path, review_path, _, _ = self._fixtures(root)
            ledger = RemoteRendererResearchLedgerBuilder(root).build(
                benchmark_report_path=report_path,
                human_review_path=review_path,
            )
            self.assertEqual(ledger["schema"], LEDGER_SCHEMA)
            self.assertEqual(ledger["research_leader"], "qwen-image-2512")
            self.assertEqual(ledger["research_leader_output_sha256"], ledger["entries"][0]["output_sha256"])
            self.assertTrue(ledger["research_only"])
            self.assertTrue(ledger["canonical_admission_required"])
            self.assertFalse(ledger["canonical_golden_eligible"])
            self.assertFalse(ledger["semantic_approved"])
            self.assertFalse(ledger["golden_quality_approved"])
            self.assertFalse(ledger["publication_ready"])
            self.assertEqual(Path(ledger["entries"][0]["output"]), output.resolve())
            self.assertEqual(len(ledger["ledger_sha256"]), 64)

    def test_png_tampering_after_benchmark_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, report_path, review_path, _, _ = self._fixtures(root)
            output.write_bytes(PNG + b"tampered")
            with self.assertRaisesRegex(ValueError, "REMOTE_RESEARCH_OUTPUT_SHA_MISMATCH"):
                RemoteRendererResearchLedgerBuilder(root).build(
                    benchmark_report_path=report_path,
                    human_review_path=review_path,
                )

    def test_hard_blocker_prevents_research_leader_even_with_high_scores(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, report_path, review_path, _, review = self._fixtures(root)
            renderer_review = review["renderers"]["qwen-image-2512"]
            for key in renderer_review["scores"]:
                renderer_review["scores"][key] = 9.9
            renderer_review["hard_blockers"]["broken_geometry"] = True
            review_path.write_text(json.dumps(review), encoding="utf-8")
            ledger = RemoteRendererResearchLedgerBuilder(root).build(
                benchmark_report_path=report_path,
                human_review_path=review_path,
            )
            self.assertIsNone(ledger["research_leader"])
            self.assertFalse(ledger["entries"][0]["research_score_floor_met"])
            self.assertFalse(ledger["publication_ready"])

    def test_review_must_bind_same_png_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, report_path, review_path, _, review = self._fixtures(root)
            review["renderers"]["qwen-image-2512"]["output_sha256"] = "b" * 64
            review_path.write_text(json.dumps(review), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "REMOTE_RESEARCH_REVIEW_OUTPUT_MISMATCH"):
                RemoteRendererResearchLedgerBuilder(root).build(
                    benchmark_report_path=report_path,
                    human_review_path=review_path,
                )

    def test_remote_report_can_never_claim_canonical_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, report_path, review_path, report, _ = self._fixtures(root)
            report["canonical_golden_eligible"] = True
            report_path.write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "REMOTE_RESEARCH_CANONICAL_AUTHORITY_FORBIDDEN"):
                RemoteRendererResearchLedgerBuilder(root).build(
                    benchmark_report_path=report_path,
                    human_review_path=review_path,
                )

    def test_path_escape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            outside = Path(tmp) / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "REMOTE_RESEARCH_PATH_ESCAPE"):
                RemoteRendererResearchLedgerBuilder(root).build(
                    benchmark_report_path=outside,
                    human_review_path=outside,
                )


if __name__ == "__main__":
    unittest.main()
