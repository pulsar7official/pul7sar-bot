from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa as qa
from engine.intelligence.qwen25_vl_inspector import SemanticInspectionStage
from engine.intelligence.qwen_image_composed_candidate_byte_admission import SCHEMA as CS272_SCHEMA
from engine.intelligence.semantic_visual_verdict import (
    InspectionState,
    SemanticCheck,
    SemanticVisualVerdict,
)


def _check(
    state: InspectionState = InspectionState.PASS, confidence: float = 0.99
) -> SemanticCheck:
    return SemanticCheck(state=state, confidence=confidence, detail="fixture")


def _verdict(
    *,
    geometry: InspectionState = InspectionState.PASS,
    readable: InspectionState = InspectionState.PASS,
    confidence: float = 0.99,
    verifier_id: str | None = None,
) -> SemanticVisualVerdict:
    expected = verifier_id or (
        f"{qa.QWEN25_VL_VERIFIER_ID}:{SemanticInspectionStage.HYBRID_SURFACE.value}"
    )
    return SemanticVisualVerdict(
        verifier_id=expected,
        readable_text_absent=_check(readable, confidence),
        platform_brand_absent=_check(confidence=confidence),
        fake_entity_marks_absent=_check(confidence=confidence),
        single_scene=_check(confidence=confidence),
        severe_defects_absent=_check(confidence=confidence),
        subject_framing_valid=_check(confidence=confidence),
        sport_geometry_alignment_valid=_check(geometry, confidence),
        identity_valid=None,
        exact_numbers_absent=_check(confidence=confidence),
        generated_sport_geometry_absent=_check(confidence=confidence),
    )


class _Inspector:
    def __init__(self, verdict: SemanticVisualVerdict) -> None:
        self.verdict = verdict
        self.calls: list[tuple[str, SemanticInspectionStage]] = []

    def inspect_file(self, path: str, *, stage: SemanticInspectionStage):
        self.calls.append((path, stage))
        return self.verdict


class ComposedCandidateHybridSurfaceSemanticQATests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.artifacts = self.repo / "artifacts"
        self.artifacts.mkdir()
        self.cs272 = self.artifacts / "cs272.json"
        self.cs272.write_text("{}\n", encoding="utf-8")
        self.composed = self.artifacts / "composed_candidate.png"
        self.composed.write_bytes(b"\x89PNG\r\n\x1a\ncomposed-semantic-fixture")
        self.story_sha = "2" * 64

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _binding(self, path: Path, **extra: object) -> dict[str, object]:
        raw = path.read_bytes()
        return {
            "repository_relative_path": path.relative_to(self.repo).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
            **extra,
        }

    def _source(self) -> dict[str, object]:
        return {
            "schema": CS272_SCHEMA,
            "receipt_sha256": "a" * 64,
            "story_snapshot_sha256": self.story_sha,
            "composed_candidate_png": self._binding(
                self.composed, width=1024, height=1024
            ),
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _run(self, verdict: SemanticVisualVerdict | None = None):
        inspector = _Inspector(verdict or _verdict())
        source = self._source()
        patcher = patch.object(
            qa,
            "verify_composed_candidate_byte_admission",
            return_value=source,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        run = qa.run_composed_candidate_hybrid_surface_semantic_qa(
            self.cs272,
            self.artifacts / "cs273",
            repo_root=self.repo,
            inspector=inspector,
        )
        return run, inspector

    def test_passes_hybrid_surface_without_escalating_global_authority(self) -> None:
        run, inspector = self._run()
        receipt = qa.verify_composed_candidate_hybrid_surface_semantic_qa(
            run.receipt_path, repo_root=self.repo
        )
        self.assertTrue(run.approved)
        self.assertTrue(receipt["hybrid_surface_semantic_qa_approved"])
        self.assertTrue(receipt["semantic_inspection_executed"])
        self.assertEqual(inspector.calls[0][1], SemanticInspectionStage.HYBRID_SURFACE)
        self.assertFalse(receipt["composed_visual_approved"])
        self.assertFalse(receipt["semantic_approved"])
        self.assertFalse(receipt["human_visual_review_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["golden_quality_approved"])
        self.assertFalse(receipt["publication_ready"])

    def test_geometry_alignment_failure_is_rejected(self) -> None:
        run, _inspector = self._run(_verdict(geometry=InspectionState.FAIL))
        receipt = qa.verify_composed_candidate_hybrid_surface_semantic_qa(
            run.receipt_path, repo_root=self.repo
        )
        self.assertFalse(run.approved)
        self.assertFalse(receipt["hybrid_surface_semantic_qa_approved"])
        self.assertIn(
            "sport_geometry_alignment_valid:failed",
            receipt["semantic_gate"]["blockers"],
        )

    def test_low_confidence_is_fail_closed(self) -> None:
        run, _inspector = self._run(_verdict(confidence=0.80))
        receipt = qa.verify_composed_candidate_hybrid_surface_semantic_qa(
            run.receipt_path, repo_root=self.repo
        )
        self.assertFalse(run.approved)
        self.assertIn(
            "readable_text_absent:confidence_below_threshold",
            receipt["semantic_gate"]["blockers"],
        )

    def test_generated_text_residue_is_rejected(self) -> None:
        run, _inspector = self._run(_verdict(readable=InspectionState.FAIL))
        receipt = qa.verify_composed_candidate_hybrid_surface_semantic_qa(
            run.receipt_path, repo_root=self.repo
        )
        self.assertFalse(run.approved)
        self.assertTrue(
            receipt["semantic_layer_evidence"]["evidence"]["generated_text_detected"]
        )

    def test_composed_byte_drift_invalidates_receipt(self) -> None:
        run, _inspector = self._run()
        self.composed.write_bytes(self.composed.read_bytes() + b"tamper")
        with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
            qa.verify_composed_candidate_hybrid_surface_semantic_qa(
                run.receipt_path, repo_root=self.repo
            )

    def test_cs272_byte_drift_invalidates_receipt(self) -> None:
        run, _inspector = self._run()
        self.cs272.write_text('{"changed":true}\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
            qa.verify_composed_candidate_hybrid_surface_semantic_qa(
                run.receipt_path, repo_root=self.repo
            )

    def test_premature_golden_authority_is_rejected(self) -> None:
        source = self._source()
        source["genuine_golden_png_created"] = True
        inspector = _Inspector(_verdict())
        with patch.object(
            qa,
            "verify_composed_candidate_byte_admission",
            return_value=source,
        ):
            with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY"):
                qa.run_composed_candidate_hybrid_surface_semantic_qa(
                    self.cs272,
                    self.artifacts / "cs273",
                    repo_root=self.repo,
                    inspector=inspector,
                )

    def test_verifier_identity_drift_is_rejected(self) -> None:
        inspector = _Inspector(_verdict(verifier_id="unapproved-verifier"))
        with patch.object(
            qa,
            "verify_composed_candidate_byte_admission",
            return_value=self._source(),
        ):
            with self.assertRaisesRegex(ValueError, "VERIFIER_DRIFT"):
                qa.run_composed_candidate_hybrid_surface_semantic_qa(
                    self.cs272,
                    self.artifacts / "cs273",
                    repo_root=self.repo,
                    inspector=inspector,
                )

    def test_existing_output_directory_blocks_reuse(self) -> None:
        out = self.artifacts / "cs273"
        out.mkdir()
        with patch.object(
            qa,
            "verify_composed_candidate_byte_admission",
            return_value=self._source(),
        ):
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                qa.run_composed_candidate_hybrid_surface_semantic_qa(
                    self.cs272,
                    out,
                    repo_root=self.repo,
                    inspector=_Inspector(_verdict()),
                )


if __name__ == "__main__":
    unittest.main()
