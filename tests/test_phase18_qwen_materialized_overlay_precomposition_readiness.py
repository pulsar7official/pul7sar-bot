from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_materialized_overlay_precomposition_readiness as cs335


SHA_A = "a" * 64
SHA_B = "b" * 64
CANDIDATE = {
    "repository_relative_path": "tmp/candidate.png",
    "sha256": SHA_B,
    "byte_size": 123,
}
BUNDLE = {
    "schema": cs335.CS334_SCHEMA,
    "status": "MATERIALIZED_OVERLAY_COMPOSITION_MANIFESTS_READY",
    "story_snapshot_sha256": SHA_A,
    "candidate_png": CANDIDATE,
    "composition_input_binding_ready": True,
    "composition_executed": False,
    "composed_visual_approved": False,
    "semantic_approved": False,
    "human_visual_review_approved": False,
    "golden_quality_approved": False,
    "genuine_golden_png_created": False,
    "publication_ready": False,
}


def gate_receipt(field: str) -> dict:
    value = {
        "story_snapshot_sha256": SHA_A,
        "candidate_png": CANDIDATE,
        "composition_executed": False,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        field: True,
    }
    return value


class Phase18MaterializedOverlayPrecompositionReadinessTests(unittest.TestCase):
    def test_build_chains_269_270_331_without_consuming_cs271(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_dir = root / "source"
            source_dir.mkdir()
            cs268 = source_dir / "cs268.json"
            bundle = source_dir / "bundle.json"
            composition = source_dir / "composition.json"
            payload = source_dir / "payload.json"
            for path in (cs268, bundle, composition, payload):
                path.write_text("{}\n", encoding="utf-8")
            output = root / "out"

            r269 = gate_receipt("composition_request_ready")
            r270 = gate_receipt("composition_execution_ready")
            r331 = gate_receipt("overlay_execution_ready")
            r269["receipt_sha256"] = "1" * 64
            r270["receipt_sha256"] = "2" * 64
            r331["receipt_sha256"] = "3" * 64
            r270["source_cs269_receipt"] = {"sha256": "9" * 64}
            r331["source_cs270_receipt"] = {"sha256": "8" * 64}

            def fake_build269(*args, **kwargs):
                out = args[2]
                out.mkdir()
                receipt = out / "deterministic_composition_request.json"
                receipt.write_text("269\n", encoding="utf-8")
                return type("Run", (), {"receipt_path": receipt, "composition_request_ready": True})()

            def fake_build270(*args, **kwargs):
                out = args[2]
                out.mkdir()
                receipt = out / "composition_execution_preflight.json"
                receipt.write_text("270\n", encoding="utf-8")
                return type("Run", (), {"receipt_path": receipt, "composition_execution_ready": True})()

            def fake_build331(*args, **kwargs):
                out = args[1]
                out.mkdir()
                receipt = out / "production_overlay_execution_readiness.json"
                receipt.write_text("331\n", encoding="utf-8")
                return type("Run", (), {"receipt_path": receipt, "overlay_execution_ready": True})()

            with (
                patch.object(cs335, "_load_cs334_bundle", return_value=(BUNDLE, composition, payload)),
                patch.object(cs335, "build_deterministic_composition_request", side_effect=fake_build269) as b269,
                patch.object(cs335, "verify_deterministic_composition_request", return_value=r269),
                patch.object(cs335, "build_composition_execution_preflight", side_effect=fake_build270) as b270,
                patch.object(cs335, "verify_composition_execution_preflight", return_value=r270),
                patch.object(cs335, "build_production_overlay_execution_readiness", side_effect=fake_build331) as b331,
                patch.object(cs335, "verify_production_overlay_execution_readiness", return_value=r331),
            ):
                run = cs335.build_materialized_overlay_precomposition_readiness(
                    cs268,
                    bundle,
                    output,
                    repo_root=root,
                )

            self.assertTrue(run.precomposition_execution_ready)
            receipt = cs335._read_json(run.receipt_path, "bad")
            self.assertTrue(receipt["precomposition_execution_ready"])
            self.assertFalse(receipt["cs271_attempt_consumed"])
            self.assertFalse(receipt["composition_executed"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])
            b269.assert_called_once()
            b270.assert_called_once()
            b331.assert_called_once()

    def test_lineage_drift_is_rejected_before_later_authority(self) -> None:
        drift = gate_receipt("composition_request_ready")
        drift["story_snapshot_sha256"] = "c" * 64
        with self.assertRaisesRegex(ValueError, "CS335_CS269_LINEAGE_DRIFT"):
            cs335._assert_same_lineage(drift, BUNDLE, "CS335_CS269")

    def test_premature_semantic_authority_is_rejected(self) -> None:
        bad = gate_receipt("composition_execution_ready")
        bad["semantic_approved"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:semantic_approved"):
            cs335._assert_same_lineage(bad, BUNDLE, "CS335_CS270")

    def test_source_contains_no_generation_composition_or_publication_side_effect(self) -> None:
        source = Path(cs335.__file__).read_text(encoding="utf-8")
        forbidden = (
            "QwenImagePipeline",
            ".from_pretrained(",
            "requests.",
            "httpx.",
            "urllib.",
            "compose_visual(",
            "execute_canonical_candidate_composition(",
            "publish(",
            "upload(",
            '"composition_executed": True',
            '"semantic_approved": True',
            '"genuine_golden_png_created": True',
            '"publication_ready": True',
        )
        for token in forbidden:
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
