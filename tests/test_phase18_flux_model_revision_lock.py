import tempfile
import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    assert_full_commit_sha,
    assert_snapshot_revision,
)
from engine.intelligence.flux2_klein_diffusers import build_flux2_klein_pipeline_factory


class _FakeTorch:
    float16 = "fp16"
    bfloat16 = "bf16"
    float32 = "fp32"


class _FakePipe:
    def __init__(self):
        self.sequential = False

    def enable_sequential_cpu_offload(self):
        self.sequential = True


class FluxModelRevisionLockTests(unittest.TestCase):
    def test_approved_revision_is_full_immutable_commit_sha(self):
        self.assertEqual(len(FLUX2_KLEIN_4B_REVISION), 40)
        self.assertEqual(assert_full_commit_sha(FLUX2_KLEIN_4B_REVISION), FLUX2_KLEIN_4B_REVISION)
        self.assertEqual(FLUX2_KLEIN_4B_MODEL_ID, "black-forest-labs/FLUX.2-klein-4B")

    def test_snapshot_path_must_resolve_to_exact_approved_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "models--black-forest-labs--FLUX.2-klein-4B" / "snapshots"
            approved = root / FLUX2_KLEIN_4B_REVISION
            approved.mkdir(parents=True)
            self.assertEqual(
                assert_snapshot_revision(approved, FLUX2_KLEIN_4B_REVISION),
                FLUX2_KLEIN_4B_REVISION,
            )
            drifted = root / ("0" * 40)
            drifted.mkdir()
            with self.assertRaisesRegex(RuntimeError, "revision drift"):
                assert_snapshot_revision(drifted, FLUX2_KLEIN_4B_REVISION)

    def test_noncanonical_or_short_snapshot_revision_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            noncanonical = Path(temp) / FLUX2_KLEIN_4B_REVISION
            noncanonical.mkdir()
            with self.assertRaisesRegex(RuntimeError, "canonical Hugging Face"):
                assert_snapshot_revision(noncanonical, FLUX2_KLEIN_4B_REVISION)
        with self.assertRaisesRegex(ValueError, "40-character"):
            assert_full_commit_sha("e7b7dc2")

    def test_diffusers_factory_passes_pinned_revision_to_loader(self):
        calls = []
        pipe = _FakePipe()

        def loader(model_id, **kwargs):
            calls.append((model_id, kwargs))
            return pipe

        factory = build_flux2_klein_pipeline_factory(
            pipeline_loader=loader,
            torch_module=_FakeTorch,
        )
        factory(FLUX2_KLEIN_4B_MODEL_ID, "bfloat16")
        self.assertTrue(pipe.sequential)
        self.assertEqual(calls[0][0], FLUX2_KLEIN_4B_MODEL_ID)
        self.assertEqual(calls[0][1]["revision"], FLUX2_KLEIN_4B_REVISION)
        self.assertEqual(calls[0][1]["torch_dtype"], "bf16")

    def test_prefetch_command_pins_same_revision_for_cache_and_download(self):
        text = Path("tools/phase18_prefetch_flux2.py").read_text(encoding="utf-8")
        self.assertIn("FLUX2_KLEIN_4B_REVISION", text)
        self.assertIn("revision=revision", text)
        self.assertIn("revision=FLUX2_KLEIN_4B_REVISION", text)
        self.assertIn('"schema": "pul7sar-phase18-model-cache-v2"', text)
        self.assertIn('"revision_pinned": True', text)
        self.assertIn("assert_snapshot_revision", text)


if __name__ == "__main__":
    unittest.main()
