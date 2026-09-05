from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    PAYLOAD_MANIFEST_SCHEMA,
    build_composition_execution_preflight,
    verify_composition_execution_preflight,
)
from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import SCHEMA as CS269_SCHEMA


class CompositionExecutionPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.candidate = self.repo / "candidate.png"
        self.candidate.write_bytes(b"\x89PNG\r\n\x1a\nphase18-candidate")
        self.cs269_path = self.repo / "cs269.json"
        self.cs269_path.write_text("{}\n", encoding="utf-8")
        self.payload = self.repo / "typography_payload.json"
        self.payload.write_text('{"headline":"TRANSFER UPDATE"}\n', encoding="utf-8")
        self.manifest_path = self.repo / "payload_manifest.json"
        self.story_sha = "1" * 64
        self.payload_sha = hashlib.sha256(self.payload.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _binding(self, path: Path, **extra: object) -> dict[str, object]:
        raw = path.read_bytes()
        return {
            "repository_relative_path": path.relative_to(self.repo).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
            **extra,
        }

    def _candidate_binding(self) -> dict[str, object]:
        return self._binding(self.candidate, width=1024, height=1024)

    def _cs269(self) -> dict[str, object]:
        return {
            "schema": CS269_SCHEMA,
            "receipt_sha256": "a" * 64,
            "story_snapshot_sha256": self.story_sha,
            "candidate_png": self._candidate_binding(),
            "composition_layers": [
                {"name": "atmosphere_base", "source": "generative", "candidate_owned": True},
                {
                    "name": "editorial_typography",
                    "source": "deterministic",
                    "renderer_contract": "pul7sar-deterministic-typography-v1",
                    "payload_sha256": self.payload_sha,
                },
            ],
            "composition_request_ready": True,
            "composition_executed": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _write_manifest(self, *, include_payload: bool = True, contract: str = "pul7sar-deterministic-typography-v1") -> None:
        payloads: list[dict[str, object]] = []
        if include_payload:
            payloads.append(
                {
                    "name": "editorial_typography",
                    "renderer_contract": contract,
                    "payload_file": self._binding(self.payload),
                }
            )
        self.manifest_path.write_text(
            json.dumps(
                {
                    "schema": PAYLOAD_MANIFEST_SCHEMA,
                    "story_snapshot_sha256": self.story_sha,
                    "candidate_png_sha256": self._candidate_binding()["sha256"],
                    "deterministic_payloads": payloads,
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def _patch_cs269(self):
        return patch(
            "engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight.verify_deterministic_composition_request",
            return_value=self._cs269(),
        )

    def test_ready_preflight_materializes_payload_without_upgrading_authority(self) -> None:
        self._write_manifest()
        with self._patch_cs269():
            run = build_composition_execution_preflight(
                self.cs269_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
            receipt = verify_composition_execution_preflight(run.receipt_path, repo_root=self.repo)
        self.assertTrue(receipt["composition_execution_ready"])
        self.assertFalse(receipt["composition_executed"])
        self.assertFalse(receipt["composed_visual_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])
        self.assertEqual(receipt["deterministic_payloads"][0]["payload_sha256"], self.payload_sha)

    def test_missing_payload_blocks_preflight(self) -> None:
        self._write_manifest(include_payload=False)
        with self._patch_cs269():
            run = build_composition_execution_preflight(
                self.cs269_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
        receipt = json.loads(run.receipt_path.read_text(encoding="utf-8"))
        self.assertFalse(receipt["composition_execution_ready"])
        self.assertIn("missing_deterministic_payload_file:editorial_typography", receipt["blockers"])

    def test_renderer_contract_drift_is_rejected(self) -> None:
        self._write_manifest(contract="wrong-contract")
        with self._patch_cs269():
            with self.assertRaisesRegex(ValueError, "RENDERER_CONTRACT_DRIFT"):
                build_composition_execution_preflight(
                    self.cs269_path, self.manifest_path, self.repo / "out", repo_root=self.repo
                )

    def test_payload_digest_drift_is_rejected(self) -> None:
        self._write_manifest()
        self.payload.write_text('{"headline":"TAMPERED"}\n', encoding="utf-8")
        with self._patch_cs269():
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT|PAYLOAD_DIGEST_DRIFT"):
                build_composition_execution_preflight(
                    self.cs269_path, self.manifest_path, self.repo / "out", repo_root=self.repo
                )

    def test_payload_byte_drift_invalidates_existing_receipt(self) -> None:
        self._write_manifest()
        with self._patch_cs269():
            run = build_composition_execution_preflight(
                self.cs269_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
            self.payload.write_bytes(self.payload.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composition_execution_preflight(run.receipt_path, repo_root=self.repo)

    def test_candidate_byte_drift_invalidates_existing_receipt(self) -> None:
        self._write_manifest()
        with self._patch_cs269():
            run = build_composition_execution_preflight(
                self.cs269_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
            self.candidate.write_bytes(self.candidate.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_composition_execution_preflight(run.receipt_path, repo_root=self.repo)

    def test_existing_output_directory_is_rejected(self) -> None:
        self._write_manifest()
        out = self.repo / "out"
        out.mkdir()
        with self._patch_cs269():
            with self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
                build_composition_execution_preflight(
                    self.cs269_path, self.manifest_path, out, repo_root=self.repo
                )


if __name__ == "__main__":
    unittest.main()
