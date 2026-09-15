from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6.yml"


def _workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_golden_v6_requires_local_only_receipt_verifier_before_replay() -> None:
    text = _workflow_text()
    verifier = "python tools/phase18_verify_local_only_model_receipts.py"
    replay = "- name: Replay exact model-cache semantic resource runtime and staging evidence"

    assert "test -f tools/phase18_verify_local_only_model_receipts.py" in text
    assert verifier in text
    assert replay in text
    assert text.index(verifier) < text.index(replay)


def test_golden_v6_binds_exact_qwen_and_flux_cache_receipts() -> None:
    text = _workflow_text()

    assert "output/phase18_gpu_smoke/qwen-model-cache.json" in text
    assert "output/phase18_gpu_smoke/flux-model-cache.json" in text
    assert "output/phase18_gpu_smoke/first-genuine-golden-v6-local-only-model-receipts.json" in text
    assert 'receipt.get("status") != "PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED"' in text


def test_golden_v6_local_only_gate_remains_fail_closed() -> None:
    text = _workflow_text()

    assert 'receipt.get("cost_mode") != "$0-local"' in text
    assert 'receipt.get("network_download_authorized") is not False' in text
    assert 'receipt.get("local_files_only") is not True' in text
    assert '("generation_authorized", "publication_ready", "seeds_2_to_4_authorized")' in text


def test_golden_v6_runner_and_offline_contract_are_unchanged() -> None:
    text = _workflow_text()

    assert "runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]" in text
    assert 'PUL7SAR_PHASE18_COST_MODE: $0-local' in text
    assert 'HF_HUB_OFFLINE: "1"' in text
    assert 'TRANSFORMERS_OFFLINE: "1"' in text
    assert "CUDA-enabled PyTorch is required" in text
