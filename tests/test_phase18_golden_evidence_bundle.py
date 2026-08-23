import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.golden_evidence_bundle import build_golden_evidence_manifest


class GoldenEvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "output").mkdir()
        self.png = self.root / "output" / "candidate.png"
        self.png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"real-image-bytes")
        self.result = self.root / "output" / "first-png-result.json"
        self.result.write_text(json.dumps({
            "status": "FIRST_REAL_GOLDEN_PNG_GENERATED",
            "png": "output/candidate.png",
            "job_id": "job-1",
            "request_id": "request-1",
            "payload_sha256": "abc123",
            "publication_ready": False,
        }), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_builds_manifest_with_hashes_and_keeps_publication_gated(self):
        manifest = build_golden_evidence_manifest(
            repository_root=self.root,
            result_path=self.result,
        )
        self.assertEqual(manifest["schema"], "pul7sar-golden-gpu-evidence-v1")
        self.assertEqual(manifest["request_id"], "request-1")
        self.assertFalse(manifest["publication_ready"])
        self.assertEqual(manifest["png"], "output/candidate.png")
        self.assertEqual(len(manifest["manifest_sha256"]), 64)
        self.assertEqual({item["path"] for item in manifest["files"]}, {
            "output/candidate.png",
            "output/first-png-result.json",
        })
        for item in manifest["files"]:
            self.assertGreater(item["bytes"], 0)
            self.assertEqual(len(item["sha256"]), 64)

    def test_rejects_publication_ready_generation_result(self):
        payload = json.loads(self.result.read_text(encoding="utf-8"))
        payload["publication_ready"] = True
        self.result.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaises(ValueError):
            build_golden_evidence_manifest(repository_root=self.root, result_path=self.result)

    def test_rejects_fake_png_signature(self):
        self.png.write_bytes(b"not-a-real-png")
        with self.assertRaises(ValueError):
            build_golden_evidence_manifest(repository_root=self.root, result_path=self.result)

    def test_rejects_evidence_outside_repository(self):
        outside = Path(self.tmp.name).parent / "outside-phase18-evidence.txt"
        outside.write_text("outside", encoding="utf-8")
        try:
            with self.assertRaises(ValueError):
                build_golden_evidence_manifest(
                    repository_root=self.root,
                    result_path=self.result,
                    additional_paths=[outside],
                )
        finally:
            outside.unlink(missing_ok=True)

    def test_additional_receipt_is_hashed_once(self):
        receipt = self.root / "output" / "qualification.json"
        receipt.write_text('{"eligible": true}', encoding="utf-8")
        manifest = build_golden_evidence_manifest(
            repository_root=self.root,
            result_path=self.result,
            additional_paths=[receipt, receipt],
        )
        paths = [item["path"] for item in manifest["files"]]
        self.assertEqual(paths.count("output/qualification.json"), 1)


if __name__ == "__main__":
    unittest.main()
