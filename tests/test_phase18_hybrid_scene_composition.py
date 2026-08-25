import pytest

from engine.intelligence.hybrid_scene_composition import (
    HybridCompositionPlan, HybridCompositionRegistry, HybridLayer, LayerOwner,
)
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def test_all_generative_families_keep_exact_layers_out_of_synthesis():
    families = (
        EditorialSceneFamily.RESULT_STATEMENT,
        EditorialSceneFamily.TRANSFER_SIGNATURE,
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
        EditorialSceneFamily.DATA_MONUMENT,
        EditorialSceneFamily.EVENT_EDITORIAL,
    )
    for family in families:
        plan = HybridCompositionRegistry.get(family)
        plan.validate()
        assert plan.base_scene.owner is LayerOwner.SYNTHESIS
        assert plan.generated_base_must_be_unbranded
        assert plan.generated_base_must_have_no_readable_facts
        assert plan.publication_ready is False
        assert all(l.owner is not LayerOwner.SYNTHESIS for l in plan.layers)


def test_result_score_and_club_identity_are_exact_owned():
    plan = HybridCompositionRegistry.get(EditorialSceneFamily.RESULT_STATEMENT)
    owners = {l.name: l.owner for l in plan.layers}
    assert owners["score"] is LayerOwner.DETERMINISTIC
    assert owners["club_name"] is LayerOwner.DETERMINISTIC
    assert owners["club_crest"] is LayerOwner.VERIFIED_ASSET


def test_verified_subject_identity_cannot_be_generated():
    plan = HybridCompositionRegistry.get(EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
    subject = next(l for l in plan.layers if l.name == "verified_subject")
    assert subject.owner is LayerOwner.VERIFIED_ASSET
    assert subject.required


def test_fail_closed_if_synthesis_claims_exact_score():
    plan = HybridCompositionPlan(
        family=EditorialSceneFamily.RESULT_STATEMENT,
        base_scene=HybridLayer("environment", LayerOwner.SYNTHESIS),
        layers=(HybridLayer("score", LayerOwner.SYNTHESIS),),
    )
    with pytest.raises(ValueError, match="exact layer cannot be synthesis-owned"):
        plan.validate()


def test_tactical_never_enters_synthesis_base_path():
    with pytest.raises(ValueError, match="TACTICAL_BOARD_HAS_NO_SYNTHESIS_BASE"):
        HybridCompositionRegistry.get(EditorialSceneFamily.TACTICAL_BOARD)
