from __future__ import annotations

import ast
import inspect
import unittest

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
)
from engine.intelligence.flux2_klein_diffusers import (
    Flux2KleinInferenceConfig,
    build_flux2_klein_pipeline_factory,
)
from tools import phase18_prefetch_flux2
from tools.phase18_prefetch_flux2 import _require_cached_snapshot


class _FakeTorch:
    float16 = object()
    bfloat16 = object()
    float32 = object()


class _FakePipe:
    def __init__(self) -> None:
        self.sequential_enabled = False

    def enable_sequential_cpu_offload(self) -> None:
        self.sequential_enabled = True


class Flux2LocalCacheOnlyTests(unittest.TestCase):
    def test_pipeline_loader_is_revision_pinned_and_local_files_only(self) -> None:
        calls: list[tuple[str, dict[str, object]]] = []
        pipe = _FakePipe()

        def loader(model_id: str, **kwargs: object) -> _FakePipe:
            calls.append((model_id, dict(kwargs)))
            return pipe

        factory = build_flux2_klein_pipeline_factory(
            pipeline_loader=loader,
            torch_module=_FakeTorch(),
        )
        wrapper = factory(FLUX2_KLEIN_4B_MODEL_ID, "bfloat16")

        self.assertEqual(len(calls), 1)
        model_id, kwargs = calls[0]
        self.assertEqual(model_id, FLUX2_KLEIN_4B_MODEL_ID)
        self.assertEqual(kwargs["revision"], FLUX2_KLEIN_4B_REVISION)
        self.assertIs(kwargs["torch_dtype"], _FakeTorch.bfloat16)
        self.assertIs(kwargs["local_files_only"], True)
        self.assertTrue(pipe.sequential_enabled)
        self.assertEqual(wrapper._offload_mode, "sequential_cpu")

    def test_missing_local_pipeline_snapshot_fails_closed_without_alternate_load(self) -> None:
        calls: list[dict[str, object]] = []

        def loader(model_id: str, **kwargs: object) -> _FakePipe:
            calls.append(dict(kwargs))
            raise OSError("approved snapshot is not present in local cache")

        factory = build_flux2_klein_pipeline_factory(
            inference=Flux2KleinInferenceConfig(cpu_offload=False),
            pipeline_loader=loader,
            torch_module=_FakeTorch(),
        )

        with self.assertRaisesRegex(OSError, "local cache"):
            factory(FLUX2_KLEIN_4B_MODEL_ID, "bfloat16")

        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0]["local_files_only"], True)
        self.assertEqual(calls[0]["revision"], FLUX2_KLEIN_4B_REVISION)

    def test_unapproved_revision_remains_blocked_before_loader_call(self) -> None:
        called = False

        def loader(model_id: str, **kwargs: object) -> _FakePipe:
            nonlocal called
            called = True
            return _FakePipe()

        with self.assertRaisesRegex(ValueError, "approved immutable revision"):
            build_flux2_klein_pipeline_factory(
                pipeline_loader=loader,
                torch_module=_FakeTorch(),
                model_revision="0" * 40,
            )

        self.assertFalse(called)

    def test_cache_proof_is_revision_pinned_and_local_files_only(self) -> None:
        calls: list[dict[str, object]] = []

        def snapshot_download(**kwargs: object) -> str:
            calls.append(dict(kwargs))
            return "/cache/flux2-approved-snapshot"

        resolved = _require_cached_snapshot(
            snapshot_download,
            FLUX2_KLEIN_4B_MODEL_ID,
            FLUX2_KLEIN_4B_REVISION,
        )

        self.assertEqual(resolved, "/cache/flux2-approved-snapshot")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["repo_id"], FLUX2_KLEIN_4B_MODEL_ID)
        self.assertEqual(calls[0]["revision"], FLUX2_KLEIN_4B_REVISION)
        self.assertIs(calls[0]["local_files_only"], True)

    def test_missing_cache_proof_snapshot_fails_closed_without_network_fallback(self) -> None:
        calls: list[dict[str, object]] = []

        def snapshot_download(**kwargs: object) -> str:
            calls.append(dict(kwargs))
            raise OSError("snapshot missing from local cache")

        with self.assertRaisesRegex(RuntimeError, "FLUX2_APPROVED_LOCAL_SNAPSHOT_REQUIRED"):
            _require_cached_snapshot(
                snapshot_download,
                FLUX2_KLEIN_4B_MODEL_ID,
                FLUX2_KLEIN_4B_REVISION,
            )

        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0]["local_files_only"], True)
        self.assertEqual(calls[0]["revision"], FLUX2_KLEIN_4B_REVISION)

    def test_cache_proof_main_has_no_direct_snapshot_download_bypass(self) -> None:
        tree = ast.parse(inspect.getsource(phase18_prefetch_flux2.main))
        direct_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "snapshot_download"
        ]
        guarded_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_require_cached_snapshot"
        ]

        self.assertEqual(direct_calls, [])
        self.assertEqual(len(guarded_calls), 1)

    def test_cache_proof_zero_cost_receipt_is_explicitly_fail_closed(self) -> None:
        source = inspect.getsource(phase18_prefetch_flux2.main)
        self.assertIn('"downloaded_now": False', source)
        self.assertIn('"network_download_authorized": False', source)
        self.assertIn('"local_files_only": True', source)
        self.assertNotIn('"downloaded_now": downloaded', source)


if __name__ == "__main__":
    unittest.main()
