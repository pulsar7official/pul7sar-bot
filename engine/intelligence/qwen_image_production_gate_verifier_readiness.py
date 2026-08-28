"""Fail-closed readiness audit for production gate replay verifier wiring.

Change Set 239 does not perform semantic replay and grants no generation authority.
It answers one narrower question before Change Set 238 can be used with production
code: are all six required fresh-story gates bound to explicit callable production
adapters with stable verifier identity/version metadata?

The canonical registry is intentionally empty until real adapters exist. Missing,
extra, non-callable, weakly identified, or incompatible callables keep readiness
false (or fail closed for registry-shape drift). Test fixtures cannot become Golden
or publication authority through this layer.
"""
from __future__ import annotations

import inspect
from typing import Any, Callable, Mapping

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

PRODUCTION_GATE_VERIFIER_READINESS_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-production-gate-verifier-readiness-v1"
)
CANONICAL_REGISTRY_MODULE = (
    "engine.intelligence.qwen_image_production_gate_verifier_registry"
)
VERIFIER_ID_ATTRIBUTE = "PUL7SAR_VERIFIER_ID"
VERIFIER_VERSION_ATTRIBUTE = "PUL7SAR_VERIFIER_VERSION"

_FORBIDDEN_AUTHORITY_FIELDS = (
    "runtime_floor_proven",
    "local_runtime_qualified",
    "canonical_generation_authorized",
    "canonical_pixels_reusable",
    "queue_mutated",
    "semantic_approved",
    "human_visual_review_approved",
    "golden_quality_approved",
    "publication_ready",
)


def _valid_identity(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value.strip()) <= 160


def _signature_accepts_replay_call(verifier: Callable[..., Any]) -> bool:
    """Return whether the callable can accept (Path, story_sha, receipt)."""
    try:
        signature = inspect.signature(verifier)
        signature.bind(object(), "0" * 64, {})
    except (TypeError, ValueError):
        return False
    return True


def audit_production_gate_verifier_readiness(
    registry: Mapping[str, Callable[..., Any]],
    *,
    registry_module: str = CANONICAL_REGISTRY_MODULE,
) -> dict[str, Any]:
    """Audit wiring only; never execute gate semantics or grant downstream authority."""
    if registry_module != CANONICAL_REGISTRY_MODULE:
        raise ValueError("QWEN_PRODUCTION_VERIFIER_REGISTRY_MODULE_DRIFT")
    if not isinstance(registry, Mapping):
        raise ValueError("QWEN_PRODUCTION_VERIFIER_REGISTRY_INVALID")

    extras = [gate_id for gate_id in registry if gate_id not in REQUIRED_FRESH_GATE_EVIDENCE]
    if extras:
        raise ValueError("QWEN_PRODUCTION_VERIFIER_REGISTRY_EXTRA_GATE")

    bindings: list[dict[str, Any]] = []
    missing_gate_ids: list[str] = []
    invalid_gate_ids: list[str] = []
    verifier_ids: set[str] = set()

    for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
        verifier = registry.get(gate_id)
        if verifier is None:
            missing_gate_ids.append(gate_id)
            bindings.append(
                {
                    "gate_id": gate_id,
                    "binding_status": "missing",
                    "callable_module": None,
                    "callable_qualname": None,
                    "verifier_id": None,
                    "verifier_version": None,
                    "signature_compatible": False,
                }
            )
            continue

        callable_ok = callable(verifier)
        signature_ok = callable_ok and _signature_accepts_replay_call(verifier)
        verifier_id = getattr(verifier, VERIFIER_ID_ATTRIBUTE, None) if callable_ok else None
        verifier_version = (
            getattr(verifier, VERIFIER_VERSION_ATTRIBUTE, None) if callable_ok else None
        )
        identity_ok = _valid_identity(verifier_id) and _valid_identity(verifier_version)
        identity_unique = bool(identity_ok and verifier_id not in verifier_ids)
        valid = bool(callable_ok and signature_ok and identity_ok and identity_unique)
        if valid:
            verifier_ids.add(verifier_id)
        else:
            invalid_gate_ids.append(gate_id)

        bindings.append(
            {
                "gate_id": gate_id,
                "binding_status": "ready" if valid else "invalid",
                "callable_module": getattr(verifier, "__module__", None) if callable_ok else None,
                "callable_qualname": getattr(verifier, "__qualname__", None) if callable_ok else None,
                "verifier_id": verifier_id if _valid_identity(verifier_id) else None,
                "verifier_version": verifier_version if _valid_identity(verifier_version) else None,
                "signature_compatible": bool(signature_ok),
            }
        )

    all_bound = not missing_gate_ids and not invalid_gate_ids
    payload = {
        "schema": PRODUCTION_GATE_VERIFIER_READINESS_SCHEMA,
        "status": (
            "QWEN_IMAGE_2512_PRODUCTION_GATE_VERIFIERS_READY"
            if all_bound
            else "QWEN_IMAGE_2512_PRODUCTION_GATE_VERIFIERS_NOT_READY"
        ),
        "cost_mode": COST_MODE,
        "canonical_registry_module": CANONICAL_REGISTRY_MODULE,
        "required_gate_order": list(REQUIRED_FRESH_GATE_EVIDENCE),
        "bindings": bindings,
        "missing_gate_ids": missing_gate_ids,
        "invalid_gate_ids": invalid_gate_ids,
        "all_production_verifiers_bound": all_bound,
        "production_semantic_replay_executed": False,
        "fresh_story_gates_passed": False,
        "controlled_trial_preflight_valid": False,
        "model_weights_loaded": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["production_gate_verifier_readiness_sha256"] = sha256_json(payload)
    return payload


def verify_production_gate_verifier_readiness(
    readiness_receipt: dict[str, Any],
    registry: Mapping[str, Callable[..., Any]],
    *,
    registry_module: str = CANONICAL_REGISTRY_MODULE,
) -> str:
    """Re-audit live registry wiring and require exact receipt equivalence."""
    expected = audit_production_gate_verifier_readiness(
        registry,
        registry_module=registry_module,
    )
    if readiness_receipt != expected:
        raise ValueError("QWEN_PRODUCTION_VERIFIER_READINESS_RECEIPT_MISMATCH")
    claimed = readiness_receipt.get("production_gate_verifier_readiness_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("QWEN_PRODUCTION_VERIFIER_READINESS_DIGEST_INVALID")
    return claimed
