import json
import tempfile
import unittest
from pathlib import Path

import tools.phase18_colab_first_genuine_golden as golden


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"pul7sar-golden"
PAYLOAD_SHA = "a" * 64
REQUEST_ID = "golden-season-opener-editorial-v6-001"
SEED = 7007001


class FirstGenuineGoldenTests(unittest.TestCase):
    def _fixtures(self, root: Path):
        png = root / "candidate-01.png"
        latest = root / "latest.json"
        semantic = root / "semantic.json"
        executor = root / "executor.json"
        metadata = root / "metadata.json"
        png.write_bytes(PNG_BYTES)

        metadata.write_text(json.dumps({
            "request_id": REQUEST_ID,
            "seed": SEED,
            "model": golden.FLUX2_KLEIN_4B_MODEL_ID,
            "model_revision": golden.FLUX2_KLEIN_4B_REVISION,
            "cost_mode": golden.EXPECTED_COST_MODE,
            "output_ref": str(png),
        }), encoding="utf-8")
        executor.write_text(json.dumps({
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "request_id": REQUEST_ID,
            "seed": SEED,
            "model_id": golden.FLUX2_KLEIN_4B_MODEL_ID,
            "payload_sha256": PAYLOAD_SHA,
            "cost_mode": golden.EXPECTED_COST_MODE,
            "resolved_dtype": golden.EXPECTED_DTYPE,
            "precision_quality_tier": golden.EXPECTED_PRECISION_TIER,
            "png": str(png),
            "metadata": str(metadata),
        }), encoding="utf-8")
        latest.write_text(json.dumps({
            "status": "COLAB_REAL_GOLDEN_EDITORIAL_GENERATED",
            "manifest_version": golden.EXPECTED_MANIFEST_VERSION,
            "benchmark": golden.EXPECTED_BENCHMARK,
            "candidate": 1,
            "publication_ready": False,
            "visual_grammar_surface_visibility": "context_only",
            "hybrid_surface_replacement_required": False,
            "focal_anchor": golden.EXPECTED_FOCAL_ANCHOR,
            "copy_negative_space": golden.EXPECTED_COPY_NEGATIVE_SPACE,
            "brand_quiet_zone": golden.EXPECTED_BRAND_QUIET_ZONE,
            "request_id": REQUEST_ID,
            "seed": SEED,
            "payload_sha256": PAYLOAD_SHA,
            "model_id": golden.FLUX2_KLEIN_4B_MODEL_ID,
            "generation_provenance_status": golden.EXPECTED_PROVENANCE_STATUS,
            "provenance_resolved_dtype": golden.EXPECTED_DTYPE,
            "provenance_precision_quality_tier": golden.EXPECTED_PRECISION_TIER,
            "provenance_cost_mode": golden.EXPECTED_COST_MODE,
            "executor_result": str(executor),
            "png": str(png),
        }), encoding="utf-8")
        semantic.write_text(json.dumps({
            "status": golden.EXPECTED_RECEIPT_STATUS,
            "candidate": 1,
            "publication_ready": False,
            "deterministic_pitch_applied": False,
            "pitch_replacement_required": False,
            "editorial_png": str(png),
            "semantic_runtime": {
                "ready": True,
                "model_id": golden.QWEN25_VL_3B_MODEL_ID,
                "cuda_available": True,
            },
            "semantic_visual_inspection": {
                "approved": True,
                "verifier_id": golden.EXPECTED_QWEN_BASE_VERIFIER_ID,
            },
            "base_scene_layer_gate": {"allowed": True, "inspection_complete": True},
        }), encoding="utf-8")
        return png, latest, semantic, executor, metadata

    def test_verified_candidate_stays_review_only_and_binds_provenance(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            png, latest, semantic, executor, metadata = self._fixtures(Path(temp))
            expected_sha = golden._sha256(png)
            expected_executor_sha = golden._sha256(executor)
            expected_metadata_sha = golden._sha256(metadata)
            expected_semantic_sha = golden._sha256(semantic)
            payload = golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)
        self.assertEqual(payload["schema"], "pul7sar-first-genuine-golden-staging-v3")
        self.assertEqual(payload["status"], "FIRST_GENUINE_GOLDEN_EDITORIAL_CANDIDATE_READY_FOR_HUMAN_REVIEW")
        self.assertEqual(payload["png_sha256"], expected_sha)
        self.assertEqual(payload["executor_result_sha256"], expected_executor_sha)
        self.assertEqual(payload["proof_metadata_sha256"], expected_metadata_sha)
        self.assertEqual(payload["semantic_receipt_sha256"], expected_semantic_sha)
        self.assertEqual(payload["model_id"], golden.FLUX2_KLEIN_4B_MODEL_ID)
        self.assertEqual(payload["model_revision"], golden.FLUX2_KLEIN_4B_REVISION)
        self.assertEqual(payload["semantic_model_id"], golden.QWEN25_VL_3B_MODEL_ID)
        self.assertEqual(payload["semantic_model_revision"], golden.QWEN25_VL_3B_REVISION)
        self.assertEqual(payload["semantic_verifier_id"], golden.EXPECTED_QWEN_BASE_VERIFIER_ID)
        self.assertTrue(payload["semantic_runtime_ready"])
        self.assertTrue(payload["semantic_cuda_available"])
        self.assertEqual(payload["cost_mode"], "$0-local")
        self.assertEqual(payload["resolved_dtype"], "bfloat16")
        self.assertEqual(payload["precision_quality_tier"], "golden_reference")
        self.assertEqual(payload["generation_provenance_status"], golden.EXPECTED_PROVENANCE_STATUS)
        self.assertTrue(payload["semantic_approved"])
        self.assertTrue(payload["layer_ownership_approved"])
        self.assertTrue(payload["human_visual_review_required"])
        self.assertFalse(payload["golden_quality_approved"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])
        self.assertFalse(payload["deterministic_pitch_applied"])

    def test_engineering_or_failed_semantic_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(semantic.read_text(encoding="utf-8"))
            payload["status"] = "GOLDEN_EDITORIAL_ENGINEERING_PROOF"
            payload["semantic_visual_inspection"] = {"approved": False}
            semantic.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_RECEIPT_NOT_APPROVED"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_semantic_runtime_identity_drift_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(semantic.read_text(encoding="utf-8"))
            payload["semantic_runtime"]["model_id"] = "other/semantic-model"
            semantic.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_MODEL_ID_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(semantic.read_text(encoding="utf-8"))
            payload["semantic_runtime"]["ready"] = False
            semantic.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_RUNTIME_NOT_READY"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(semantic.read_text(encoding="utf-8"))
            payload["semantic_runtime"]["cuda_available"] = False
            semantic.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_RUNTIME_CUDA_NOT_PROVEN"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_semantic_verifier_identity_drift_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(semantic.read_text(encoding="utf-8"))
            payload["semantic_visual_inspection"]["verifier_id"] = "qwen-unpinned:base_scene"
            semantic.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_VERIFIER_ID_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_composition_map_drift_is_rejected_before_review(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(latest.read_text(encoding="utf-8"))
            payload["focal_anchor"] = "center_pitch"
            latest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "COMPOSITION_MAP_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_pitch_replacement_regression_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(latest.read_text(encoding="utf-8"))
            payload["hybrid_surface_replacement_required"] = True
            latest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "MUST_NOT_REQUIRE_PITCH_REPLACEMENT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_png_path_drift_between_generation_and_semantic_receipt_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            root = Path(temp)
            _, latest, semantic, _, _ = self._fixtures(root)
            other = root / "other.png"
            other.write_bytes(PNG_BYTES + b"other")
            payload = json.loads(semantic.read_text(encoding="utf-8"))
            payload["editorial_png"] = str(other)
            semantic.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "PNG_PATH_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_t4_engineering_preview_provenance_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(latest.read_text(encoding="utf-8"))
            payload["generation_provenance_status"] = "GENERATION_PROVENANCE_ENGINEERING_PREVIEW_VERIFIED"
            payload["provenance_resolved_dtype"] = "float16"
            payload["provenance_precision_quality_tier"] = "t4_engineering_preview"
            latest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "PROVENANCE_STATUS_NOT_GOLDEN_REFERENCE"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_zero_cost_or_model_identity_drift_is_rejected_before_provenance_replay(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(latest.read_text(encoding="utf-8"))
            payload["provenance_cost_mode"] = "$paid"
            latest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "ZERO_COST_CONTRACT_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, _ = self._fixtures(Path(temp))
            payload = json.loads(latest.read_text(encoding="utf-8"))
            payload["model_id"] = "other/model"
            latest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "MODEL_ID_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_provenance_replay_detects_executor_or_revision_tampering(self):
        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, executor, _ = self._fixtures(Path(temp))
            result = json.loads(executor.read_text(encoding="utf-8"))
            result["cost_mode"] = "$paid"
            executor.write_text(json.dumps(result), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "COST_MODE_DRIFT"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

        with tempfile.TemporaryDirectory(dir=golden.ROOT) as temp:
            _, latest, semantic, _, metadata = self._fixtures(Path(temp))
            proof = json.loads(metadata.read_text(encoding="utf-8"))
            proof["model_revision"] = "b" * 40
            metadata.write_text(json.dumps(proof), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "MODEL_REVISION_MISMATCH"):
                golden.verify_genuine_candidate(latest_path=latest, semantic_receipt_path=semantic)

    def test_cli_source_forces_candidate_one_and_strict_semantic(self):
        source = Path(golden.__file__).read_text(encoding="utf-8")
        self.assertIn('"--candidate", "1"', source)
        self.assertIn('"--semantic-inspection", "qwen"', source)
        self.assertIn('"--strict-semantic"', source)
        self.assertNotIn('"--candidate", str(args.candidate)', source)


if __name__ == "__main__":
    unittest.main()