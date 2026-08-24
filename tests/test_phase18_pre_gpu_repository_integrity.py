from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine.intelligence.brand_embedded_master import EmbeddedBrandMasterLoader
from engine.intelligence.pre_gpu_repository_integrity import (
    EXPECTED_BRANCH,
    LEGACY_TRUNCATED_TRANSPORT,
    PreGpuRepositoryIntegrityGate,
)


class PreGpuRepositoryIntegrityTests(unittest.TestCase):
    def test_current_repository_compact_brand_is_ready_and_non_authorizing(self) -> None:
        root = Path(__file__).resolve().parents[1]
        receipt = PreGpuRepositoryIntegrityGate().inspect(repository_root=root, branch=EXPECTED_BRANCH)
        self.assertTrue(receipt.ready, receipt.blockers)
        self.assertEqual(receipt.cost_mode, "$0-local")
        self.assertTrue(receipt.compact_brand_member_integrity_pinned)
        self.assertTrue(receipt.compact_brand_self_contained)
        self.assertTrue(receipt.compact_brand_study_only)
        self.assertFalse(receipt.legacy_transport_authoritative)
        self.assertFalse(receipt.network_required)
        self.assertFalse(receipt.gpu_required)
        self.assertFalse(receipt.generation_authorized)
        self.assertFalse(receipt.queue_mutated)
        self.assertFalse(receipt.png_created)
        self.assertFalse(receipt.publication_ready)

    def test_wrong_branch_fails_closed(self) -> None:
        root = Path(__file__).resolve().parents[1]
        receipt = PreGpuRepositoryIntegrityGate().inspect(repository_root=root, branch="main")
        self.assertFalse(receipt.ready)
        self.assertIn("unexpected_branch", receipt.blockers)

    def test_legacy_truncated_transport_is_never_authoritative(self) -> None:
        root = Path(__file__).resolve().parents[1]
        legacy = root / LEGACY_TRUNCATED_TRANSPORT
        self.assertTrue(legacy.is_file())
        receipt = PreGpuRepositoryIntegrityGate().inspect(repository_root=root, branch=EXPECTED_BRANCH)
        self.assertTrue(receipt.legacy_transport_exists)
        self.assertFalse(receipt.legacy_transport_authoritative)

    def test_compact_publication_authority_drift_fails_closed(self) -> None:
        root = Path(__file__).resolve().parents[1]
        master = EmbeddedBrandMasterLoader().load(root)
        bad = replace(master.receipt, publication_ready=True)
        bad_master = replace(master, receipt=bad)
        with patch(
            "engine.intelligence.pre_gpu_repository_integrity.EmbeddedBrandMasterLoader.load",
            return_value=bad_master,
        ):
            receipt = PreGpuRepositoryIntegrityGate().inspect(repository_root=root, branch=EXPECTED_BRANCH)
        self.assertFalse(receipt.ready)
        self.assertIn("compact_brand_publication_authority_drift", receipt.blockers)

    def test_missing_or_corrupt_compact_transport_fails_without_gpu_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = PreGpuRepositoryIntegrityGate().inspect(repository_root=root, branch=EXPECTED_BRANCH)
        self.assertFalse(receipt.ready)
        self.assertTrue(any(item.startswith("compact_brand_integrity_failed:") for item in receipt.blockers))
        self.assertFalse(receipt.gpu_required)
        self.assertFalse(receipt.generation_authorized)
        self.assertFalse(receipt.publication_ready)


if __name__ == "__main__":
    unittest.main()
