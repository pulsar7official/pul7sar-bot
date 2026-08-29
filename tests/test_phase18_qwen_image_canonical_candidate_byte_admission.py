from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct

import pytest

import engine.intelligence.qwen_image_canonical_candidate_byte_admission as admission
from engine.intelligence.qwen_image_one_shot_canonical_inference import (
    ONE_SHOT_CANONICAL_INFERENCE_SCHEMA,
)


def _png(width: int = 32, height: int = 24) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", width, height)


def _source(candidate: bytes) -> dict:
    return {
        "schema": ONE_SHOT_CANONICAL_INFERENCE_SCHEMA,
        "receipt_sha256": "a" * 64,
        "story_snapshot_sha256": "b" * 64,
        "model_id": "Qwen/Qwen-Image-2512",
        "model_revision": "c" * 40,
        "cost_mode": "$0-local",
        "expected_runtime_fingerprint_sha256": "d" * 64,
        "observed_runtime_fingerprint_sha256": "d" * 64,
        "prompt": {"sha256": "e" * 64, "byte_size": 10},
        "negative_prompt": {"sha256": "f" * 64, "byte_size": 0},
        "width": 32,
        "height": 24,
        "seed": 7,
        "num_inference_steps": 8,
        "guidance_scale": 1.0,
        "png": {
            "filename": "canonical_candidate.png",
            "sha256": hashlib.sha256(candidate).hexdigest(),
            "byte_size": len(candidate),
            "width": 32,
            "height": 24,
        },
        "production_semantic_replay_executed": True,
        "fresh_story_gates_passed": True,
        "controlled_trial_preflight_valid": True,
        "canonical_generation_authorized": True,
        "inference_executed": True,
        "genuine_canonical_inference_executed": True,
        "genuine_golden_png_created": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }


def _fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    repo = tmp_path / "repo"
    run = repo / "artifacts" / "cs262"
    run.mkdir(parents=True)
    raw = _png()
    candidate = run / "canonical_candidate.png"
    candidate.write_bytes(raw)
    receipt = run / "canonical_inference_receipt.json"
    receipt.write_text("{}\n", encoding="utf-8")
    source = _source(raw)
    monkeypatch.setattr(admission, "verify_one_shot_canonical_inference", lambda *_args, **_kwargs: source)
    return repo, receipt, candidate, source


def test_admits_exact_candidate_without_upgrading_quality_authority(tmp_path, monkeypatch):
    repo, receipt, _candidate, _source_receipt = _fixture(tmp_path, monkeypatch)
    out = repo / "artifacts" / "cs263"
    run = admission.admit_canonical_candidate_bytes(receipt, out, repo_root=repo)
    result = admission.verify_canonical_candidate_byte_admission(run.receipt_path, repo_root=repo)
    assert result["candidate_bytes_admitted_for_post_generation_qa"] is True
    assert result["genuine_golden_png_created"] is False
    assert result["semantic_approved"] is False
    assert result["human_visual_review_approved"] is False
    assert result["golden_quality_approved"] is False
    assert result["publication_ready"] is False


def test_rejects_candidate_tamper_after_admission(tmp_path, monkeypatch):
    repo, receipt, candidate, _source_receipt = _fixture(tmp_path, monkeypatch)
    run = admission.admit_canonical_candidate_bytes(receipt, repo / "artifacts" / "cs263", repo_root=repo)
    candidate.write_bytes(_png(31, 24))
    with pytest.raises(ValueError, match="PNG_BYTE_DRIFT"):
        admission.verify_canonical_candidate_byte_admission(run.receipt_path, repo_root=repo)


def test_rejects_premature_golden_authority(tmp_path, monkeypatch):
    repo, receipt, _candidate, source = _fixture(tmp_path, monkeypatch)
    source["genuine_golden_png_created"] = True
    with pytest.raises(ValueError, match="PREMATURE_AUTHORITY:genuine_golden_png_created"):
        admission.admit_canonical_candidate_bytes(receipt, repo / "artifacts" / "cs263", repo_root=repo)


def test_rejects_symlinked_candidate(tmp_path, monkeypatch):
    repo, receipt, candidate, source = _fixture(tmp_path, monkeypatch)
    real = candidate.with_name("real.png")
    candidate.rename(real)
    candidate.symlink_to(real)
    source["png"]["sha256"] = hashlib.sha256(real.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="PNG_OUTSIDE_REPOSITORY"):
        admission.admit_canonical_candidate_bytes(receipt, repo / "artifacts" / "cs263", repo_root=repo)


def test_rejects_existing_output_directory(tmp_path, monkeypatch):
    repo, receipt, _candidate, _source_receipt = _fixture(tmp_path, monkeypatch)
    out = repo / "artifacts" / "cs263"
    out.mkdir()
    with pytest.raises(ValueError, match="OUTPUT_ALREADY_EXISTS"):
        admission.admit_canonical_candidate_bytes(receipt, out, repo_root=repo)
