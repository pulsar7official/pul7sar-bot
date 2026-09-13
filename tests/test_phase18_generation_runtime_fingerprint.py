import unittest

from engine.intelligence.generation_runtime_fingerprint import (
    capture_generation_runtime_fingerprint,
    verify_matching_runtime_fingerprints,
)


class GenerationRuntimeFingerprintTests(unittest.TestCase):
    @staticmethod
    def _versions():
        values = {
            "transformers": "4.56.2",
            "Pillow": "11.3.0",
            "diffusers": "0.40.1",
            "accelerate": "1.10.1",
            "safetensors": "0.6.2",
            "huggingface_hub": "0.34.4",
            "tokenizers": "0.22.0",
        }
        return lambda name: values[name]

    @staticmethod
    def _torch():
        return {
            "torch_version": "2.8.0+cu128",
            "torch_cuda_version": "12.8",
            "cuda_available": True,
            "gpu_name": "NVIDIA Test GPU",
            "compute_capability": "8.0",
        }

    def _capture(self):
        return capture_generation_runtime_fingerprint(
            package_version_getter=self._versions(),
            torch_snapshot=self._torch(),
            python_version="3.13.7",
            machine="x86_64",
        )

    def test_same_runtime_has_same_fingerprint(self):
        before = self._capture()
        after = self._capture()
        self.assertEqual(
            verify_matching_runtime_fingerprints(before, after),
            before["runtime_fingerprint_sha256"],
        )
        self.assertFalse(before["generation_authorized"])
        self.assertFalse(before["publication_ready"])

    def test_dependency_drift_is_detected(self):
        before = self._capture()
        versions = self._versions()
        values = {name: versions(name) for name in (
            "transformers", "Pillow", "diffusers", "accelerate", "safetensors", "huggingface_hub", "tokenizers"
        )}
        values["tokenizers"] = "0.22.1"
        after = capture_generation_runtime_fingerprint(
            package_version_getter=lambda name: values[name],
            torch_snapshot=self._torch(),
            python_version="3.13.7",
            machine="x86_64",
        )
        with self.assertRaisesRegex(RuntimeError, "RUNTIME_CHANGED_DURING_FIRST_GOLDEN_RUN"):
            verify_matching_runtime_fingerprints(before, after)

    def test_exact_semantic_dependency_drift_is_rejected(self):
        versions = self._versions()
        with self.assertRaisesRegex(RuntimeError, "EXACT_VERSION_DRIFT:transformers"):
            capture_generation_runtime_fingerprint(
                package_version_getter=lambda name: "4.57.0" if name == "transformers" else versions(name),
                torch_snapshot=self._torch(),
            )

    def test_out_of_range_diffusers_is_rejected(self):
        versions = self._versions()
        with self.assertRaisesRegex(RuntimeError, "VERSION_OUT_OF_RANGE:diffusers"):
            capture_generation_runtime_fingerprint(
                package_version_getter=lambda name: "0.41.0" if name == "diffusers" else versions(name),
                torch_snapshot=self._torch(),
            )

    def test_cuda_absence_is_rejected(self):
        torch_data = self._torch()
        torch_data["cuda_available"] = False
        with self.assertRaisesRegex(RuntimeError, "CUDA_NOT_AVAILABLE"):
            capture_generation_runtime_fingerprint(
                package_version_getter=self._versions(),
                torch_snapshot=torch_data,
            )

    def test_authority_drift_is_rejected(self):
        before = self._capture()
        after = self._capture()
        after["publication_ready"] = True
        with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:publication_ready"):
            verify_matching_runtime_fingerprints(before, after)


if __name__ == "__main__":
    unittest.main()
