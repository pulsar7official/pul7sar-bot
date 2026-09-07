from __future__ import annotations

import hashlib
import json
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
SNAPSHOT_LINEAGE = {
    "snapshot_byte_inventory_verified": True,
    "snapshot_inventory_sha256": "e" * 64,
    "snapshot_file_count": 17,
    "snapshot_total_bytes": 987654,
    "model_revision": "approved-qwen-image-revision",
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

    def _upstream_values(
        self,
        root: Path,
        cs270_path: Path,
        cs271_path: Path,
        composed_binding: dict,
    ) -> tuple[dict, dict]:
        cs271_value = {
            "schema": cs336.CS271_SCHEMA,
            "story_snapshot_sha256": STORY_SHA,
            "candidate_png": CANDIDATE,
            "source_cs270_receipt": {**bind(cs270_path, root), "receipt_sha256": "1" * 64},
            "composed_candidate_png": composed_binding,
            "runner_id": cs336.RUNNER_ID,
            "receipt_sha256": "2" * 64,
            "composition_executed": True,
            **SNAPSHOT_LINEAGE,
            **downstream_false(),
        }
        cs272_value = {
            "schema": cs336.CS272_SCHEMA,
            "story_snapshot_sha256": STORY_SHA,
            "source_candidate_png": CANDIDATE,
            "source_cs271_receipt": {
                **bind(cs271_path, root),
                "receipt_sha256": cs271_value["receipt_sha256"],
            },
            "composed_candidate_png": composed_binding,
            "composition_executed": True,
            "composed_candidate_bytes_admitted_for_post_composition_qa": True,
            **SNAPSHOT_LINEAGE,
            **downstream_false(),
        }
        return cs271_value, cs272_value

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
            cs271_receipt_bytes = b"271\n"
            cs271_receipt_path = output / "cs271" / "one_shot_composition_execution.json"
            # Build the mocked upstream values from the exact bytes the fakes create.
            cs271_receipt_path.parent.mkdir(parents=True)
            cs271_receipt_path.write_bytes(cs271_receipt_bytes)
            cs271_value, cs272_value = self._upstream_values(
                root, cs270_path, cs271_receipt_path, composed_binding
            )
            cs271_receipt_path.unlink()
            cs271_receipt_path.parent.rmdir()

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
            for field, expected in SNAPSHOT_LINEAGE.items():
                self.assertEqual(receipt[field], expected)
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

    def test_unverified_snapshot_inventory_is_rejected(self) -> None:
        value = dict(SNAPSHOT_LINEAGE)
        value["snapshot_byte_inventory_verified"] = False
        with self.assertRaisesRegex(ValueError, "SNAPSHOT_INVENTORY_NOT_VERIFIED"):
            cs336._snapshot_lineage(value, "CS336")

    def test_snapshot_inventory_tamper_is_rejected(self) -> None:
        verified = dict(SNAPSHOT_LINEAGE)
        sealed = dict(SNAPSHOT_LINEAGE)
        sealed["snapshot_inventory_sha256"] = "f" * 64
        with self.assertRaisesRegex(
            ValueError,
            "SNAPSHOT_LINEAGE_DRIFT:snapshot_inventory_sha256",
        ):
            cs336._assert_snapshot_lineage_matches(sealed, verified, "CS336")

    def test_model_revision_tamper_is_rejected(self) -> None:
        verified = dict(SNAPSHOT_LINEAGE)
        sealed = dict(SNAPSHOT_LINEAGE)
        sealed["model_revision"] = "tampered-revision"
        with self.assertRaisesRegex(ValueError, "SNAPSHOT_LINEAGE_DRIFT:model_revision"):
            cs336._assert_snapshot_lineage_matches(sealed, verified, "CS336")

    def test_recomputed_outer_digest_does_not_hide_snapshot_tamper(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cs335_path, cs335_value, cs270_path, _ = self._fixture(root)
            evidence = root / "evidence"
            evidence.mkdir()
            cs271_path = evidence / "cs271.json"
            cs272_path = evidence / "cs272.json"
            composed_path = evidence / "composed.png"
            cs271_path.write_text("271\n", encoding="utf-8")
            cs272_path.write_text("272\n", encoding="utf-8")
            composed_path.write_bytes(b"png")
            composed_binding = {
                **bind(composed_path, root),
                "width": 4,
                "height": 4,
            }
            cs271_value, cs272_value = self._upstream_values(
                root, cs270_path, cs271_path, composed_binding
            )
            receipt = {
                "schema": cs336.SCHEMA,
                "status": "PRECOMPOSITION_ONE_SHOT_COMPOSED_BYTES_ADMITTED",
                "story_snapshot_sha256": STORY_SHA,
                **SNAPSHOT_LINEAGE,
                "candidate_png": CANDIDATE,
                "source_cs335_receipt": bind(cs335_path, root),
                "source_cs270_receipt": bind(cs270_path, root),
                "cs271_receipt": bind(cs271_path, root),
                "cs272_receipt": bind(cs272_path, root),
                "composed_candidate_png": composed_binding,
                "runner_id": cs336.RUNNER_ID,
                "precomposition_execution_ready": True,
                "cs271_attempt_consumed": True,
                "composition_executed": True,
                "composed_candidate_bytes_admitted_for_post_composition_qa": True,
                "composed_visual_approved": False,
                "semantic_approved": False,
                "human_visual_review_approved": False,
                "golden_quality_approved": False,
                "genuine_golden_png_created": False,
                "publication_ready": False,
                "authoritative": False,
                "policy": {},
            }
            receipt["snapshot_inventory_sha256"] = "f" * 64
            receipt["receipt_sha256"] = cs336.sha256_json(receipt)
            receipt_path = root / "cs336.json"
            receipt_path.write_text(
                json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            with (
                patch.object(cs336, "verify_materialized_overlay_precomposition_readiness", return_value=cs335_value),
                patch.object(cs336, "verify_one_shot_composition_execution", return_value=cs271_value),
                patch.object(cs336, "verify_composed_candidate_byte_admission", return_value=cs272_value),
            ):
                with self.assertRaisesRegex(
                    ValueError,
                    "SNAPSHOT_LINEAGE_DRIFT:snapshot_inventory_sha256",
                ):
                    cs336.verify_precomposition_to_composed_byte_admission(
                        receipt_path,
                        repo_root=root,
                    )

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
