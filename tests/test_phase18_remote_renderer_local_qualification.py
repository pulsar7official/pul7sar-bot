from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.remote_renderer_local_qualification import (
    DOCKET_SCHEMA,
    QUALIFICATION_SCORE_FLOOR,
    RemoteRendererLocalQualificationDocketBuilder,
)


PNG = b"\x89PNG\r\n\x1a\n" + b"research-leader"


def _sha256_json(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class RemoteRendererLocalQualificationTests(unittest.TestCase):
    def _fixture(self, root: Path):
        output = root / "output" / "qwen.png"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(PNG)
        output_sha = hashlib.sha256(PNG).hexdigest()
        entry = {
            "renderer": "qwen-image-2512",
            "space": "Qwen/Qwen-Image-2512",
            "seed": 1902001,
            "prompt_sha256": "a" * 64,
            "output": str(output.resolve()),
            "output_sha256": output_sha,
            "output_bytes": len(PNG),
            "scores": {
                "editorial_composition": 8.8,
                "photorealism": 8.7,
                "geometry_integrity": 8.8,
                "scene_continuity": 8.6,
                "entity_neutrality": 9.2,
                "text_and_brand_cleanliness": 9.3,
            },
            "average_score": 8.9,
            "hard_blockers": {
                "broken_geometry": False,
                "pseudo_text": False,
                "identifiable_entity_cue": False,
                "multi_scene_or_collage": False,
                "generated_brand_or_crest": False,
            },
            "blocker_free": True,
            "research_score_floor": 8.0,
            "research_score_floor_met": True,
            "canonical_golden_eligible": False,
            "publication_ready": False,
        }
        ledger = {
            "schema": "pul7sar-phase18-remote-renderer-research-ledger-v1",
            "status": "REMOTE_RENDERER_RESEARCH_LEDGER_READY",
            "benchmark_report": str(root / "benchmark.json"),
            "benchmark_report_sha256": "b" * 64,
            "human_review": str(root / "review.json"),
            "human_review_sha256": "c" * 64,
            "prompt_sha256": "a" * 64,
            "entries": [entry],
            "research_leader": "qwen-image-2512",
            "research_leader_output_sha256": output_sha,
            "research_only": True,
            "canonical_admission_required": True,
            "canonical_golden_eligible": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "cost_mode": "$0-remote-zerogpu-study",
        }
        ledger["ledger_sha256"] = _sha256_json(ledger)
        path = root / "research-ledger.json"
        path.write_text(json.dumps(ledger), encoding="utf-8")
        return output, path, ledger

    @staticmethod
    def _rewrite(path: Path, ledger: dict) -> None:
        ledger.pop("ledger_sha256", None)
        ledger["ledger_sha256"] = _sha256_json(ledger)
        path.write_text(json.dumps(ledger), encoding="utf-8")

    def test_builds_non_authoritative_local_measurement_docket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, path, _ = self._fixture(root)
            docket = RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)
            self.assertEqual(docket["schema"], DOCKET_SCHEMA)
            self.assertEqual(docket["renderer"], "qwen-image-2512")
            self.assertEqual(docket["research_output"], str(output.resolve()))
            self.assertEqual(docket["research_output_bytes"], len(PNG))
            self.assertTrue(docket["recommended_for_local_measurement"])
            self.assertTrue(docket["requires_explicit_local_model_candidate"])
            self.assertIsNone(docket["local_model_candidate_id"])
            self.assertFalse(docket["local_runtime_qualified"])
            self.assertFalse(docket["canonical_generation_authorized"])
            self.assertFalse(docket["remote_pixels_reusable_as_canonical_evidence"])
            self.assertFalse(docket["canonical_golden_eligible"])
            self.assertFalse(docket["publication_ready"])
            self.assertEqual(docket["canonical_cost_mode_required"], "$0-local")
            self.assertEqual(docket["qualification_score_floor"], QUALIFICATION_SCORE_FLOOR)
            self.assertIn("measured_$0-local_runtime_readiness", docket["required_local_gates"])
            self.assertEqual(len(docket["docket_sha256"]), 64)

    def test_research_average_below_local_qualification_floor_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, path, ledger = self._fixture(root)
            ledger["entries"][0]["average_score"] = 8.49
            self._rewrite(path, ledger)
            with self.assertRaisesRegex(ValueError, "SCORE_BELOW_QUALIFICATION_FLOOR"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)

    def test_critical_geometry_floor_blocks_measurement_recommendation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, path, ledger = self._fixture(root)
            ledger["entries"][0]["scores"]["geometry_integrity"] = 8.4
            self._rewrite(path, ledger)
            with self.assertRaisesRegex(ValueError, "CRITICAL_SCORE_BELOW_FLOOR: geometry_integrity"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)

    def test_hard_blocker_is_replayed_not_trusted_from_blocker_free_boolean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, path, ledger = self._fixture(root)
            ledger["entries"][0]["hard_blockers"]["pseudo_text"] = True
            ledger["entries"][0]["blocker_free"] = True
            self._rewrite(path, ledger)
            with self.assertRaisesRegex(ValueError, "HARD_BLOCKER_PRESENT: pseudo_text"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)

    def test_remote_authority_drift_is_forbidden(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, path, ledger = self._fixture(root)
            ledger["canonical_golden_eligible"] = True
            self._rewrite(path, ledger)
            with self.assertRaisesRegex(ValueError, "REMOTE_AUTHORITY_FORBIDDEN"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)

    def test_ledger_digest_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, path, ledger = self._fixture(root)
            ledger["entries"][0]["average_score"] = 9.9
            path.write_text(json.dumps(ledger), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "LEDGER_SHA_MISMATCH"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)

    def test_research_png_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, path, _ = self._fixture(root)
            output.write_bytes(PNG + b"tamper")
            with self.assertRaisesRegex(ValueError, "LEADER_PNG_SHA_MISMATCH"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)

    def test_non_png_bytes_are_rejected_even_if_ledger_is_rehashed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output, path, ledger = self._fixture(root)
            payload = b"not-a-png"
            output.write_bytes(payload)
            ledger["entries"][0]["output_sha256"] = hashlib.sha256(payload).hexdigest()
            ledger["entries"][0]["output_bytes"] = len(payload)
            ledger["research_leader_output_sha256"] = ledger["entries"][0]["output_sha256"]
            self._rewrite(path, ledger)
            with self.assertRaisesRegex(ValueError, "LEADER_OUTPUT_NOT_PNG"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)

    def test_no_research_leader_cannot_create_docket(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, path, ledger = self._fixture(root)
            ledger["research_leader"] = None
            ledger["research_leader_output_sha256"] = None
            self._rewrite(path, ledger)
            with self.assertRaisesRegex(ValueError, "NO_RESEARCH_LEADER"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=path)

    def test_path_escape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            outside = Path(tmp) / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "PATH_ESCAPE"):
                RemoteRendererLocalQualificationDocketBuilder(root).build(research_ledger_path=outside)


if __name__ == "__main__":
    unittest.main()
