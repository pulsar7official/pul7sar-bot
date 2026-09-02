from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tools.phase18_continue_final_presentation_evidence_to_composed_approval as subject


def _png(sha: str = "a" * 64) -> dict[str, object]:
    return {
        "repository_relative_path": "artifacts/composed.png",
        "sha256": sha,
        "byte_size": 123,
    }


class FinalPresentationEvidenceComposedApprovalCheckpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _fixture(self, *, approved: bool = True):
        story = "b" * 64
        png = _png()
        cs279_path = self.root / "cs279.json"
        cs279_path.write_text("{}", encoding="utf-8")
        external = self.root / "external_review.json"
        external.write_text("{}", encoding="utf-8")
        checkpoint_path = self.root / "cs325.json"
        checkpoint_path.write_text(
            json.dumps(
                {
                    "schema": subject.CS325_SCHEMA,
                    "status": "FINAL_PRESENTATION_REVIEW_EVIDENCE_REQUIRED",
                    "authoritative": False,
                    "story_snapshot_sha256": story,
                    "candidate_png": {"sha256": "c" * 64},
                    "composed_candidate_png": png,
                    "cs279_receipt": "cs279.json",
                    "golden_quality_approved": True,
                    "human_visual_review_approved": True,
                    "final_presentation_review_requested": True,
                    "final_presentation_review_executed": False,
                    "final_presentation_review_approved": False,
                    "exact_brand_integrity_approved": False,
                    "typography_integrity_approved": False,
                    "composed_visual_approved": False,
                    "semantic_approved": False,
                    "genuine_golden_png_created": False,
                    "publication_ready": False,
                }
            ),
            encoding="utf-8",
        )
        cs279 = {
            "schema": subject.CS279_SCHEMA,
            "story_snapshot_sha256": story,
            "composed_candidate_png": png,
            "final_presentation_review_requested": True,
            "final_presentation_review_executed": False,
            "final_presentation_review_approved": False,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        cs280 = {
            "schema": subject.CS280_SCHEMA,
            "story_snapshot_sha256": story,
            "composed_candidate_png": png,
            "final_presentation_review_approved": approved,
            "exact_brand_integrity_approved": approved,
            "typography_integrity_approved": approved,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        return checkpoint_path, external, story, png, cs279, cs280

    def _cs280_builder(self, external: Path):
        def build280(_cs279, review, output, *, repo_root):
            self.assertEqual(review, external)
            output.mkdir()
            path = output / "cs280.json"
            path.write_text("{}", encoding="utf-8")
            return path

        return build280

    def test_approved_external_cs280_continues_to_exact_cs281(self):
        checkpoint, external, story, png, cs279, cs280 = self._fixture(approved=True)
        cs273_path = self.root / "cs273.json"
        cs273_path.write_text("{}", encoding="utf-8")
        cs273 = {
            "schema": subject.CS273_SCHEMA,
            "story_snapshot_sha256": story,
            "composed_candidate_png": png,
        }
        calls = {"cs281": 0}

        def build281(given273, given280, output, *, repo_root):
            calls["cs281"] += 1
            self.assertEqual(given273, cs273_path)
            self.assertEqual(given280.name, "cs280.json")
            output.mkdir()
            path = output / "cs281.json"
            path.write_text("{}", encoding="utf-8")
            return path

        cs281 = {
            "schema": subject.CS281_SCHEMA,
            "story_snapshot_sha256": story,
            "composed_candidate_png": png,
            "composed_visual_approved": True,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }
        with (
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_presentation_review_request",
                return_value=cs279,
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_presentation_review_evidence",
                side_effect=self._cs280_builder(external),
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_presentation_review_evidence",
                return_value=cs280,
            ),
            mock.patch.object(
                subject,
                "_derive_exact_cs273",
                return_value=(cs273_path, cs273),
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_composed_visual_approval",
                side_effect=build281,
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_composed_visual_approval",
                return_value=cs281,
            ),
        ):
            out = subject.continue_final_presentation_evidence_to_composed_approval(
                checkpoint, external, self.root / "out", repo_root=self.root
            )

        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(calls["cs281"], 1)
        self.assertEqual(
            payload["status"],
            "FINAL_COMPOSED_VISUAL_APPROVED_AWAITING_FINAL_SEMANTIC_APPROVAL",
        )
        self.assertIs(payload["final_presentation_review_approved"], True)
        self.assertIs(payload["exact_brand_integrity_approved"], True)
        self.assertIs(payload["typography_integrity_approved"], True)
        self.assertIs(payload["composed_visual_approved"], True)
        self.assertIs(payload["semantic_approved"], False)
        self.assertIs(payload["genuine_golden_png_created"], False)
        self.assertIs(payload["publication_ready"], False)
        self.assertIs(payload["authoritative"], False)

    def test_rejected_external_cs280_never_builds_cs281(self):
        checkpoint, external, _story, _png_value, cs279, cs280 = self._fixture(
            approved=False
        )
        with (
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_presentation_review_request",
                return_value=cs279,
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_presentation_review_evidence",
                side_effect=self._cs280_builder(external),
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_presentation_review_evidence",
                return_value=cs280,
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_composed_visual_approval",
                side_effect=AssertionError(
                    "CS281 must not run after presentation rejection"
                ),
            ),
        ):
            out = subject.continue_final_presentation_evidence_to_composed_approval(
                checkpoint, external, self.root / "out", repo_root=self.root
            )

        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["status"],
            "COMPOSED_CANDIDATE_REJECTED_BY_FINAL_PRESENTATION_REVIEW",
        )
        self.assertIsNone(payload["cs281_receipt"])
        self.assertIs(payload["composed_visual_approved"], False)
        self.assertIs(payload["semantic_approved"], False)
        self.assertIs(payload["publication_ready"], False)

    def test_cs280_composed_byte_drift_fails_closed(self):
        checkpoint, external, _story, _png_value, cs279, cs280 = self._fixture(
            approved=True
        )
        cs280["composed_candidate_png"] = _png("d" * 64)
        with (
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_presentation_review_request",
                return_value=cs279,
            ),
            mock.patch.object(
                subject,
                "build_composed_candidate_final_presentation_review_evidence",
                side_effect=self._cs280_builder(external),
            ),
            mock.patch.object(
                subject,
                "verify_composed_candidate_final_presentation_review_evidence",
                return_value=cs280,
            ),
            self.assertRaisesRegex(ValueError, "CS280_COMPOSED_BYTES_DRIFT"),
        ):
            subject.continue_final_presentation_evidence_to_composed_approval(
                checkpoint, external, self.root / "out", repo_root=self.root
            )

    def test_orchestrator_does_not_generate_review_or_grant_semantic_publication(self):
        source = Path(subject.__file__).read_text(encoding="utf-8")
        self.assertIn("build_composed_candidate_final_presentation_review_evidence", source)
        self.assertIn("build_composed_candidate_final_composed_visual_approval", source)
        self.assertNotIn("QwenImagePipeline", source)
        self.assertNotIn("build_composed_candidate_final_semantic_approval", source)
        self.assertIn('"semantic_approved": False', source)
        self.assertIn('"genuine_golden_png_created": False', source)
        self.assertIn('"publication_ready": False', source)
        self.assertNotIn("independent_manual_final_presentation_review", source)


if __name__ == "__main__":
    unittest.main()
