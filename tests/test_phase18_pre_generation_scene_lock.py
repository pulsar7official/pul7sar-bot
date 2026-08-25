from engine.intelligence.pre_generation_scene_lock import PreGenerationSceneLockRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


GENERATIVE_FAMILIES = (
    EditorialSceneFamily.TRANSFER_SIGNATURE,
    EditorialSceneFamily.RESULT_STATEMENT,
    EditorialSceneFamily.VERIFIED_SUBJECT_NEWS,
    EditorialSceneFamily.DATA_MONUMENT,
    EditorialSceneFamily.EVENT_EDITORIAL,
)


def test_all_generative_families_are_association_football_locked():
    for family in GENERATIVE_FAMILIES:
        lock = PreGenerationSceneLockRegistry.get(family)
        assert lock.sport == "association_football"
        assert lock.semantic_anchor
        assert lock.required_visual_cues
        assert "American football" in lock.forbidden_visual_cues
        assert "generated logos or crests" in lock.forbidden_visual_cues


def test_generator_prefix_is_compact_positive_sport_ownership_only():
    prefix = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.RESULT_STATEMENT).prompt_prefix()
    assert prefix == "Association soccer editorial scene. "
    assert "American football" not in prefix
    assert "gridiron" not in prefix


def test_result_lock_keeps_exact_score_outside_generator():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.RESULT_STATEMENT)
    assert "exact score absent" in lock.semantic_anchor
    assert "invented score digits" in lock.forbidden_visual_cues
    assert "exact score" in lock.exact_layers_reserved


def test_data_monument_is_man_made_information_architecture():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.DATA_MONUMENT)
    assert "man-made information pedestal" in lock.required_visual_cues
    assert "natural rock formation" in lock.forbidden_visual_cues
    assert "generic outdoor landscape" in lock.forbidden_visual_cues


def test_verified_subject_scene_reserves_identity_for_verified_asset():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
    assert "large empty hero zone" in lock.required_visual_cues
    assert "human face" in lock.forbidden_visual_cues
    assert "invented athlete" in lock.forbidden_visual_cues
    assert "verified real-person identity" in lock.exact_layers_reserved


def test_tactical_board_stays_deterministic_first():
    try:
        PreGenerationSceneLockRegistry.get(EditorialSceneFamily.TACTICAL_BOARD)
    except ValueError as exc:
        assert str(exc) == "TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST"
    else:
        raise AssertionError("TACTICAL_BOARD must not enter generative scene lock")
