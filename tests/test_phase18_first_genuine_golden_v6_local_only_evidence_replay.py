from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_workflow_replays_bound_local_only_model_receipts() -> None:
    workflow = _read(".github/workflows/phase18-first-genuine-golden-v6.yml")

    assert '"local_only_model_receipts",' in workflow
    assert 'evidence["local_only_model_receipts"]' in workflow
    assert 'pul7sar-phase18-local-only-model-receipt-verification-v1' in workflow
    assert 'PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED' in workflow
    assert 'network_download_authorized' in workflow
    assert 'local_files_only' in workflow
    assert 'local-only model receipt network policy drift during replay' in workflow
    assert 'local-only Qwen identity drift during replay' in workflow
    assert 'local-only FLUX identity drift during replay' in workflow


def test_artifact_verifier_requires_tenth_local_only_evidence_record() -> None:
    verifier = _read("tools/phase18_verify_first_genuine_golden_v6_artifact.py")

    assert '"local_only_model_receipts",' in verifier
    assert 'resolved["local_only_model_receipts"]' in verifier
    assert 'pul7sar-phase18-local-only-model-receipt-verification-v1' in verifier
    assert 'PHASE18_LOCAL_ONLY_MODEL_RECEIPTS_VERIFIED' in verifier
    assert 'FIRST_GENUINE_GOLDEN_V6_EVIDENCE_LOCAL_ONLY_NETWORK_POLICY_DRIFT' in verifier
    assert 'FIRST_GENUINE_GOLDEN_V6_EVIDENCE_LOCAL_ONLY_QWEN_DRIFT' in verifier
    assert 'FIRST_GENUINE_GOLDEN_V6_EVIDENCE_LOCAL_ONLY_FLUX_DRIFT' in verifier


def test_replay_keeps_downstream_authorities_fail_closed() -> None:
    workflow = _read(".github/workflows/phase18-first-genuine-golden-v6.yml")
    verifier = _read("tools/phase18_verify_first_genuine_golden_v6_artifact.py")

    for field in (
        "human_visual_review_approved",
        "golden_quality_approved",
        "publication_ready",
        "seeds_2_to_4_authorized",
    ):
        assert field in workflow
        assert field in verifier

    assert '"publication_ready": False' in verifier
    assert '"seeds_2_to_4_authorized": False' in verifier
