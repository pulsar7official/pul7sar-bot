from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from phase18_verify_first_genuine_golden_v6_artifact import verify


class FirstGenuineGoldenV6ArtifactVerifierTests(unittest.TestCase):
    def _fixture(
        self,
        root: Path,
        *,
        archive_flattens_output: bool = False,
        recorded_png: str = "output/candidate.png",
    ) -> Path:
        png = root / ("candidate.png" if archive_flattens_output else "output/candidate.png")
        png.parent.mkdir(parents=True, exist_ok=True)
        png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"genuine-test-bytes")
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
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
            "png": recorded_png,
            "png_sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
            "png_bytes": png.stat().st_size,
        }
        receipt = root / "receipt.json"
        receipt.write_text(json.dumps(payload), encoding="utf-8")
        return receipt

    def test_accepts_bound_png_without_granting_downstream_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = verify(self._fixture(root), artifact_root=root)
            self.assertEqual(result["status"], "FIRST_GENUINE_GOLDEN_V6_ARTIFACT_REPLAY_VERIFIED")
            self.assertFalse(result["publication_ready"])
            self.assertFalse(result["golden_quality_approved"])

    def test_accepts_upload_artifact_lca_layout_with_runner_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            receipt = self._fixture(
                root,
                archive_flattens_output=True,
                recorded_png="/home/actions-runner/_work/pul7sar-bot/pul7sar-bot/output/candidate.png",
            )
            result = verify(receipt, artifact_root=root)
            self.assertEqual(Path(result["png"]), (root / "candidate.png").resolve())

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
