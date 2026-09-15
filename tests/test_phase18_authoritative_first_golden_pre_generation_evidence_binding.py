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


def _network(source_sha: str) -> dict:
    return {
        "schema": "pul7sar-phase18-zero-cost-network-guard-evidence-v1",
        "ready": True,
        "source_branch": "phase18/story-intelligence",
        "source_sha": source_sha,
        "cost_mode": "$0-local",
        "hf_hub_offline": True,
        "transformers_offline": True,
        "sitecustomize_guard_active": True,
        "external_network_paths_blocked": True,
        "network_download_authorized": False,
    }


def _runner(source_sha: str) -> dict:
    return {
        "schema": "pul7sar-phase18-first-golden-runner-identity-v1",
        "repository": "pulsar7official/pul7sar-bot",
        "branch": "phase18/story-intelligence",
        "source_commit_sha": source_sha,
        "cost_mode": "$0-local",
        "offline_only": True,
        "runner_identity_verified": True,
        "blockers": [],
        "runtime": {"cuda_available": True, "cuda_runtime": "12.8", "cuda_device_count": 1, "native_bf16": True},
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _snapshots() -> dict:
    model = {"ready": True, "blockers": [], "file_count": 2, "total_bytes": 1024, "inventory_sha256": "d" * 64}
    return {
        "schema": "pul7sar-phase18-approved-snapshot-inventory-v1",
        "branch_required": "phase18/story-intelligence",
        "cost_mode": "$0-local",
        "offline_only": True,
        "ready": True,
        "blockers": [],
        "qwen": dict(model),
        "flux": dict(model),
        "authoritative_gate": False,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _files(tmp_path: Path, source_sha: str):
    return (
        _write(tmp_path / "network.json", _network(source_sha)),
        _write(tmp_path / "runner.json", _runner(source_sha)),
        _write(tmp_path / "snapshots.json", _snapshots()),
        _write(tmp_path / "blocker.json", _blocker()),
    )


def test_binds_four_exact_semantically_validated_evidence_files_and_keeps_authority_closed(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    source_sha = "a" * 40
    network, runner, snapshots, blocker = _files(tmp_path, source_sha)
    result = bind(source_sha=source_sha, branch="phase18/story-intelligence", network=network, runner=runner, snapshots=snapshots, blocker=blocker)
    assert result["schema"] == "pul7sar-phase18-authoritative-first-golden-pre-generation-evidence-binding-v2"
    assert result["source_sha"] == source_sha
    assert all(result["semantic_validation"].values())
    assert set(result["evidence"]) == {"zero_cost_network_guard", "runner_identity", "approved_snapshot_inventory", "execution_blocker"}
    for item in result["evidence"].values():
        assert len(item["sha256"]) == 64
        assert item["size_bytes"] > 0
    for field in ("authoritative_gate", "generation_authorized", "human_review_authorized", "golden_approved", "publication_ready", "seeds_2_to_4_authorized"):
        assert result[field] is False


def test_rejects_network_source_sha_or_guard_drift(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    source_sha = "a" * 40
    network, runner, snapshots, blocker = _files(tmp_path, source_sha)
    bad = _network("b" * 40)
    _write(network, bad)
    with pytest.raises(RuntimeError, match="NETWORK_SOURCE_SHA_DRIFT"):
        bind(source_sha=source_sha, branch="phase18/story-intelligence", network=network, runner=runner, snapshots=snapshots, blocker=blocker)
    bad = _network(source_sha); bad["external_network_paths_blocked"] = False
    _write(network, bad)
    with pytest.raises(RuntimeError, match="NETWORK_GUARD_NOT_PROVEN"):
        bind(source_sha=source_sha, branch="phase18/story-intelligence", network=network, runner=runner, snapshots=snapshots, blocker=blocker)


def test_rejects_runner_without_cuda_native_bf16(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    source_sha = "a" * 40
    network, runner, snapshots, blocker = _files(tmp_path, source_sha)
    bad = _runner(source_sha); bad["runtime"]["native_bf16"] = False
    _write(runner, bad)
    with pytest.raises(RuntimeError, match="RUNNER_CUDA_BF16_NOT_PROVEN"):
        bind(source_sha=source_sha, branch="phase18/story-intelligence", network=network, runner=runner, snapshots=snapshots, blocker=blocker)


def test_rejects_unready_or_empty_approved_snapshot_inventory(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    source_sha = "a" * 40
    network, runner, snapshots, blocker = _files(tmp_path, source_sha)
    bad = _snapshots(); bad["flux"]["file_count"] = 0
    _write(snapshots, bad)
    with pytest.raises(RuntimeError, match="SNAPSHOT_MODEL_NOT_READY:flux"):
        bind(source_sha=source_sha, branch="phase18/story-intelligence", network=network, runner=runner, snapshots=snapshots, blocker=blocker)


def test_rejects_non_ready_blocker(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    source_sha = "b" * 40
    network, runner, snapshots, blocker = _files(tmp_path, source_sha)
    bad = _blocker(); bad["ready_for_authoritative_golden_preflight"] = False; bad["blockers"] = ["CUDA_UNAVAILABLE"]
    _write(blocker, bad)
    with pytest.raises(RuntimeError, match="AUTHORITATIVE_PREGEN_NOT_READY"):
        bind(source_sha=source_sha, branch="phase18/story-intelligence", network=network, runner=runner, snapshots=snapshots, blocker=blocker)


def test_rejects_branch_or_source_drift(tmp_path, monkeypatch):
    import tools.phase18_bind_authoritative_first_golden_pre_generation_evidence as mod
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    source_sha = "c" * 40
    network, runner, snapshots, blocker = _files(tmp_path, source_sha)
    with pytest.raises(RuntimeError, match="AUTHORITATIVE_PREGEN_BRANCH_DRIFT"):
        bind(source_sha=source_sha, branch="main", network=network, runner=runner, snapshots=snapshots, blocker=blocker)
    with pytest.raises(RuntimeError, match="AUTHORITATIVE_PREGEN_SOURCE_SHA_INVALID"):
        bind(source_sha="short", branch="phase18/story-intelligence", network=network, runner=runner, snapshots=snapshots, blocker=blocker)
