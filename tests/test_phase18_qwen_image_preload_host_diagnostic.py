from __future__ import annotations

import unittest

from engine.intelligence.qwen_image_preload_host_diagnostic import (
    compare_preload_identity,
    non_authority_fields,
)


class QwenImagePreloadHostDiagnosticTests(unittest.TestCase):
    def test_reports_all_identity_drift(self) -> None:
        observed = {
            "gpu_name": "GPU-B",
            "gpu_total_vram_gb": 23.0,
            "torch_version": "2.9.0",
            "cuda_version": "12.8",
        }
        expected = {
            "gpu_name": "GPU-A",
            "gpu_total_vram_gb": 24.0,
            "torch_version": "2.8.0",
            "cuda_version": "12.6",
        }
        self.assertEqual(
            compare_preload_identity(observed, expected),
            [
                "identity_drift:cuda_version",
                "identity_drift:gpu_name",
                "identity_drift:gpu_total_vram_gb",
                "identity_drift:torch_version",
            ],
        )

    def test_accepts_equivalent_vram_observation(self) -> None:
        self.assertEqual(
            compare_preload_identity(
                {"gpu_total_vram_gb": 23.98}, {"gpu_total_vram_gb": 24.0}
            ),
            [],
        )

    def test_diagnostic_never_grants_downstream_authority(self) -> None:
        fields = non_authority_fields()
        self.assertTrue(fields)
        self.assertTrue(all(value is False for value in fields.values()))
        self.assertIn("genuine_golden_png_created", fields)
        self.assertIn("publication_ready", fields)


if __name__ == "__main__":
    unittest.main()
