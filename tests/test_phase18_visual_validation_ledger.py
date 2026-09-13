import tempfile
import unittest
from pathlib import Path

from engine.intelligence.visual_benchmark_suite import PHASE18_VISUAL_BENCHMARKS
from engine.intelligence.visual_validation_ledger import (
    GOLDEN_MINIMUM,
    VisualValidationLedgerError,
    build_canonical_visual_validation_ledger,
    candidate_png_evidence,
    record_visual_review,
    validate_visual_validation_ledger,
)


class VisualValidationLedgerTests(unittest.TestCase):
    def _candidate(self):
        return {"path": "output/candidate.png", "sha256": "a" * 64, "bytes": 4096}

    def _passing_checks(self):
        return {
            "factual_integrity_passed": True,
            "identity_integrity_passed": True,
            "sentiment_neutrality_passed": True,
            "sport_geometry_passed": True,
            "protected_zones_passed": True,
            "platform_crop_passed": True,
            "semantic_qa_passed": True,
            "provenance_passed": True,
        }

    def test_canonical_ledger_contains_every_benchmark_and_never_authorizes_publication(self):
        ledger = build_canonical_visual_validation_ledger()
        summary = validate_visual_validation_ledger(ledger)
        self.assertEqual(len(ledger["cases"]), len(PHASE18_VISUAL_BENCHMARKS))
        self.assertEqual(summary["accepted"], 0)
        self.assertEqual(summary["pending"], len(PHASE18_VISUAL_BENCHMARKS))
        self.assertFalse(summary["multi_family_visual_validation_complete"])
        self.assertFalse(summary["ready_for_publication_claim"])
        self.assertFalse(summary["publication_ready"])

    def test_real_png_evidence_requires_png_signature(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "fake.png"
            bad.write_bytes(b"not a png")
            with self.assertRaisesRegex(VisualValidationLedgerError, "CANDIDATE_NOT_PNG"):
                candidate_png_evidence(bad)

            good = Path(tmp) / "real.png"
            good.write_bytes(b"\x89PNG\r\n\x1a\n" + b"candidate-bytes")
            evidence = candidate_png_evidence(good)
            self.assertEqual(evidence["bytes"], good.stat().st_size)
            self.assertEqual(len(evidence["sha256"]), 64)

    def test_accepted_candidate_requires_every_integrity_gate_owner_acceptance_and_8_5(self):
        ledger = build_canonical_visual_validation_ledger()
        benchmark_id = PHASE18_VISUAL_BENCHMARKS[0].benchmark_id

        checks = self._passing_checks()
        checks["identity_integrity_passed"] = False
        with self.assertRaisesRegex(VisualValidationLedgerError, "ACCEPTED_CASE_CHECK_FAILED"):
            record_visual_review(
                ledger,
                benchmark_id=benchmark_id,
                candidate=self._candidate(),
                status="accepted",
                checks=checks,
                owner_visual_accepted=True,
                golden_quality_score=9.2,
            )

        with self.assertRaisesRegex(VisualValidationLedgerError, "OWNER_ACCEPTANCE_REQUIRED"):
            record_visual_review(
                ledger,
                benchmark_id=benchmark_id,
                candidate=self._candidate(),
                status="accepted",
                checks=self._passing_checks(),
                owner_visual_accepted=False,
                golden_quality_score=9.2,
            )

        with self.assertRaisesRegex(VisualValidationLedgerError, "GOLDEN_SCORE_BELOW_MINIMUM"):
            record_visual_review(
                ledger,
                benchmark_id=benchmark_id,
                candidate=self._candidate(),
                status="accepted",
                checks=self._passing_checks(),
                owner_visual_accepted=True,
                golden_quality_score=GOLDEN_MINIMUM - 0.1,
            )

    def test_broken_sport_geometry_hard_blocker_defeats_9_9_score(self):
        ledger = build_canonical_visual_validation_ledger()
        benchmark_id = next(case.benchmark_id for case in PHASE18_VISUAL_BENCHMARKS if case.event.value == "preview")
        with self.assertRaisesRegex(VisualValidationLedgerError, "ACCEPTED_CASE_HAS_HARD_BLOCKER"):
            record_visual_review(
                ledger,
                benchmark_id=benchmark_id,
                candidate=self._candidate(),
                status="accepted",
                checks=self._passing_checks(),
                owner_visual_accepted=True,
                golden_quality_score=9.9,
                hard_blockers=("broken_sport_surface_geometry",),
            )

    def test_rejected_candidate_is_recordable_without_becoming_publication_ready(self):
        ledger = build_canonical_visual_validation_ledger()
        benchmark_id = next(case.benchmark_id for case in PHASE18_VISUAL_BENCHMARKS if case.event.value == "preview")
        checks = self._passing_checks()
        checks["sport_geometry_passed"] = False
        updated = record_visual_review(
            ledger,
            benchmark_id=benchmark_id,
            candidate=self._candidate(),
            status="rejected",
            checks=checks,
            owner_visual_accepted=False,
            golden_quality_score=8.9,
            hard_blockers=("broken_sport_surface_geometry",),
            rejection_reasons=("isolated partial goal geometry is physically inconsistent",),
        )
        summary = validate_visual_validation_ledger(updated)
        self.assertEqual(summary["rejected"], 1)
        self.assertFalse(summary["publication_ready"])
        self.assertFalse(updated["ready_for_publication_claim"])

    def test_all_seven_acceptances_complete_visual_validation_but_still_do_not_authorize_publication(self):
        ledger = build_canonical_visual_validation_ledger()
        for case in PHASE18_VISUAL_BENCHMARKS:
            ledger = record_visual_review(
                ledger,
                benchmark_id=case.benchmark_id,
                candidate={"path": f"output/{case.benchmark_id}.png", "sha256": "b" * 64, "bytes": 8192},
                status="accepted",
                checks=self._passing_checks(),
                owner_visual_accepted=True,
                golden_quality_score=9.0,
            )
        summary = validate_visual_validation_ledger(ledger)
        self.assertEqual(summary["accepted"], len(PHASE18_VISUAL_BENCHMARKS))
        self.assertTrue(summary["multi_family_visual_validation_complete"])
        self.assertFalse(summary["ready_for_publication_claim"])
        self.assertFalse(summary["publication_ready"])

    def test_ledger_cannot_claim_publication_ready(self):
        ledger = build_canonical_visual_validation_ledger()
        ledger["publication_ready"] = True
        with self.assertRaisesRegex(VisualValidationLedgerError, "CANNOT_AUTHORIZE_PUBLICATION"):
            validate_visual_validation_ledger(ledger)


if __name__ == "__main__":
    unittest.main()
