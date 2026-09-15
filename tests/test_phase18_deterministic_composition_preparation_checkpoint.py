from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "phase18_prepare_deterministic_composition_checkpoint.py"


def _source() -> str:
    return TOOL.read_text(encoding="utf-8")


def test_cs319_exists_and_reuses_verified_cs269_cs270_contracts() -> None:
    source = _source()
    assert "verify_canonical_candidate_generated_layer_qa" in source
    assert "build_deterministic_composition_request" in source
    assert "verify_deterministic_composition_request" in source
    assert "build_composition_execution_preflight" in source
    assert "verify_composition_execution_preflight" in source
    assert "generated_layer_qa_approved" in source


def test_cs319_never_invents_composition_inputs_or_executes_pixels() -> None:
    source = _source()
    assert "--composition-manifest" in source
    assert "--payload-manifest" in source
    assert '"checkpoint_never_executes_composition": True' in source
    assert '"checkpoint_never_synthesizes_layer_inputs": True' in source
    assert '"authoritative": False' in source
    assert "render(" not in source
    assert "Image.open" not in source
    assert "QwenImagePipeline" not in source


def test_cs319_keeps_all_downstream_authorities_closed() -> None:
    source = _source()
    for field in (
        "composition_executed",
        "composed_visual_approved",
        "semantic_approved",
        "human_visual_review_approved",
        "golden_quality_approved",
        "genuine_golden_png_created",
        "publication_ready",
    ):
        assert f'"{field}": False' in source
    assert "_assert_downstream_closed(cs268" in source
    assert "_assert_downstream_closed(cs269" in source
    assert "_assert_downstream_closed(cs270" in source


def test_cs319_requires_repository_bound_explicit_manifests() -> None:
    source = _source()
    assert "QWEN_COMPOSITION_PREPARATION_OUTPUT_OUTSIDE_REPOSITORY" in source
    assert "QWEN_COMPOSITION_PREPARATION_MANIFEST_INVALID" in source
    assert "QWEN_COMPOSITION_PREPARATION_PAYLOAD_MANIFEST_INVALID" in source
    assert '"explicit_repository_composition_manifest_required": True' in source
    assert '"explicit_repository_payload_manifest_required_for_cs270": True' in source
    assert '"missing_or_drifting_inputs_fail_closed": True' in source


def test_cs319_reports_the_exact_precomposition_blocking_stage() -> None:
    source = _source()
    assert 'status = "COMPOSITION_INPUT_MANIFEST_BLOCKED"' in source
    assert 'status = "DETERMINISTIC_PAYLOAD_MANIFEST_REQUIRED"' in source
    assert 'status = "DETERMINISTIC_PAYLOAD_BINDING_BLOCKED"' in source
    assert 'status = "COMPOSITION_EXECUTION_PREFLIGHT_READY"' in source
    assert "composition_request_ready" in source
    assert "composition_execution_ready" in source


def test_cs319_rejects_story_or_candidate_lineage_drift() -> None:
    source = _source()
    assert "QWEN_COMPOSITION_PREPARATION_CS269_LINEAGE_DRIFT" in source
    assert "QWEN_COMPOSITION_PREPARATION_CS270_LINEAGE_DRIFT" in source
    assert 'cs269.get("story_snapshot_sha256") != story_sha' in source
    assert 'cs269.get("candidate_png") != candidate' in source
    assert 'cs270.get("story_snapshot_sha256") != story_sha' in source
    assert 'cs270.get("candidate_png") != candidate' in source
