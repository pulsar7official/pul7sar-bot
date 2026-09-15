import json
from pathlib import Path

import pytest

from tools.phase18_bind_first_golden_preflight_evidence import EXPECTED_BRANCH, REQUIRED, bind


def _ready_blocker():
    return {
        "schema": "pul7sar-phase18-first-golden-execution-blocker-probe-v6",
        "branch_required": EXPECTED_BRANCH,
        "ready_for_authoritative_golden_preflight": True,
        "blockers": [],
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _evidence_dir(tmp_path: Path) -> Path:
    # bind() intentionally rejects paths outside the repository, so place fixtures under repo output.
    root = Path(__file__).resolve().parents[1]
    target = root / "output" / "phase18_test_preflight_binding"
    target.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED:
        payload = _ready_blocker() if name == "preflight-execution-blocker.json" else {"fixture": name}
        (target / name).write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return target


def test_binding_hashes_all_required_evidence_and_preserves_closed_authority(tmp_path):
    evidence = _evidence_dir(tmp_path)
    try:
        payload = bind(evidence_dir=evidence, source_sha="a" * 40, branch=EXPECTED_BRANCH)
        assert payload["schema"] == "pul7sar-phase18-first-golden-preflight-evidence-binding-v1"
        assert set(payload["evidence"]) == set(REQUIRED)
        assert all(len(item["sha256"]) == 64 for item in payload["evidence"].values())
        for field in ("authoritative_gate", "generation_authorized", "human_review_authorized", "golden_approved", "publication_ready", "seeds_2_to_4_authorized"):
            assert payload[field] is False
    finally:
        for p in evidence.glob("*"):
            p.unlink()
        evidence.rmdir()


def test_binding_rejects_nonready_blocker(tmp_path):
    evidence = _evidence_dir(tmp_path)
    try:
        blocker_path = evidence / "preflight-execution-blocker.json"
        blocker = _ready_blocker()
        blocker["ready_for_authoritative_golden_preflight"] = False
        blocker["blockers"] = ["CUDA_UNAVAILABLE"]
        blocker_path.write_text(json.dumps(blocker) + "\n", encoding="utf-8")
        with pytest.raises(RuntimeError, match="FIRST_GOLDEN_PREFLIGHT_NOT_READY"):
            bind(evidence_dir=evidence, source_sha="b" * 40, branch=EXPECTED_BRANCH)
    finally:
        for p in evidence.glob("*"):
            p.unlink()
        evidence.rmdir()


def test_binding_rejects_branch_and_sha_drift(tmp_path):
    evidence = _evidence_dir(tmp_path)
    try:
        with pytest.raises(RuntimeError, match="BRANCH_DRIFT"):
            bind(evidence_dir=evidence, source_sha="c" * 40, branch="main")
        with pytest.raises(RuntimeError, match="SOURCE_SHA_INVALID"):
            bind(evidence_dir=evidence, source_sha="not-a-sha", branch=EXPECTED_BRANCH)
    finally:
        for p in evidence.glob("*"):
            p.unlink()
        evidence.rmdir()
