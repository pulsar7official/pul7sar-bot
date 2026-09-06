from __future__ import annotations

from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    run_canonical_candidate_generated_layer_qa,
    verify_canonical_candidate_generated_layer_qa,
)
from engine.intelligence.qwen_image_canonical_candidate_identity_requirement import (
    SCHEMA as IDENTITY_REQUIREMENT_SCHEMA,
)
from engine.intelligence.qwen_image_canonical_candidate_pixel_identity_review_evidence import (
    SCHEMA as PIXEL_IDENTITY_EVIDENCE_SCHEMA,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json


class CanonicalCandidateGeneratedLayerQATests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.candidate = self.repo / "candidate.png"
        self.candidate.write_bytes(b"\x89PNG\r\n\x1a\nphase18-candidate")
        self.cs264_path = self.repo / "cs264.json"
        self.cs265_path = self.repo / "cs265.json"
        self.cs266_path = self.repo / "cs266.json"
        self.cs267_path = self.repo / "cs267.json"
        self.cs264_path.write_text("{}\n", encoding="utf-8")
        self.cs265_path.write_text("{}\n", encoding="utf-8")
        self.cs266_path.write_text("{}\n", encoding="utf-8")
        self.cs267_path.write_text("{}\n", encoding="utf-8")
        self.story_sha = "1" * 64
        self.inventory_sha = "9" * 64
        self.model_revision = "f" * 40

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _file_binding(self, path: Path) -> dict[str, object]:
        raw = path.read_bytes()
        return {
            "repository_relative_path": path.relative_to(self.repo).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "byte_size": len(raw),
        }

    def _candidate_binding(self) -> dict[str, object]:
        return {
            **self._file_binding(self.candidate),
            "width": 1024,
            "height": 1024,
        }

    def _snapshot_lineage(self) -> dict[str, object]:
        return {
            "snapshot_byte_inventory_verified": True,
            "snapshot_inventory_sha256": self.inventory_sha,
            "snapshot_file_count": 17,
            "snapshot_total_bytes": 123456789,
            "model_revision": self.model_revision,
        }

    def _cs264(
        self, *, generated_text: bool = False, unverified_identity: bool = False
    ) -> dict[str, object]:
        return {
            "schema": CANONICAL_CANDIDATE_SEMANTIC_BASE_QA_SCHEMA,
            "receipt_sha256": "a" * 64,
            "story_snapshot_sha256": self.story_sha,
            "candidate_png": self._candidate_binding(),
            **self._snapshot_lineage(),
            "semantic_base_scene_approved": True,
            "semantic_layer_evidence": {
                "complete": True,
                "blockers": [],
                "evidence": {
                    "generated_text_detected": generated_text,
                    "generated_platform_brand_detected": False,
                    "generated_exact_numbers_detected": False,
                    "generated_entity_mark_detected": False,
                    "generated_unverified_identity_detected": unverified_identity,
                    "generated_sport_geometry_detected": False,
                    "notes": [],
                },
            },
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _cs265(self, *, required: bool) -> dict[str, object]:
        return {
            "schema": IDENTITY_REQUIREMENT_SCHEMA,
            "receipt_sha256": "b" * 64,
            "story_snapshot_sha256": self.story_sha,
            "candidate_png": self._candidate_binding(),
            "source_cs264_receipt": {
                **self._file_binding(self.cs264_path),
                "receipt_sha256": "a" * 64,
            },
            "identity_requirement_classified": True,
            "pixel_identity_review_required": required,
            "identity_approved": False,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _cs266(self) -> dict[str, object]:
        return {
            "receipt_sha256": "d" * 64,
            "source_cs265_receipt": {
                **self._file_binding(self.cs265_path),
                "receipt_sha256": "b" * 64,
            },
        }

    def _cs267(self) -> dict[str, object]:
        return {
            "schema": PIXEL_IDENTITY_EVIDENCE_SCHEMA,
            "receipt_sha256": "c" * 64,
            "story_snapshot_sha256": self.story_sha,
            "candidate_png": self._candidate_binding(),
            "source_cs266_request": {
                **self._file_binding(self.cs266_path),
                "receipt_sha256": "d" * 64,
            },
            "pixel_identity_review_executed": True,
            "identity_approved": True,
            "semantic_approved": False,
            "human_visual_review_approved": False,
            "genuine_golden_png_created": False,
            "golden_quality_approved": False,
            "publication_ready": False,
        }

    def _patch(
        self,
        cs264: dict[str, object],
        cs265: dict[str, object],
        cs267: dict[str, object] | None = None,
    ) -> list[object]:
        patches: list[object] = [
            patch(
                "engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa.verify_canonical_candidate_semantic_base_qa",
                return_value=cs264,
            ),
            patch(
                "engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa.verify_identity_requirement",
                return_value=cs265,
            ),
        ]
        if cs267 is not None:
            patches.extend(
                (
                    patch(
                        "engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa.verify_pixel_identity_review_evidence",
                        return_value=cs267,
                    ),
                    patch(
                        "engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa.verify_pixel_identity_review_request",
                        return_value=self._cs266(),
                    ),
                )
            )
        return patches

    def _enter_patches(self, stack: ExitStack, patches: list[object]) -> None:
        for current in patches:
            stack.enter_context(current)

    def test_human_candidate_requires_and_uses_approved_identity_evidence(self) -> None:
        cs264, cs265, cs267 = self._cs264(), self._cs265(required=True), self._cs267()
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265, cs267))
            run = run_canonical_candidate_generated_layer_qa(
                self.cs264_path,
                self.cs265_path,
                self.repo / "out",
                repo_root=self.repo,
                cs267_receipt_path=self.cs267_path,
            )
            receipt = verify_canonical_candidate_generated_layer_qa(run.receipt_path, repo_root=self.repo)
        self.assertTrue(receipt["generated_layer_qa_approved"])
        self.assertTrue(receipt["identity_approved"])
        self.assertFalse(receipt["composition_executed"])
        self.assertFalse(receipt["semantic_approved"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        self.assertFalse(receipt["publication_ready"])

    def test_snapshot_lineage_is_preserved_from_fresh_cs264_replay(self) -> None:
        cs264, cs265 = self._cs264(), self._cs265(required=False)
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265))
            run = run_canonical_candidate_generated_layer_qa(
                self.cs264_path,
                self.cs265_path,
                self.repo / "out",
                repo_root=self.repo,
            )
            receipt = verify_canonical_candidate_generated_layer_qa(run.receipt_path, repo_root=self.repo)
        for field, expected in self._snapshot_lineage().items():
            self.assertEqual(receipt[field], expected)
        self.assertTrue(receipt["policy"]["generator_snapshot_lineage_preserved"])

    def test_missing_snapshot_inventory_proof_fails_closed(self) -> None:
        cs264, cs265 = self._cs264(), self._cs265(required=False)
        cs264["snapshot_byte_inventory_verified"] = False
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265))
            with self.assertRaisesRegex(ValueError, "SNAPSHOT_INVENTORY_UNVERIFIED"):
                run_canonical_candidate_generated_layer_qa(
                    self.cs264_path,
                    self.cs265_path,
                    self.repo / "out",
                    repo_root=self.repo,
                )

    def test_snapshot_lineage_tamper_fails_even_with_recomputed_outer_digest(self) -> None:
        cs264, cs265 = self._cs264(), self._cs265(required=False)
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265))
            run = run_canonical_candidate_generated_layer_qa(
                self.cs264_path,
                self.cs265_path,
                self.repo / "out",
                repo_root=self.repo,
            )
            receipt = json.loads(run.receipt_path.read_text(encoding="utf-8"))
            receipt["snapshot_inventory_sha256"] = "8" * 64
            unsigned = dict(receipt)
            unsigned.pop("receipt_sha256", None)
            receipt["receipt_sha256"] = sha256_json(unsigned)
            run.receipt_path.write_text(
                json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "SNAPSHOT_LINEAGE_DRIFT"):
                verify_canonical_candidate_generated_layer_qa(run.receipt_path, repo_root=self.repo)

    def test_human_candidate_fails_closed_without_identity_evidence(self) -> None:
        cs264, cs265 = self._cs264(), self._cs265(required=True)
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265))
            with self.assertRaisesRegex(ValueError, "PIXEL_IDENTITY_EVIDENCE_REQUIRED"):
                run_canonical_candidate_generated_layer_qa(
                    self.cs264_path,
                    self.cs265_path,
                    self.repo / "out",
                    repo_root=self.repo,
                )

    def test_non_human_candidate_can_pass_without_fabricating_identity_approval(self) -> None:
        cs264, cs265 = self._cs264(), self._cs265(required=False)
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265))
            run = run_canonical_candidate_generated_layer_qa(
                self.cs264_path,
                self.cs265_path,
                self.repo / "out",
                repo_root=self.repo,
            )
            receipt = verify_canonical_candidate_generated_layer_qa(run.receipt_path, repo_root=self.repo)
        self.assertTrue(receipt["generated_layer_qa_approved"])
        self.assertFalse(receipt["identity_approved"])
        self.assertIsNone(receipt["source_cs267_receipt"])

    def test_existing_hybrid_gate_rejects_generated_text_leakage(self) -> None:
        cs264, cs265 = self._cs264(generated_text=True), self._cs265(required=False)
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265))
            run = run_canonical_candidate_generated_layer_qa(
                self.cs264_path,
                self.cs265_path,
                self.repo / "out",
                repo_root=self.repo,
            )
        receipt = json.loads(run.receipt_path.read_text(encoding="utf-8"))
        self.assertFalse(receipt["generated_layer_qa_approved"])
        self.assertIn(
            "generated_text_leaked_into_deterministic_typography",
            receipt["hybrid_layer_gate"]["blockers"],
        )

    def test_upstream_unverified_identity_evidence_is_never_suppressed(self) -> None:
        cs264 = self._cs264(unverified_identity=True)
        cs265 = self._cs265(required=True)
        cs267 = self._cs267()
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265, cs267))
            run = run_canonical_candidate_generated_layer_qa(
                self.cs264_path,
                self.cs265_path,
                self.repo / "out",
                repo_root=self.repo,
                cs267_receipt_path=self.cs267_path,
            )
        receipt = json.loads(run.receipt_path.read_text(encoding="utf-8"))
        self.assertFalse(receipt["generated_layer_qa_approved"])
        self.assertTrue(receipt["layer_leakage_evidence"]["generated_unverified_identity_detected"])
        self.assertIn(
            "generated_identity_leaked_into_verified_identity_layer",
            receipt["hybrid_layer_gate"]["blockers"],
        )

    def test_candidate_byte_drift_invalidates_receipt(self) -> None:
        cs264, cs265 = self._cs264(), self._cs265(required=False)
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265))
            run = run_canonical_candidate_generated_layer_qa(
                self.cs264_path,
                self.cs265_path,
                self.repo / "out",
                repo_root=self.repo,
            )
            self.candidate.write_bytes(self.candidate.read_bytes() + b"tamper")
            with self.assertRaisesRegex(ValueError, "BYTE_DRIFT"):
                verify_canonical_candidate_generated_layer_qa(run.receipt_path, repo_root=self.repo)

    def test_existing_output_directory_is_rejected(self) -> None:
        out = self.repo / "out"
        out.mkdir()
        cs264, cs265 = self._cs264(), self._cs265(required=False)
        with ExitStack() as stack:
            self._enter_patches(stack, self._patch(cs264, cs265))
            with self.assertRaisesRegex(ValueError, "OUTPUT_INVALID"):
                run_canonical_candidate_generated_layer_qa(
                    self.cs264_path,
                    self.cs265_path,
                    out,
                    repo_root=self.repo,
                )


if __name__ == "__main__":
    unittest.main()
