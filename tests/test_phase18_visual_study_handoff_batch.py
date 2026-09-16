import json
import tempfile
import unittest
from pathlib import Path

from tools.phase18_build_visual_study_handoffs import build


class VisualStudyHandoffBatchTests(unittest.TestCase):
    def test_builds_three_human_review_contracts_and_no_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = build(tmp)
            self.assertEqual(manifest["handoff_count"], 3)
            self.assertEqual(manifest["candidate_image_count"], 0)
            self.assertFalse(manifest["publication_ready"])
            self.assertFalse(manifest["exact_brand_geometry_ready"])
            files = {item.name for item in Path(tmp).iterdir()}
            self.assertEqual(
                files,
                {
                    "manifest.json",
                    "transfer-signature-v1.json",
                    "result-statement-v1.json",
                    "verified-subject-news-v1.json",
                },
            )
            self.assertFalse(any(Path(tmp).glob("*.png")))

    def test_each_handoff_is_human_review_allowed_but_publication_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = build(tmp)
            for entry in manifest["handoffs"]:
                payload = json.loads((Path(tmp) / entry["path"]).read_text(encoding="utf-8"))
                self.assertTrue(payload["human_review_allowed"])
                self.assertFalse(payload["publication_ready"])
                self.assertEqual(payload["readiness_status"], "publication_geometry_blocked")
                self.assertEqual(len(payload["payload_sha256"]), 64)
                self.assertFalse(payload["metadata"]["legacy_repo_logo_allowed"])


if __name__ == "__main__":
    unittest.main()
