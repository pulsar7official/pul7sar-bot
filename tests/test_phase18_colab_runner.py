import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.phase18_colab_runner import (
    _assert_current_golden_contract,
    _attach_generation_provenance,
    _candidate,
    _proof_from_result,
    _result_matches_candidate,
)


class Phase18ColabRunnerTests(unittest.TestCase):
    def test_candidate_selection_uses_manifest_candidate_number(self):
        manifest = {"candidates": [{"candidate": 1, "seed": 7007001}, {"candidate": 2, "seed": 7007002}]}
        self.assertEqual(_candidate(manifest, 2)["seed"], 7007002)
        with self.assertRaisesRegex(ValueError, "not present"):
            _candidate(manifest, 3)

    def test_candidate_number_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            _candidate({"candidates": []}, 0)

    def test_current_v6_editorial_contract_is_required_before_gpu(self):
        current = {
            "manifest_version": "pul7sar-golden-batch-v6",
            "composition_grammar": "single_continuous_scene",
            "visual_grammar_surface_visibility": "context_only",
            "sport_geometry": "contextual_optional_not_required",
            "generated_sport_geometry_allowed": False,
            "partial_sport_geometry_allowed": False,
            "sport_geometry_integrity_policy": "exact_verified_or_visually_indeterminate",
            "partial_sport_geometry_hallucination_is_hard_failure": True,
            "hybrid_surface_replacement_required": False,
            "football_camera_preset": "editorial_environmental_oblique",
            "generated_branding_allowed": False,
            "brand_composition_policy": "dynamic_deterministic_after_generation",
            "visual_priority": "story_focal_hierarchy_before_sport_surface",
            "focal_anchor": "illuminated_tunnel_lower_left",
            "copy_negative_space": "right_center",
            "brand_quiet_zone": "upper_left",
        }
        _assert_current_golden_contract(current)
        for key, bad in (
            ("manifest_version", "pul7sar-golden-batch-v5"),
            ("composition_grammar", "multi_panel"),
            ("visual_grammar_surface_visibility", "partial_deterministic"),
            ("sport_geometry", "deterministic_football_pitch_projective_v1"),
            ("generated_sport_geometry_allowed", True),
            ("partial_sport_geometry_allowed", True),
            ("sport_geometry_integrity_policy", "best_effort"),
            ("partial_sport_geometry_hallucination_is_hard_failure", False),
            ("hybrid_surface_replacement_required", True),
            ("football_camera_preset", "high_wide_central"),
            ("generated_branding_allowed", True),
            ("brand_composition_policy", None),
            ("visual_priority", "sport_surface_before_story"),
            ("focal_anchor", "center_pitch"),
            ("copy_negative_space", "none"),
            ("brand_quiet_zone", "lower_right"),
        ):
            changed = dict(current); changed[key] = bad
            with self.assertRaisesRegex(RuntimeError, "COLAB_STALE_GOLDEN_CONTRACT"):
                _assert_current_golden_contract(changed)

    def test_result_reuse_requires_request_seed_model_sha_and_zero_cost(self):
        selected = {"request_id": "golden-season-opener-editorial-v6-001", "seed": 7007001, "model_id": "black-forest-labs/FLUX.2-klein-4B", "payload_sha256": "a" * 64}
        result = {"status": "REAL_VISUAL_PROOF_GENERATED", "request_id": "golden-season-opener-editorial-v6-001", "seed": 7007001, "model_id": "black-forest-labs/FLUX.2-klein-4B", "payload_sha256": "a" * 64, "cost_mode": "$0-local"}
        self.assertTrue(_result_matches_candidate(result, selected))
        for key, bad in (("request_id", "stale"), ("seed", 9), ("model_id", "other-model"), ("payload_sha256", "b" * 64), ("cost_mode", "paid")):
            changed = dict(result); changed[key] = bad
            self.assertFalse(_result_matches_candidate(changed, selected), key)

    def test_legacy_result_without_payload_sha_is_never_reused(self):
        selected = {"request_id": "golden-season-opener-editorial-v6-001", "seed": 7007001, "model_id": "black-forest-labs/FLUX.2-klein-4B", "payload_sha256": "a" * 64}
        legacy = {"status": "REAL_VISUAL_PROOF_GENERATED", "request_id": "golden-season-opener-editorial-v6-001", "seed": 7007001, "model_id": "black-forest-labs/FLUX.2-klein-4B", "cost_mode": "$0-local"}
        self.assertFalse(_result_matches_candidate(legacy, selected))

    def test_proof_result_requires_real_existing_png(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); png = root / "proof.png"; png.write_bytes(b"\x89PNG\r\n\x1a\nproof")
            self.assertEqual(_proof_from_result({"status": "REAL_VISUAL_PROOF_GENERATED", "png": "proof.png"}, root), png.resolve())

    def test_proof_result_rejects_non_success_status(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError, "REAL_VISUAL_PROOF_GENERATED"):
                _proof_from_result({"status": "FAILED", "png": "proof.png"}, Path(temp))

    def test_colab_acceptance_attaches_verified_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); png = root / "proof.png"; png.write_bytes(b"\x89PNG\r\n\x1a\nproof")
            payload = {"candidate": 1, "request_id": "golden-season-opener-editorial-v6-001", "seed": 7007001, "model_id": "black-forest-labs/FLUX.2-klein-4B", "payload_sha256": "a" * 64, "publication_ready": False}
            verified = {"status": "GENERATION_PROVENANCE_LOCK_VERIFIED", "base_png": str(png.resolve()), "base_png_sha256": "b" * 64, "executor_result": str(root / "result.json"), "executor_result_sha256": "c" * 64, "metadata": str(root / "metadata.json"), "metadata_sha256": "d" * 64, "resolved_dtype": "bfloat16", "cost_mode": "$0-local", "publication_ready": False}
            with patch("tools.phase18_colab_runner.GenerationProvenanceLock") as factory:
                factory.return_value.verify.return_value = verified
                accepted = _attach_generation_provenance(root=root, payload=payload, png=png)
            self.assertEqual(accepted["generation_provenance_status"], "GENERATION_PROVENANCE_LOCK_VERIFIED")
            self.assertEqual(accepted["base_png_sha256"], "b" * 64)
            self.assertEqual(accepted["provenance_resolved_dtype"], "bfloat16")
            self.assertEqual(accepted["provenance_cost_mode"], "$0-local")
            self.assertFalse(accepted["publication_ready"])

    def test_colab_acceptance_rejects_unverified_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); png = root / "proof.png"; png.write_bytes(b"\x89PNG\r\n\x1a\nproof")
            with patch("tools.phase18_colab_runner.GenerationProvenanceLock") as factory:
                factory.return_value.verify.return_value = {"status": "NOT_VERIFIED", "publication_ready": False}
                with self.assertRaisesRegex(RuntimeError, "COLAB_GENERATION_PROVENANCE_NOT_VERIFIED"):
                    _attach_generation_provenance(root=root, payload={"publication_ready": False}, png=png)

    def test_colab_acceptance_never_consumes_publication_ready_input(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); png = root / "proof.png"; png.write_bytes(b"\x89PNG\r\n\x1a\nproof")
            with self.assertRaisesRegex(RuntimeError, "COLAB_PROVENANCE_REQUIRES_UNPUBLISHED_INPUT"):
                _attach_generation_provenance(root=root, payload={"publication_ready": True}, png=png)


if __name__ == "__main__":
    unittest.main()
