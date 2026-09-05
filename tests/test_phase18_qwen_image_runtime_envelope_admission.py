from __future__ import annotations

import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_inference_measurement import (
    PROBE_OFFLOAD_MODE,
    QwenImageInferenceMeasurement,
    QwenImageInferenceObservation,
    sha256_file,
    sha256_json,
)
from engine.intelligence.qwen_image_runtime_envelope_admission import (
    build_runtime_envelope_admission,
    verify_runtime_envelope_admission,
    verify_single_inference_artifact,
)


class QwenImageRuntimeEnvelopeAdmissionTests(unittest.TestCase):
    def _fixture(self, root: Path) -> dict:
        png = root / "output" / "probe.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"engineering-probe-bytes")
        observation = QwenImageInferenceObservation(
            child_exit_code=0,
            inference_succeeded=True,
            pipeline_class="QwenImagePipeline",
            offload_mode=PROBE_OFFLOAD_MODE,
            torch_version="2.test",
            cuda_version="12.test",
            diffusers_version="0.test",
            gpu_name="test-gpu",
            native_bf16=True,
            gpu_total_vram_gb=24.0,
            gpu_free_vram_gb_before=20.0,
            gpu_free_vram_gb_after=18.0,
            max_cuda_allocated_gb=5.0,
            max_cuda_reserved_gb=6.0,
            process_max_rss_gb=10.0,
            elapsed_seconds=12.5,
            output_png_path=str(png),
            output_png_sha256=sha256_file(png),
            output_png_size_bytes=png.stat().st_size,
        )
        return QwenImageInferenceMeasurement(
            load_receipt_sha256="a" * 64,
            load_receipt_file_sha256="b" * 64,
            exact_snapshot_path=f"/cache/snapshots/{__import__('engine.intelligence.approved_model_revisions', fromlist=['QWEN_IMAGE_2512_REVISION']).QWEN_IMAGE_2512_REVISION}",
            observation=observation,
        ).as_receipt()

    def test_success_is_byte_bound_but_not_runtime_qualified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            evidence = verify_single_inference_artifact(receipt, repo_root=root)
            admission = build_runtime_envelope_admission(
                receipt,
                inference_receipt_file_sha256="c" * 64,
                repo_root=root,
            )
            self.assertEqual(evidence["png_sha256"], receipt["output_png_sha256"])
            self.assertTrue(admission["runtime_envelope_measurement_admitted"])
            self.assertFalse(admission["runtime_floor_proven"])
            self.assertFalse(admission["local_runtime_qualified"])
            self.assertFalse(admission["canonical_generation_authorized"])
            self.assertFalse(admission["golden_quality_approved"])
            self.assertFalse(admission["publication_ready"])
            self.assertEqual(verify_runtime_envelope_admission(admission), admission["admission_sha256"])

    def test_modified_png_is_rejected_even_when_receipt_digest_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            Path(receipt["output_png_path"]).write_bytes(b"\x89PNG\r\n\x1a\nchanged")
            with self.assertRaisesRegex(ValueError, "PNG_SIZE_MISMATCH|PNG_SHA_MISMATCH"):
                verify_single_inference_artifact(receipt, repo_root=root)

    def test_non_png_signature_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            path = Path(receipt["output_png_path"])
            path.write_bytes(b"not-a-png-engineering-probe")
            receipt["output_png_size_bytes"] = path.stat().st_size
            receipt["output_png_sha256"] = sha256_file(path)
            receipt["receipt_sha256"] = sha256_json({k: v for k, v in receipt.items() if k != "receipt_sha256"})
            with self.assertRaisesRegex(ValueError, "PNG_SIGNATURE_INVALID"):
                verify_single_inference_artifact(receipt, repo_root=root)

    def test_path_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            receipt = self._fixture(root)
            foreign = Path(outside) / "probe.png"
            foreign.write_bytes(Path(receipt["output_png_path"]).read_bytes())
            receipt["output_png_path"] = str(foreign)
            receipt["output_png_sha256"] = sha256_file(foreign)
            receipt["output_png_size_bytes"] = foreign.stat().st_size
            receipt["receipt_sha256"] = sha256_json({k: v for k, v in receipt.items() if k != "receipt_sha256"})
            with self.assertRaisesRegex(ValueError, "PATH_ESCAPE"):
                verify_single_inference_artifact(receipt, repo_root=root)

    def test_inconsistent_cuda_telemetry_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            receipt["max_cuda_allocated_gb"] = 7.0
            receipt["max_cuda_reserved_gb"] = 6.0
            receipt["receipt_sha256"] = sha256_json({k: v for k, v in receipt.items() if k != "receipt_sha256"})
            with self.assertRaisesRegex(ValueError, "CUDA_TELEMETRY_INCONSISTENT"):
                verify_single_inference_artifact(receipt, repo_root=root)

    def test_authority_drift_is_rejected_even_with_recomputed_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            admission = build_runtime_envelope_admission(
                receipt,
                inference_receipt_file_sha256="c" * 64,
                repo_root=root,
            )
            forged = copy.deepcopy(admission)
            forged["canonical_generation_authorized"] = True
            forged["admission_sha256"] = sha256_json({k: v for k, v in forged.items() if k != "admission_sha256"})
            with self.assertRaisesRegex(ValueError, "AUTHORITY_FORBIDDEN"):
                verify_runtime_envelope_admission(forged)


if __name__ == "__main__":
    unittest.main()
