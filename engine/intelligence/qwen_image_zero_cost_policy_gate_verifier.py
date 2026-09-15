"""Production-backed $0-local gate replay verifier for the first Golden trial.

This is the first real production gate adapter admitted after Change Sets 239-243.
It is deliberately narrow: it proves only that the byte-bound evidence declares a
strictly local/free execution path and that the existing DevelopmentCostPolicy also
accepts the provider economics. It grants no generation, pixel reuse, semantic,
visual-review, Golden-quality, or publication authority.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.cost_policy import (
    BillingClass,
    DevelopmentCostPolicy,
    ProviderEconomics,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE

ZERO_COST_EVIDENCE_SCHEMA = "pul7sar-phase18-zero-cost-policy-evidence-v1"
ZERO_COST_GATE_ID = "zero_cost_policy"
VERIFIER_ID = "pul7sar.production.zero_cost_policy"
VERIFIER_VERSION = "1.0.0"

_REQUIRED_EVIDENCE_FIELDS = (
    "schema",
    "gate_id",
    "story_snapshot_sha256",
    "cost_mode",
    "provider_id",
    "billing_class",
    "requires_payment_method",
    "external_paid_api_used",
    "canonical_execution_local_only",
)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value.lower())
    )


def _load_evidence(evidence_path: Path) -> tuple[dict[str, Any], bytes]:
    if not isinstance(evidence_path, Path) or not evidence_path.is_file():
        raise ValueError("QWEN_ZERO_COST_EVIDENCE_MISSING")
    raw = evidence_path.read_bytes()
    if not raw:
        raise ValueError("QWEN_ZERO_COST_EVIDENCE_EMPTY")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_ZERO_COST_EVIDENCE_JSON_INVALID") from exc
    if not isinstance(payload, dict) or tuple(payload.keys()) != _REQUIRED_EVIDENCE_FIELDS:
        raise ValueError("QWEN_ZERO_COST_EVIDENCE_SHAPE_INVALID")
    return payload, raw


def verify_zero_cost_policy_evidence(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Recompute strict local/free policy semantics from the exact evidence bytes."""
    if not _is_sha256(story_snapshot_sha256):
        raise ValueError("QWEN_ZERO_COST_STORY_SHA_INVALID")
    if not isinstance(receipt, Mapping):
        raise ValueError("QWEN_ZERO_COST_RECEIPT_INVALID")
    if receipt.get("verifier_id") != VERIFIER_ID:
        raise ValueError("QWEN_ZERO_COST_VERIFIER_ID_MISMATCH")
    if receipt.get("verifier_version") != VERIFIER_VERSION:
        raise ValueError("QWEN_ZERO_COST_VERIFIER_VERSION_MISMATCH")

    evidence, raw = _load_evidence(evidence_path)
    if evidence["schema"] != ZERO_COST_EVIDENCE_SCHEMA:
        raise ValueError("QWEN_ZERO_COST_EVIDENCE_SCHEMA_DRIFT")
    if evidence["gate_id"] != ZERO_COST_GATE_ID:
        raise ValueError("QWEN_ZERO_COST_GATE_DRIFT")
    if evidence["story_snapshot_sha256"] != story_snapshot_sha256:
        raise ValueError("QWEN_ZERO_COST_CROSS_STORY_EVIDENCE")
    if evidence["cost_mode"] != COST_MODE:
        raise ValueError("QWEN_ZERO_COST_MODE_DRIFT")
    if evidence["billing_class"] != BillingClass.LOCAL_FREE.value:
        raise ValueError("QWEN_ZERO_COST_PROVIDER_NOT_LOCAL_FREE")
    if evidence["requires_payment_method"] is not False:
        raise ValueError("QWEN_ZERO_COST_PAYMENT_METHOD_REQUIRED")
    if evidence["external_paid_api_used"] is not False:
        raise ValueError("QWEN_ZERO_COST_EXTERNAL_PAID_API_USED")
    if evidence["canonical_execution_local_only"] is not True:
        raise ValueError("QWEN_ZERO_COST_LOCAL_EXECUTION_NOT_PROVEN")

    economics = ProviderEconomics(
        provider_id=evidence["provider_id"],
        billing_class=BillingClass(evidence["billing_class"]),
        requires_payment_method=evidence["requires_payment_method"],
        notes="Phase 18 canonical Golden-trial zero-cost replay evidence",
    )
    decision = DevelopmentCostPolicy(zero_cost_only=True).evaluate(economics)
    if decision.allowed is not True:
        raise ValueError("QWEN_ZERO_COST_DEVELOPMENT_POLICY_REJECTED")

    details = {
        "policy": COST_MODE,
        "provider_id": economics.provider_id,
        "billing_class": economics.billing_class.value,
        "requires_payment_method": economics.requires_payment_method,
        "external_paid_api_used": False,
        "canonical_execution_local_only": True,
        "development_cost_policy_allowed": True,
        "development_cost_policy_reason": decision.reason,
    }
    return {
        "gate_id": ZERO_COST_GATE_ID,
        "story_snapshot_sha256": story_snapshot_sha256,
        "source_evidence_sha256": hashlib.sha256(raw).hexdigest(),
        "source_evidence_byte_size": len(raw),
        "verifier_id": VERIFIER_ID,
        "verifier_version": VERIFIER_VERSION,
        "gate_passed": True,
        "verification_details": details,
    }


def replay_zero_cost_policy_gate(
    evidence_path: Path,
    story_snapshot_sha256: str,
    receipt: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Canonical replay adapter; delegates to the production semantic verifier."""
    return verify_zero_cost_policy_evidence(evidence_path, story_snapshot_sha256, receipt)


replay_zero_cost_policy_gate.PUL7SAR_VERIFIER_ID = VERIFIER_ID
replay_zero_cost_policy_gate.PUL7SAR_VERIFIER_VERSION = VERIFIER_VERSION
replay_zero_cost_policy_gate.PUL7SAR_VERIFIER_GATE_ID = ZERO_COST_GATE_ID
replay_zero_cost_policy_gate.PUL7SAR_PRODUCTION_BACKED = True
replay_zero_cost_policy_gate.PUL7SAR_SOURCE_MODULE = __name__
replay_zero_cost_policy_gate.PUL7SAR_SOURCE_CALLABLE = "verify_zero_cost_policy_evidence"
replay_zero_cost_policy_gate.PUL7SAR_SOURCE_CALLABLE_OBJECT = verify_zero_cost_policy_evidence
