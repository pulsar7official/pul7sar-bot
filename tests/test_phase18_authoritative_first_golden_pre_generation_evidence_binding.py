import json
from pathlib import Path

import pytest

from tools.phase18_bind_authoritative_first_golden_pre_generation_evidence import bind


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _blocker() -> dict:
    return {
        "schema": "pul7sar-phase18-first-golden-execution-blocker-probe-v6",
        "branch_required": "phase18/story-intelligence",
        "ready_for_authoritative_golden_preflight": True,
        "blockers": [],
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def test_binds_four_exact_evidence_files_and_keeps_authority_closed(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    network = _write(tmp_path / "network.json", {"cost_mode": "$0-local"})
    runner = _write(tmp_path / "runner.json", {"cuda": True})
    snapshots = _write(tmp_path / "snapshots.json", {"offline": True})
    blocker = _write(tmp_path / "blocker.json", _blocker())
    result = bind(source_sha="a" * 40, branch="phase18/story-intelligence", network=network, runner=runner, snapshots=snapshots, blocker=blocker)
    assert result["schema"] == "pul7sar-phase18-authoritative-first-golden-pre-generation-evidence-binding-v1"
    assert result["source_sha"] == "a" * 40
    assert set(result["evidence"]) == {"zero_cost_network_guard", "runner_identity", "approved_snapshot_inventory", "execution_blocker"}
    for item in result["evidence"].values():
        assert len(item["sha256"]) == 64
        assert item["size_bytes"] > 0
    for field in ("authoritative_gate", "generation_authorized", "human_review_authorized", "golden_approved", "publication_ready", "seeds_2_to_4_authorized"):
        assert result[field] is False


def test_rejects_non_ready_blocker(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    files = [_write(tmp_path / f"e{i}.json", {}) for i in range(3)]
    bad = _blocker(); bad["ready_for_authoritative_golden_preflight"] = False; bad["blockers"] = ["CUDA_UNAVAILABLE"]
    blocker = _write(tmp_path / "blocker.json", bad)
    with pytest.raises(RuntimeError, match="AUTHORITATIVE_PREGEN_NOT_READY"):
        bind(source_sha="b" * 40, branch="phase18/story-intelligence", network=files[0], runner=files[1], snapshots=files[2], blocker=blocker)


def test_rejects_branch_or_source_drift(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    files = [_write(tmp_path / f"e{i}.json", {}) for i in range(3)]
    blocker = _write(tmp_path / "blocker.json", _blocker())
    with pytest.raises(RuntimeError, match="AUTHORITATIVE_PREGEN_BRANCH_DRIFT"):
        bind(source_sha="c" * 40, branch="main", network=files[0], runner=files[1], snapshots=files[2], blocker=blocker)
    with pytest.raises(RuntimeError, match="AUTHORITATIVE_PREGEN_SOURCE_SHA_INVALID"):
        bind(source_sha="short", branch="phase18/story-intelligence", network=files[0], runner=files[1], snapshots=files[2], blocker=blocker)
