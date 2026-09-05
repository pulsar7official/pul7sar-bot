import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.football_pitch_semantic_review import FootballPitchSemanticReviewGate
from engine.intelligence.semantic_visual_verdict import InspectionState, SemanticCheck, SemanticVisualVerdict


REQUIRED_GATES = [
    "fact_lock",
    "identity_verification",
    "sentiment_neutrality",
    "semantic_layer_ownership",
    "semantic_publication",
    "golden_visual_quality",
    "exact_brand_integrity",
    "typography_integrity",
    "publication_readiness",
]


def passed(detail="ok"):
    return SemanticCheck(InspectionState.PASS, 0.99, detail)


def verdict(*, geometry=None, generated_geometry=None):
    return SemanticVisualVerdict(
        verifier_id="unit-test:hybrid_surface",
        readable_text_absent=passed(),
        platform_brand_absent=passed(),
        fake_entity_marks_absent=passed(),
        single_scene=passed(),
        severe_defects_absent=passed(),
        subject_framing_valid=passed(),
        sport_geometry_alignment_valid=geometry if geometry is not None else passed("aligned"),
        exact_numbers_absent=passed(),
        generated_sport_geometry_absent=generated_geometry if generated_geometry is not None else passed("no conflict"),
    )


class FootballPitchSemanticReviewTests(unittest.TestCase):
    def _fixture(self, root: Path):
        locked = root / "locked.png"
        locked.write_bytes(b"real-locked-png-bytes")
        sha = hashlib.sha256(locked.read_bytes()).hexdigest()
        lock = root / "selection-lock.json"
        lock.write_text(json.dumps({
            "status": "FOOTBALL_PITCH_SELECTION_LOCKED",
            "selection_only": True,
            "publication_ready": False,
            "candidate": 1,
            "request_id": "golden-v5-001",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "selection_is_manual": True,
            "selected_preset": "high_wide_central",
            "locked_png": str(locked),
            "locked_png_sha256": sha,
            "source_variant_sha256": sha,
            "artifact_integrity_proven": True,
            "gates_not_waived": REQUIRED_GATES,
        }), encoding="utf-8")
        return lock, locked

    def test_clean_locked_artifact_can_pass_semantic_alignment_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock, _ = self._fixture(root)
            payload = FootballPitchSemanticReviewGate().review(
                selection_lock_path=str(lock),
                verdict=verdict(),
                output_dir=str(root / "out"),
            )
            self.assertTrue(payload["semantic_approved"])
            self.assertFalse(payload["publication_ready"])
            self.assertFalse(payload["golden_quality_approved"])
            self.assertEqual(payload["semantic_stage"], "hybrid_surface")
            self.assertTrue(Path(payload["receipt"]).is_file())

    def test_bad_geometry_alignment_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock, _ = self._fixture(root)
            bad = SemanticCheck(InspectionState.FAIL, 0.99, "floating pitch")
            payload = FootballPitchSemanticReviewGate().review(
                selection_lock_path=str(lock),
                verdict=verdict(geometry=bad),
                output_dir=str(root / "out"),
            )
            self.assertFalse(payload["semantic_approved"])
            self.assertIn("sport_geometry_alignment_valid:failed", payload["semantic_failures"])

    def test_missing_conflicting_geometry_check_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock, _ = self._fixture(root)
            incomplete = verdict()
            incomplete = SemanticVisualVerdict(
                verifier_id=incomplete.verifier_id,
                readable_text_absent=incomplete.readable_text_absent,
                platform_brand_absent=incomplete.platform_brand_absent,
                fake_entity_marks_absent=incomplete.fake_entity_marks_absent,
                single_scene=incomplete.single_scene,
                severe_defects_absent=incomplete.severe_defects_absent,
                subject_framing_valid=incomplete.subject_framing_valid,
                sport_geometry_alignment_valid=incomplete.sport_geometry_alignment_valid,
                exact_numbers_absent=incomplete.exact_numbers_absent,
                generated_sport_geometry_absent=None,
            )
            payload = FootballPitchSemanticReviewGate().review(
                selection_lock_path=str(lock),
                verdict=incomplete,
                output_dir=str(root / "out"),
            )
            self.assertFalse(payload["semantic_approved"])
            self.assertIn("generated_sport_geometry_absence_not_inspected", payload["semantic_failures"])

    def test_locked_png_tampering_is_rejected_before_semantic_claim(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock, locked = self._fixture(root)
            locked.write_bytes(b"tampered")
            with self.assertRaisesRegex(RuntimeError, "SHA256_MISMATCH"):
                FootballPitchSemanticReviewGate().review(
                    selection_lock_path=str(lock),
                    verdict=verdict(),
                    output_dir=str(root / "out"),
                )

    def test_downstream_gate_list_cannot_be_weakened(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            lock, _ = self._fixture(root)
            data = json.loads(lock.read_text(encoding="utf-8"))
            data["gates_not_waived"] = ["semantic_publication"]
            lock.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "DOWNSTREAM_GATES_NOT_PRESERVED"):
                FootballPitchSemanticReviewGate().review(
                    selection_lock_path=str(lock),
                    verdict=verdict(),
                    output_dir=str(root / "out"),
                )


if __name__ == "__main__":
    unittest.main()
