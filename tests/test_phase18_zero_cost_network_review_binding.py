from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from tools.phase18_bind_zero_cost_network_guard_to_review_bundle import bind, verify


BLOCK_MARKER = "PUL7SAR_PHASE18_ZERO_COST_NETWORK_BLOCKED"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ZeroCostNetworkReviewBindingTests(unittest.TestCase):
    def _fixture(self, root: Path):
        bundle = root / "output/phase18_golden_review/123-1"
        bundle.mkdir(parents=True)
        candidate = bundle / "candidate-1.png"
        candidate.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
        entry = {"path": "candidate-1.png", "sha256": sha(candidate), "bytes": candidate.stat().st_size}
        manifest = {
            "schema": "pul7sar-phase18-first-genuine-golden-v6-review-bundle-v1",
            "branch": "phase18/story-intelligence",
            "candidate": 1,
            "cost_mode": "$0-local",
            "offline_only": True,
            "source_commit_sha": "a" * 40,
            "exact_evidence_only": True,
            "eligible_for_human_visual_review": True,
            "entries": {"candidate_png": entry},
            "authoritative_gate": False,
            "network_download_authorized": False,
            "generation_authorized": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        (bundle / "review-bundle-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        evidence = {
            "schema": "pul7sar-phase18-zero-cost-network-guard-evidence-v1",
            "ready": True,
            "source_branch": "phase18/story-intelligence",
            "source_sha": "a" * 40,
            "cost_mode": "$0-local",
            "hf_hub_offline": True,
            "transformers_offline": True,
            "sitecustomize_guard_active": True,
            "network_download_authorized": False,
            "external_network_paths_blocked": True,
            "synthetic_checks": [
                {"name": "socket.connect_ipv4", "blocked": True, "marker": BLOCK_MARKER},
                {"name": "socket.connect_ex_ipv4", "blocked": True, "marker": BLOCK_MARKER},
                {"name": "socket.create_connection", "blocked": True, "marker": BLOCK_MARKER},
                {"name": "socket.getaddrinfo_external_dns", "blocked": True, "marker": BLOCK_MARKER},
            ],
            "github_run_id": "123",
            "github_run_attempt": "1",
        }
        canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        evidence["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()
        evidence_path = root / "output/phase18_gpu_smoke/network.json"
        evidence_path.parent.mkdir(parents=True)
        evidence_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return bundle, evidence_path

    def test_binds_and_replays_exact_network_evidence(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle, evidence = self._fixture(Path(tmp))
            result = bind(bundle_dir=bundle, network_evidence_path=evidence, run_id="123", run_attempt="1")
            self.assertTrue(result["zero_cost_network_guard_verified"])
            self.assertFalse(result["network_download_authorized"])
            self.assertTrue((bundle / "evidence/zero_cost_network_guard.json").is_file())
            replay = verify(bundle_dir=bundle, run_id="123", run_attempt="1")
            self.assertEqual(replay["zero_cost_network_guard_evidence_sha256"], sha(bundle / "evidence/zero_cost_network_guard.json"))

    def test_rejects_network_evidence_source_drift(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle, evidence = self._fixture(Path(tmp))
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            payload["source_sha"] = "b" * 40
            canonical_payload = dict(payload); canonical_payload.pop("evidence_sha256", None)
            canonical = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
            payload["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()
            evidence.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "NETWORK_SOURCE_DRIFT"):
                bind(bundle_dir=bundle, network_evidence_path=evidence, run_id="123", run_attempt="1")

    def test_rejects_unblocked_network_path(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle, evidence = self._fixture(Path(tmp))
            payload = json.loads(evidence.read_text(encoding="utf-8"))
            payload["synthetic_checks"][0]["blocked"] = False
            canonical_payload = dict(payload); canonical_payload.pop("evidence_sha256", None)
            canonical = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
            payload["evidence_sha256"] = hashlib.sha256(canonical).hexdigest()
            evidence.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "CHECK_NOT_BLOCKED"):
                bind(bundle_dir=bundle, network_evidence_path=evidence, run_id="123", run_attempt="1")

    def test_rejects_bundle_evidence_byte_drift_after_binding(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle, evidence = self._fixture(Path(tmp))
            bind(bundle_dir=bundle, network_evidence_path=evidence, run_id="123", run_attempt="1")
            (bundle / "evidence/zero_cost_network_guard.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "EVIDENCE_FILE_DRIFT"):
                verify(bundle_dir=bundle, run_id="123", run_attempt="1")

    def test_rejects_authority_drift_in_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            bundle, evidence = self._fixture(Path(tmp))
            manifest = bundle / "review-bundle-manifest.json"
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["publication_ready"] = True
            manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "BUNDLE_AUTHORITY_DRIFT:publication_ready"):
                bind(bundle_dir=bundle, network_evidence_path=evidence, run_id="123", run_attempt="1")


if __name__ == "__main__":
    unittest.main()
