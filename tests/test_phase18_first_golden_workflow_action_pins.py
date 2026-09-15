from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase18-first-genuine-golden-v6-fresh.yml"

CHECKOUT_SHA = "11bd71901bbe5b1630ceea73d27597364c9af683"  # actions/checkout v4.2.2
UPLOAD_ARTIFACT_SHA = "ea165f8d65b6e75b540449e92b4886f43607fa02"  # actions/upload-artifact v4.6.2


class FirstGoldenWorkflowActionPinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")
        cls.uses = re.findall(r"^\s*uses:\s*([^\s#]+)", cls.text, flags=re.MULTILINE)

    def test_checkout_is_pinned_to_verified_commit(self) -> None:
        self.assertIn(f"actions/checkout@{CHECKOUT_SHA}", self.uses)
        self.assertNotIn("actions/checkout@v4", self.uses)
        self.assertNotIn("actions/checkout@main", self.uses)

    def test_upload_artifact_is_pinned_for_success_and_failure_paths(self) -> None:
        expected = f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}"
        self.assertEqual(self.uses.count(expected), 2)
        self.assertNotIn("actions/upload-artifact@v4", self.uses)
        self.assertNotIn("actions/upload-artifact@main", self.uses)

    def test_all_external_actions_use_full_commit_sha(self) -> None:
        external = [entry for entry in self.uses if not entry.startswith("./")]
        self.assertTrue(external)
        for entry in external:
            owner_action, separator, ref = entry.partition("@")
            self.assertTrue(separator, msg=f"missing action ref: {entry}")
            self.assertRegex(owner_action, r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
            self.assertRegex(ref, r"^[0-9a-f]{40}$", msg=f"mutable or non-SHA action ref: {entry}")


if __name__ == "__main__":
    unittest.main()
