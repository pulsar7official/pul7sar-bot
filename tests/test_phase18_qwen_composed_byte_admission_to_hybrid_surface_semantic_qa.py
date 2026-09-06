from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_composed_byte_admission_to_hybrid_surface_semantic_qa as cs337


STORY_SHA = "a" * 64
CANDIDATE = {
    "repository_relative_path": "source/candidate.png",
    "sha256": "b" * 64,
    "byte_size": 123,
    "width": 4,
    "height": 4,
}


def bind(path: Path, root: Path) -> dict:
    raw = path.read_bytes()
    return {
        "repository_relative_path": path.resolve().relative_to(root.resolve()).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "byte_size": len(raw),
    }


def downstream_false() -> dict:
    return {
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }


class Phase18ComposedByteAdmissionToHybridSurfaceSemanticQATests(unittest.TestCase):
    def _fixture(self, root: Path, *, approved: bool = True):
        source = root / "source"
        source.mkdir()
        candidate_path = source / "candidate.png"
        composed_path = source / "composed.png"
        cs336_path = source / "cs336.json"
        cs272_path = source / "cs272.json"
        candidate_path.write_bytes(b"candidate")
        composed_path.write_bytes(b"composed")
        cs336_path.write_text("336\n", encoding="utf-8")
        cs272_path.write_text("272\n", encoding="utf-8")

        candidate = {**CANDIDATE, **bind(candidate_path, root)}
        composed = {**bind(composed_path, root), "width": 4, "height": 4}
        cs272_binding = bind(cs272_path, root)
        cs336 = {
            "schema": cs337.CS336_SCHEMA,
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": candidate,
            "composed_candidate_png": composed,
            "cs272_receipt": cs272_binding,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            "authoritative": False,
            **downstream_false(),
        }
        cs272 = {
            "schema": cs337.CS272_SCHEMA,
            "story_snapshot_sha256": STORY_SHA,
            "source_candidate_png": candidate,
            "composed_candidate_png": composed,
            "receipt_sha256": "d" * 64,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            **downstream_false(),
        }
        cs273 = {
            "schema": cs337.CS273_SCHEMA,
            "story_snapshot_sha256": STORY_SHA,
            "source_cs272_receipt": {
                **cs272_binding,
                "receipt_sha256": cs272["receipt_sha256"],
            },
            "composed_candidate_png": composed,
            "semantic_inspection_executed": True,
            "hybrid_surface_semantic_qa_approved": approved,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            **downstream_false(),
        }
        return cs336_path, cs272_path, cs336, cs272, cs273

    def _fake_run(self, root: Path):
        def run(*args, **kwargs):
            out = args[1]
            out.mkdir()
            receipt = out / "composed_candidate_hybrid_surface_semantic_qa.json"
            receipt.write_text("273\n", encoding="utf-8")
            return type("Run", (), {"receipt_path": receipt})()
        return run

    def test_pass_replays_exact_cs272_runs_cs273_and_stops_before_cs274(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs336_path, _, cs336, cs272, cs273 = self._fixture(root, approved=True)
            with (
                patch.object(cs337, "verify_precomposition_to_composed_byte_admission", return_value=cs336),
                patch.object(cs337, "verify_composed_candidate_byte_admission", return_value=cs272),
                patch.object(
                    cs337,
                    "run_composed_candidate_hybrid_surface_semantic_qa",
                    side_effect=self._fake_run(root),
                ) as run273,
                patch.object(
                    cs337,
                    "verify_composed_candidate_hybrid_surface_semantic_qa",
                    return_value=cs273,
                ),
            ):
                run = cs337.continue_composed_byte_admission_to_hybrid_surface_semantic_qa(
                    cs336_path, root / "out", repo_root=root, inspector=object()
                )

            receipt = cs337._read_json(run.receipt_path, "bad")
            self.assertTrue(run.hybrid_surface_semantic_qa_approved)
            self.assertEqual(receipt["status"], "HYBRID_SURFACE_SEMANTIC_QA_PASSED")
            self.assertTrue(receipt["semantic_inspection_executed"])
            self.assertFalse(receipt["visual_quality_review_requested"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])
            run273.assert_called_once()

    def test_semantic_rejection_is_preserved_without_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs336_path, _, cs336, cs272, cs273 = self._fixture(root, approved=False)
            with (
                patch.object(cs337, "verify_precomposition_to_composed_byte_admission", return_value=cs336),
                patch.object(cs337, "verify_composed_candidate_byte_admission", return_value=cs272),
                patch.object(
                    cs337,
                    "run_composed_candidate_hybrid_surface_semantic_qa",
                    side_effect=self._fake_run(root),
                ),
                patch.object(
                    cs337,
                    "verify_composed_candidate_hybrid_surface_semantic_qa",
                    return_value=cs273,
                ),
            ):
                run = cs337.continue_composed_byte_admission_to_hybrid_surface_semantic_qa(
                    cs336_path, root / "out", repo_root=root, inspector=object()
                )
            receipt = cs337._read_json(run.receipt_path, "bad")
            self.assertFalse(run.hybrid_surface_semantic_qa_approved)
            self.assertEqual(receipt["status"], "HYBRID_SURFACE_SEMANTIC_QA_REJECTED")
            self.assertFalse(receipt["visual_quality_review_requested"])
            self.assertFalse(receipt["composed_visual_approved"])
            self.assertFalse(receipt["semantic_approved"])

    def test_cross_story_cs272_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs336_path, _, cs336, cs272, _ = self._fixture(root)
            cs272["story_snapshot_sha256"] = "f" * 64
            with (
                patch.object(cs337, "verify_precomposition_to_composed_byte_admission", return_value=cs336),
                patch.object(cs337, "verify_composed_candidate_byte_admission", return_value=cs272),
            ):
                with self.assertRaisesRegex(ValueError, "CS272_LINEAGE_DRIFT"):
                    cs337.continue_composed_byte_admission_to_hybrid_surface_semantic_qa(
                        cs336_path, root / "out", repo_root=root, inspector=object()
                    )

    def test_cs273_must_bind_exact_cs336_selected_cs272(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs336_path, _, cs336, cs272, cs273 = self._fixture(root)
            cs273["source_cs272_receipt"]["sha256"] = "e" * 64
            with (
                patch.object(cs337, "verify_precomposition_to_composed_byte_admission", return_value=cs336),
                patch.object(cs337, "verify_composed_candidate_byte_admission", return_value=cs272),
                patch.object(
                    cs337,
                    "run_composed_candidate_hybrid_surface_semantic_qa",
                    side_effect=self._fake_run(root),
                ),
                patch.object(
                    cs337,
                    "verify_composed_candidate_hybrid_surface_semantic_qa",
                    return_value=cs273,
                ),
            ):
                with self.assertRaisesRegex(ValueError, "CS273_CS272_BINDING_DRIFT"):
                    cs337.continue_composed_byte_admission_to_hybrid_surface_semantic_qa(
                        cs336_path, root / "out", repo_root=root, inspector=object()
                    )

    def test_premature_global_semantic_authority_is_rejected(self) -> None:
        value = {
            "schema": cs337.CS273_SCHEMA,
            "semantic_inspection_executed": True,
            **downstream_false(),
        }
        value["semantic_approved"] = True
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:semantic_approved"):
            cs337._assert_downstream_closed(value, "CS337_CS273")

    def test_source_has_no_generation_composition_network_or_downstream_shortcut(self) -> None:
        source = Path(cs337.__file__).read_text(encoding="utf-8")
        forbidden = (
            "QwenImagePipeline",
            ".from_pretrained(",
            "execute_one_shot_composition(",
            "compose_visual(",
            "build_composed_candidate_visual_quality_review_request(",
            "requests.",
            "httpx.",
            "urllib.",
            "publish(",
            "upload(",
            '"visual_quality_review_requested": True',
            '"composed_visual_approved": True',
            '"semantic_approved": True',
            '"human_visual_review_approved": True',
            '"golden_quality_approved": True',
            '"genuine_golden_png_created": True',
            '"publication_ready": True',
        )
        for token in forbidden:
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
