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


def test_forbidden_concepts_are_qa_metadata_not_positive_prompt_tokens():
    forbidden_tokens = (
        "American football",
        "gridiron",
        "rugby",
        "basketball",
        "baseball",
        "ice-hockey",
        "tennis court",
    )
    for family in GENERATIVE_FAMILIES:
        prompt = PreGenerationSceneLockRegistry.locked_prompt(family, "premium cinematic scene")
        for token in forbidden_tokens:
            assert token.casefold() not in prompt.casefold(), (family.value, token, prompt)
        assert "association football" in prompt.casefold()
        assert "soccer" in prompt.casefold()


def test_result_lock_reserves_score_and_uses_positive_soccer_semantics():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.RESULT_STATEMENT)
    assert "gridiron field markings" in lock.forbidden_visual_cues
    assert "invented score digits" in lock.forbidden_visual_cues
    prompt = PreGenerationSceneLockRegistry.locked_prompt(EditorialSceneFamily.RESULT_STATEMENT, "scene")
    assert "post-match soccer result atmosphere" in prompt
    assert "classic round black-and-white soccer ball" in prompt
    assert "American football" not in prompt


def test_data_monument_is_locked_to_man_made_information_architecture():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.DATA_MONUMENT)
    assert "clearly man-made architectural information pedestal" in lock.required_visual_cues
    assert "natural rock formation" in lock.forbidden_visual_cues
    assert "generic outdoor landscape" in lock.forbidden_visual_cues
    prompt = PreGenerationSceneLockRegistry.locked_prompt(EditorialSceneFamily.DATA_MONUMENT, "scene")
    assert "premium indoor soccer information gallery" in prompt
    assert "natural rock" not in prompt.casefold()
    assert "mountain" not in prompt.casefold()


def test_verified_subject_scene_reserves_identity_for_verified_asset():
    lock = PreGenerationSceneLockRegistry.get(EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
    assert "large clear empty hero zone" in lock.required_visual_cues
    assert "human face" in lock.forbidden_visual_cues
    assert "invented athlete" in lock.forbidden_visual_cues


def test_tactical_board_stays_deterministic_first():
    try:
        PreGenerationSceneLockRegistry.get(EditorialSceneFamily.TACTICAL_BOARD)
    except ValueError as exc:
        assert str(exc) == "TACTICAL_BOARD_REMAINS_DETERMINISTIC_FIRST"
    else:
        raise AssertionError("TACTICAL_BOARD must not enter generative scene lock")
