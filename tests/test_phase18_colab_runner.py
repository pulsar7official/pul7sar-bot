import tempfile
import unittest
from pathlib import Path

from tools.phase18_colab_runner import (
    _assert_current_golden_contract,
    _candidate,
    _proof_from_result,
    _result_matches_candidate,
)


class Phase18ColabRunnerTests(unittest.TestCase):
    def test_candidate_selection_uses_manifest_candidate_number(self):
        manifest = {
            "candidates": [
                {"candidate": 1, "seed": 7007001},
                {"candidate": 2, "seed": 7007002},
            ]
        }
        self.assertEqual(_candidate(manifest, 2)["seed"], 7007002)
        with self.assertRaisesRegex(ValueError, "not present"):
            _candidate(manifest, 3)

    def test_candidate_number_must_be_positive(self):
        with self.assertRaisesRegex(ValueError, "positive"):
            _candidate({"candidates": []}, 0)

    def test_current_v4_contract_is_required_before_gpu(self):
        current = {
            "manifest_version": "pul7sar-golden-batch-v4",
            "composition_grammar": "single_continuous_scene",
            "sport_geometry": "association_football_regulation_pitch",
            "generated_branding_allowed": False,
            "brand_composition_policy": "exact_assets_only_after_generation",
        }
        _assert_current_golden_contract(current)
        for key, bad in (
            ("manifest_version", "pul7sar-golden-batch-v2"),
            ("composition_grammar", "multi_panel"),
            ("sport_geometry", None),
            ("generated_branding_allowed", True),
            ("brand_composition_policy", None),
        ):
            changed = dict(current)
            changed[key] = bad
            with self.assertRaisesRegex(RuntimeError, "COLAB_STALE_GOLDEN_CONTRACT"):
                _assert_current_golden_contract(changed)

    def test_result_reuse_requires_request_seed_model_sha_and_zero_cost(self):
        selected = {
            "request_id": "golden-v4-001",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "payload_sha256": "a" * 64,
        }
        result = {
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "request_id": "golden-v4-001",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "payload_sha256": "a" * 64,
            "cost_mode": "$0-local",
        }
        self.assertTrue(_result_matches_candidate(result, selected))
        for key, bad in (
            ("request_id", "stale"),
            ("seed", 9),
            ("model_id", "other-model"),
            ("payload_sha256", "b" * 64),
            ("cost_mode", "paid"),
        ):
            changed = dict(result)
            changed[key] = bad
            self.assertFalse(_result_matches_candidate(changed, selected), key)

    def test_legacy_result_without_payload_sha_is_never_reused(self):
        selected = {
            "request_id": "golden-v4-001",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "payload_sha256": "a" * 64,
        }
        legacy = {
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "request_id": "golden-v4-001",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "cost_mode": "$0-local",
        }
        self.assertFalse(_result_matches_candidate(legacy, selected))

    def test_proof_result_requires_real_existing_png(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            png = root / "proof.png"
            png.write_bytes(b"\x89PNG\r\n\x1a\nproof")
            result = {"status": "REAL_VISUAL_PROOF_GENERATED", "png": "proof.png"}
            self.assertEqual(_proof_from_result(result, root), png.resolve())

    def test_proof_result_rejects_non_success_status(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(RuntimeError, "REAL_VISUAL_PROOF_GENERATED"):
                _proof_from_result({"status": "FAILED", "png": "proof.png"}, Path(temp))


if __name__ == "__main__":
    unittest.main()
