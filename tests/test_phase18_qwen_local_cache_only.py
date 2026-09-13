from __future__ import annotations

import ast
import inspect
import unittest

from engine.intelligence.approved_model_revisions import (
    QWEN25_VL_3B_MODEL_ID,
    QWEN25_VL_3B_REVISION,
)
from tools import phase18_prefetch_qwen
from tools.phase18_prefetch_qwen import _require_cached_snapshot


class QwenLocalCacheOnlyTests(unittest.TestCase):
    def test_cached_snapshot_resolution_is_revision_pinned_and_local_files_only(self) -> None:
        calls: list[dict[str, object]] = []

        def snapshot_download(**kwargs: object) -> str:
            calls.append(dict(kwargs))
            return "/cache/qwen-approved-snapshot"

        resolved = _require_cached_snapshot(
            snapshot_download,
            QWEN25_VL_3B_MODEL_ID,
            QWEN25_VL_3B_REVISION,
        )

        self.assertEqual(resolved, "/cache/qwen-approved-snapshot")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["repo_id"], QWEN25_VL_3B_MODEL_ID)
        self.assertEqual(calls[0]["revision"], QWEN25_VL_3B_REVISION)
        self.assertIs(calls[0]["local_files_only"], True)

    def test_missing_local_snapshot_fails_closed_without_network_fallback(self) -> None:
        calls: list[dict[str, object]] = []

        def snapshot_download(**kwargs: object) -> str:
            calls.append(dict(kwargs))
            raise OSError("snapshot missing from local cache")

        with self.assertRaisesRegex(RuntimeError, "QWEN_APPROVED_LOCAL_SNAPSHOT_REQUIRED"):
            _require_cached_snapshot(
                snapshot_download,
                QWEN25_VL_3B_MODEL_ID,
                QWEN25_VL_3B_REVISION,
            )

        self.assertEqual(len(calls), 1)
        self.assertIs(calls[0]["local_files_only"], True)
        self.assertEqual(calls[0]["revision"], QWEN25_VL_3B_REVISION)

    def test_main_has_no_direct_snapshot_download_call_that_can_bypass_local_cache_guard(self) -> None:
        tree = ast.parse(inspect.getsource(phase18_prefetch_qwen.main))
        direct_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "snapshot_download"
        ]
        guarded_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_require_cached_snapshot"
        ]

        self.assertEqual(direct_calls, [])
        self.assertEqual(len(guarded_calls), 1)

    def test_zero_cost_receipt_contract_is_explicitly_fail_closed(self) -> None:
        source = inspect.getsource(phase18_prefetch_qwen.main)
        self.assertIn('"downloaded_now": False', source)
        self.assertIn('"network_download_authorized": False', source)
        self.assertIn('"local_files_only": True', source)
        self.assertNotIn('"downloaded_now": downloaded', source)


if __name__ == "__main__":
    unittest.main()
