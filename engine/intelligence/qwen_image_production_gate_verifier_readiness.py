"""Fail-closed readiness audit for production gate replay verifier wiring.

Change Set 239 introduced the canonical production registry audit. Change Set 240
hardens that audit so a callable cannot become "production ready" merely by carrying
an ID/version pair. Every adapter must also attest its exact gate, production-backed
status, and the source module/callable it delegates to. This still does not execute
semantic replay and grants no generation authority.

The canonical registry remains intentionally empty until real adapters exist. Missing,
extra, non-callable, weakly identified, source-less, test/stub-like, or incompatible
callables keep readiness false. Test fixtures cannot become Golden or publication
authority through this layer.
"""
from __future__ import annotations

import inspect
from typing import Any, Callable, Mapping

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

PRODUCTION_GATE_VERIFIER_READINESS_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-production-gate-verifier-readiness-v2"
)
CANONICAL_REGISTRY_MODULE = (
    "engine.intelligence.qwen_image_production_gate_verifier_registry"
)
VERIFIER_ID_ATTRIBUTE = "PUL7SAR_VERIFIER_ID"
VERIFIER_VERSION_ATTRIBUTE = "PUL7SAR_VERIFIER_VERSION"
VERIFIER_GATE_ATTRIBUTE = "PUL7SAR_VERIFIER_GATE_ID"
VERIFIER_PRODUCTION_BACKED_ATTRIBUTE = "PUL7SAR_PRODUCTION_BACKED"
VERIFIER_SOURCE_MODULE_ATTRIBUTE = "PUL7SAR_SOURCE_MODULE"
VERIFIER_SOURCE_CALLABLE_ATTRIBUTE = "PUL7SAR_SOURCE_CALLABLE"

_FORBIDDEN_SOURCE_PREFIXES = ("tests", "test", "unittest", "__main__")
_FORBIDDEN_SOURCE_TOKENS = ("fixture", "stub", "fake", "mock", "dummy", "placeholder")

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


def _valid_source_module(value: Any) -> bool:
    if not _valid_identity(value):
        return False
    normalized = value.strip().lower()
    if normalized.startswith(_FORBIDDEN_SOURCE_PREFIXES):
        return False
    return not any(token in normalized for token in _FORBIDDEN_SOURCE_TOKENS)


def _valid_source_callable(value: Any) -> bool:
    if not _valid_identity(value):
        return False
    normalized = value.strip().lower()
    return not any(token in normalized for token in _FORBIDDEN_SOURCE_TOKENS)


def audit_production_gate_verifier_readiness(
    registry: Mapping[str, Callable[..., Any]],
    *,
    registry_module: str = CANONICAL_REGISTRY_MODULE,
) -> dict[str, Any]:
    """Audit wiring/provenance only; never execute gate semantics or grant authority."""
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
    source_bindings: set[tuple[str, str]] = set()

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
                    "declared_gate_id": None,
                    "production_backed": False,
                    "source_module": None,
                    "source_callable": None,
                    "signature_compatible": False,
                    "provenance_complete": False,
                }
            )
            continue

        callable_ok = callable(verifier)
        signature_ok = callable_ok and _signature_accepts_replay_call(verifier)
        verifier_id = getattr(verifier, VERIFIER_ID_ATTRIBUTE, None) if callable_ok else None
        verifier_version = (
            getattr(verifier, VERIFIER_VERSION_ATTRIBUTE, None) if callable_ok else None
        )
        declared_gate_id = getattr(verifier, VERIFIER_GATE_ATTRIBUTE, None) if callable_ok else None
        production_backed = (
            getattr(verifier, VERIFIER_PRODUCTION_BACKED_ATTRIBUTE, False) if callable_ok else False
        )
        source_module = (
            getattr(verifier, VERIFIER_SOURCE_MODULE_ATTRIBUTE, None) if callable_ok else None
        )
        source_callable = (
            getattr(verifier, VERIFIER_SOURCE_CALLABLE_ATTRIBUTE, None) if callable_ok else None
        )

        identity_ok = _valid_identity(verifier_id) and _valid_identity(verifier_version)
        gate_binding_ok = declared_gate_id == gate_id
        source_ok = _valid_source_module(source_module) and _valid_source_callable(source_callable)
        source_binding = (source_module, source_callable) if source_ok else None
        identity_unique = bool(identity_ok and verifier_id not in verifier_ids)
        source_unique = bool(source_binding is not None and source_binding not in source_bindings)
        provenance_complete = bool(
            gate_binding_ok and production_backed is True and source_ok and source_unique
        )
        valid = bool(
            callable_ok
            and signature_ok
            and identity_ok
            and identity_unique
            and provenance_complete
        )
        if valid:
            verifier_ids.add(verifier_id)
            source_bindings.add(source_binding)
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
                "declared_gate_id": declared_gate_id if _valid_identity(declared_gate_id) else None,
                "production_backed": production_backed is True,
                "source_module": source_module if _valid_source_module(source_module) else None,
                "source_callable": source_callable if _valid_source_callable(source_callable) else None,
                "signature_compatible": bool(signature_ok),
                "provenance_complete": provenance_complete,
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
        "all_bindings_provenance_complete": all_bound,
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
