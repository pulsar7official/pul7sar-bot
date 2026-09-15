"""AST-only candidate audit for genuine production semantic gate verifiers.

Change Set 242 reduces the gap left after source-object/source-byte readiness hardening.
It inventories repository Python callables that *might* be relevant to the six required
fresh-story gates without importing or executing them. Candidates are advisory only:
no candidate discovered here is production-backed, semantically qualified, registered,
or authorized for replay/generation by virtue of this audit.

The audit is deliberately fail-closed and byte-bound. It scans repository ``engine/``
Python source, excludes tests/stubs/placeholders and the Phase-18 verifier plumbing
itself, parses source with ``ast``, scores callable names/docstrings/module paths against
explicit per-gate semantic tokens, and records each source file SHA-256.
"""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path
from typing import Any, Iterable

from engine.intelligence.qwen_image_controlled_golden_trial_preflight import (
    REQUIRED_FRESH_GATE_EVIDENCE,
)
from engine.intelligence.qwen_image_inference_measurement import COST_MODE, sha256_json

PRODUCTION_GATE_VERIFIER_CANDIDATE_AUDIT_SCHEMA = (
    "pul7sar-phase18-qwen-image-2512-production-gate-verifier-candidate-audit-v1"
)

_GATE_TOKENS: dict[str, tuple[str, ...]] = {
    "fact_lock": (
        "fact", "verify", "verified", "evidence", "source", "claim", "truth", "score", "result",
    ),
    "entity_identity_verification": (
        "entity", "identity", "person", "player", "club", "team", "disambigu", "verify", "match",
    ),
    "sentiment_neutrality": (
        "sentiment", "neutral", "respect", "tone", "loser", "winner", "humili", "mock", "editorial",
    ),
    "story_semantic_preflight": (
        "semantic", "story", "intent", "meaning", "preflight", "editorial", "concept", "narrative",
    ),
    "zero_cost_policy": (
        "cost", "free", "zero", "local", "budget", "paid", "billing", "provider", "policy",
    ),
    "semantic_layer_ownership": (
        "layer", "ownership", "semantic", "text", "brand", "geometry", "generated", "pixel", "boundary",
    ),
}

_FORBIDDEN_PATH_PARTS = {
    "tests", "test", "fixtures", "fixture", "mocks", "mock", "stubs", "stub",
    "fakes", "fake", "dummies", "dummy", "placeholders", "placeholder", "__pycache__",
}
_FORBIDDEN_NAME_TOKENS = ("fixture", "mock", "stub", "fake", "dummy", "placeholder")
_EXCLUDED_FILE_PREFIXES = (
    "qwen_image_production_gate_verifier_",
    "qwen_image_fresh_story_gate_",
)
_MAX_CANDIDATES_PER_GATE = 12
_MIN_TOKEN_SCORE = 2

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


def _iter_engine_python_files(root: Path) -> Iterable[Path]:
    engine = root / "engine"
    if not engine.is_dir():
        return ()
    files: list[Path] = []
    for path in sorted(engine.rglob("*.py")):
        relative = path.relative_to(root)
        parts = {part.lower() for part in relative.parts}
        if parts & _FORBIDDEN_PATH_PARTS:
            continue
        if path.name.startswith(_EXCLUDED_FILE_PREFIXES):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        files.append(path)
    return tuple(files)


def _callable_text(module_name: str, node: ast.AST) -> tuple[str, str]:
    name = getattr(node, "name", "")
    doc = ast.get_docstring(node, clean=True) or ""
    return name, f"{module_name} {name} {doc}".lower()


def _score(text: str, gate_id: str) -> tuple[int, list[str]]:
    matched = [token for token in _GATE_TOKENS[gate_id] if token in text]
    return len(matched), matched


def audit_production_gate_verifier_candidates(*, repo_root: Path | None = None) -> dict[str, Any]:
    """Inventory potential source callables without importing/executing repository code."""
    root = (repo_root or _repo_root()).resolve()
    candidates: dict[str, list[dict[str, Any]]] = {
        gate_id: [] for gate_id in REQUIRED_FRESH_GATE_EVIDENCE
    }
    parse_failures: list[dict[str, str]] = []
    files_scanned = 0

    for path in _iter_engine_python_files(root):
        raw = path.read_bytes()
        if not raw:
            continue
        relative = path.relative_to(root).as_posix()
        module_name = relative[:-3].replace("/", ".")
        try:
            source = raw.decode("utf-8")
            tree = ast.parse(source, filename=relative)
        except (UnicodeDecodeError, SyntaxError) as exc:
            parse_failures.append({"path": relative, "error_type": type(exc).__name__})
            continue
        files_scanned += 1
        source_sha = hashlib.sha256(raw).hexdigest()

        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            callable_name, text = _callable_text(module_name, node)
            lowered_name = callable_name.lower()
            if any(token in lowered_name for token in _FORBIDDEN_NAME_TOKENS):
                continue
            positional = list(node.args.posonlyargs) + list(node.args.args)
            signature_summary = {
                "positional_parameter_count": len(positional),
                "required_positional_parameter_count": max(
                    0, len(positional) - len(node.args.defaults)
                ),
                "has_varargs": node.args.vararg is not None,
                "has_varkw": node.args.kwarg is not None,
            }
            for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
                score, matched = _score(text, gate_id)
                if score < _MIN_TOKEN_SCORE:
                    continue
                candidates[gate_id].append(
                    {
                        "module": module_name,
                        "callable": callable_name,
                        "repository_relative_path": relative,
                        "source_file_byte_size": len(raw),
                        "source_file_sha256": source_sha,
                        "line_number": getattr(node, "lineno", None),
                        "semantic_token_score": score,
                        "matched_tokens": matched,
                        "signature_summary": signature_summary,
                        "candidate_only": True,
                        "production_backed": False,
                        "semantic_replay_qualified": False,
                        "registered": False,
                    }
                )

    for gate_id in REQUIRED_FRESH_GATE_EVIDENCE:
        candidates[gate_id].sort(
            key=lambda item: (
                -item["semantic_token_score"],
                item["repository_relative_path"],
                item["line_number"] or 0,
                item["callable"],
            )
        )
        candidates[gate_id] = candidates[gate_id][:_MAX_CANDIDATES_PER_GATE]

    payload: dict[str, Any] = {
        "schema": PRODUCTION_GATE_VERIFIER_CANDIDATE_AUDIT_SCHEMA,
        "status": "QWEN_IMAGE_2512_PRODUCTION_GATE_VERIFIER_CANDIDATES_AUDITED",
        "cost_mode": COST_MODE,
        "required_gate_order": list(REQUIRED_FRESH_GATE_EVIDENCE),
        "scan_mode": "ast_only_no_import_no_execution",
        "files_scanned": files_scanned,
        "parse_failures": parse_failures,
        "candidates": candidates,
        "candidate_counts": {gate: len(items) for gate, items in candidates.items()},
        "candidate_discovery_is_not_verification": True,
        "production_registry_mutated": False,
        "production_semantic_replay_executed": False,
        "fresh_story_gates_passed": False,
        "model_weights_loaded": False,
        "inference_executed": False,
        "genuine_golden_png_created": False,
        **{field: False for field in _FORBIDDEN_AUTHORITY_FIELDS},
    }
    payload["candidate_audit_sha256"] = sha256_json(payload)
    return payload


def verify_production_gate_verifier_candidate_audit(
    receipt: dict[str, Any], *, repo_root: Path | None = None
) -> str:
    """Re-scan live source bytes and require exact candidate-audit equivalence."""
    expected = audit_production_gate_verifier_candidates(repo_root=repo_root)
    if receipt != expected:
        raise ValueError("QWEN_PRODUCTION_VERIFIER_CANDIDATE_AUDIT_MISMATCH")
    claimed = receipt.get("candidate_audit_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("QWEN_PRODUCTION_VERIFIER_CANDIDATE_AUDIT_DIGEST_INVALID")
    return claimed
