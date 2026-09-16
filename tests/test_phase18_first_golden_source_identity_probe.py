from __future__ import annotations

import unittest

from tools.phase18_probe_first_golden_source_identity import EXPECTED_BRANCH, inspect


HEAD = "a" * 40
BASE = "b" * 40


def runner(*, branch=EXPECTED_BRANCH, head=HEAD, tracked_status="", merge_base=BASE, diff_names="tools/example.py\n"):
    def _run(command: list[str]) -> tuple[int, str, str]:
        key = tuple(command)
        if key == ("branch", "--show-current"):
            return 0, branch, ""
        if key == ("rev-parse", "HEAD"):
            return 0, head, ""
        if key == ("status", "--porcelain", "--untracked-files=no"):
            return 0, tracked_status, ""
        if key == ("merge-base", "origin/main", "HEAD"):
            return 0, merge_base, ""
        if key == ("diff", "--name-only", f"{merge_base}...HEAD"):
            return 0, diff_names, ""
        return 1, "", "unexpected command"
    return _run


class FirstGoldenSourceIdentityProbeTests(unittest.TestCase):
    def test_ready_only_on_phase18_exact_clean_source(self):
        payload = inspect(expected_commit=HEAD, git_runner=runner())
        self.assertTrue(payload["source_identity_ready"])
        self.assertEqual(payload["branch_observed"], EXPECTED_BRANCH)
        self.assertEqual(payload["head_commit"], HEAD)
        self.assertEqual(payload["expected_commit"], HEAD)
        self.assertTrue(payload["tracked_worktree_clean"])
        self.assertFalse(payload["main_py_modified"])
        self.assertEqual(payload["blockers"], [])
        self.assertFalse(payload["authoritative_gate"])
        self.assertFalse(payload["network_download_authorized"])
        self.assertFalse(payload["generation_authorized"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_main_branch_is_rejected(self):
        payload = inspect(expected_commit=HEAD, git_runner=runner(branch="main"))
        self.assertIn("PHASE18_EXECUTION_BRANCH_MISMATCH", payload["blockers"])
        self.assertFalse(payload["source_identity_ready"])

    def test_dispatch_commit_mismatch_is_rejected(self):
        payload = inspect(expected_commit="c" * 40, git_runner=runner())
        self.assertIn("PHASE18_EXECUTION_COMMIT_MISMATCH", payload["blockers"])
        self.assertFalse(payload["source_identity_ready"])

    def test_dirty_tracked_source_is_rejected(self):
        payload = inspect(expected_commit=HEAD, git_runner=runner(tracked_status=" M tools/example.py"))
        self.assertIn("PHASE18_TRACKED_WORKTREE_DIRTY", payload["blockers"])
        self.assertFalse(payload["source_identity_ready"])

    def test_main_py_diff_is_rejected(self):
        payload = inspect(expected_commit=HEAD, git_runner=runner(diff_names="main.py\ntools/example.py\n"))
        self.assertIn("PHASE18_MAIN_PY_MODIFIED", payload["blockers"])
        self.assertTrue(payload["main_py_modified"])
        self.assertFalse(payload["source_identity_ready"])

    def test_invalid_expected_commit_is_rejected(self):
        payload = inspect(expected_commit="phase18/story-intelligence", git_runner=runner())
        self.assertIn("EXPECTED_COMMIT_INVALID", payload["blockers"])
        self.assertFalse(payload["source_identity_ready"])


if __name__ == "__main__":
    unittest.main()
