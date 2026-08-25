from engine.intelligence.hybrid_scene_contract import HybridSceneContractRegistry
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


def test_every_family_has_hybrid_contract():
    for family in EditorialSceneFamily:
        c = HybridSceneContractRegistry.get(family)
        assert c.family is family
        assert c.generated_owns
        assert c.deterministic_owns
        assert c.required_clear_zones
        assert "PUL7SAR approved brand master" in c.deterministic_owns


def test_result_exact_score_is_never_generated():
    c = HybridSceneContractRegistry.get(EditorialSceneFamily.RESULT_STATEMENT)
    assert "exact score" in c.deterministic_owns
    assert all("score" not in item for item in c.generated_owns)
    assert "invented score visible in generated base" in c.reject_if


def test_verified_subject_identity_is_exact():
    c = HybridSceneContractRegistry.get(EditorialSceneFamily.VERIFIED_SUBJECT_NEWS)
    assert "verified subject cutout/asset" in c.deterministic_owns
    assert "generated human presented as the named real person" in c.reject_if


def test_tactical_geometry_remains_deterministic():
    c = HybridSceneContractRegistry.get(EditorialSceneFamily.TACTICAL_BOARD)
    assert "pitch geometry" in c.deterministic_owns
    assert "movement arrows" in c.deterministic_owns
    assert "generated tactical geometry" in c.reject_if


def test_no_family_allows_generated_brand_or_crest_ownership():
    for family in EditorialSceneFamily:
        c = HybridSceneContractRegistry.get(family)
        generated = " ".join(c.generated_owns).lower()
        assert "crest" not in generated
        assert "pul7sar" not in generated
        assert "brand master" not in generated
