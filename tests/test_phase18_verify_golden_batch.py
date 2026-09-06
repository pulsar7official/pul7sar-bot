import json
import tempfile
import unittest
from pathlib import Path

from tools.phase18_build_golden_batch import build_batch
from tools.phase18_verify_golden_batch import verify_batch


class VerifyGoldenBatchTests(unittest.TestCase):
    def test_real_builder_output_verifies_without_gpu(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, (7007001, 7007002))
            result = verify_batch(str(Path(temp) / "manifest.json"))
            self.assertEqual(result["status"], "GOLDEN_BATCH_INTEGRITY_VERIFIED")
            self.assertEqual(result["candidate_count"], 2)
            self.assertEqual(result["cost_mode"], "$0-local")

    def test_manifest_hash_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, (7007001,))
            path = Path(temp) / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["candidates"][0]["payload_sha256"] = "0" * 64
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                verify_batch(str(path))

    def test_unmanifested_candidate_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, (7007001,))
            (Path(temp) / "candidate-extra.json").write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "coverage mismatch"):
                verify_batch(str(Path(temp) / "manifest.json"))

    def test_manifest_seed_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            build_batch(temp, (7007001,))
            path = Path(temp) / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["candidates"][0]["seed"] = 999
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "seed mismatch"):
                verify_batch(str(path))


if __name__ == "__main__":
    unittest.main()
