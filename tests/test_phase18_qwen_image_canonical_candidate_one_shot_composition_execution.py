from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import SCHEMA as CS270_SCHEMA
from engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution import (
    execute_one_shot_composition,
    verify_one_shot_composition_execution,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json


def _png(width: int, height: int, tail: bytes = b"") -> bytes:
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"\x08\x06\x00\x00\x00" + tail


class OneShotCompositionExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.preflight_path = self.repo / "cs270.json"
        self.preflight_path.write_text("{}\n", encoding="utf-8")
        self.candidate = self.repo / "candidate.png"
        self.candidate.write_bytes(_png(1024, 1024, b"candidate"))
        self.story_sha = "1" * 64
        self.snapshot_sha = "2" * 64
        self.model_revision = "qwen-image-test-revision"
        self._loaded_modules: list[str] = []
        self.runner_source, self.runner = self._make_runner(
            "runner",
            "compose",
            _png(1024, 1024, b"composed"),
        )

    def tearDown(self) -> None:
        for name in self._loaded_modules:
            sys.modules.pop(name, None)
        self.tmp.cleanup()

    def _make_runner(
        self,
        module_stem: str,
        entrypoint: str,
        output_bytes: bytes | None,
        *,
        raises: bool = False,
        lambda_runner: bool = False,
    ):
        path = self.repo / f"{module_stem}.py"
        if lambda_runner:
            source = (
                "from pathlib import Path\n"
                f"{entrypoint} = lambda preflight, output_path, repo_root: output_path.write_bytes({output_bytes!r})\n"
            )
        elif raises:
            source = (
                "from pathlib import Path\n"
                f"def {entrypoint}(preflight, output_path: Path, repo_root: Path) -> None:\n"
                "    del preflight, output_path, repo_root\n"
                "    raise RuntimeError('renderer failed')\n"
            )
        else:
            source = (
                "from pathlib import Path\n"
                f"def {entrypoint}(preflight, output_path: Path, repo_root: Path) -> None:\n"
                "    del preflight, repo_root\n"
                f"    output_path.write_bytes({output_bytes!r})\n"
            )
        path.write_text(source, encoding="utf-8")
        module_name = f"phase18_test_{module_stem}_{id(self)}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError("could not create test runner module")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        self._loaded_modules.append(module_name)
        spec.loader.exec_module(module)
        return path, getattr(module, entrypoint)

    def _binding(self, path: Path, **extra: object) -> dict[str, object]:
        raw = path.read_bytes()
        return {
            "repository_relative_path": path.relative_to(self.repo).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
            **extra,
        }

    def _preflight(self) -> dict[str, object]:
        return {
            "schema": CS270_SCHEMA,
            "receipt_sha256": "a" * 64,
            "story_snapshot_sha256": self.story_sha,
            "candidate_png": self._binding(self.candidate, width=1024, height=1024),
            "snapshot_byte_inventory_verified": True,
            "snapshot_inventory_sha256": self.snapshot_sha,
            "snapshot_file_count": 17,
            "snapshot_total_bytes": 123456,
            "model_revision": self.model_revision,
            "composition_execution_ready": True,
            "composition_executed": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _patch_preflight(self, value: dict[str, object] | None = None):
        return patch(
            "engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution.verify_composition_execution_preflight",
            return_value=self._preflight() if value is None else value,
        )

    def _execute(self):
        return execute_one_shot_composition(
            self.preflight_path,
            self.repo / "out",
            repo_root=self.repo,
            runner_source_path=self.runner_source,
            runner_id="test-project-native-runner-v1",
            compose_fn=self.runner,
        )

    def _rewrite_receipt(self, path: Path, mutate) -> None:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        mutate(receipt)
        receipt.pop("receipt_sha256", None)
        receipt["receipt_sha256"] = sha256_json(receipt)
        path.write_text(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    def test_executes_once_and_keeps_quality_authorities_closed(self) -> None:
        with self._patch_preflight():
            run = self._execute()
            receipt = verify_one_shot_composition_execution(run.receipt_path, repo_root=self.repo)
        self.assertTrue(receipt["composition_executed"])
        self.assertFalse(receipt["composed_visual_approved"])
        self.assertFalse(receipt["semantic_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        self.assertEqual(receipt["runner_entrypoint"], "compose")
        self.assertEqual(receipt["composed_candidate_png"]["width"], 1024)

    def test_snapshot_lineage_is_preserved_in_consumption_and_receipt(self) -> None:
        with self._patch_preflight():
            run = self._execute()
            receipt = verify_one_shot_composition_execution(run.receipt_path, repo_root=self.repo)
        consumption_path = self.repo / receipt["composition_attempt_consumption"]["repository_relative_path"]
        consumption = json.loads(consumption_path.read_text(encoding="utf-8"))
        for sealed in (receipt, consumption):
            self.assertIs(sealed["snapshot_byte_inventory_verified"], True)
            self.assertEqual(sealed["snapshot_inventory_sha256"], self.snapshot_sha)
            self.assertEqual(sealed["snapshot_file_count"], 17)
            self.assertEqual(sealed["snapshot_total_bytes"], 123456)
            self.assertEqual(sealed["model_revision"], self.model_revision)

    def test_unverified_upstream_snapshot_inventory_is_rejected_before_consumption(self) -> None:
        preflight = self._preflight()
        preflight["snapshot_byte_inventory_verified"] = False
        with self._patch_preflight(preflight):
            with self.assertRaisesRegex(ValueError, "SNAPSHOT_BYTE_INVENTORY_UNVERIFIED"):
                self._execute()
        self.assertFalse((self.repo / "out").exists())

    def test_snapshot_inventory_tampering_with_recomputed_outer_digest_is_rejected(self) -> None:
        with self._patch_preflight():
            run = self._execute()
            self._rewrite_receipt(run.receipt_path, lambda receipt: receipt.__setitem__("snapshot_inventory_sha256", "3" * 64))
            with self.assertRaisesRegex(ValueError, "SNAPSHOT_LINEAGE_DRIFT"):
                verify_one_shot_composition_execution(run.receipt_path, repo_root=self.repo)

    def test_generator_revision_tampering_with_recomputed_outer_digest_is_rejected(self) -> None:
        with self._patch_preflight():
            run = self._execute()
            self._rewrite_receipt(run.receipt_path, lambda receipt: receipt.__setitem__("model_revision", "tampered-generator-revision"))
            with self.assertRaisesRegex(ValueError, "SNAPSHOT_LINEAGE_DRIFT"):
                verify_one_shot_composition_execution(run.receipt_path, repo_root=self.repo)

    def test_failed_runner_still_consumes_attempt_with_snapshot_lineage(self) -> None:
        runner_source, fail_runner = self._make_runner("fail_runner", "compose", None, raises=True)
        out = self.repo / "out"
        with self._patch_preflight():
            with self.assertRaisesRegex(RuntimeError, "renderer failed"):
                execute_one_shot_composition(
                    self.preflight_path,
                    out,
                    repo_root=self.repo,
                    runner_source_path=runner_source,
                    runner_id="test-project-native-runner-v1",
                    compose_fn=fail_runner,
                )
        consumption_path = out / "composition_attempt_consumption.json"
        self.assertTrue(consumption_path.is_file())
        consumption = json.loads(consumption_path.read_text(encoding="utf-8"))
        self.assertEqual(consumption["snapshot_inventory_sha256"], self.snapshot_sha)
        self.assertEqual(consumption["model_revision"], self.model_revision)
        self.assertFalse((out / "one_shot_composition_execution.json").exists())

    def test_output_dimension_drift_is_rejected_after_consumption(self) -> None:
        runner_source, wrong_size = self._make_runner(
            "wrong_size_runner",
            "compose",
            _png(512, 512, b"wrong"),
        )
        out = self.repo / "out"
        with self._patch_preflight():
            with self.assertRaisesRegex(ValueError, "CANVAS_DIMENSION_DRIFT"):
                execute_one_shot_composition(
                    self.preflight_path,
                    out,
                    repo_root=self.repo,
                    runner_source_path=runner_source,
                    runner_id="test-project-native-runner-v1",
                    compose_fn=wrong_size,
                )
        self.assertTrue((out / "composition_attempt_consumption.json").is_file())

    def test_compose_callable_must_come_from_bound_runner_source(self) -> None:
        _, foreign_runner = self._make_runner(
            "foreign_runner",
            "compose",
            _png(1024, 1024, b"foreign"),
        )
        with self._patch_preflight():
            with self.assertRaisesRegex(ValueError, "COMPOSE_CALLABLE_SOURCE_MISMATCH"):
                execute_one_shot_composition(
                    self.preflight_path,
                    self.repo / "out",
                    repo_root=self.repo,
                    runner_source_path=self.runner_source,
                    runner_id="test-project-native-runner-v1",
                    compose_fn=foreign_runner,
                )
        self.assertFalse((self.repo / "out").exists())

    def test_compose_callable_must_be_top_level_named_function(self) -> None:
        runner_source, lambda_runner = self._make_runner(
            "lambda_runner",
            "compose",
            _png(1024, 1024, b"lambda"),
            lambda_runner=True,
        )
        with self._patch_preflight():
            with self.assertRaisesRegex(ValueError, "COMPOSE_ENTRYPOINT_NOT_TOP_LEVEL"):
                execute_one_shot_composition(
                    self.preflight_path,
                    self.repo / "out",
                    repo_root=self.repo,
                    runner_source_path=runner_source,
                    runner_id="test-project-native-runner-v1",
                    compose_fn=lambda_runner,
                )

    def test_composed_png_byte_drift_invalidates_receipt(self) -> None:
        with self._patch_preflight():
            run = self._execute()
            run.composed_png_path.write_bytes(run.composed_png_path.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_one_shot_composition_execution(run.receipt_path, repo_root=self.repo)

    def test_runner_source_byte_drift_invalidates_receipt(self) -> None:
        with self._patch_preflight():
            run = self._execute()
            self.runner_source.write_text("# changed runner\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_one_shot_composition_execution(run.receipt_path, repo_root=self.repo)

    def test_existing_output_directory_blocks_reuse(self) -> None:
        out = self.repo / "out"
        out.mkdir()
        with self._patch_preflight():
            with self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
                execute_one_shot_composition(
                    self.preflight_path,
                    out,
                    repo_root=self.repo,
                    runner_source_path=self.runner_source,
                    runner_id="test-project-native-runner-v1",
                    compose_fn=self.runner,
                )


if __name__ == "__main__":
    unittest.main()
