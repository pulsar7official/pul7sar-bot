from engine.intelligence.pre_generation_scene_lock import PreGenerationSceneLockRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def test_all_generative_families_are_association_football_locked():
    families = (
        EditorialSceneFamily.TRANSFER_SIGNATURE,
        EditorialSceneFamily.RESULT_STATEMENT,
        EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
        EditorialSceneFamily.DATA_MONUMENT,
        EditorialSceneFamily.EVENT_EDITORIAL,
    )
    for family in families:
        lock = PreGenerationSceneLockRegistry.get(family)
        assert lock.sport == "association_football"
        assert lock.semantic_anchor
        assert lock.required_visual_cues
        assert "American football" in lock.forbidden_visual_cues
        assert "generated logos or crests" in lock.forbidden_visual_cues


def test_result_lock_rejects_gridiron_and_invented_score_semantics():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.RESULT_STATEMENT)
    assert "gridiron field markings" in lock.forbidden_visual_cues
    assert "invented score digits" in lock.forbidden_visual_cues
    prompt = PreGenerationSceneLockRegistry.locked_prompt(EditorialSceneFamily.RESULT_STATEMENT, "scene")
    assert "SPORT LOCK: association football (soccer) only" in prompt
    assert "post-match association-football result atmosphere" in prompt


def test_data_monument_is_not_allowed_to_become_a_rock_landscape():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.DATA_MONUMENT)
    assert "architectural information pedestal or monument" in lock.required_visual_cues
    assert "natural rock formation" in lock.forbidden_visual_cues
    assert "generic outdoor landscape" in lock.forbidden_visual_cues


def test_verified_subject_scene_reserves_identity_for_verified_asset():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
    assert "clear empty hero zone" in lock.required_visual_cues
    assert "human face" in lock.forbidden_visual_cues
    assert "invented athlete" in lock.forbidden_visual_cues


def test_tactical_board_stays_deterministic_first():
    try:
        PreGenerationSceneLockRegistry.get(EditorialSceneFamily.TACTICAL_BOARD)
    except ValueError as exc:
        assert str(exc) == "TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST"
    else:
        raise AssertionError("TACTICAL_BOARD must not enter generative scene lock")
