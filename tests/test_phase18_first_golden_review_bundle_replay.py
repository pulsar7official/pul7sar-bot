import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.phase18_verify_first_genuine_golden_v6_review_bundle import verify_bundle


PNG = b"\x89PNG\r\n\x1a\n" + b"candidate-one"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FirstGoldenReviewBundleReplayTests(unittest.TestCase):
    def _bundle(self, root: Path) -> Path:
        bundle = root / "output/phase18_golden_review/1-1"
        evidence = bundle / "evidence"
        evidence.mkdir(parents=True)
        files = {
            "candidate_png": bundle / "candidate-1.png",
            "fresh_source_bound_manifest": bundle / "fresh-source-bound-manifest.json",
            "snapshot_bound_manifest": bundle / "snapshot-bound-manifest.json",
            "approved_snapshot_inventory": bundle / "approved-snapshot-inventory.json",
            "evidence_resource_lock": evidence / "resource_lock.json",
        }
        files["candidate_png"].write_bytes(PNG)
        for key, path in files.items():
            if key != "candidate_png":
                path.write_text(json.dumps({"key": key}) + "\n", encoding="utf-8")
        entries = {
            key: {
                "path": path.relative_to(bundle).as_posix(),
                "sha256": sha(path),
                "bytes": path.stat().st_size,
            }
            for key, path in files.items()
        }
        manifest = {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1",
            "status": "FIRST_GENUINE_GOLDEN_V6_REVIEW_BUNDLE_CRYPTOGRAPHICALLY_BOUND",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "offline_only": True,
            "source_commit_sha": "a" * 40,
            "png_sha256": sha(files["candidate_png"]),
            "exact_evidence_only": True,
            "eligible_for_human_visual_review": True,
            "entries": entries,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        (bundle / "review-bundle-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return bundle

    def test_verifies_exact_closed_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle = self._bundle(Path(tmp))
            result = verify_bundle(bundle_dir=bundle)
            self.assertTrue(result["exact_closed_file_set"])
            self.assertTrue(result["eligible_for_human_visual_review"])
            self.assertFalse(result["human_visual_review_approved"])
            self.assertFalse(result["publication_ready"])
            self.assertEqual(result["png_sha256"], sha(bundle / "candidate-1.png"))
            self.assertEqual(result["verified_entry_count"], 5)

    def test_rejects_undeclared_file(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle = self._bundle(Path(tmp))
            (bundle / "unexpected.txt").write_text("not declared\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "UNDECLARED_FILE"):
                verify_bundle(bundle_dir=bundle)

    def test_rejects_declared_file_byte_drift(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle = self._bundle(Path(tmp))
            (bundle / "evidence/resource_lock.json").write_text("drift\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "ENTRY_(SIZE|SHA)_DRIFT"):
                verify_bundle(bundle_dir=bundle)

    def test_rejects_authority_drift(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle = self._bundle(Path(tmp))
            manifest_path = bundle / "review-bundle-manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["golden_quality_approved"] = True
            manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:golden_quality_approved"):
                verify_bundle(bundle_dir=bundle)


if __name__ == "__main__":
    unittest.main()
