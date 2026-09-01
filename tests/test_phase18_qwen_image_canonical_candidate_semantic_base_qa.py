from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa as qa
from engine.intelligence.qwen25_vl_inspector import SemanticInspectionStage
from engine.intelligence.qwen_image_canonical_candidate_byte_admission import (
    CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
)
from engine.intelligence.semantic_visual_verdict import (
    InspectionState,
    SemanticCheck,
    SemanticVisualVerdict,
)


def _check(state: InspectionState = InspectionState.PASS, confidence: float = 0.99) -> SemanticCheck:
    return SemanticCheck(state=state, confidence=confidence, detail="fixture")


def _verdict(*, readable: InspectionState = InspectionState.PASS, verifier_id: str | None = None) -> SemanticVisualVerdict:
    expected = verifier_id or f"{qa.QWEN25_VL_VERIFIER_ID}:{SemanticInspectionStage.BASE_SCENE.value}"
    return SemanticVisualVerdict(
        verifier_id=expected,
        readable_text_absent=_check(readable),
        platform_brand_absent=_check(),
        fake_entity_marks_absent=_check(),
        single_scene=_check(),
        severe_defects_absent=_check(),
        subject_framing_valid=_check(),
        sport_geometry_alignment_valid=_check(),
        identity_valid=None,
        exact_numbers_absent=_check(),
        generated_sport_geometry_absent=_check(),
    )


class _Inspector:
    def __init__(self, verdict: SemanticVisualVerdict) -> None:
        self.verdict = verdict
        self.calls: list[tuple[str, SemanticInspectionStage]] = []

    def inspect_file(self, path: str, *, stage: SemanticInspectionStage):
        self.calls.append((path, stage))
        return self.verdict


class CanonicalCandidateSemanticBaseQATests(unittest.TestCase):
    def _fixture(self, root: Path, verdict: SemanticVisualVerdict | None = None):
        repo = root / "repo"
        candidate_dir = repo / "artifacts" / "cs262"
        candidate_dir.mkdir(parents=True)
        candidate = candidate_dir / "canonical_candidate.png"
        raw = b"\x89PNG\r\n\x1a\nsemantic-qa-fixture"
        candidate.write_bytes(raw)
        admission_dir = repo / "artifacts" / "cs303"
        admission_dir.mkdir()
        admission_receipt = admission_dir / "canonical_candidate_byte_admission_receipt.json"
        admission_receipt.write_text("{}\n", encoding="utf-8")
        source = {
            "schema": CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
            "receipt_sha256": "a" * 64,
            "story_snapshot_sha256": "b" * 64,
            "cost_mode": "$0-local",
            "network_allowed": False,
            "local_files_only": True,
            "source_candidate_handoff": {
                "repository_relative_path": "artifacts/cs302/canonical_candidate_handoff.json",
                "sha256": "c" * 64,
                "byte_size": 123,
                "handoff_sha256": "d" * 64,
            },
            "candidate_png": {
                "repository_relative_path": "artifacts/cs262/canonical_candidate.png",
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byte_size": len(raw),
                "width": 32,
                "height": 24,
            },
            "genuine_canonical_inference_executed": True,
            "handoff_sealed": True,
            "candidate_bytes_admitted_for_post_generation_qa": True,
            "genuine_golden_png_created": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        patcher = mock.patch.object(
            qa,
            "verify_canonical_candidate_byte_admission",
            side_effect=lambda *_args, **_kwargs: source,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        inspector = _Inspector(verdict or _verdict())
        return repo, admission_receipt, candidate, source, inspector

    def test_passes_base_semantics_from_cs303_without_escalating_global_authority(self):
        with tempfile.TemporaryDirectory() as td:
            repo, admission, _candidate, source, inspector = self._fixture(Path(td))
            run = qa.run_canonical_candidate_semantic_base_qa(
                admission,
                repo / "artifacts" / "cs304",
                repo_root=repo,
                inspector=inspector,
            )
            result = qa.verify_canonical_candidate_semantic_base_qa(run.receipt_path, repo_root=repo)
            self.assertTrue(run.approved)
            self.assertTrue(result["semantic_inspection_executed"])
            self.assertTrue(result["semantic_base_scene_approved"])
            self.assertEqual(
                result["source_candidate_admission"]["candidate_handoff_sha256"],
                source["source_candidate_handoff"]["handoff_sha256"],
            )
            self.assertFalse(result["identity_approved"])
            self.assertFalse(result["semantic_approved"])
            self.assertFalse(result["human_visual_review_approved"])
            self.assertFalse(result["golden_quality_approved"])
            self.assertFalse(result["publication_ready"])
            self.assertEqual(inspector.calls[0][1], SemanticInspectionStage.BASE_SCENE)

    def test_records_rejection_when_generated_text_is_detected(self):
        with tempfile.TemporaryDirectory() as td:
            repo, admission, _candidate, _source, inspector = self._fixture(
                Path(td), _verdict(readable=InspectionState.FAIL)
            )
            run = qa.run_canonical_candidate_semantic_base_qa(
                admission,
                repo / "artifacts" / "cs304",
                repo_root=repo,
                inspector=inspector,
            )
            result = qa.verify_canonical_candidate_semantic_base_qa(run.receipt_path, repo_root=repo)
            self.assertFalse(run.approved)
            self.assertFalse(result["semantic_base_scene_approved"])
            self.assertIn("readable_text_absent:failed", result["semantic_gate"]["blockers"])
            self.assertTrue(result["semantic_layer_evidence"]["evidence"]["generated_text_detected"])

    def test_rejects_candidate_byte_tamper_after_semantic_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            repo, admission, candidate, _source, inspector = self._fixture(Path(td))
            run = qa.run_canonical_candidate_semantic_base_qa(
                admission,
                repo / "artifacts" / "cs304",
                repo_root=repo,
                inspector=inspector,
            )
            candidate.write_bytes(candidate.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "CANDIDATE_BYTE_DRIFT"):
                qa.verify_canonical_candidate_semantic_base_qa(run.receipt_path, repo_root=repo)

    def test_rejects_legacy_admission_authority_shape(self):
        with tempfile.TemporaryDirectory() as td:
            repo, admission, _candidate, source, inspector = self._fixture(Path(td))
            source.pop("handoff_sealed")
            source.update(
                {
                    "production_semantic_replay_executed": True,
                    "fresh_story_gates_passed": True,
                    "controlled_trial_preflight_valid": True,
                    "canonical_generation_authorized": True,
                    "inference_executed": True,
                }
            )
            with self.assertRaisesRegex(ValueError, "REQUIRED_GATE_MISSING:handoff_sealed"):
                qa.run_canonical_candidate_semantic_base_qa(
                    admission,
                    repo / "artifacts" / "cs304",
                    repo_root=repo,
                    inspector=inspector,
                )

    def test_rejects_missing_handoff_binding(self):
        with tempfile.TemporaryDirectory() as td:
            repo, admission, _candidate, source, inspector = self._fixture(Path(td))
            source.pop("source_candidate_handoff")
            with self.assertRaisesRegex(ValueError, "HANDOFF_BINDING_MISSING"):
                qa.run_canonical_candidate_semantic_base_qa(
                    admission,
                    repo / "artifacts" / "cs304",
                    repo_root=repo,
                    inspector=inspector,
                )

    def test_rejects_paid_or_network_enabled_admission(self):
        with tempfile.TemporaryDirectory() as td:
            repo, admission, _candidate, source, inspector = self._fixture(Path(td))
            source["cost_mode"] = "$paid"
            with self.assertRaisesRegex(ValueError, "COST_MODE_DRIFT"):
                qa.run_canonical_candidate_semantic_base_qa(
                    admission,
                    repo / "artifacts" / "cs304",
                    repo_root=repo,
                    inspector=inspector,
                )

        with tempfile.TemporaryDirectory() as td:
            repo, admission, _candidate, source, inspector = self._fixture(Path(td))
            source["network_allowed"] = True
            with self.assertRaisesRegex(ValueError, "LOCAL_ONLY_DRIFT"):
                qa.run_canonical_candidate_semantic_base_qa(
                    admission,
                    repo / "artifacts" / "cs304",
                    repo_root=repo,
                    inspector=inspector,
                )

    def test_rejects_semantic_verifier_identity_drift(self):
        with tempfile.TemporaryDirectory() as td:
            repo, admission, _candidate, _source, inspector = self._fixture(
                Path(td), _verdict(verifier_id="unapproved-verifier")
            )
            with self.assertRaisesRegex(ValueError, "VERIFIER_DRIFT"):
                qa.run_canonical_candidate_semantic_base_qa(
                    admission,
                    repo / "artifacts" / "cs304",
                    repo_root=repo,
                    inspector=inspector,
                )

    def test_rejects_existing_output_directory(self):
        with tempfile.TemporaryDirectory() as td:
            repo, admission, _candidate, _source, inspector = self._fixture(Path(td))
            out = repo / "artifacts" / "cs304"
            out.mkdir()
            with self.assertRaisesRegex(ValueError, "OUTPUT_ALREADY_EXISTS"):
                qa.run_canonical_candidate_semantic_base_qa(
                    admission, out, repo_root=repo, inspector=inspector
                )


if __name__ == "__main__":
    unittest.main()
