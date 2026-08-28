from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.remote_renderer_local_candidate import (
    DECLARATION_SCHEMA,
    RemoteRendererExplicitLocalCandidateBuilder,
)


def _sha256_json(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


class RemoteRendererExplicitLocalCandidateTests(unittest.TestCase):
    def _docket(self, root: Path, *, renderer: str = "qwen-image-2512") -> tuple[Path, dict]:
        docket = {
            "schema": "pul7sar-phase18-remote-renderer-local-qualification-v1",
            "status": "REMOTE_RENDERER_LOCAL_QUALIFICATION_DOCKET_READY",
            "research_ledger": str((root / "research-ledger.json").resolve()),
            "research_ledger_file_sha256": "a" * 64,
            "research_ledger_sha256": "b" * 64,
            "renderer": renderer,
            "remote_space": "Qwen/Qwen-Image-2512" if renderer == "qwen-image-2512" else "black-forest-labs/FLUX.2-dev",
            "research_output": str((root / "research.png").resolve()),
            "research_output_sha256": "c" * 64,
            "research_output_bytes": 100,
            "research_average_score": 9.0,
            "research_scores": {
                "geometry_integrity": 9.0,
                "entity_neutrality": 9.2,
                "text_and_brand_cleanliness": 9.3,
            },
            "qualification_score_floor": 8.5,
            "critical_score_floors": {
                "geometry_integrity": 8.5,
                "entity_neutrality": 9.0,
                "text_and_brand_cleanliness": 9.0,
            },
            "research_signal_only": True,
            "recommended_for_local_measurement": True,
            "requires_explicit_local_model_candidate": True,
            "local_model_candidate_id": None,
            "local_runtime_qualified": False,
            "canonical_generation_authorized": False,
            "remote_pixels_reusable_as_canonical_evidence": False,
            "required_local_gates": ["explicit_local_model_candidate", "measured_$0-local_runtime_readiness"],
            "canonical_golden_eligible": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "remote_cost_mode": "$0-remote-zerogpu-study",
            "canonical_cost_mode_required": "$0-local",
        }
        docket["docket_sha256"] = _sha256_json(docket)
        path = root / "qualification-docket.json"
        path.write_text(json.dumps(docket), encoding="utf-8")
        return path, docket

    @staticmethod
    def _rewrite(path: Path, docket: dict) -> None:
        docket.pop("docket_sha256", None)
        docket["docket_sha256"] = _sha256_json(docket)
        path.write_text(json.dumps(docket), encoding="utf-8")

    def test_explicit_qwen_candidate_is_declared_but_not_runtime_qualified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _ = self._docket(root)
            declaration = RemoteRendererExplicitLocalCandidateBuilder(root).build(
                qualification_docket_path=path,
                local_model_candidate_id="local-qwen-image-2512",
            )
            self.assertEqual(declaration["schema"], DECLARATION_SCHEMA)
            self.assertEqual(declaration["remote_renderer"], "qwen-image-2512")
            self.assertEqual(declaration["local_model_id"], "Qwen/Qwen-Image-2512")
            self.assertTrue(declaration["exact_remote_model_match"])
            self.assertTrue(declaration["explicit_candidate_selection"])
            self.assertFalse(declaration["runtime_floor_proven"])
            self.assertTrue(declaration["pinned_model_revision_required"])
            self.assertIsNone(declaration["pinned_model_revision"])
            self.assertTrue(declaration["measured_runtime_readiness_required"])
            self.assertFalse(declaration["local_runtime_qualified"])
            self.assertFalse(declaration["local_generation_authorized"])
            self.assertFalse(declaration["research_pixels_reusable_as_canonical_evidence"])
            self.assertFalse(declaration["canonical_golden_eligible"])
            self.assertFalse(declaration["publication_ready"])
            self.assertEqual(declaration["canonical_cost_mode_required"], "$0-local")
            self.assertEqual(len(declaration["declaration_sha256"]), 64)

    def test_flux2_dev_has_no_exact_curated_local_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _ = self._docket(root, renderer="flux2-dev")
            with self.assertRaisesRegex(ValueError, "NO_EXACT_CURATED_LOCAL_MATCH"):
                RemoteRendererExplicitLocalCandidateBuilder(root).build(
                    qualification_docket_path=path,
                    local_model_candidate_id="local-flux2-klein-4b",
                )

    def test_wrong_local_model_cannot_be_substituted_for_qwen_research_leader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _ = self._docket(root)
            with self.assertRaisesRegex(ValueError, "EXACT_MODEL_MISMATCH"):
                RemoteRendererExplicitLocalCandidateBuilder(root).build(
                    qualification_docket_path=path,
                    local_model_candidate_id="local-flux2-klein-4b",
                )

    def test_unknown_local_candidate_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _ = self._docket(root)
            with self.assertRaisesRegex(ValueError, "NOT_CURATED"):
                RemoteRendererExplicitLocalCandidateBuilder(root).build(
                    qualification_docket_path=path,
                    local_model_candidate_id="local-unreviewed-model",
                )

    def test_explicit_candidate_id_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, _ = self._docket(root)
            with self.assertRaisesRegex(ValueError, "EXPLICIT_ID_REQUIRED"):
                RemoteRendererExplicitLocalCandidateBuilder(root).build(
                    qualification_docket_path=path,
                    local_model_candidate_id=" ",
                )

    def test_docket_authority_drift_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, docket = self._docket(root)
            docket["canonical_generation_authorized"] = True
            self._rewrite(path, docket)
            with self.assertRaisesRegex(ValueError, "DOCKET_AUTHORITY_FORBIDDEN"):
                RemoteRendererExplicitLocalCandidateBuilder(root).build(
                    qualification_docket_path=path,
                    local_model_candidate_id="local-qwen-image-2512",
                )

    def test_docket_digest_tampering_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, docket = self._docket(root)
            docket["research_average_score"] = 9.9
            path.write_text(json.dumps(docket), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DOCKET_SHA_MISMATCH"):
                RemoteRendererExplicitLocalCandidateBuilder(root).build(
                    qualification_docket_path=path,
                    local_model_candidate_id="local-qwen-image-2512",
                )

    def test_path_escape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            outside = Path(tmp) / "outside.json"
            outside.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "PATH_ESCAPE"):
                RemoteRendererExplicitLocalCandidateBuilder(root).build(
                    qualification_docket_path=outside,
                    local_model_candidate_id="local-qwen-image-2512",
                )


if __name__ == "__main__":
    unittest.main()
