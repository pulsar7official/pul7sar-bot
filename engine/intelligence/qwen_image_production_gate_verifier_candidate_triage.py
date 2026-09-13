"""Fail-closed structural triage for Change Set 242 verifier candidates.

Change Set 243 narrows the production-verifier gap without promoting discovered
callables to production verifiers. It reuses the AST-only Change Set 242 inventory,
then rejects candidates that cannot satisfy the Change Set 238 replay calling
contract based on source structure alone. No candidate module is imported or run.

A structurally viable candidate is still only a candidate: semantic correctness,
production provenance, adapter implementation, Change Set 241 readiness, and
Change Set 238 replay are all still required before any generation authority.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json
from engine.intelligence.qwen_image_production_gate_verifier_candidate_audit import (
    audit_production_gate_verifier_candidates,
    verify_production_gate_verifier_candidate_audit,
)

PRODUCTION_GATE_VERIFIER_CANDIDATE_TRIAGE_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-production-gate-verifier-candidate-triage-v1"
)

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


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _function_node(path: Path, callable_name: str, line_number: Any) -> ast.AST | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name == callable_name and getattr(node, "lineno", None) == line_number:
            return node
    return None


def _has_explicit_return(node: ast.AST) -> bool:
    return any(
        isinstance(child, ast.Return) and child.value is not None
        for child in ast.walk(node)
        if child is not node
    )


def _three_argument_compatible(node: ast.AST) -> bool:
    args = node.args
    positional = list(args.posonlyargs) + list(args.args)
    required = max(0, len(positional) - len(args.defaults))
    maximum = None if args.vararg is not None else len(positional)
    accepts_three = required <= 3 and (maximum is None or maximum >= 3)
    if accepts_three:
        return True
    # **kwargs cannot accept missing positional evidence/story/receipt arguments.
    return False


def _candidate_triage(candidate: dict[str, Any], *, root: Path) -> dict[str, Any]:
    relative = candidate.get("repository_relative_path")
    path = root / relative if isinstance(relative, str) else root / "__invalid__"
    node = _function_node(path, candidate.get("callable", ""), candidate.get("line_number"))
    reasons: list[str] = []
    if node is None:
        reasons.append("source_callable_not_resolved")
    else:
        if isinstance(node, ast.AsyncFunctionDef):
            reasons.append("async_callable_not_supported_by_sync_replay_contract")
        if not _three_argument_compatible(node):
            reasons.append("cannot_accept_three_positional_replay_arguments")
        if not _has_explicit_return(node):
            reasons.append("no_explicit_value_return")

    structurally_viable = not reasons
    return {
        "module": candidate.get("module"),
        "callable": candidate.get("callable"),
        "repository_relative_path": relative,
        "line_number": candidate.get("line_number"),
        "source_file_byte_size": candidate.get("source_file_byte_size"),
        "source_file_sha256": candidate.get("source_file_sha256"),
        "semantic_token_score": candidate.get("semantic_token_score"),
        "matched_tokens": candidate.get("matched_tokens"),
        "structurally_viable_for_adapter_review": structurally_viable,
        "structural_disqualifiers": reasons,
        "candidate_only": True,
        "production_backed": False,
        "semantic_replay_qualified": False,
        "registered": False,
    }


def build_production_gate_verifier_candidate_triage(
    *, repo_root: Path | None = None
) -> dict[str, Any]:
    """Re-audit and structurally triage candidates without importing/executing them."""
    root = (repo_root or _repo_root()).resolve()
    audit = audit_production_gate_verifier_candidates(repo_root=root)
    audit_sha = verify_production_gate_verifier_candidate_audit(audit, repo_root=root)

    triage: dict[str, list[dict[str, Any]]] = {}
    viable_counts: dict[str, int] = {}
    for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
        items = [
            _candidate_triage(candidate, root=root)
            for candidate in audit["candidates"][gate_id]
        ]
        triage[gate_id] = items
        viable_counts[gate_id] = sum(
            1 for item in items if item["structurally_viable_for_adapter_review"]
        )

    payload: dict[str, Any] = {
        "schema": PRODUCTION_GATE_VERIFIER_CANDIDATE_TRIAGE_SCHEMA,
        "status": "QWEN_IMAGE_2512_PRODUCTION_GATE_VERIFIER_CANDIDATES_STRUCTURALLY_TRIAGED",
        "cost_mode": COST_MODE,
        "source_candidate_audit_sha256": audit_sha,
        "required_gate_order": list(REQUIRED_FRESH_GATE_EVIDENCE),
        "triage_mode": "ast_only_no_import_no_execution",
        "triage": triage,
        "structurally_viable_candidate_counts": viable_counts,
        "structural_viability_is_not_semantic_verification": True,
        "manual_semantic_source_review_required": True,
        "production_adapter_implementation_required": True,
        "production_registry_mutated": False,
        "production_semantic_replay_executed": False,
        "fresh_story_gates_passed": False,
        "model_weights_loaded": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["candidate_triage_sha256"] = sha256_json(payload)
    return payload


def verify_production_gate_verifier_candidate_triage(
    receipt: dict[str, Any], *, repo_root: Path | None = None
) -> str:
    """Re-run structural triage against live source and require exact equivalence."""
    expected = build_production_gate_verifier_candidate_triage(repo_root=repo_root)
    if receipt != expected:
        raise ValueError("QWEN_PRODUCTION_VERIFIER_CANDIDATE_TRIAGE_MISMATCH")
    claimed = receipt.get("candidate_triage_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("QWEN_PRODUCTION_VERIFIER_CANDIDATE_TRIAGE_DIGEST_INVALID")
    return claimed
