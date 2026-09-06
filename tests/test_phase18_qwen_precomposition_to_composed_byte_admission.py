from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence import qwen_image_precomposition_to_composed_byte_admission as cs336


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


class Phase18PrecompositionToComposedByteAdmissionTests(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, dict, Path, Path]:
        source = root / "source"
        source.mkdir()
        cs335_path = source / "cs335.json"
        cs270_path = source / "cs270.json"
        candidate_path = source / "candidate.png"
        cs335_path.write_text("cs335\n", encoding="utf-8")
        cs270_path.write_text("cs270\n", encoding="utf-8")
        candidate_path.write_bytes(b"candidate")
        cs270_binding = bind(cs270_path, root)
        cs335_value = {
            "schema": cs336.CS335_SCHEMA,
            "status": "MATERIALIZED_OVERLAY_PRECOMPOSITION_EXECUTION_READY",
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": CANDIDATE,
            "cs270_receipt": cs270_binding,
            "precomposition_execution_ready": True,
            "cs271_attempt_consumed": False,
            "composition_executed": False,
            "authoritative": False,
            **downstream_false(),
        }
        return cs335_path, cs335_value, cs270_path, candidate_path

    def test_build_executes_exactly_one_cs271_then_cs272_and_stops(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs335_path, cs335_value, cs270_path, _ = self._fixture(root)
            runner_source = root / "runner.py"
            runner_source.write_text("def compose_visual(*args):\n    pass\n", encoding="utf-8")
            output = root / "out"

            composed_binding = {
                "repository_relative_path": "out/cs271/composed_candidate.png",
                "sha256": "c" * 64,
                "byte_size": 77,
                "width": 4,
                "height": 4,
            }
            cs271_value = {
                "schema": cs336.CS271_SCHEMA,
                "story_snapshot_sha256": STORY_SHA,
                "candidate_png": CANDIDATE,
                "source_cs270_receipt": {**bind(cs270_path, root), "receipt_sha256": "1" * 64},
                "composed_candidate_png": composed_binding,
                "runner_id": cs336.RUNNER_ID,
                "receipt_sha256": "2" * 64,
                "composition_executed": True,
                **downstream_false(),
            }
            cs271_receipt_bytes = b"271\n"
            cs272_value = {
                "schema": cs336.CS272_SCHEMA,
                "story_snapshot_sha256": STORY_SHA,
                "source_candidate_png": CANDIDATE,
                "source_cs271_receipt": {
                    "repository_relative_path": "out/cs271/one_shot_composition_execution.json",
                    "sha256": hashlib.sha256(cs271_receipt_bytes).hexdigest(),
                    "byte_size": len(cs271_receipt_bytes),
                    "receipt_sha256": cs271_value["receipt_sha256"],
                },
                "composed_candidate_png": composed_binding,
                "composition_executed": True,
                "composed_candidate_bytes_admitted_for_post_composition_qa": True,
                **downstream_false(),
            }

            def fake_execute(*args, **kwargs):
                out = args[1]
                out.mkdir()
                receipt = out / "one_shot_composition_execution.json"
                receipt.write_bytes(cs271_receipt_bytes)
                composed = out / "composed_candidate.png"
                composed.write_bytes(b"png")
                return type("Run", (), {"receipt_path": receipt, "composed_png_path": composed})()

            def fake_admit(*args, **kwargs):
                out = args[1]
                out.mkdir()
                receipt = out / "composed_candidate_byte_admission_receipt.json"
                receipt.write_text("272\n", encoding="utf-8")
                return type("Run", (), {"receipt_path": receipt})()

            with (
                patch.object(cs336, "verify_materialized_overlay_precomposition_readiness", return_value=cs335_value),
                patch.object(cs336, "_runner_source_path", return_value=runner_source),
                patch.object(cs336, "execute_one_shot_composition", side_effect=fake_execute) as execute,
                patch.object(cs336, "verify_one_shot_composition_execution", return_value=cs271_value),
                patch.object(cs336, "admit_composed_candidate_bytes", side_effect=fake_admit) as admit,
                patch.object(cs336, "verify_composed_candidate_byte_admission", return_value=cs272_value),
            ):
                run = cs336.continue_precomposition_to_composed_byte_admission(
                    cs335_path,
                    output,
                    repo_root=root,
                )

            receipt = cs336._read_json(run.receipt_path, "bad")
            self.assertTrue(run.composed_candidate_bytes_admitted_for_post_composition_qa)
            self.assertTrue(receipt["cs271_attempt_consumed"])
            self.assertTrue(receipt["composition_executed"])
            self.assertTrue(receipt["composed_candidate_bytes_admitted_for_post_composition_qa"])
            self.assertFalse(receipt["composed_visual_approved"])
            self.assertFalse(receipt["semantic_approved"])
            self.assertFalse(receipt["human_visual_review_approved"])
            self.assertFalse(receipt["golden_quality_approved"])
            self.assertFalse(receipt["genuine_golden_png_created"])
            self.assertFalse(receipt["publication_ready"])
            self.assertFalse(receipt["authoritative"])
            execute.assert_called_once()
            admit.assert_called_once()

    def test_cs271_failure_is_not_retried_and_cs272_is_not_called(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs335_path, cs335_value, _, _ = self._fixture(root)
            runner_source = root / "runner.py"
            runner_source.write_text("def compose_visual(*args):\n    pass\n", encoding="utf-8")
            output = root / "out"
            with (
                patch.object(cs336, "verify_materialized_overlay_precomposition_readiness", return_value=cs335_value),
                patch.object(cs336, "_runner_source_path", return_value=runner_source),
                patch.object(cs336, "execute_one_shot_composition", side_effect=RuntimeError("render failed")) as execute,
                patch.object(cs336, "admit_composed_candidate_bytes") as admit,
            ):
                with self.assertRaisesRegex(RuntimeError, "render failed"):
                    cs336.continue_precomposition_to_composed_byte_admission(
                        cs335_path,
                        output,
                        repo_root=root,
                    )
            execute.assert_called_once()
            admit.assert_not_called()

    def test_lineage_drift_is_rejected(self) -> None:
        cs335_value = {
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": CANDIDATE,
            **downstream_false(),
        }
        cs271_value = {
            "story_snapshot_sha256": "d" * 64,
            "candidate_png": CANDIDATE,
            **downstream_false(),
        }
        with self.assertRaisesRegex(ValueError, "LINEAGE_DRIFT"):
            cs336._assert_same_lineage(cs271_value, cs335_value, "CS336_CS271")

    def test_premature_semantic_authority_is_rejected(self) -> None:
        value = {
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": CANDIDATE,
            **downstream_false(),
        }
        value["semantic_approved"] = True
        cs335_value = {
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": CANDIDATE,
        }
        with self.assertRaisesRegex(ValueError, "PREMATURE_AUTHORITY:semantic_approved"):
            cs336._assert_same_lineage(value, cs335_value, "CS336_CS271")

    def test_source_has_no_generation_network_retry_or_downstream_authority_shortcut(self) -> None:
        source = Path(cs336.__file__).read_text(encoding="utf-8")
        forbidden = (
            "QwenImagePipeline",
            ".from_pretrained(",
            "requests.",
            "httpx.",
            "urllib.",
            "for attempt in",
            "while True",
            "publish(",
            "upload(",
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
