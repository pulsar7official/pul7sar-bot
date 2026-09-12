from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from phase18_verify_first_genuine_golden_v6_artifact import (
    EXPECTED_EVIDENCE,
    FLUX2_KLEIN_4B_MODEL_ID,
    FLUX2_KLEIN_4B_REVISION,
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
    verify,
)


def _runtime_payload() -> dict[str, object]:
    contract = {
        "schema": "pul7sar-generation-runtime-fingerprint-v1",
        "fixture": "stable",
        "cost_mode": "$0-local",
    }
    encoded = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    return {
        "schema": "pul7sar-generation-runtime-fingerprint-v1",
        "captured_at": "2026-09-11T00:00:00+00:00",
        "runtime_contract": contract,
        "runtime_fingerprint_sha256": digest,
        "generation_authorized": False,
        "queue_mutated": False,
        "png_created": False,
        "semantic_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "cost_mode": "$0-local",
    }


class FirstGenuineGoldenV6ArtifactVerifierTests(unittest.TestCase):
    def _evidence_payloads(self, png_sha: str) -> dict[str, dict[str, object]]:
        runtime = _runtime_payload()
        return {
            "gpu_host_qualification": {
                "eligible": True,
                "cuda_available": True,
                "bf16_supported": True,
                "cost_mode": "$0-local",
                "gpu_free_vram_gb": 24.0,
                "required_vram_gb": 16.0,
            },
            "host_memory_preflight": {"ready": True, "cost_mode": "$0-local"},
            "cache_budget": {
                "schema": "pul7sar-first-golden-cache-budget-v1",
                "branch": "phase18/story-intelligence",
                "cost_mode": "$0-local",
                "ready": True,
                "revisions_pinned": True,
                "qwen_model_id": QWEN25_VL_3B_MODEL_ID,
                "qwen_model_revision": QWEN25_VL_3B_REVISION,
                "flux_model_id": FLUX2_KLEIN_4B_MODEL_ID,
                "flux_model_revision": FLUX2_KLEIN_4B_REVISION,
                "downloads_performed": False,
                "generation_authorized": False,
                "queue_mutated": False,
                "png_created": False,
                "publication_ready": False,
            },
            "semantic_preflight": {
                "schema": "pul7sar-phase18-semantic-gpu-preflight-v2",
                "branch": "phase18/story-intelligence",
                "model_id": QWEN25_VL_3B_MODEL_ID,
                "model_revision": QWEN25_VL_3B_REVISION,
                "resolved_snapshot_revision": QWEN25_VL_3B_REVISION,
                "revision_pinned": True,
                "semantic_runtime_ready": True,
                "semantic_model_ready": True,
                "cuda_available": True,
                "cost_mode": "$0-local",
                "model_downloaded_now": False,
                "generation_authorized": False,
                "queue_mutated": False,
                "png_created": False,
                "publication_ready": False,
            },
            "qwen_model_cache": {
                "schema": "pul7sar-phase18-qwen-model-cache-v2",
                "ready": True,
                "model_id": QWEN25_VL_3B_MODEL_ID,
                "model_revision": QWEN25_VL_3B_REVISION,
                "resolved_snapshot_revision": QWEN25_VL_3B_REVISION,
                "revision_pinned": True,
                "cost_mode": "$0-local",
                "downloaded_now": False,
            },
            "flux_model_cache": {
                "schema": "pul7sar-phase18-model-cache-v2",
                "ready": True,
                "model_id": FLUX2_KLEIN_4B_MODEL_ID,
                "model_revision": FLUX2_KLEIN_4B_REVISION,
                "resolved_snapshot_revision": FLUX2_KLEIN_4B_REVISION,
                "revision_pinned": True,
                "cost_mode": "$0-local",
                "downloaded_now": False,
                "working_headroom_ready": True,
            },
            "local_only_model_receipts": {
                "schema": "pul7sar-phase18-local-only-model-receipt-verification-v1",
                "status": "PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED",
                "cost_mode": "$0-local",
                "network_download_authorized": False,
                "local_files_only": True,
                "qwen_model_id": QWEN25_VL_3B_MODEL_ID,
                "qwen_model_revision": QWEN25_VL_3B_REVISION,
                "flux_model_id": FLUX2_KLEIN_4B_MODEL_ID,
                "flux_model_revision": FLUX2_KLEIN_4B_REVISION,
                "generation_authorized": False,
                "publication_ready": False,
                "seeds_2_to_4_authorized": False,
            },
            "runtime_fingerprint_pre": dict(runtime),
            "runtime_fingerprint_post": dict(runtime),
            "strict_golden_staging": {
                "schema": "pul7sar-first-genuine-golden-staging-v3",
                "status": "FIRST_GENUINE_GOLDEN_EDITORIAL_CANDIDATE_READY_FOR_HUMAN_REVIEW",
                "candidate": 1,
                "cost_mode": "$0-local",
                "model_id": FLUX2_KLEIN_4B_MODEL_ID,
                "model_revision": FLUX2_KLEIN_4B_REVISION,
                "resolved_dtype": "bfloat16",
                "precision_quality_tier": "golden_reference",
                "semantic_model_id": QWEN25_VL_3B_MODEL_ID,
                "semantic_model_revision": QWEN25_VL_3B_REVISION,
                "semantic_approved": True,
                "layer_ownership_approved": True,
                "golden_quality_approved": False,
                "publication_ready": False,
                "seeds_2_to_4_authorized": False,
                "png_sha256": png_sha,
            },
        }

    def _fixture(
        self,
        root: Path,
        *,
        archive_flattens_output: bool = False,
        recorded_png: str = "output/candidate.png",
    ) -> Path:
        archive_prefix = root if archive_flattens_output else root / "output"
        png = archive_prefix / "candidate.png"
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"genuine-test-bytes")
        png_sha = hashlib.sha256(png.read_bytes()).hexdigest()

        evidence: dict[str, dict[str, object]] = {}
        for label, evidence_payload in self._evidence_payloads(png_sha).items():
            evidence_path = archive_prefix / "evidence" / f"{label}.json"
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text(json.dumps(evidence_payload, sort_keys=True), encoding="utf-8")
            data = evidence_path.read_bytes()
            evidence[label] = {
                "path": f"output/evidence/{label}.json",
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
            }
        self.assertEqual(set(evidence), EXPECTED_EVIDENCE)

        payload = {
            "schema": "pul7sar-first-genuine-golden-v6-resource-lock-v4",
            "status": "FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "native_bf16_proven": True,
            "gpu_eligible": True,
            "semantic_preflight_bound": True,
            "runtime_stable_across_generation": True,
            "runtime_fingerprint_sha256": _runtime_payload()["runtime_fingerprint_sha256"],
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
            "staging_receipt": "output/evidence/strict_golden_staging.json",
            "evidence": evidence,
            "png": recorded_png,
            "png_sha256": png_sha,
            "png_bytes": png.stat().st_size,
        }
        receipt = root / "receipt.json"
        receipt.write_text(json.dumps(payload), encoding="utf-8")
        return receipt

    def _rewrite_evidence(self, root: Path, receipt: Path, label: str, mutator) -> None:
        payload = json.loads(receipt.read_text(encoding="utf-8"))
        path = root / "output" / "evidence" / f"{label}.json"
        evidence_payload = json.loads(path.read_text(encoding="utf-8"))
        mutator(evidence_payload)
        path.write_text(json.dumps(evidence_payload, sort_keys=True), encoding="utf-8")
        data = path.read_bytes()
        payload["evidence"][label]["sha256"] = hashlib.sha256(data).hexdigest()
        payload["evidence"][label]["bytes"] = len(data)
        receipt.write_text(json.dumps(payload), encoding="utf-8")

    def test_accepts_bound_png_and_all_evidence_without_granting_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = verify(self._fixture(root), artifact_root=root)
            self.assertEqual(result["status"], "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_REPLAY_VERIFIED")
            self.assertEqual(result["evidence_files_verified"], 10)
            self.assertTrue(result["evidence_semantics_verified"])
            self.assertFalse(result["publication_ready"])
            self.assertFalse(result["golden_quality_approved"])

    def test_accepts_upload_artifact_lca_layout_with_runner_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root, archive_flattens_output=True, recorded_png="/home/actions-runner/_work/pul7sar-bot/pul7sar-bot/output/candidate.png")
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            for label, record in payload["evidence"].items():
                record["path"] = f"/home/actions-runner/_work/pul7sar-bot/pul7sar-bot/output/evidence/{label}.json"
            payload["staging_receipt"] = "/home/actions-runner/_work/pul7sar-bot/pul7sar-bot/output/evidence/strict_golden_staging.json"
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            result = verify(receipt, artifact_root=root)
            self.assertEqual(Path(result["png"]), (root / "candidate.png").resolve())

    def test_rejects_semantic_evidence_rewritten_with_matching_receipt_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            self._rewrite_evidence(root, receipt, "semantic_preflight", lambda payload: payload.__setitem__("model_downloaded_now", True))
            with self.assertRaisesRegex(RuntimeError, "SEMANTIC_ZERO_COST_DRIFT"):
                verify(receipt, artifact_root=root)

    def test_rejects_gpu_evidence_rewritten_with_matching_receipt_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            self._rewrite_evidence(root, receipt, "gpu_host_qualification", lambda payload: payload.__setitem__("bf16_supported", False))
            with self.assertRaisesRegex(RuntimeError, "GPU_BF16_UNPROVEN"):
                verify(receipt, artifact_root=root)

    def test_rejects_local_only_network_authority_rewritten_with_matching_receipt_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            self._rewrite_evidence(root, receipt, "local_only_model_receipts", lambda payload: payload.__setitem__("network_download_authorized", True))
            with self.assertRaisesRegex(RuntimeError, "LOCAL_ONLY_NETWORK_POLICY_DRIFT"):
                verify(receipt, artifact_root=root)

    def test_rejects_staging_authority_rewritten_with_matching_receipt_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            self._rewrite_evidence(root, receipt, "strict_golden_staging", lambda payload: payload.__setitem__("publication_ready", True))
            with self.assertRaisesRegex(RuntimeError, "EVIDENCE_AUTHORITY_DRIFT:strict_golden_staging:publication_ready"):
                verify(receipt, artifact_root=root)

    def test_rejects_png_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            (root / "output" / "candidate.png").write_bytes(b"\x89PNG\r\n\x1a\nchanged")
            with self.assertRaisesRegex(RuntimeError, "PNG_SHA_DRIFT"):
                verify(receipt, artifact_root=root)

    def test_rejects_png_byte_count_drift_even_with_matching_sha(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["png_bytes"] += 1
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "PNG_BYTE_COUNT_DRIFT"):
                verify(receipt, artifact_root=root)

    def test_rejects_evidence_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            evidence_path = root / "output" / "evidence" / "semantic_preflight.json"
            evidence_path.write_text('{"tampered":true}', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "EVIDENCE_BYTE_COUNT_DRIFT|EVIDENCE_SHA_DRIFT"):
                verify(receipt, artifact_root=root)

    def test_rejects_incomplete_evidence_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            del payload["evidence"]["runtime_fingerprint_post"]
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "EVIDENCE_SET_INCOMPLETE"):
                verify(receipt, artifact_root=root)

    def test_rejects_staging_receipt_binding_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            alternate = root / "output" / "alternate-staging.json"
            alternate.write_text("{}", encoding="utf-8")
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["staging_receipt"] = "output/alternate-staging.json"
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "STAGING_RECEIPT_BINDING_DRIFT"):
                verify(receipt, artifact_root=root)

    def test_rejects_illegal_publication_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "ILLEGAL_AUTHORITY:publication_ready"):
                verify(receipt, artifact_root=root)

    def test_rejects_non_output_rooted_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            payload["png"] = "/tmp/untrusted/candidate.png"
            receipt.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "PNG_PATH_NOT_OUTPUT_ROOTED"):
                verify(receipt, artifact_root=root)

    def test_rejects_ambiguous_rebased_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(root)
            duplicate = root / "candidate.png"
            duplicate.write_bytes((root / "output" / "candidate.png").read_bytes())
            with self.assertRaisesRegex(RuntimeError, "PNG_PATH_AMBIGUOUS"):
                verify(receipt, artifact_root=root)


if __name__ == "__main__":
    unittest.main()
