from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-golden-preflight-only.yml"


def _workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_preflight_only_workflow_is_gpu_bound_zero_cost_and_offline() -> None:
    text = _workflow()
    assert "runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]" in text
    assert "PUL7SAR_PHASE18_COST_MODE: $0-local" in text
    assert 'HF_HUB_OFFLINE: "1"' in text
    assert 'TRANSFORMERS_OFFLINE: "1"' in text
    assert 'test "$DISPATCH_REF" = "refs/heads/phase18/story-intelligence"' in text


def test_preflight_only_workflow_never_invokes_generation_or_publication() -> None:
    text = _workflow()
    forbidden = (
        "phase18_run_first_genuine_golden_v6_canonical_fresh.py",
        "phase18_package_first_genuine_golden_v6_review_bundle.py",
        "phase18_golden_review/",
        "seeds_2_to_4_authorized: true",
        "generation_authorized: true",
        "publication_ready: true",
    )
    for token in forbidden:
        assert token not in text


def test_preflight_probe_runs_after_identity_and_snapshot_capture() -> None:
    text = _workflow()
    runner = text.index("phase18_capture_first_golden_runner_identity.py")
    snapshots = text.index("phase18_capture_approved_snapshot_inventory.py")
    probe = text.index("phase18_probe_first_golden_execution_blocker.py")
    readiness = text.index("Assert preflight readiness and preserve fail-closed authority")
    upload = text.index("Upload preflight diagnostics only")
    assert runner < probe
    assert snapshots < probe
    assert probe < readiness < upload


def test_preflight_preserves_diagnostics_when_probe_reports_blockers() -> None:
    text = _workflow()
    assert "continue-on-error: true" in text
    assert "if: always()" in text
    assert "ready_for_authoritative_golden_preflight" in text
    assert 'p.get(field) is not False' in text
    assert "candidate host is not ready for authoritative Golden preflight" in text


def test_preflight_probe_execution_failure_cannot_be_masked_by_continue_on_error() -> None:
    text = _workflow()
    assert "BLOCKER_PROBE_OUTCOME: ${{ steps.blocker_probe.outcome }}" in text
    assert 'test "$BLOCKER_PROBE_OUTCOME" = "success"' in text
    assert "execution-blocker probe did not complete successfully" in text
    outcome_check = text.index('test "$BLOCKER_PROBE_OUTCOME" = "success"')
    json_read = text.index('json.loads(Path("output/phase18_gpu_smoke/preflight-execution-blocker.json")')
    assert outcome_check < json_read
