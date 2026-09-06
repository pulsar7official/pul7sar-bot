"""Build a deterministic canonical Qwen prompt from CS257-replayed evidence.

This is part of Change Set 262. It closes the free-form prompt substitution gap:
a CS261 authorization may only be paired with prompt bytes deterministically derived
from the exact evidence set that CS257 independently replayed for the same story.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.qwen_image_fresh_story_evidence_manifest import (
    FRESH_STORY_EVIDENCE_MANIFEST_SCHEMA,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json
from engine.intelligence.qwen_image_story_bound_controlled_trial_request import (
    _validate_cs257_run,
)
from engine.intelligence.qwen_image_story_bound_generation_authorization import (
    verify_story_bound_generation_authorization,
)

STORY_BOUND_CANONICAL_PROMPT_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-story-bound-canonical-prompt-v1"
)
_REQUIRED_GATES = (
    "fact_lock",
    "entity_identity_verification",
    "sentiment_neutrality",
    "story_semantic_preflight",
    "zero_cost_policy",
    "semantic_layer_ownership",
)


@dataclass(frozen=True)
class StoryBoundCanonicalPrompt:
    story_snapshot_sha256: str
    prompt: str
    negative_prompt: str
    contract: dict[str, Any]


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        ch in "0123456789abcdef" for ch in value.lower()
    )


def _read_json(path: Path, code: str) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    raw = path.read_bytes()
    if not raw:
        raise ValueError(code)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(code) from exc
    if not isinstance(payload, dict):
        raise ValueError(code)
    return payload, raw


def _repo_file(repo_root: Path, relative: str, code: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError(code)
    if ".." in Path(relative).parts:
        raise ValueError(code)
    root = repo_root.resolve()
    path = root / relative
    if path.is_symlink():
        raise ValueError(code)
    resolved = path.resolve()
    try:
        canonical = resolved.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    if canonical != Path(relative).as_posix() or not resolved.is_file():
        raise ValueError(code)
    return resolved


def _texts(values: Any, code: str) -> list[str]:
    if not isinstance(values, list):
        raise ValueError(code)
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(code)
        result.append(" ".join(value.split()))
    return result


def build_story_bound_canonical_prompt(
    cs257_run_dir: Path,
    authorization_path: Path,
    *,
    repo_root: Path,
) -> StoryBoundCanonicalPrompt:
    """Derive immutable prompt text from the exact same-story replayed evidence."""
    story_sha, _, _ = _validate_cs257_run(cs257_run_dir, repo_root)
    authorization = verify_story_bound_generation_authorization(
        authorization_path, repo_root=repo_root
    )
    if authorization.get("story_snapshot_sha256") != story_sha:
        raise ValueError("QWEN_CANONICAL_PROMPT_CROSS_STORY_AUTHORIZATION")
    if authorization.get("canonical_generation_authorized") is not True:
        raise ValueError("QWEN_CANONICAL_PROMPT_GENERATION_NOT_AUTHORIZED")

    manifest_path = cs257_run_dir.resolve() / "fresh_story_evidence_manifest.json"
    manifest, manifest_raw = _read_json(
        manifest_path, "QWEN_CANONICAL_PROMPT_EVIDENCE_MANIFEST_INVALID"
    )
    if manifest.get("schema") != FRESH_STORY_EVIDENCE_MANIFEST_SCHEMA:
        raise ValueError("QWEN_CANONICAL_PROMPT_EVIDENCE_MANIFEST_SCHEMA_DRIFT")
    bindings = manifest.get("evidence_bindings")
    if not isinstance(bindings, list) or len(bindings) != len(_REQUIRED_GATES):
        raise ValueError("QWEN_CANONICAL_PROMPT_EVIDENCE_BINDINGS_INVALID")

    evidence: dict[str, dict[str, Any]] = {}
    binding_receipts: list[dict[str, Any]] = []
    for gate_id, binding in zip(_REQUIRED_GATES, bindings, strict=True):
        if not isinstance(binding, Mapping) or binding.get("gate_id") != gate_id:
            raise ValueError("QWEN_CANONICAL_PROMPT_EVIDENCE_GATE_ORDER_DRIFT")
        relative = binding.get("repository_relative_path")
        path = _repo_file(
            repo_root,
            relative,
            "QWEN_CANONICAL_PROMPT_EVIDENCE_PATH_INVALID",
        )
        payload, raw = _read_json(path, "QWEN_CANONICAL_PROMPT_EVIDENCE_INVALID")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != binding.get("sha256") or len(raw) != binding.get("byte_size"):
            raise ValueError("QWEN_CANONICAL_PROMPT_EVIDENCE_BYTE_DRIFT")
        if payload.get("gate_id") != gate_id or payload.get(
            "story_snapshot_sha256"
        ) != story_sha:
            raise ValueError("QWEN_CANONICAL_PROMPT_EVIDENCE_CROSS_STORY")
        evidence[gate_id] = payload
        binding_receipts.append(
            {
                "gate_id": gate_id,
                "repository_relative_path": relative,
                "sha256": digest,
                "byte_size": len(raw),
            }
        )

    facts = _texts(
        evidence["fact_lock"].get("required_facts"),
        "QWEN_CANONICAL_PROMPT_REQUIRED_FACTS_INVALID",
    )
    entities_raw = evidence["entity_identity_verification"].get("canonical_entities")
    if not isinstance(entities_raw, list) or not entities_raw:
        raise ValueError("QWEN_CANONICAL_PROMPT_ENTITIES_INVALID")
    entities: list[str] = []
    for entity in entities_raw:
        if not isinstance(entity, Mapping):
            raise ValueError("QWEN_CANONICAL_PROMPT_ENTITIES_INVALID")
        name = entity.get("display_name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("QWEN_CANONICAL_PROMPT_ENTITIES_INVALID")
        entities.append(" ".join(name.split()))

    semantic = evidence["story_semantic_preflight"]
    editorial = semantic.get("editorial_request")
    visual = semantic.get("proposed_visual_plan")
    if not isinstance(editorial, Mapping) or not isinstance(visual, Mapping):
        raise ValueError("QWEN_CANONICAL_PROMPT_SEMANTIC_PLAN_INVALID")
    if semantic.get("qwen_generation_requested") is not True:
        raise ValueError("QWEN_CANONICAL_PROMPT_QWEN_NOT_REQUESTED")

    story_core = editorial.get("story_core")
    angle = editorial.get("editorial_angle")
    sport = editorial.get("sport")
    event = editorial.get("event")
    family = visual.get("visual_family")
    scene = visual.get("scene_concept")
    generated = _texts(
        visual.get("generated_elements"),
        "QWEN_CANONICAL_PROMPT_GENERATED_ELEMENTS_INVALID",
    )
    forbidden = _texts(
        visual.get("forbidden_generated_elements"),
        "QWEN_CANONICAL_PROMPT_FORBIDDEN_ELEMENTS_INVALID",
    )
    for value, code in (
        (story_core, "STORY_CORE"),
        (angle, "EDITORIAL_ANGLE"),
        (sport, "SPORT"),
        (event, "EVENT"),
        (family, "VISUAL_FAMILY"),
        (scene, "SCENE_CONCEPT"),
    ):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"QWEN_CANONICAL_PROMPT_{code}_INVALID")

    sentiment = evidence["sentiment_neutrality"]
    if sentiment.get("outcome_is_competitive_result") is True and sentiment.get(
        "opponent_or_loser_present"
    ) is True:
        neutrality = (
            "Present the result neutrally and respectfully. Celebrate the verified winner "
            "without humiliating, mocking, degrading, caricaturing, or visually diminishing "
            "the losing side."
        )
    else:
        neutrality = "Maintain factual, restrained editorial sentiment without invented emotion."

    layer = evidence["semantic_layer_ownership"]
    layer_plan = layer.get("layer_plan")
    if not isinstance(layer_plan, list) or not layer_plan:
        raise ValueError("QWEN_CANONICAL_PROMPT_LAYER_PLAN_INVALID")

    prompt = "\n".join(
        (
            "Create only the generative image layer for a premium global sports-news editorial visual.",
            f"Sport/event: {sport.strip()} / {event.strip()}.",
            f"Verified story core: {story_core.strip()}",
            "Verified required facts: " + " | ".join(facts),
            "Verified canonical entities: " + " | ".join(entities),
            f"Editorial angle: {angle.strip()}",
            f"Visual family: {family.strip()}.",
            f"Scene concept: {scene.strip()}",
            "Generate only these approved semantic elements: " + ", ".join(generated) + ".",
            neutrality,
            "Do not generate any exact text, score, statistic, logo, crest, wordmark, competition mark, or other element reserved for deterministic/verified overlay layers.",
            "Forbidden generated elements from the approved plan: " + ", ".join(forbidden) + ".",
            "Do not invent people, identities, emotions, facts, scores, geometry, sponsors, brands, or symbols beyond the verified story evidence.",
            "Prioritize realistic premium sports-editorial lighting, depth, material detail, hierarchy, negative space for later deterministic overlays, and clean composition; no fantasy spectacle unless explicitly present in the approved scene concept.",
        )
    )
    negative_prompt = (
        "generated text, letters, numbers, score, statistics, logo, crest, wordmark, "
        "competition logo, watermark, invented identity, invented person, unverified face, "
        "mockery, humiliation, degradation, caricature, shame, fantasy spectacle, malformed sports geometry"
    )

    contract = {
        "schema": STORY_BOUND_CANONICAL_PROMPT_SCHEMA,
        "status": "QWEN_IMAGE_2512_STORY_BOUND_CANONICAL_PROMPT_DERIVED",
        "story_snapshot_sha256": story_sha,
        "authorization_sha256": authorization["authorization_sha256"],
        "evidence_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "evidence_bindings": binding_receipts,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "prompt_byte_size": len(prompt.encode("utf-8")),
        "negative_prompt_sha256": hashlib.sha256(
            negative_prompt.encode("utf-8")
        ).hexdigest(),
        "negative_prompt_byte_size": len(negative_prompt.encode("utf-8")),
        "deterministically_derived_from_replayed_story_evidence": True,
        "free_form_prompt_substitution_allowed": False,
        "canonical_generation_authorized": True,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "golden_quality_approved": False,
        "publication_ready": False,
    }
    contract["contract_sha256"] = sha256_json(contract)
    return StoryBoundCanonicalPrompt(
        story_snapshot_sha256=story_sha,
        prompt=prompt,
        negative_prompt=negative_prompt,
        contract=contract,
    )
