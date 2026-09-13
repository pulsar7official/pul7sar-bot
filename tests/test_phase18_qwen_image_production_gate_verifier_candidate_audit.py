from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_production_gate_verifier_candidate_audit import (
    audit_production_gate_verifier_candidates,
    verify_production_gate_verifier_candidate_audit,
)


class QwenProductionGateVerifierCandidateAuditTests(unittest.TestCase):
    def _root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "engine" / "editorial").mkdir(parents=True)
        return temp, root

    def test_discovers_candidates_without_granting_authority(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        (root / "engine" / "editorial" / "checks.py").write_text(
            "def verify_story_facts(evidence, story_sha, receipt):\n"
            "    \"\"\"Verify factual claims against source evidence and result score.\"\"\"\n"
            "    return True\n\n"
            "def assess_neutral_tone(evidence, story_sha, receipt):\n"
            "    \"\"\"Check sentiment neutrality and respectful winner loser editorial tone.\"\"\"\n"
            "    return True\n",
            encoding="utf-8",
        )
        receipt = audit_production_gate_verifier_candidates(repo_root=root)
        self.assertTrue(receipt["candidates"]["fact_lock"])
        self.assertTrue(receipt["candidates"]["sentiment_neutrality"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["production_semantic_replay_executed"])
        self.assertFalse(receipt["fresh_story_gates_passed"])
        self.assertFalse(receipt["genuine_golden_png_created"])
        for items in receipt["candidates"].values():
            for item in items:
                self.assertTrue(item["candidate_only"])
                self.assertFalse(item["production_backed"])
                self.assertFalse(item["registered"])

    def test_excludes_test_stub_and_phase18_plumbing_paths(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        (root / "engine" / "tests").mkdir(parents=True)
        (root / "engine" / "tests" / "identity.py").write_text(
            "def verify_entity_identity(evidence, story_sha, receipt):\n    return True\n",
            encoding="utf-8",
        )
        (root / "engine" / "editorial" / "qwen_image_fresh_story_gate_fake.py").write_text(
            "def verify_entity_identity(evidence, story_sha, receipt):\n    return True\n",
            encoding="utf-8",
        )
        receipt = audit_production_gate_verifier_candidates(repo_root=root)
        all_paths = {
            item["repository_relative_path"]
            for items in receipt["candidates"].values()
            for item in items
        }
        self.assertNotIn("engine/tests/identity.py", all_paths)
        self.assertNotIn(
            "engine/editorial/qwen_image_fresh_story_gate_fake.py", all_paths
        )

    def test_source_bytes_are_bound_and_drift_breaks_replay(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        path = root / "engine" / "editorial" / "identity.py"
        path.write_text(
            "def verify_entity_identity(evidence, story_sha, receipt):\n"
            "    \"\"\"Verify entity identity and disambiguate player club team matches.\"\"\"\n"
            "    return True\n",
            encoding="utf-8",
        )
        receipt = audit_production_gate_verifier_candidates(repo_root=root)
        candidate = receipt["candidates"]["entity_identity_verification"][0]
        self.assertEqual(len(candidate["source_file_sha256"]), 64)
        self.assertGreater(candidate["source_file_byte_size"], 0)
        verify_production_gate_verifier_candidate_audit(receipt, repo_root=root)
        path.write_text(path.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "CANDIDATE_AUDIT_MISMATCH"):
            verify_production_gate_verifier_candidate_audit(receipt, repo_root=root)

    def test_receipt_authority_forgery_fails_even_if_digest_is_rewritten(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        receipt = audit_production_gate_verifier_candidates(repo_root=root)
        forged = json.loads(json.dumps(receipt))
        forged["canonical_generation_authorized"] = True
        forged["candidate_audit_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "CANDIDATE_AUDIT_MISMATCH"):
            verify_production_gate_verifier_candidate_audit(forged, repo_root=root)

    def test_parse_failure_is_recorded_not_executed(self) -> None:
        temp, root = self._root()
        self.addCleanup(temp.cleanup)
        path = root / "engine" / "editorial" / "broken.py"
        path.write_text("def broken(:\n", encoding="utf-8")
        receipt = audit_production_gate_verifier_candidates(repo_root=root)
        self.assertEqual(receipt["files_scanned"], 0)
        self.assertEqual(receipt["parse_failures"][0]["path"], "engine/editorial/broken.py")
        self.assertEqual(receipt["parse_failures"][0]["error_type"], "SyntaxError")


if __name__ == "__main__":
    unittest.main()
