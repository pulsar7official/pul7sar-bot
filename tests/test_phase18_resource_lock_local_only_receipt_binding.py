from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOURCE_LOCK = ROOT / "tools" / "phase18_colab_first_genuine_resources_locked.py"


def _source() -> str:
    return RESOURCE_LOCK.read_text(encoding="utf-8")


def test_resource_lock_verifies_local_only_receipts_before_candidate_generation() -> None:
    text = _source()
    verifier = 'str(ROOT / "tools" / "phase18_verify_local_only_model_receipts.py")'
    candidate = 'command = [sys.executable, str(ROOT / "tools" / "phase18_colab_first_genuine_golden.py")]'

    assert verifier in text
    assert 'str(QWEN_MODEL_CACHE)' in text
    assert 'str(FLUX_MODEL_CACHE)' in text
    assert 'str(LOCAL_ONLY_MODEL_RECEIPTS)' in text
    assert verifier in text and candidate in text
    assert text.index(verifier) < text.index(candidate)


def test_resource_lock_local_only_contract_is_fail_closed() -> None:
    text = _source()

    assert 'payload.get("status") != "PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED"' in text
    assert 'payload.get("cost_mode") != "$0-local"' in text
    assert 'payload.get("network_download_authorized") is not False' in text
    assert 'payload.get("local_files_only") is not True' in text
    assert '("generation_authorized", "publication_ready", "seeds_2_to_4_authorized")' in text


def test_resource_lock_binds_local_only_receipt_hash_into_evidence() -> None:
    text = _source()

    assert '"local_only_model_receipts": _record(LOCAL_ONLY_MODEL_RECEIPTS)' in text
    assert '"local_only_model_receipts_bound": True' in text
    assert '"network_download_authorized": False' in text
    assert '"local_files_only": True' in text


def test_resource_lock_preserves_downstream_human_and_publication_gates() -> None:
    text = _source()

    assert '"human_visual_review_required": True' in text
    assert '"human_visual_review_approved": False' in text
    assert '"golden_quality_approved": False' in text
    assert '"publication_ready": False' in text
    assert '"seeds_2_to_4_authorized": False' in text
