"""Byte-bound, non-canonical research ledger for remote renderer studies.

This module deliberately cannot promote a remote ZeroGPU result into canonical
Golden evidence. It exists only to make renderer research reproducible while
the canonical `$0-local` CUDA path is unavailable.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


BENCHMARK_SCHEMA = "pul7sar-phase18-remote-renderer-benchmark-v3"
LEDGER_SCHEMA = "pul7sar-phase18-remote-renderer-research-ledger-v1"
COST_MODE = "$0-remote-zerogpu-study"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
RESEARCH_SCORE_FLOOR = 8.0
REQUIRED_SCORE_FIELDS = (
    "editorial_composition",
    "photorealism",
    "geometry_integrity",
    "scene_continuity",
    "entity_neutrality",
    "text_and_brand_cleanliness",
)
HARD_BLOCKERS = (
    "broken_geometry",
    "pseudo_text",
    "identifiable_entity_cue",
    "multi_scene_or_collage",
    "generated_brand_or_crest",
)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_json(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _sha256_bytes(raw)


def _require_repo_path(path: Path, repo_root: Path) -> Path:
    resolved = path.resolve()
    root = repo_root.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"REMOTE_RESEARCH_PATH_ESCAPE: {resolved}")
    return resolved


def _validate_benchmark_report(report: dict[str, Any]) -> None:
    if report.get("schema") != BENCHMARK_SCHEMA:
        raise ValueError("REMOTE_RESEARCH_BENCHMARK_SCHEMA_MISMATCH")
    if report.get("cost_mode") != COST_MODE:
        raise ValueError("REMOTE_RESEARCH_COST_MODE_MISMATCH")
    required_true = ("engineering_benchmark_only", "entity_neutral_benchmark", "human_visual_review_required")
    if any(report.get(key) is not True for key in required_true):
        raise ValueError("REMOTE_RESEARCH_BENCHMARK_AUTHORITY_MISMATCH")
    required_false = (
        "canonical_golden_eligible",
        "semantic_approved",
        "golden_quality_approved",
        "publication_ready",
        "verified_identity_asset_used",
        "verified_venue_asset_used",
    )
    if any(report.get(key) is not False for key in required_false):
        raise ValueError("REMOTE_RESEARCH_CANONICAL_AUTHORITY_FORBIDDEN")
    prompt_sha = report.get("prompt_sha256")
    if not isinstance(prompt_sha, str) or len(prompt_sha) != 64:
        raise ValueError("REMOTE_RESEARCH_PROMPT_SHA_INVALID")


def _validate_scores(scores: dict[str, Any]) -> tuple[dict[str, float], float]:
    normalized: dict[str, float] = {}
    for field in REQUIRED_SCORE_FIELDS:
        value = scores.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"REMOTE_RESEARCH_SCORE_MISSING: {field}")
        numeric = float(value)
        if not 0.0 <= numeric <= 10.0:
            raise ValueError(f"REMOTE_RESEARCH_SCORE_OUT_OF_RANGE: {field}")
        normalized[field] = numeric
    average = round(sum(normalized.values()) / len(normalized), 3)
    return normalized, average


def _validate_blockers(blockers: dict[str, Any]) -> dict[str, bool]:
    normalized: dict[str, bool] = {}
    for field in HARD_BLOCKERS:
        value = blockers.get(field)
        if not isinstance(value, bool):
            raise ValueError(f"REMOTE_RESEARCH_BLOCKER_MISSING: {field}")
        normalized[field] = value
    return normalized


@dataclass(frozen=True)
class RemoteRendererResearchLedgerBuilder:
    repo_root: Path

    def build(
        self,
        *,
        benchmark_report_path: Path,
        human_review_path: Path,
    ) -> dict[str, Any]:
        benchmark_path = _require_repo_path(benchmark_report_path, self.repo_root)
        review_path = _require_repo_path(human_review_path, self.repo_root)
        report = json.loads(benchmark_path.read_text(encoding="utf-8"))
        review = json.loads(review_path.read_text(encoding="utf-8"))
        _validate_benchmark_report(report)

        if review.get("schema") != "pul7sar-phase18-remote-renderer-human-review-v1":
            raise ValueError("REMOTE_RESEARCH_REVIEW_SCHEMA_MISMATCH")
        if review.get("prompt_sha256") != report.get("prompt_sha256"):
            raise ValueError("REMOTE_RESEARCH_REVIEW_PROMPT_MISMATCH")

        successful = report.get("successful")
        if not isinstance(successful, list) or not successful:
            raise ValueError("REMOTE_RESEARCH_NO_SUCCESSFUL_RENDERERS")
        reviews = review.get("renderers")
        if not isinstance(reviews, dict):
            raise ValueError("REMOTE_RESEARCH_REVIEW_RENDERERS_MISSING")

        entries: list[dict[str, Any]] = []
        for result in successful:
            renderer = result.get("renderer")
            if not isinstance(renderer, str) or not renderer:
                raise ValueError("REMOTE_RESEARCH_RENDERER_ID_INVALID")
            if result.get("cost_mode") != COST_MODE:
                raise ValueError("REMOTE_RESEARCH_RESULT_COST_MODE_MISMATCH")
            if result.get("canonical_golden_eligible") is not False or result.get("publication_ready") is not False:
                raise ValueError("REMOTE_RESEARCH_RESULT_AUTHORITY_FORBIDDEN")
            if result.get("entity_neutral_benchmark") is not True:
                raise ValueError("REMOTE_RESEARCH_RESULT_ENTITY_NEUTRALITY_MISSING")

            output = result.get("output")
            if not isinstance(output, str) or not output:
                raise ValueError("REMOTE_RESEARCH_OUTPUT_PATH_INVALID")
            output_path = _require_repo_path(Path(output), self.repo_root)
            payload = output_path.read_bytes()
            if not payload.startswith(PNG_SIGNATURE):
                raise ValueError("REMOTE_RESEARCH_OUTPUT_NOT_PNG")
            actual_sha = _sha256_bytes(payload)
            if actual_sha != result.get("output_sha256"):
                raise ValueError("REMOTE_RESEARCH_OUTPUT_SHA_MISMATCH")
            if len(payload) != result.get("output_bytes"):
                raise ValueError("REMOTE_RESEARCH_OUTPUT_SIZE_MISMATCH")
            if result.get("prompt_sha256") != report.get("prompt_sha256"):
                raise ValueError("REMOTE_RESEARCH_RESULT_PROMPT_MISMATCH")

            renderer_review = reviews.get(renderer)
            if not isinstance(renderer_review, dict):
                raise ValueError(f"REMOTE_RESEARCH_REVIEW_MISSING: {renderer}")
            if renderer_review.get("output_sha256") != actual_sha:
                raise ValueError(f"REMOTE_RESEARCH_REVIEW_OUTPUT_MISMATCH: {renderer}")
            scores, average = _validate_scores(renderer_review.get("scores") or {})
            blockers = _validate_blockers(renderer_review.get("hard_blockers") or {})
            blocker_free = not any(blockers.values())
            research_floor_met = blocker_free and average >= RESEARCH_SCORE_FLOOR
            entries.append(
                {
                    "renderer": renderer,
                    "space": result.get("space"),
                    "seed": result.get("seed"),
                    "prompt_sha256": report.get("prompt_sha256"),
                    "output": str(output_path),
                    "output_sha256": actual_sha,
                    "output_bytes": len(payload),
                    "scores": scores,
                    "average_score": average,
                    "hard_blockers": blockers,
                    "blocker_free": blocker_free,
                    "research_score_floor": RESEARCH_SCORE_FLOOR,
                    "research_score_floor_met": research_floor_met,
                    "canonical_golden_eligible": False,
                    "publication_ready": False,
                }
            )

        ranked = sorted(entries, key=lambda item: (item["research_score_floor_met"], item["average_score"]), reverse=True)
        leader = ranked[0] if ranked and ranked[0]["research_score_floor_met"] else None
        payload = {
            "schema": LEDGER_SCHEMA,
            "status": "REMOTE_RENDERER_RESEARCH_LEDGER_READY",
            "benchmark_report": str(benchmark_path),
            "benchmark_report_sha256": _sha256_file(benchmark_path),
            "human_review": str(review_path),
            "human_review_sha256": _sha256_file(review_path),
            "prompt_sha256": report.get("prompt_sha256"),
            "entries": entries,
            "research_leader": leader["renderer"] if leader else None,
            "research_leader_output_sha256": leader["output_sha256"] if leader else None,
            "research_only": True,
            "canonical_admission_required": True,
            "canonical_golden_eligible": False,
            "semantic_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "cost_mode": COST_MODE,
        }
        payload["ledger_sha256"] = _sha256_json(payload)
        return payload
