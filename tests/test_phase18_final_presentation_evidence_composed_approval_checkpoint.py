from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.phase18_continue_final_presentation_evidence_to_composed_approval as subject


def _png(sha: str = "a" * 64) -> dict[str, object]:
    return {
        "repository_relative_path": "artifacts/composed.png",
        "sha256": sha,
        "byte_size": 123,
    }


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, approved: bool = True):
    story = "b" * 64
    png = _png()
    cs279_path = tmp_path / "cs279.json"
    cs279_path.write_text("{}", encoding="utf-8")
    external = tmp_path / "external_review.json"
    external.write_text("{}", encoding="utf-8")
    checkpoint_path = tmp_path / "cs325.json"
    checkpoint_path.write_text(
        json.dumps(
            {
                "schema": subject.CS325_SCHEMA,
                "status": "FINAL_PRESENTATION_REVIEW_EVIDENCE_REQUIRED",
                "authoritative": False,
                "story_snapshot_sha256": story,
                "candidate_png": {"sha256": "c" * 64},
                "composed_candidate_png": png,
                "cs279_receipt": "cs279.json",
                "golden_quality_approved": True,
                "human_visual_review_approved": True,
                "final_presentation_review_requested": True,
                "final_presentation_review_executed": False,
                "final_presentation_review_approved": False,
                "exact_brand_integrity_approved": False,
                "typography_integrity_approved": False,
                "composed_visual_approved": False,
                "semantic_approved": False,
                "genuine_golden_png_created": False,
                "publication_ready": False,
            }
        ),
        encoding="utf-8",
    )
    cs279 = {
        "schema": subject.CS279_SCHEMA,
        "story_snapshot_sha256": story,
        "composed_candidate_png": png,
        "final_presentation_review_requested": True,
        "final_presentation_review_executed": False,
        "final_presentation_review_approved": False,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    cs280 = {
        "schema": subject.CS280_SCHEMA,
        "story_snapshot_sha256": story,
        "composed_candidate_png": png,
        "final_presentation_review_approved": approved,
        "exact_brand_integrity_approved": approved,
        "typography_integrity_approved": approved,
        "semantic_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
    }
    monkeypatch.setattr(
        subject,
        "verify_composed_candidate_final_presentation_review_request",
        lambda *_args, **_kwargs: cs279,
    )

    def build280(_cs279, review, output, *, repo_root):
        assert review == external
        output.mkdir()
        path = output / "cs280.json"
        path.write_text("{}", encoding="utf-8")
        return path

    monkeypatch.setattr(
        subject,
        "build_composed_candidate_final_presentation_review_evidence",
        build280,
    )
    monkeypatch.setattr(
        subject,
        "verify_composed_candidate_final_presentation_review_evidence",
        lambda *_args, **_kwargs: cs280,
    )
    return checkpoint_path, external, story, png, cs280


def test_approved_external_cs280_continues_to_exact_cs281(tmp_path, monkeypatch):
    checkpoint, external, story, png, _cs280 = _fixture(tmp_path, monkeypatch, approved=True)
    cs273_path = tmp_path / "cs273.json"
    cs273_path.write_text("{}", encoding="utf-8")
    cs273 = {
        "schema": subject.CS273_SCHEMA,
        "story_snapshot_sha256": story,
        "composed_candidate_png": png,
    }
    monkeypatch.setattr(
        subject,
        "_derive_exact_cs273",
        lambda *_args, **_kwargs: (cs273_path, cs273),
    )

    calls = {"cs281": 0}

    def build281(given273, given280, output, *, repo_root):
        calls["cs281"] += 1
        assert given273 == cs273_path
        assert given280.name == "cs280.json"
        output.mkdir()
        path = output / "cs281.json"
        path.write_text("{}", encoding="utf-8")
        return path

    monkeypatch.setattr(
        subject,
        "build_composed_candidate_final_composed_visual_approval",
        build281,
    )
    monkeypatch.setattr(
        subject,
        "verify_composed_candidate_final_composed_visual_approval",
        lambda *_args, **_kwargs: {
            "schema": subject.CS281_SCHEMA,
            "story_snapshot_sha256": story,
            "composed_candidate_png": png,
            "composed_visual_approved": True,
            "semantic_approved": False,
            "genuine_golden_png_created": False,
            "publication_ready": False,
        },
    )

    out = subject.continue_final_presentation_evidence_to_composed_approval(
        checkpoint, external, tmp_path / "out", repo_root=tmp_path
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert calls["cs281"] == 1
    assert payload["status"] == "FINAL_COMPOSED_VISUAL_APPROVED_AWAITING_FINAL_SEMANTIC_APPROVAL"
    assert payload["final_presentation_review_approved"] is True
    assert payload["exact_brand_integrity_approved"] is True
    assert payload["typography_integrity_approved"] is True
    assert payload["composed_visual_approved"] is True
    assert payload["semantic_approved"] is False
    assert payload["genuine_golden_png_created"] is False
    assert payload["publication_ready"] is False
    assert payload["authoritative"] is False


def test_rejected_external_cs280_never_builds_cs281(tmp_path, monkeypatch):
    checkpoint, external, _story, _png_value, _cs280 = _fixture(
        tmp_path, monkeypatch, approved=False
    )
    monkeypatch.setattr(
        subject,
        "build_composed_candidate_final_composed_visual_approval",
        lambda *_args, **_kwargs: pytest.fail(
            "CS281 must not run after presentation rejection"
        ),
    )
    out = subject.continue_final_presentation_evidence_to_composed_approval(
        checkpoint, external, tmp_path / "out", repo_root=tmp_path
    )
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["status"] == "COMPOSED_CANDIDATE_REJECTED_BY_FINAL_PRESENTATION_REVIEW"
    assert payload["cs281_receipt"] is None
    assert payload["composed_visual_approved"] is False
    assert payload["semantic_approved"] is False
    assert payload["publication_ready"] is False


def test_cs280_composed_byte_drift_fails_closed(tmp_path, monkeypatch):
    checkpoint, external, _story, _png_value, cs280 = _fixture(
        tmp_path, monkeypatch, approved=True
    )
    cs280["composed_candidate_png"] = _png("d" * 64)
    with pytest.raises(ValueError, match="CS280_COMPOSED_BYTES_DRIFT"):
        subject.continue_final_presentation_evidence_to_composed_approval(
            checkpoint, external, tmp_path / "out", repo_root=tmp_path
        )


def test_orchestrator_does_not_generate_review_or_grant_semantic_publication():
    source = Path(subject.__file__).read_text(encoding="utf-8")
    assert "build_composed_candidate_final_presentation_review_evidence" in source
    assert "build_composed_candidate_final_composed_visual_approval" in source
    assert "QwenImagePipeline" not in source
    assert "build_composed_candidate_final_semantic_approval" not in source
    assert '"semantic_approved": False' in source
    assert '"genuine_golden_png_created": False' in source
    assert '"publication_ready": False' in source
    assert "independent_manual_final_presentation_review" not in source
