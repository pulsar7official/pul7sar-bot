from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from engine.intelligence.qwen_image_production_gate_verifier_candidate_triage import (
    build_production_gate_verifier_candidate_triage,
    verify_production_gate_verifier_candidate_triage,
)


class ProductionGateVerifierCandidateTriageTests(unittest.TestCase):
    def _root(self, source: str) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        target = root / "engine" / "quality"
        target.mkdir(parents=True)
        (target / "candidate.py").write_text(source, encoding="utf-8")
        return root

    def test_viable_candidate_remains_fail_closed(self) -> None:
        root = self._root(
            'def verify_fact_evidence(evidence_path, story_sha, receipt):\n'
            '    """verify fact source claim evidence truth result"""\n'
            '    return {"ok": True}\n'
        )
        receipt = build_production_gate_verifier_candidate_triage(repo_root=root)
        fact = receipt["triage"]["fact_lock"]
        self.assertTrue(fact)
        self.assertTrue(fact[0]["structurally_viable_for_adapter_review"])
        self.assertFalse(receipt["production_registry_mutated"])
        self.assertFalse(receipt["fresh_story_gates_passed"])
        self.assertFalse(receipt["canonical_generation_authorized"])
        self.assertFalse(receipt["genuine_golden_png_created"])

    def test_two_argument_candidate_is_structurally_disqualified(self) -> None:
        root = self._root(
            'def verify_fact_evidence(evidence_path, story_sha):\n'
            '    """verify fact source claim evidence truth result"""\n'
            '    return True\n'
        )
        receipt = build_production_gate_verifier_candidate_triage(repo_root=root)
        item = receipt["triage"]["fact_lock"][0]
        self.assertFalse(item["structurally_viable_for_adapter_review"])
        self.assertIn(
            "cannot_accept_three_positional_replay_arguments",
            item["structural_disqualifiers"],
        )

    def test_async_candidate_is_structurally_disqualified(self) -> None:
        root = self._root(
            'async def verify_fact_evidence(evidence_path, story_sha, receipt):\n'
            '    """verify fact source claim evidence truth result"""\n'
            '    return {"ok": True}\n'
        )
        receipt = build_production_gate_verifier_candidate_triage(repo_root=root)
        item = receipt["triage"]["fact_lock"][0]
        self.assertIn(
            "async_callable_not_supported_by_sync_replay_contract",
            item["structural_disqualifiers"],
        )

    def test_candidate_without_value_return_is_disqualified(self) -> None:
        root = self._root(
            'def verify_fact_evidence(evidence_path, story_sha, receipt):\n'
            '    """verify fact source claim evidence truth result"""\n'
            '    evidence_path = evidence_path\n'
        )
        receipt = build_production_gate_verifier_candidate_triage(repo_root=root)
        item = receipt["triage"]["fact_lock"][0]
        self.assertIn("no_explicit_value_return", item["structural_disqualifiers"])

    def test_live_source_drift_invalidates_triage_receipt(self) -> None:
        root = self._root(
            'def verify_fact_evidence(evidence_path, story_sha, receipt):\n'
            '    """verify fact source claim evidence truth result"""\n'
            '    return {"ok": True}\n'
        )
        receipt = build_production_gate_verifier_candidate_triage(repo_root=root)
        path = root / "engine" / "quality" / "candidate.py"
        path.write_text(path.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "TRIAGE_MISMATCH"):
            verify_production_gate_verifier_candidate_triage(receipt, repo_root=root)

    def test_forged_generation_authority_is_rejected(self) -> None:
        root = self._root(
            'def verify_fact_evidence(evidence_path, story_sha, receipt):\n'
            '    """verify fact source claim evidence truth result"""\n'
            '    return {"ok": True}\n'
        )
        receipt = build_production_gate_verifier_candidate_triage(repo_root=root)
        receipt["canonical_generation_authorized"] = True
        with self.assertRaisesRegex(ValueError, "TRIAGE_MISMATCH"):
            verify_production_gate_verifier_candidate_triage(receipt, repo_root=root)


if __name__ == "__main__":
    unittest.main()
