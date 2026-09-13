from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_sealed_candidate_execution import (
    CANONICAL_HANDOFF_FILENAME,
    execute_and_seal_canonical_candidate,
)


class QwenImageSealedCandidateExecutionTests(unittest.TestCase):
    @staticmethod
    def _handoff_payload() -> dict:
        return {
            "genuine_canonical_inference_executed": True,
            "handoff_sealed": True,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        }

    def test_nonzero_inference_exit_is_propagated_without_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch(
                "engine.intelligence.qwen_image_sealed_candidate_execution.execute_manifest_bound_inference",
                return_value=19,
            ), patch(
                "engine.intelligence.qwen_image_sealed_candidate_execution.build_canonical_candidate_handoff"
            ) as build:
                code = execute_and_seal_canonical_candidate(
                    root / "launch.json", root / "runs/output", repo_root=root
                )
            self.assertEqual(code, 19)
            build.assert_not_called()

    def test_zero_exit_builds_and_replays_handoff_before_success(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "runs/output"
            output.mkdir(parents=True)
            payload = self._handoff_payload()
            with patch(
                "engine.intelligence.qwen_image_sealed_candidate_execution.execute_manifest_bound_inference",
                return_value=0,
            ), patch(
                "engine.intelligence.qwen_image_sealed_candidate_execution.build_canonical_candidate_handoff",
                return_value=payload,
            ) as build, patch(
                "engine.intelligence.qwen_image_sealed_candidate_execution.verify_canonical_candidate_handoff",
                return_value=payload,
            ) as verify:
                code = execute_and_seal_canonical_candidate(
                    root / "launch.json", output, repo_root=root
                )
            handoff = output / CANONICAL_HANDOFF_FILENAME
            self.assertEqual(code, 0)
            build.assert_called_once_with(output, handoff, repo_root=root.resolve())
            verify.assert_called_once_with(handoff, repo_root=root.resolve())

    def test_premature_downstream_authority_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "runs/output"
            output.mkdir(parents=True)
            payload = self._handoff_payload()
            payload["semantic_approved"] = True
            with patch(
                "engine.intelligence.qwen_image_sealed_candidate_execution.execute_manifest_bound_inference",
                return_value=0,
            ), patch(
                "engine.intelligence.qwen_image_sealed_candidate_execution.build_canonical_candidate_handoff",
                return_value=payload,
            ):
                with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:semantic_approved"):
                    execute_and_seal_canonical_candidate(
                        root / "launch.json", output, repo_root=root
                    )

    def test_existing_handoff_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "runs/output"
            output.mkdir(parents=True)
            (output / CANONICAL_HANDOFF_FILENAME).write_text("{}\n", encoding="utf-8")
            with patch(
                "engine.intelligence.qwen_image_sealed_candidate_execution.execute_manifest_bound_inference",
                return_value=0,
            ):
                with self.assertRaisesRegex(ValueError, "HANDOFF_ALREADY_EXISTS"):
                    execute_and_seal_canonical_candidate(
                        root / "launch.json", output, repo_root=root
                    )


if __name__ == "__main__":
    unittest.main()
