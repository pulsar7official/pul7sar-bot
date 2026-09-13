from __future__ import annotations

from pathlib import Path

import pytest

import tools.phase18_run_first_golden_pre_gpu_attested as runner


SHA = "a" * 40


def _ready_receipt() -> dict[str, object]:
    return {
        "schema": "pul7sar-phase18-first-golden-pre-gpu-probe-v1",
        "ready_for_authoritative_golden_preflight": True,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def _ready_attestation() -> dict[str, object]:
    return {
        "schema": "pul7sar-phase18-first-golden-pre-gpu-attestation-v1",
        "receipt_attested": True,
        "ready_for_authoritative_golden_preflight": True,
        "network_download_authorized": False,
        "generation_authorized": False,
        "publication_ready": False,
        "seeds_2_to_4_authorized": False,
    }


def test_runner_writes_receipt_before_attestation_and_returns_ready(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    order: list[str] = []

    def fake_inspect(*, expected_commit: str) -> dict[str, object]:
        assert expected_commit == SHA
        order.append("inspect")
        return _ready_receipt()

    def fake_attest(*, receipt_path: Path, expected_commit: str) -> dict[str, object]:
        assert expected_commit == SHA
        assert receipt_path.is_file()
        order.append("attest")
        return _ready_attestation()

    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "inspect_pre_gpu", fake_inspect)
    monkeypatch.setattr(runner, "attest", fake_attest)

    result = runner.run(
        expected_commit=SHA,
        receipt_path=Path("out/receipt.json"),
        attestation_path=Path("out/attestation.json"),
    )

    assert order == ["inspect", "attest"]
    assert result["ready_for_authoritative_golden_preflight"] is True
    assert result["receipt_attested"] is True
    assert result["blockers"] == []
    assert result["generation_authorized"] is False
    assert result["publication_ready"] is False
    assert result["seeds_2_to_4_authorized"] is False


def test_runner_fails_closed_when_pre_gpu_receipt_is_not_ready(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    receipt = _ready_receipt()
    receipt["ready_for_authoritative_golden_preflight"] = False

    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "inspect_pre_gpu", lambda **_: receipt)
    monkeypatch.setattr(runner, "attest", lambda **_: _ready_attestation())

    result = runner.run(
        expected_commit=SHA,
        receipt_path=Path("receipt.json"),
        attestation_path=Path("attestation.json"),
    )

    assert result["ready_for_authoritative_golden_preflight"] is False
    assert "PRE_GPU_RECEIPT_NOT_READY" in result["blockers"]


def test_runner_fails_closed_when_attestation_does_not_verify(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    attestation = _ready_attestation()
    attestation["receipt_attested"] = False

    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "inspect_pre_gpu", lambda **_: _ready_receipt())
    monkeypatch.setattr(runner, "attest", lambda **_: attestation)

    result = runner.run(
        expected_commit=SHA,
        receipt_path=Path("receipt.json"),
        attestation_path=Path("attestation.json"),
    )

    assert result["ready_for_authoritative_golden_preflight"] is False
    assert "PRE_GPU_RECEIPT_NOT_ATTESTED" in result["blockers"]


def test_runner_rejects_authority_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    receipt = _ready_receipt()
    receipt["generation_authorized"] = True

    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "inspect_pre_gpu", lambda **_: receipt)
    monkeypatch.setattr(runner, "attest", lambda **_: _ready_attestation())

    result = runner.run(
        expected_commit=SHA,
        receipt_path=Path("receipt.json"),
        attestation_path=Path("attestation.json"),
    )

    assert result["ready_for_authoritative_golden_preflight"] is False
    assert "RECEIPT_GENERATION_AUTHORITY_DRIFT" in result["blockers"]


def test_runner_rejects_invalid_expected_commit_without_running_probes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)

    def forbidden(**_: object) -> dict[str, object]:
        raise AssertionError("probe must not run for invalid immutable commit")

    monkeypatch.setattr(runner, "inspect_pre_gpu", forbidden)
    monkeypatch.setattr(runner, "attest", forbidden)

    result = runner.run(
        expected_commit="not-a-sha",
        receipt_path=Path("receipt.json"),
        attestation_path=Path("attestation.json"),
    )

    assert result["ready_for_authoritative_golden_preflight"] is False
    assert result["blockers"] == ["EXPECTED_COMMIT_INVALID"]


def test_runner_rejects_same_receipt_and_attestation_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="MUST_DIFFER"):
        runner.run(
            expected_commit=SHA,
            receipt_path=Path("same.json"),
            attestation_path=Path("same.json"),
        )


def test_runner_rejects_output_escape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="ESCAPES_REPOSITORY"):
        runner.run(
            expected_commit=SHA,
            receipt_path=tmp_path.parent / "outside.json",
            attestation_path=Path("attestation.json"),
        )
