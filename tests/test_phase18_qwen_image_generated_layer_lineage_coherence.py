from pathlib import Path
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_canonical_candidate_generated_layer_qa as qa


class CS306GeneratedLayerLineageCoherenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.binding = {
            "repository_relative_path": "runs/cs264/semantic.json",
            "sha256": "a" * 64,
            "byte_size": 123,
        }
        self.receipt = {"receipt_sha256": "b" * 64}

    def test_exact_receipt_binding_accepts_only_same_bound_receipt(self) -> None:
        qa._assert_exact_receipt_binding(
            {**self.binding, "receipt_sha256": "b" * 64},
            self.binding,
            self.receipt,
            "DRIFT",
        )

    def test_exact_receipt_binding_rejects_same_story_cross_run_substitution(self) -> None:
        substituted = {
            **self.binding,
            "repository_relative_path": "runs/other/semantic.json",
            "receipt_sha256": "b" * 64,
        }
        with self.assertRaisesRegex(ValueError, "DRIFT"):
            qa._assert_exact_receipt_binding(
                substituted,
                self.binding,
                self.receipt,
                "DRIFT",
            )

    def test_exact_receipt_binding_rejects_receipt_digest_substitution(self) -> None:
        substituted = {**self.binding, "receipt_sha256": "c" * 64}
        with self.assertRaisesRegex(ValueError, "DRIFT"):
            qa._assert_exact_receipt_binding(
                substituted,
                self.binding,
                self.receipt,
                "DRIFT",
            )

    def test_required_identity_lineage_rejects_cs266_bound_to_other_cs265(self) -> None:
        cs265_binding = {
            "repository_relative_path": "runs/cs265/identity.json",
            "sha256": "d" * 64,
            "byte_size": 456,
        }
        cs265 = {"receipt_sha256": "e" * 64}
        cs267 = {
            "source_cs266_request": {
                "repository_relative_path": "runs/cs266/request.json",
                "sha256": "f" * 64,
                "byte_size": 789,
                "receipt_sha256": "1" * 64,
            }
        }
        wrong_cs266 = {
            "receipt_sha256": "1" * 64,
            "source_cs265_receipt": {
                **cs265_binding,
                "repository_relative_path": "runs/other/identity.json",
                "receipt_sha256": "e" * 64,
            },
        }
        with patch.object(qa, "_reopen_binding", return_value=Path("/repo/runs/cs266/request.json")), patch.object(
            qa, "verify_pixel_identity_review_request", return_value=wrong_cs266
        ):
            with self.assertRaisesRegex(
                ValueError, "QWEN_GENERATED_LAYER_QA_CS265_CS267_LINEAGE_DRIFT"
            ):
                qa._verify_required_identity_lineage(
                    repo_root=Path("/repo"),
                    cs267=cs267,
                    cs265_binding=cs265_binding,
                    cs265=cs265,
                )

    def test_required_identity_lineage_accepts_exact_cs265_chain(self) -> None:
        cs265_binding = {
            "repository_relative_path": "runs/cs265/identity.json",
            "sha256": "d" * 64,
            "byte_size": 456,
        }
        cs265 = {"receipt_sha256": "e" * 64}
        cs267 = {
            "source_cs266_request": {
                "repository_relative_path": "runs/cs266/request.json",
                "sha256": "f" * 64,
                "byte_size": 789,
                "receipt_sha256": "1" * 64,
            }
        }
        cs266 = {
            "receipt_sha256": "1" * 64,
            "source_cs265_receipt": {**cs265_binding, "receipt_sha256": "e" * 64},
        }
        with patch.object(qa, "_reopen_binding", return_value=Path("/repo/runs/cs266/request.json")), patch.object(
            qa, "verify_pixel_identity_review_request", return_value=cs266
        ):
            qa._verify_required_identity_lineage(
                repo_root=Path("/repo"),
                cs267=cs267,
                cs265_binding=cs265_binding,
                cs265=cs265,
            )


if __name__ == "__main__":
    unittest.main()
