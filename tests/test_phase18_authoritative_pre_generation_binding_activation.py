from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py"


def test_binding_is_required_before_canonical_candidate_1():
    text = WRAPPER.read_text(encoding="utf-8")
    bind_call = text.index("pre_generation_binding = bind_pre_generation_evidence(")
    binding_write = text.index("_write_json(pre_generation_binding_path, pre_generation_binding)")
    freshness_capture = text.index("baseline = capture_freshness()")
    canonical_call = text.index("canonical = run_canonical(")
    assert bind_call < binding_write < freshness_capture < canonical_call


def test_binding_consumes_all_authoritative_pre_generation_evidence():
    text = WRAPPER.read_text(encoding="utf-8")
    for token in (
        "network=_inside_repository(network_evidence_path)",
        "runner=_inside_repository(runner_identity_path)",
        "snapshots=_inside_repository(snapshot_inventory_path)",
        "blocker=_inside_repository(execution_blocker_path)",
        "source_sha=expected_commit",
        'branch=EXPECTED_BRANCH',
    ):
        assert token in text


def test_wrapper_reports_binding_without_escalating_authority():
    text = WRAPPER.read_text(encoding="utf-8")
    assert '"pre_generation_evidence_bound": True' in text
    assert '"pre_generation_evidence_binding_schema"' in text
    for field in (
        '"authoritative_gate": False',
        '"network_download_authorized": False',
        '"generation_authorized": False',
        '"publication_ready": False',
        '"seeds_2_to_4_authorized": False',
    ):
        assert field in text
