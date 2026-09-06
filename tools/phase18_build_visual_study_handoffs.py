#!/usr/bin/env python3
"""Build SHA-locked Phase 18 human visual-study handoffs without generating images."""
from __future__ import annotations

import argparse
from dataclasses import fields
import json
from pathlib import Path

from engine.intelligence.editorial_headline_grammar import HeadlineTone
from engine.intelligence.story_to_visual_orchestrator import StoryToVisualOrchestrator, VerifiedEditorialStory
from engine.intelligence.story_visual_editorial import EditorialEvent
from engine.intelligence.visual_study_handoff import VisualStudyHandoff, VisualStudyHandoffCompiler


CASES = (
    (
        "transfer-signature-v1",
        EditorialEvent.TRANSFER_CONFIRMED,
        "Verified Player",
        "PLAYER JOINS CLUB",
        "Verified agreement on a long-term deal",
    ),
    (
        "result-statement-v1",
        EditorialEvent.RESULT,
        "Verified Winner",
        "TEAM WINS 2-1",
        None,
    ),
    (
        "verified-subject-news-v1",
        EditorialEvent.INJURY,
        "Verified Player",
        "PLAYER RULED OUT",
        "Verified availability update",
    ),
)


def _serializable(handoff: VisualStudyHandoff) -> dict[str, object]:
    payload: dict[str, object] = {}
    for item in fields(handoff):
        value = getattr(handoff, item.name)
        if item.name == "metadata":
            value = dict(value)
        payload[item.name] = value
    return payload


def build(output_dir: str) -> dict[str, object]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    orchestrator = StoryToVisualOrchestrator()
    compiler = VisualStudyHandoffCompiler()
    entries: list[dict[str, object]] = []

    for benchmark_id, event, subject, headline, support in CASES:
        decision = orchestrator.decide(VerifiedEditorialStory(
            event=event,
            sport="football",
            subject=subject,
            fact_phrase="verified benchmark fact",
            story_core="non-publication Phase 18 visual study benchmark",
            tone=HeadlineTone.NEUTRAL,
            confidence=1.0,
        ))
        handoff = compiler.compile(decision, headline=headline, supporting_copy=support)
        compiler.verify(handoff)
        if handoff.benchmark_id != benchmark_id:
            raise RuntimeError(f"benchmark drift: expected {benchmark_id}, got {handoff.benchmark_id}")
        path = out / f"{benchmark_id}.json"
        path.write_text(json.dumps(_serializable(handoff), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        entries.append({
            "benchmark_id": benchmark_id,
            "path": path.name,
            "payload_sha256": handoff.payload_sha256,
            "readiness_status": handoff.readiness_status,
            "human_review_allowed": handoff.human_review_allowed,
            "publication_ready": handoff.publication_ready,
        })

    manifest = {
        "manifest_version": "pul7sar-visual-study-handoff-batch-v1",
        "candidate_image_count": 0,
        "handoff_count": len(entries),
        "exact_brand_geometry_ready": False,
        "publication_ready": False,
        "purpose": "locked pre-image human visual-study contracts",
        "handoffs": entries,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output/phase18_visual_study_handoffs")
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
