from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import phase18_bind_first_genuine_golden_source_commit as source_binding


GOOD_SHA = "a" * 40


def _resource_lock(path: Path) -> None:
    payload = {
        "schema": source_binding.RESOURCE_LOCK_SCHEMA,
        "status": source_binding.RESOURCE_LOCK_STATUS,
        "branch": source_binding.EXPECTED_BRANCH,
        "candidate": 1,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


class FirstGenuineGoldenV6SourceBindingTests(unittest.TestCase):
    def test_bind_and_verify_exact_source_commit_without_granting_authority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = root / "lock.json"
            envelope = root / "source-binding.json"
            _resource_lock(lock)
            with mock.patch.object(source_binding, "_git", side_effect=[source_binding.EXPECTED_BRANCH, GOOD_SHA]):
                bound = source_binding.bind(lock, envelope, repo_root=root)
            self.assertEqual(bound["source_commit_sha"], GOOD_SHA)
            replay = source_binding.verify(envelope, lock, expected_source_sha=GOOD_SHA)
            self.assertEqual(replay["status"], "FIRST_GENUINE_GOLDEN_V6_SOURCE_BINDING_REPLAY_VERIFIED")
            self.assertFalse(replay["publication_ready"])
            self.assertFalse(replay["golden_quality_approved"])

    def test_rejects_different_expected_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = root / "lock.json"
            envelope = root / "source-binding.json"
            _resource_lock(lock)
            with mock.patch.object(source_binding, "_git", side_effect=[source_binding.EXPECTED_BRANCH, GOOD_SHA]):
                source_binding.bind(lock, envelope, repo_root=root)
            with self.assertRaisesRegex(RuntimeError, "SOURCE_COMMIT_DRIFT"):
                source_binding.verify(envelope, lock, expected_source_sha="b" * 40)

    def test_rejects_resource_lock_tampering_even_if_source_sha_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = root / "lock.json"
            envelope = root / "source-binding.json"
            _resource_lock(lock)
            with mock.patch.object(source_binding, "_git", side_effect=[source_binding.EXPECTED_BRANCH, GOOD_SHA]):
                source_binding.bind(lock, envelope, repo_root=root)
            payload = json.loads(lock.read_text(encoding="utf-8"))
            payload["extra"] = "tampered"
            lock.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "RESOURCE_LOCK_SHA_DRIFT|RESOURCE_LOCK_BYTES_DRIFT"):
                source_binding.verify(envelope, lock, expected_source_sha=GOOD_SHA)

    def test_rejects_wrong_branch_at_binding_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = root / "lock.json"
            envelope = root / "source-binding.json"
            _resource_lock(lock)
            with mock.patch.object(source_binding, "_git", side_effect=["main", GOOD_SHA]):
                with self.assertRaisesRegex(RuntimeError, "SOURCE_BRANCH_BLOCKED"):
                    source_binding.bind(lock, envelope, repo_root=root)

    def test_rejects_authority_drift_in_source_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock = root / "lock.json"
            envelope = root / "source-binding.json"
            _resource_lock(lock)
            with mock.patch.object(source_binding, "_git", side_effect=[source_binding.EXPECTED_BRANCH, GOOD_SHA]):
                source_binding.bind(lock, envelope, repo_root=root)
            payload = json.loads(envelope.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            envelope.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SOURCE_ILLEGAL_AUTHORITY:publication_ready"):
                source_binding.verify(envelope, lock, expected_source_sha=GOOD_SHA)


if __name__ == "__main__":
    unittest.main()
