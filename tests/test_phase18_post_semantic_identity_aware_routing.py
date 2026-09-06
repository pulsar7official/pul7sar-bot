import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    SCHEMA as GENERATED_LAYER_QA_SCHEMA,
)
from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    SCHEMA as IDENTITY_REQUIREMENT_SCHEMA,
)
from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_request import (
    SCHEMA as PIXEL_IDENTITY_REQUEST_SCHEMA,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
)
from tools.phase18_route_semantic_checkpoint_after_identity_requirement import (
    route_after_identity_requirement,
)


DOWNSTREAM_FALSE = {
    "semantic_approved": False,
    "human_visual_review_approved": False,
    "golden_quality_approved": False,
    "genuine_golden_png_created": False,
    "publication_ready": False,
}


class Phase18PostSemanticIdentityAwareRoutingTests(unittest.TestCase):
    def _upstream(self, review_required: bool):
        candidate = {
            "repository_relative_path": "output/canonical_candidate.png",
            "sha256": "a" * 64,
            "byte_size": 123,
        }
        cs304 = {
            "schema": CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
            "story_snapshot_sha256": "b" * 64,
            "candidate_png": candidate,
            "semantic_base_scene_approved": True,
            **DOWNSTREAM_FALSE,
        }
        cs305 = {
            "schema": IDENTITY_REQUIREMENT_SCHEMA,
            "story_snapshot_sha256": "b" * 64,
            "candidate_png": candidate,
            "identity_requirement_classified": True,
            "pixel_identity_review_required": review_required,
            "identity_approved": False,
            **DOWNSTREAM_FALSE,
        }
        return candidate, cs304, cs305

    def test_human_identity_path_creates_cs266_and_never_runs_cs268(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cs304_path = repo / "cs304.json"
            cs305_path = repo / "cs305.json"
            cs266_path = repo / "route/cs266-pixel-identity-review-request/request.json"
            candidate, cs304, cs305 = self._upstream(True)
            cs266 = {
                "schema": PIXEL_IDENTITY_REQUEST_SCHEMA,
                "story_snapshot_sha256": cs304["story_snapshot_sha256"],
                "candidate_png": candidate,
                "pixel_identity_review_required": True,
                "pixel_identity_review_request_created": True,
                "pixel_identity_review_executed": False,
                "identity_approved": False,
                **DOWNSTREAM_FALSE,
            }
            with (
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_canonical_candidate_semantic_base_qa",
                    return_value=cs304,
                ),
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_identity_requirement",
                    return_value=cs305,
                ),
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.build_pixel_identity_review_request",
                    return_value=SimpleNamespace(receipt_path=cs266_path),
                ) as build_request,
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_pixel_identity_review_request",
                    return_value=cs266,
                ),
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.run_canonical_candidate_generated_layer_qa"
                ) as run_generated,
            ):
                summary_path, accepted = route_after_identity_requirement(
                    cs304_path,
                    cs305_path,
                    repo / "route",
                    repo_root=repo,
                )
            self.assertTrue(accepted)
            build_request.assert_called_once()
            run_generated.assert_not_called()
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(
                summary["status"],
                "QWEN_IMAGE_CANONICAL_CANDIDATE_AWAITING_PIXEL_IDENTITY_REVIEW",
            )
            self.assertTrue(summary["pixel_identity_review_request_created"])
            self.assertFalse(summary["generated_layer_qa_executed"])
            self.assertFalse(summary["identity_approved"])
            for field in DOWNSTREAM_FALSE:
                self.assertFalse(summary[field])

    def test_nonhuman_path_runs_cs268_without_manufacturing_identity_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            cs304_path = repo / "cs304.json"
            cs305_path = repo / "cs305.json"
            cs268_path = repo / "route/cs268-generated-layer-qa/generated.json"
            candidate, cs304, cs305 = self._upstream(False)
            cs268 = {
                "schema": GENERATED_LAYER_QA_SCHEMA,
                "story_snapshot_sha256": cs304["story_snapshot_sha256"],
                "candidate_png": candidate,
                "pixel_identity_review_required": False,
                "identity_approved": False,
                "generated_layer_qa_approved": True,
                "composition_executed": False,
                "composed_visual_approved": False,
                **DOWNSTREAM_FALSE,
            }
            with (
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_canonical_candidate_semantic_base_qa",
                    return_value=cs304,
                ),
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_identity_requirement",
                    return_value=cs305,
                ),
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.build_pixel_identity_review_request"
                ) as build_request,
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.run_canonical_candidate_generated_layer_qa",
                    return_value=SimpleNamespace(receipt_path=cs268_path),
                ) as run_generated,
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_canonical_candidate_generated_layer_qa",
                    return_value=cs268,
                ),
            ):
                summary_path, accepted = route_after_identity_requirement(
                    cs304_path,
                    cs305_path,
                    repo / "route",
                    repo_root=repo,
                )
            self.assertTrue(accepted)
            build_request.assert_not_called()
            run_generated.assert_called_once()
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(
                summary["status"],
                "QWEN_IMAGE_CANONICAL_CANDIDATE_GENERATED_LAYER_QA_PASSED",
            )
            self.assertTrue(summary["generated_layer_qa_executed"])
            self.assertTrue(summary["generated_layer_qa_approved"])
            self.assertFalse(summary["identity_approved"])
            for field in DOWNSTREAM_FALSE:
                self.assertFalse(summary[field])

    def test_upstream_story_or_candidate_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _, cs304, cs305 = self._upstream(False)
            cs305 = dict(cs305)
            cs305["story_snapshot_sha256"] = "c" * 64
            with (
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_canonical_candidate_semantic_base_qa",
                    return_value=cs304,
                ),
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_identity_requirement",
                    return_value=cs305,
                ),
            ):
                with self.assertRaisesRegex(ValueError, "UPSTREAM_LINEAGE_DRIFT"):
                    route_after_identity_requirement(
                        repo / "cs304.json",
                        repo / "cs305.json",
                        repo / "route",
                        repo_root=repo,
                    )

    def test_premature_upstream_authority_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _, cs304, cs305 = self._upstream(False)
            cs305 = dict(cs305)
            cs305["publication_ready"] = True
            with (
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_canonical_candidate_semantic_base_qa",
                    return_value=cs304,
                ),
                patch(
                    "tools.phase18_route_semantic_checkpoint_after_identity_requirement.verify_identity_requirement",
                    return_value=cs305,
                ),
            ):
                with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:publication_ready"):
                    route_after_identity_requirement(
                        repo / "cs304.json",
                        repo / "cs305.json",
                        repo / "route",
                        repo_root=repo,
                    )


if __name__ == "__main__":
    unittest.main()
