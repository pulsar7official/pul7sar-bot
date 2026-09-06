import unittest
from types import SimpleNamespace

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_REVISION
from tools.phase18_flux2_execute import _verified_execution_metadata


class Flux2ActualOffloadProvenanceTests(unittest.TestCase):
    def _result(self, **metadata):
        return SimpleNamespace(metadata=metadata)

    def test_accepts_sequential_cpu_with_pinned_revision(self):
        mode, revision = _verified_execution_metadata(
            self._result(
                offload_mode="sequential_cpu",
                model_revision=FLUX2_KLEIN_4B_REVISION,
            )
        )
        self.assertEqual(mode, "sequential_cpu")
        self.assertEqual(revision, FLUX2_KLEIN_4B_REVISION)

    def test_accepts_model_cpu_when_runtime_actually_reports_it(self):
        mode, _ = _verified_execution_metadata(
            self._result(
                offload_mode="model_cpu",
                model_revision=FLUX2_KLEIN_4B_REVISION,
            )
        )
        self.assertEqual(mode, "model_cpu")

    def test_rejects_missing_or_unsafe_offload_mode(self):
        for mode in (None, "none", "cuda_only", ""):
            with self.subTest(mode=mode):
                with self.assertRaisesRegex(RuntimeError, "safe CPU offload mode"):
                    _verified_execution_metadata(
                        self._result(
                            offload_mode=mode,
                            model_revision=FLUX2_KLEIN_4B_REVISION,
                        )
                    )

    def test_rejects_model_revision_drift(self):
        with self.assertRaisesRegex(RuntimeError, "model revision drifted"):
            _verified_execution_metadata(
                self._result(
                    offload_mode="sequential_cpu",
                    model_revision="0" * 40,
                )
            )

    def test_rejects_missing_execution_metadata(self):
        with self.assertRaisesRegex(RuntimeError, "execution metadata is missing"):
            _verified_execution_metadata(SimpleNamespace(metadata=None))


if __name__ == "__main__":
    unittest.main()
