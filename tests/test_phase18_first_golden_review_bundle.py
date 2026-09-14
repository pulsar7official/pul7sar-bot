import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.phase18_package_first_genuine_golden_v6_review_bundle import build_bundle


PNG = b"\x89PNG\r\n\x1a\n" + b"candidate-one"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FirstGoldenReviewBundleTests(unittest.TestCase):
    def _fixture(self, root: Path):
        out = root / "output/phase18_gpu_smoke"
        out.mkdir(parents=True)
        png = out / "candidate.png"
        png.write_bytes(PNG)
        evidence_paths = {}
        for key in ("execution_blocker_probe", "runner_identity", "fresh_wrapper", "freshness_verification", "source_bound_replay", "resource_lock"):
            path = out / f"{key}.json"
            path.write_text(json.dumps({"key": key}) + "\n", encoding="utf-8")
            evidence_paths[key] = path
        inventory = out / "snapshot-inventory.json"
        inventory.write_text("{}\n", encoding="utf-8")
        source_sha = "a" * 40
        png_sha = sha(png)
        evidence = {
            key: {"path": str(path.relative_to(root)), "sha256": sha(path)}
            for key, path in evidence_paths.items()
        }
        evidence["png"] = {"path": str(png.relative_to(root)), "sha256": png_sha, "bytes": len(PNG)}
        fresh = {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-fresh-source-bound-manifest-v3",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "offline_only": True,
            "source_commit_sha": source_sha,
            "png_sha256": png_sha,
            "eligible_for_human_visual_review": True,
            "evidence": evidence,
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        fresh_path = out / "fresh-manifest.json"
        fresh_path.write_text(json.dumps(fresh, indent=2) + "\n", encoding="utf-8")
        snapshot = {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-snapshot-bound-manifest-v2",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "offline_only": True,
            "source_commit_sha": source_sha,
            "png_sha256": png_sha,
            "generation_runtime_fingerprint_verified_after_generation": True,
            "generation_runtime_fingerprint_sha256": "c" * 64,
            "eligible_for_human_visual_review": True,
            "upstream_manifest": {"path": str(fresh_path.relative_to(root)), "sha256": sha(fresh_path)},
            "recorded_snapshot_inventory": {"path": str(inventory.relative_to(root)), "sha256": sha(inventory)},
            "execution_blocker_probe": {
                "path": str(evidence_paths["execution_blocker_probe"].relative_to(root)),
                "sha256": sha(evidence_paths["execution_blocker_probe"]),
            },
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        snapshot_path = out / "snapshot-manifest.json"
        snapshot_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
        return fresh_path, snapshot_path, png_sha

    def test_packages_only_exact_bound_evidence_and_png(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh, snapshot, png_sha = self._fixture(root)
            bundle = root / "output/phase18_golden_review/run-1"
            manifest = build_bundle(fresh_manifest_path=fresh, snapshot_manifest_path=snapshot, repo_root=root, bundle_dir=bundle)
            self.assertEqual(manifest["png_sha256"], png_sha)
            self.assertTrue(manifest["generation_runtime_fingerprint_verified_after_generation"])
            self.assertEqual(manifest["generation_runtime_fingerprint_sha256"], "c" * 64)
            self.assertTrue(manifest["eligible_for_human_visual_review"])
            self.assertFalse(manifest["human_visual_review_approved"])
            self.assertFalse(manifest["publication_ready"])
            self.assertEqual(sha(bundle / "candidate-1.png"), png_sha)
            self.assertTrue((bundle / "review-bundle-manifest.json").is_file())
            self.assertTrue((bundle / "evidence/resource_lock.json").is_file())

    def test_rejects_png_drift_after_manifests(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh, snapshot, _ = self._fixture(root)
            png = root / json.loads(fresh.read_text(encoding="utf-8"))["evidence"]["png"]["path"]
            png.write_bytes(PNG + b"drift")
            with self.assertRaisesRegex(RuntimeError, "REF_SHA_DRIFT:png"):
                build_bundle(fresh_manifest_path=fresh, snapshot_manifest_path=snapshot, repo_root=root,
                             bundle_dir=root / "output/phase18_golden_review/run-2")

    def test_rejects_missing_runtime_replay_proof(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh, snapshot, _ = self._fixture(root)
            payload = json.loads(snapshot.read_text(encoding="utf-8"))
            payload["generation_runtime_fingerprint_verified_after_generation"] = False
            snapshot.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "RUNTIME_REPLAY_NOT_VERIFIED"):
                build_bundle(fresh_manifest_path=fresh, snapshot_manifest_path=snapshot, repo_root=root,
                             bundle_dir=root / "output/phase18_golden_review/run-runtime")

    def test_rejects_existing_bundle_target_to_prevent_stale_mix(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh, snapshot, _ = self._fixture(root)
            bundle = root / "output/phase18_golden_review/run-3"
            bundle.mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "TARGET_ALREADY_EXISTS"):
                build_bundle(fresh_manifest_path=fresh, snapshot_manifest_path=snapshot, repo_root=root, bundle_dir=bundle)

    def test_rejects_authority_drift(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh, snapshot, _ = self._fixture(root)
            payload = json.loads(snapshot.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            snapshot.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "AUTHORITY_DRIFT:snapshot:publication_ready"):
                build_bundle(fresh_manifest_path=fresh, snapshot_manifest_path=snapshot, repo_root=root,
                             bundle_dir=root / "output/phase18_golden_review/run-4")


if __name__ == "__main__":
    unittest.main()
