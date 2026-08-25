import json
from pathlib import Path

import pytest
from PIL import Image

from engine.intelligence.generated_base_provenance import GeneratedBaseProvenance
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


RESERVED = [
    "PUL7SAR brand",
    "readable editorial copy",
    "club crests and branded garments",
    "exact score",
    "exact statistics",
    "verified real-person identity",
    "exact sport geometry",
]


def _fixture(tmp_path: Path, *, contract="pul7sar-cpu-cross-family-synthesis-v4", sport="association_football", token_count=42, limit=75):
    image = tmp_path / "result_statement.png"
    Image.new("RGB", (64, 80), (10, 12, 14)).save(image)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "contract": contract,
        "publication_ready": False,
        "scenes": [{
            "family": "result_statement",
            "file": image.name,
            "sport_lock": sport,
            "prompt_policy": "compact_positive_scene_ownership_fail_closed_token_budget",
            "prompt_token_count": token_count,
            "prompt_usable_limit": limit,
            "generated_subject_policy": "environment only",
            "exact_layers_reserved": RESERVED,
        }],
    }), encoding="utf-8")
    return image, manifest


def test_valid_synthesis_manifest_binds_image_and_family(tmp_path):
    image, manifest = _fixture(tmp_path)
    p = GeneratedBaseProvenance.from_manifest(
        manifest_path=str(manifest),
        family=EditorialSceneFamily.RESULT_STATEMENT,
        image_path=str(image),
    )
    assert p.synthesis_contract == "pul7sar-cpu-cross-family-synthesis-v4"
    assert p.sport_lock == "association_football"
    assert p.prompt_token_count <= p.prompt_usable_limit


def test_unknown_synthesis_contract_fails_closed(tmp_path):
    image, manifest = _fixture(tmp_path, contract="unknown-generator-v1")
    with pytest.raises(ValueError, match="UNTRUSTED_SYNTHESIS_CONTRACT"):
        GeneratedBaseProvenance.from_manifest(
            manifest_path=str(manifest), family=EditorialSceneFamily.RESULT_STATEMENT, image_path=str(image)
        )


def test_wrong_sport_fails_closed(tmp_path):
    image, manifest = _fixture(tmp_path, sport="american_football")
    with pytest.raises(ValueError, match="SPORT_LOCK_MISMATCH"):
        GeneratedBaseProvenance.from_manifest(
            manifest_path=str(manifest), family=EditorialSceneFamily.RESULT_STATEMENT, image_path=str(image)
        )


def test_truncated_prompt_provenance_fails_closed(tmp_path):
    image, manifest = _fixture(tmp_path, token_count=80, limit=75)
    with pytest.raises(ValueError, match="PROMPT_BUDGET_PROVENANCE_INVALID"):
        GeneratedBaseProvenance.from_manifest(
            manifest_path=str(manifest), family=EditorialSceneFamily.RESULT_STATEMENT, image_path=str(image)
        )


def test_manifest_filename_must_match_actual_base(tmp_path):
    image, manifest = _fixture(tmp_path)
    other = tmp_path / "other.png"
    Image.new("RGB", (64, 80), (1, 2, 3)).save(other)
    with pytest.raises(ValueError, match="SYNTHESIS_IMAGE_MANIFEST_MISMATCH"):
        GeneratedBaseProvenance.from_manifest(
            manifest_path=str(manifest), family=EditorialSceneFamily.RESULT_STATEMENT, image_path=str(other)
        )
