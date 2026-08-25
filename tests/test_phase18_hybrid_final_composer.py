import pytest

from engine.intelligence.hybrid_final_composer import (
    FinalCompositionMode,
    HybridFinalComposer,
)
from engine.intelligence.hybrid_scene_composition import LayerOwner
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def test_generating_families_compile_as_hybrid_and_keep_exact_ownership():
    families = (
        EditorialSceneFamily.RESULT_STATEMENT,
        EditorialSceneFamily.TRANSFER_SIGNATURE,
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
        EditorialSceneFamily.DATA_MONUMENT,
        EditorialSceneFamily.EVENT_EDITORIAL,
    )
    for family in families:
        plan = HybridFinalComposer.compile(family=family, story_key=f"story-{family.value}")
        assert plan.mode is FinalCompositionMode.HYBRID
        assert plan.generated_base_required
        assert plan.generated_base_must_be_unbranded
        assert plan.generated_base_must_have_no_readable_facts
        assert plan.publication_ready is False
        assert all(layer.owner is not LayerOwner.SYNTHESIS for layer in plan.layers)


def test_result_exact_score_and_identity_survive_final_compile():
    plan = HybridFinalComposer.compile(
        family=EditorialSceneFamily.RESULT_STATEMENT,
        story_key="result-arsenal-example",
    )
    owners = {layer.name: layer.owner for layer in plan.layers}
    assert owners["score"] is LayerOwner.DETERMINISTIC
    assert owners["club_name"] is LayerOwner.DETERMINISTIC
    assert owners["club_crest"] is LayerOwner.VERIFIED_ASSET


def test_verified_subject_remains_required_verified_asset():
    plan = HybridFinalComposer.compile(
        family=EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
        story_key="verified-subject-example",
    )
    subject = next(layer for layer in plan.layers if layer.name == "verified_subject")
    assert subject.required
    assert subject.owner is LayerOwner.VERIFIED_ASSET


def test_tactical_is_deterministic_first_without_generated_base():
    plan = HybridFinalComposer.compile(
        family=EditorialSceneFamily.TACTICAL_BOARD,
        story_key="tactical-example",
    )
    assert plan.mode is FinalCompositionMode.DETERMINISTIC_FIRST
    assert not plan.generated_base_required
    owners = {layer.name: layer.owner for layer in plan.layers}
    assert owners["exact_tactical_geometry"] is LayerOwner.DETERMINISTIC


def test_recent_archetypes_are_avoided_when_alternatives_exist():
    first = HybridFinalComposer.compile(
        family=EditorialSceneFamily.EVENT_EDITORIAL,
        story_key="same-event",
        seed=11,
    )
    second = HybridFinalComposer.compile(
        family=EditorialSceneFamily.EVENT_EDITORIAL,
        story_key="same-event",
        recent_archetypes=(first.archetype_id,),
        seed=11,
    )
    assert second.archetype_id != first.archetype_id


def test_empty_story_key_fails_closed():
    with pytest.raises(ValueError, match="story_key is required"):
        HybridFinalComposer.compile(
            family=EditorialSceneFamily.RESULT_STATEMENT,
            story_key="   ",
        )
