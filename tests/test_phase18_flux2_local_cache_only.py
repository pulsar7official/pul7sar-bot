from __future__ import annotations

import unittest

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
)
from engine.intelligence.flux2_klein_diffusers import (
    Flux2KleinInferenceConfig,
    build_flux2_klein_pipeline_factory,
)


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

    def test_missing_local_snapshot_fails_closed_without_alternate_load(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
