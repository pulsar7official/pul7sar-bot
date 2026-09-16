from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import tools.phase18_run_first_genuine_golden_v6_canonical_fresh as fresh


class CanonicalFreshWrapperTests(unittest.TestCase):
    def _paths(self, root: Path) -> dict[str, Path]:
        return {
            "output_path": root / "resource-lock.json",
            "receipt_path": root / "receipt.json",
            "attestation_path": root / "attestation.json",
            "summary_path": root / "summary.json",
            "handoff_path": root / "handoff.json",
            "attempt_contract_path": root / "attempt.json",
            "freshness_baseline_path": root / "baseline.json",
            "freshness_verification_path": root / "verification.json",
        }

    def _canonical(self, **overrides: object) -> dict[str, object]:
        payload: dict[str, object] = {
            "ready": True,
            "blockers": [],
            "canonical_generation_started": True,
            "canonical_png": "output/example.png",
            "canonical_png_sha256": "a" * 64,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        payload.update(overrides)
        return payload

    def _binding(self) -> dict[str, object]:
        return {
            "schema": "pul7sar-phase18-authoritative-first-golden-pre-generation-evidence-binding-v2",
            "authoritative_gate": False,
            "generation_authorized": False,
            "human_review_authorized": False,
            "golden_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }

    def test_baseline_precedes_canonical_and_fresh_replay_controls_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            events: list[str] = []

            def write_json(path: Path, payload: dict[str, object]) -> None:
                events.append(f"write:{Path(path).name}")

            def canonical(**kwargs: object) -> dict[str, object]:
                events.append("canonical")
                self.assertIn("write:baseline.json", events)
                return self._canonical()

            def verify(payload: dict[str, object]) -> dict[str, object]:
                events.append("verify")
                return {"fresh_attempt_evidence": True, "blockers": []}

            with (
                patch.object(fresh, "_inside_repository", side_effect=lambda path: Path(path)),
                patch.object(fresh, "_prove_binding_implementation_is_immutable"),
                patch.object(fresh, "bind_pre_generation_evidence", return_value=self._binding()),
                patch.object(fresh, "_write_json", side_effect=write_json),
                patch.object(fresh, "capture_freshness", return_value={"schema": "baseline"}),
                patch.object(fresh, "run_canonical", side_effect=canonical),
                patch.object(fresh, "verify_freshness", side_effect=verify),
            ):
                result = fresh.run(expected_commit="a" * 40, **paths)

            self.assertTrue(result["ready"])
            self.assertTrue(result["fresh_attempt_evidence"])
            self.assertEqual(result["blockers"], [])
            self.assertLess(events.index("write:baseline.json"), events.index("canonical"))
            self.assertLess(events.index("canonical"), events.index("verify"))
            self.assertIn("write:verification.json", events)

    def test_stale_evidence_rejects_otherwise_ready_canonical_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with (
                patch.object(fresh, "_inside_repository", side_effect=lambda path: Path(path)),
                patch.object(fresh, "_prove_binding_implementation_is_immutable"),
                patch.object(fresh, "bind_pre_generation_evidence", return_value=self._binding()),
                patch.object(fresh, "_write_json"),
                patch.object(fresh, "capture_freshness", return_value={"schema": "baseline"}),
                patch.object(fresh, "run_canonical", return_value=self._canonical()),
                patch.object(
                    fresh,
                    "verify_freshness",
                    return_value={
                        "fresh_attempt_evidence": False,
                        "blockers": ["FRESHNESS_POST_ARTIFACT_STALE_RESOURCE_LOCK"],
                    },
                ),
            ):
                result = fresh.run(expected_commit="b" * 40, **paths)

            self.assertFalse(result["ready"])
            self.assertIn("FRESHNESS_EVIDENCE_NOT_PROVEN", result["blockers"])
            self.assertIn(
                "FRESHNESS::FRESHNESS_POST_ARTIFACT_STALE_RESOURCE_LOCK",
                result["blockers"],
            )

    def test_canonical_failure_remains_fail_closed_even_with_fresh_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            with (
                patch.object(fresh, "_inside_repository", side_effect=lambda path: Path(path)),
                patch.object(fresh, "_prove_binding_implementation_is_immutable"),
                patch.object(fresh, "bind_pre_generation_evidence", return_value=self._binding()),
                patch.object(fresh, "_write_json"),
                patch.object(fresh, "capture_freshness", return_value={"schema": "baseline"}),
                patch.object(
                    fresh,
                    "run_canonical",
                    return_value=self._canonical(ready=False, blockers=["CANONICAL_OUTPUT_MISSING"]),
                ),
                patch.object(
                    fresh,
                    "verify_freshness",
                    return_value={"fresh_attempt_evidence": True, "blockers": []},
                ),
            ):
                result = fresh.run(expected_commit="c" * 40, **paths)

            self.assertFalse(result["ready"])
            self.assertIn("CANONICAL_OUTPUT_MISSING", result["blockers"])
            self.assertIn("CANONICAL_READY_FALSE", result["blockers"])

    def test_authority_drift_is_never_promoted_by_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            canonical = self._canonical(generation_authorized=True)
            with (
                patch.object(fresh, "_inside_repository", side_effect=lambda path: Path(path)),
                patch.object(fresh, "_prove_binding_implementation_is_immutable"),
                patch.object(fresh, "bind_pre_generation_evidence", return_value=self._binding()),
                patch.object(fresh, "_write_json"),
                patch.object(fresh, "capture_freshness", return_value={"schema": "baseline"}),
                patch.object(fresh, "run_canonical", return_value=canonical),
                patch.object(
                    fresh,
                    "verify_freshness",
                    return_value={"fresh_attempt_evidence": True, "blockers": []},
                ),
            ):
                result = fresh.run(expected_commit="d" * 40, **paths)

            self.assertFalse(result["ready"])
            self.assertFalse(result["generation_authorized"])
            self.assertFalse(result["publication_ready"])
            self.assertFalse(result["seeds_2_to_4_authorized"])
            self.assertIn("CANONICAL_AUTHORITY_DRIFT_GENERATION_AUTHORIZED", result["blockers"])

    def test_path_collision_fails_before_capture_or_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = self._paths(Path(tmp))
            paths["freshness_verification_path"] = paths["freshness_baseline_path"]
            with (
                patch.object(fresh, "_inside_repository", side_effect=lambda path: Path(path)),
                patch.object(fresh, "capture_freshness") as capture,
                patch.object(fresh, "run_canonical") as canonical,
            ):
                with self.assertRaisesRegex(RuntimeError, "OUTPUT_PATH_COLLISION"):
                    fresh.run(expected_commit="e" * 40, **paths)
            capture.assert_not_called()
            canonical.assert_not_called()


if __name__ == "__main__":
    unittest.main()
