from pathlib import Path
import tempfile
import unittest

from engine.intelligence.approved_model_revisions import (
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_REVISION,
    assert_snapshot_revision,
    snapshot_revision_from_path,
)


class Phase18ApprovedModelRevisionCachePathTests(unittest.TestCase):
    def test_accepts_canonical_hugging_face_snapshot_cache_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "hub" / "models--Qwen--Qwen2.5-VL-3B-Instruct" / "snapshots" / QWEN25_VL_3B_REVISION
            self.assertEqual(snapshot_revision_from_path(path), QWEN25_VL_3B_REVISION)
            self.assertEqual(assert_snapshot_revision(path, QWEN25_VL_3B_REVISION), QWEN25_VL_3B_REVISION)

    def test_rejects_fabricated_snapshots_directory_even_with_approved_sha(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fabricated" / "snapshots" / FLUX2_KLEIN_4B_REVISION
            with self.assertRaisesRegex(RuntimeError, "canonical Hugging Face models--"):
                snapshot_revision_from_path(path)

    def test_rejects_empty_repository_component_in_cache_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "models--Qwen--" / "snapshots" / QWEN25_VL_3B_REVISION
            with self.assertRaisesRegex(RuntimeError, "canonical Hugging Face models--"):
                snapshot_revision_from_path(path)

    def test_still_rejects_revision_drift_inside_canonical_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "models--black-forest-labs--FLUX.2-klein-4B" / "snapshots" / QWEN25_VL_3B_REVISION
            with self.assertRaisesRegex(RuntimeError, "model snapshot revision drift"):
                assert_snapshot_revision(path, FLUX2_KLEIN_4B_REVISION)


if __name__ == "__main__":
    unittest.main()
