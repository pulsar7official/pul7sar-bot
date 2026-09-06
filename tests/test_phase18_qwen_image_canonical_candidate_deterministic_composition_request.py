from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    MANIFEST_SCHEMA,
    build_deterministic_composition_request,
    verify_deterministic_composition_request,
)
from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import SCHEMA as CS268_SCHEMA


class DeterministicCompositionRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.candidate = self.repo / "candidate.png"
        self.candidate.write_bytes(b"\x89PNG\r\n\x1a\nphase18-candidate")
        self.brand = self.repo / "pul7sar-brand.png"
        self.brand.write_bytes(b"verified-brand-bytes")
        self.cs268_path = self.repo / "cs268.json"
        self.cs268_path.write_text("{}\n", encoding="utf-8")
        self.manifest_path = self.repo / "composition_manifest.json"
        self.story_sha = "1" * 64

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

    def _plan(self) -> list[dict[str, object]]:
        return [
            {
                "name": "atmosphere_base",
                "source": "generative",
                "purpose": "lighting and non-factual texture",
                "required": True,
            },
            {
                "name": "sport_surface_geometry",
                "source": "optional",
                "purpose": "not required by this story",
                "required": False,
            },
            {
                "name": "exact_entity_marks",
                "source": "verified_asset",
                "purpose": "official marks when required",
                "required": False,
            },
            {
                "name": "data_and_score",
                "source": "deterministic",
                "purpose": "exact numbers",
                "required": False,
            },
            {
                "name": "editorial_typography",
                "source": "deterministic",
                "purpose": "headline and supporting copy",
                "required": True,
            },
            {
                "name": "pul7sar_brand",
                "source": "verified_asset",
                "purpose": "exact approved brand",
                "required": True,
            },
        ]

    def _cs268(self) -> dict[str, object]:
        return {
            "schema": CS268_SCHEMA,
            "receipt_sha256": "a" * 64,
            "story_snapshot_sha256": self.story_sha,
            "candidate_png": self._candidate_binding(),
            "hybrid_layer_plan": self._plan(),
            "generated_layer_qa_approved": True,
            "composition_executed": False,
            "composed_visual_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _write_manifest(self, *, include_brand: bool = True, typography_source: str = "deterministic") -> None:
        layers: list[dict[str, object]] = [
            {"name": "atmosphere_base", "source": "generative"},
            {
                "name": "editorial_typography",
                "source": typography_source,
                "renderer_contract": "pul7sar-deterministic-typography-v1",
                "payload_sha256": "2" * 64,
            },
        ]
        if include_brand:
            layers.append(
                {
                    "name": "pul7sar_brand",
                    "source": "verified_asset",
                    "asset_file": self._binding(self.brand),
                }
            )
        manifest = {
            "schema": MANIFEST_SCHEMA,
            "story_snapshot_sha256": self.story_sha,
            "candidate_png": self._candidate_binding(),
            "layers": layers,
        }
        self.manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    def _patch_cs268(self):
        return patch(
            "engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request.verify_canonical_candidate_generated_layer_qa",
            return_value=self._cs268(),
        )

    def test_ready_request_binds_candidate_verified_asset_and_deterministic_contract(self) -> None:
        self._write_manifest()
        with self._patch_cs268():
            run = build_deterministic_composition_request(
                self.cs268_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
            receipt = verify_deterministic_composition_request(run.receipt_path, repo_root=self.repo)
        self.assertTrue(receipt["composition_request_ready"])
        self.assertFalse(receipt["composition_executed"])
        self.assertFalse(receipt["composed_visual_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])

    def test_missing_required_verified_brand_blocks_request(self) -> None:
        self._write_manifest(include_brand=False)
        with self._patch_cs268():
            run = build_deterministic_composition_request(
                self.cs268_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
        receipt = json.loads(run.receipt_path.read_text(encoding="utf-8"))
        self.assertFalse(receipt["composition_request_ready"])
        self.assertIn("missing_required_composition_layer:pul7sar_brand", receipt["blockers"])

    def test_layer_source_drift_is_rejected(self) -> None:
        self._write_manifest(typography_source="verified_asset")
        with self._patch_cs268():
            with self.assertRaisesRegex(ValueError, "LAYER_SOURCE_DRIFT"):
                build_deterministic_composition_request(
                    self.cs268_path, self.manifest_path, self.repo / "out", repo_root=self.repo
                )

    def test_candidate_byte_drift_invalidates_request(self) -> None:
        self._write_manifest()
        with self._patch_cs268():
            run = build_deterministic_composition_request(
                self.cs268_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
            self.candidate.write_bytes(self.candidate.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_deterministic_composition_request(run.receipt_path, repo_root=self.repo)

    def test_verified_asset_byte_drift_invalidates_request(self) -> None:
        self._write_manifest()
        with self._patch_cs268():
            run = build_deterministic_composition_request(
                self.cs268_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
            self.brand.write_bytes(self.brand.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_deterministic_composition_request(run.receipt_path, repo_root=self.repo)

    def test_cs268_byte_drift_invalidates_request(self) -> None:
        self._write_manifest()
        with self._patch_cs268():
            run = build_deterministic_composition_request(
                self.cs268_path, self.manifest_path, self.repo / "out", repo_root=self.repo
            )
            self.cs268_path.write_text('{"tampered":true}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_deterministic_composition_request(run.receipt_path, repo_root=self.repo)

    def test_existing_output_directory_is_rejected(self) -> None:
        self._write_manifest()
        out = self.repo / "out"
        out.mkdir()
        with self._patch_cs268():
            with self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
                build_deterministic_composition_request(
                    self.cs268_path, self.manifest_path, out, repo_root=self.repo
                )


if __name__ == "__main__":
    unittest.main()
