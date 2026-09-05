"""CS276 v2: exact-lineage Golden quality adjudication for one composed candidate.

Change Set 307 upgrades the original CS276 contract to the current CS303 sealed
candidate admission and requires exact receipt-lineage coherence across the
canonical and composed branches before GoldenVisualQualitySelector may run.
Generation context is derived from the sealed admission, never from legacy
CS262 fields or user input.

A Golden-quality pass does not imply Human Review, final semantic approval,
Genuine Golden PNG creation, exact brand/typography approval, or publication.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from engine.intelligence.golden_visual_quality import (
    GoldenVisualBlockers,
    GoldenVisualEvaluation,
    GoldenVisualQualitySelector,
    GoldenVisualScores,
)
from engine.intelligence.qwen_image_canonical_candidate_byte_admission import (
    CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA,
    verify_canonical_candidate_byte_admission,
)
from engine.intelligence.qwen_image_canonical_candidate_generated_layer_qa import (
    verify_canonical_candidate_generated_layer_qa,
)
from engine.intelligence.qwen_image_canonical_candidate_semantic_base_qa import (
    verify_canonical_candidate_semantic_base_qa,
)
from engine.intelligence.qwen_image_canonical_candidate_deterministic_composition_request import (
    verify_deterministic_composition_request,
)
from engine.intelligence.qwen_image_canonical_candidate_composition_execution_preflight import (
    verify_composition_execution_preflight,
)
from engine.intelligence.qwen_image_canonical_candidate_one_shot_composition_execution import (
    verify_one_shot_composition_execution,
)
from engine.intelligence.qwen_image_composed_candidate_byte_admission import (
    SCHEMA as CS272_SCHEMA,
    verify_composed_candidate_byte_admission,
)
from engine.intelligence.qwen_image_composed_candidate_hybrid_surface_semantic_qa import (
    verify_composed_candidate_hybrid_surface_semantic_qa,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_request import (
    verify_composed_candidate_visual_quality_review_request,
)
from engine.intelligence.qwen_image_composed_candidate_visual_quality_review_evidence import (
    SCHEMA as CS275_SCHEMA,
    verify_composed_candidate_visual_quality_review_evidence,
)
from engine.intelligence.qwen_image_inference_measurement import sha256_json

SCHEMA = "pul7sar-phase18-qwen-image-composed-candidate-golden-quality-adjudication-v2"
STATUS = "QWEN_IMAGE_COMPOSED_CANDIDATE_GOLDEN_QUALITY_ADJUDICATED"
_CS263_TRUE = (
    "genuine_canonical_inference_executed",
    "handoff_sealed",
    "candidate_bytes_admitted_for_post_generation_qa",
)
_CS263_FALSE = (
    "semantic_approved",
    "human_visual_review_approved",
    "genuine_golden_png_created",
    "golden_quality_approved",
    "publication_ready",
)
_CS272_TRUE = ("composition_executed", "composed_candidate_bytes_admitted_for_post_composition_qa")
_CS272_FALSE = ("composed_visual_approved", "semantic_approved", "human_visual_review_approved", "genuine_golden_png_created", "golden_quality_approved", "publication_ready")
_CS275_TRUE = ("visual_quality_review_requested", "visual_quality_review_executed", "visual_quality_evidence_admitted", "composition_executed", "composed_candidate_bytes_admitted_for_post_composition_qa", "semantic_inspection_executed", "hybrid_surface_semantic_qa_approved")
_CS275_FALSE = ("visual_quality_review_approved", "composed_visual_approved", "semantic_approved", "human_visual_review_approved", "genuine_golden_png_created", "golden_quality_approved", "publication_ready")
_FINAL_FALSE = ("composed_visual_approved", "semantic_approved", "human_visual_review_approved", "genuine_golden_png_created", "publication_ready")
Verifier = Callable[..., dict[str, Any]]


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value.lower())


def _bind(root: Path, path: Path, code: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(code)
    rr, resolved = root.resolve(), path.resolve()
    try:
        rel = resolved.relative_to(rr).as_posix()
    except ValueError as exc:
        raise ValueError(code) from exc
    raw = resolved.read_bytes()
    if not raw:
        raise ValueError(code)
    return {"repository_relative_path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "byte_size": len(raw)}


def _reopen(root: Path, binding: Mapping[str, Any], code: str) -> Path:
    rel = binding.get("repository_relative_path")
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ValueError(code)
    path = root.resolve() / rel
    current = _bind(root, path, code)
    if any(current[key] != binding.get(key) for key in current):
        raise ValueError(code + "_BYTE_DRIFT")
    return path


def _require(receipt: Mapping[str, Any], true_fields: tuple[str, ...], false_fields: tuple[str, ...], prefix: str) -> None:
    for field in true_fields:
        if receipt.get(field) is not True:
            raise ValueError(f"{prefix}_REQUIRED_GATE_MISSING:{field}")
    for field in false_fields:
        if receipt.get(field) is not False:
            raise ValueError(f"{prefix}_PREMATURE_AUTHORITY:{field}")


def _same_png(left: Mapping[str, Any], right: Mapping[str, Any], code: str) -> None:
    for key in ("repository_relative_path", "sha256", "byte_size", "width", "height"):
        if left.get(key) != right.get(key):
            raise ValueError(f"{code}:{key}")


def _exact_receipt(binding: Mapping[str, Any], receipt: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "repository_relative_path": binding.get("repository_relative_path"),
        "sha256": binding.get("sha256"),
        "byte_size": binding.get("byte_size"),
        "receipt_sha256": receipt.get("receipt_sha256"),
    }


def _verified_source(root: Path, parent: Mapping[str, Any], field: str, verifier: Verifier, code: str) -> tuple[Mapping[str, Any], dict[str, Any]]:
    binding = parent.get(field)
    if not isinstance(binding, Mapping):
        raise ValueError(code + "_BINDING_MISSING")
    child = verifier(_reopen(root, binding, code), repo_root=root)
    if binding.get("receipt_sha256") != child.get("receipt_sha256"):
        raise ValueError(code + "_RECEIPT_DRIFT")
    return binding, child


def _derive_candidate_admission_from_cs272(root: Path, cs272: Mapping[str, Any]) -> tuple[Mapping[str, Any], dict[str, Any]]:
    _, cs271 = _verified_source(root, cs272, "source_cs271_receipt", verify_one_shot_composition_execution, "QWEN_GOLDEN_ADJUDICATION_CS271_INVALID")
    _, cs270 = _verified_source(root, cs271, "source_cs270_receipt", verify_composition_execution_preflight, "QWEN_GOLDEN_ADJUDICATION_CS270_INVALID")
    _, cs269 = _verified_source(root, cs270, "source_cs269_receipt", verify_deterministic_composition_request, "QWEN_GOLDEN_ADJUDICATION_CS269_INVALID")
    _, cs268 = _verified_source(root, cs269, "source_cs268_receipt", verify_canonical_candidate_generated_layer_qa, "QWEN_GOLDEN_ADJUDICATION_CS268_INVALID")
    _, cs264 = _verified_source(root, cs268, "source_cs264_receipt", verify_canonical_candidate_semantic_base_qa, "QWEN_GOLDEN_ADJUDICATION_CS264_INVALID")
    binding = cs264.get("source_candidate_admission")
    if not isinstance(binding, Mapping):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS303_BINDING_MISSING")
    admission = verify_canonical_candidate_byte_admission(_reopen(root, binding, "QWEN_GOLDEN_ADJUDICATION_CS303_INVALID"), repo_root=root)
    if binding.get("receipt_sha256") != admission.get("receipt_sha256"):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS303_RECEIPT_DRIFT")
    return binding, admission


def _derive_cs272_binding_from_cs275(root: Path, cs275: Mapping[str, Any]) -> Mapping[str, Any]:
    _, cs274 = _verified_source(root, cs275, "source_cs274_request", verify_composed_candidate_visual_quality_review_request, "QWEN_GOLDEN_ADJUDICATION_CS274_INVALID")
    _, cs273 = _verified_source(root, cs274, "source_cs273_receipt", verify_composed_candidate_hybrid_surface_semantic_qa, "QWEN_GOLDEN_ADJUDICATION_CS273_INVALID")
    binding = cs273.get("source_cs272_receipt")
    if not isinstance(binding, Mapping):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS272_LINEAGE_MISSING")
    return binding


def _assert_exact_lineage(*, repo_root: Path, cs263_binding: Mapping[str, Any], cs263: Mapping[str, Any], cs272_binding: Mapping[str, Any], cs272: Mapping[str, Any], cs275: Mapping[str, Any]) -> None:
    derived263_binding, derived263 = _derive_candidate_admission_from_cs272(repo_root, cs272)
    if _exact_receipt(cs263_binding, cs263) != _exact_receipt(derived263_binding, derived263):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS263_CS272_LINEAGE_DRIFT")
    derived272_binding = _derive_cs272_binding_from_cs275(repo_root, cs275)
    if _exact_receipt(cs272_binding, cs272) != _exact_receipt(derived272_binding, cs272):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS272_CS275_LINEAGE_DRIFT")


def _assert_inputs(cs263: Mapping[str, Any], cs272: Mapping[str, Any], cs275: Mapping[str, Any]) -> None:
    if cs263.get("schema") != CANONICAL_CANDIDATE_BYTE_ADMISSION_SCHEMA:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS263_SCHEMA_DRIFT")
    if cs272.get("schema") != CS272_SCHEMA:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS272_SCHEMA_DRIFT")
    if cs275.get("schema") != CS275_SCHEMA:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS275_SCHEMA_DRIFT")
    _require(cs263, _CS263_TRUE, _CS263_FALSE, "QWEN_GOLDEN_ADJUDICATION_CS263")
    _require(cs272, _CS272_TRUE, _CS272_FALSE, "QWEN_GOLDEN_ADJUDICATION_CS272")
    _require(cs275, _CS275_TRUE, _CS275_FALSE, "QWEN_GOLDEN_ADJUDICATION_CS275")
    if cs263.get("cost_mode") != "$0-local" or cs263.get("network_allowed") is not False or cs263.get("local_files_only") is not True:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CS263_LOCAL_ONLY_DRIFT")
    story = cs263.get("story_snapshot_sha256")
    if not _is_sha256(story) or cs272.get("story_snapshot_sha256") != story or cs275.get("story_snapshot_sha256") != story:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CROSS_STORY")
    c263, c272 = cs263.get("candidate_png"), cs272.get("source_candidate_png")
    p272, p275 = cs272.get("composed_candidate_png"), cs275.get("composed_candidate_png")
    if not all(isinstance(item, Mapping) for item in (c263, c272, p272, p275)):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_PNG_BINDING_INVALID")
    _same_png(c263, c272, "QWEN_GOLDEN_ADJUDICATION_BASE_CANDIDATE_DRIFT")
    _same_png(p272, p275, "QWEN_GOLDEN_ADJUDICATION_COMPOSED_CANDIDATE_DRIFT")


def _generation_context(cs263: Mapping[str, Any]) -> tuple[str, int]:
    source = cs263.get("source_canonical_inference_receipt")
    settings = cs263.get("inference_settings")
    if not isinstance(source, Mapping) or not _is_sha256(source.get("receipt_sha256")):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_CANONICAL_CONTEXT_MISSING")
    if not isinstance(settings, Mapping):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_SETTINGS_MISSING")
    seed = settings.get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_SEED_INVALID")
    return str(source["receipt_sha256"]), seed


def _evaluation(cs263: Mapping[str, Any], cs275: Mapping[str, Any]) -> GoldenVisualEvaluation:
    source_sha, seed = _generation_context(cs263)
    scores, blockers = cs275.get("scores"), cs275.get("blockers")
    if not isinstance(scores, Mapping) or not isinstance(blockers, Mapping):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_REVIEW_EVIDENCE_INVALID")
    try:
        score_obj = GoldenVisualScores(**dict(scores))
        blocker_obj = GoldenVisualBlockers(**dict(blockers))
    except (TypeError, ValueError) as exc:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_REVIEW_EVIDENCE_INVALID") from exc
    return GoldenVisualEvaluation(request_id=f"qwen-canonical-{source_sha}", seed=seed, scores=score_obj, blockers=blocker_obj)


def _adjudication_values(cs263: Mapping[str, Any], cs275: Mapping[str, Any]) -> tuple[GoldenVisualEvaluation, Any]:
    evaluation = _evaluation(cs263, cs275)
    selection = GoldenVisualQualitySelector().select((evaluation,))
    if (selection.selected is not None) != evaluation.approved:
        raise RuntimeError("QWEN_GOLDEN_ADJUDICATION_SELECTOR_STATE_DRIFT")
    return evaluation, selection


def build_composed_candidate_golden_quality_adjudication(cs263_receipt_path: Path, cs272_receipt_path: Path, cs275_receipt_path: Path, output_dir: Path, *, repo_root: Path) -> Path:
    if output_dir.exists() or not output_dir.parent.is_dir():
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_OUTPUT_INVALID")
    b263 = _bind(repo_root, cs263_receipt_path, "QWEN_GOLDEN_ADJUDICATION_CS263_INVALID")
    b272 = _bind(repo_root, cs272_receipt_path, "QWEN_GOLDEN_ADJUDICATION_CS272_INVALID")
    b275 = _bind(repo_root, cs275_receipt_path, "QWEN_GOLDEN_ADJUDICATION_CS275_INVALID")
    cs263 = verify_canonical_candidate_byte_admission(cs263_receipt_path, repo_root=repo_root)
    cs272 = verify_composed_candidate_byte_admission(cs272_receipt_path, repo_root=repo_root)
    cs275 = verify_composed_candidate_visual_quality_review_evidence(cs275_receipt_path, repo_root=repo_root)
    _assert_inputs(cs263, cs272, cs275)
    _assert_exact_lineage(repo_root=repo_root, cs263_binding=b263, cs263=cs263, cs272_binding=b272, cs272=cs272, cs275=cs275)
    evaluation, selection = _adjudication_values(cs263, cs275)
    canonical_receipt_sha, _ = _generation_context(cs263)
    receipt: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "story_snapshot_sha256": cs263["story_snapshot_sha256"],
        "source_cs263_receipt": {**b263, "receipt_sha256": cs263.get("receipt_sha256")},
        "source_cs272_receipt": {**b272, "receipt_sha256": cs272.get("receipt_sha256")},
        "source_cs275_receipt": {**b275, "receipt_sha256": cs275.get("receipt_sha256")},
        "source_candidate_png": dict(cs263["candidate_png"]),
        "composed_candidate_png": dict(cs275["composed_candidate_png"]),
        "generation_context": {
            "request_id": evaluation.request_id,
            "request_id_source": "exact_canonical_inference_receipt_sha256",
            "seed": evaluation.seed,
            "seed_source": "sealed_cs303_inference_settings",
            "canonical_inference_receipt_sha256": canonical_receipt_sha,
        },
        "scores": dict(asdict(evaluation.scores)),
        "blockers": dict(asdict(evaluation.blockers)),
        "weighted_score": evaluation.scores.weighted_score,
        "active_blockers": list(evaluation.blockers.active),
        "quality_tier": evaluation.quality_tier,
        "selected_request_id": selection.selected.request_id if selection.selected else None,
        "rejected_request_ids": list(selection.rejected_request_ids),
        "golden_quality_selector_executed": True,
        "golden_quality_approved": evaluation.approved,
        "composition_executed": True,
        "composed_candidate_bytes_admitted_for_post_composition_qa": True,
        "semantic_inspection_executed": True,
        "hybrid_surface_semantic_qa_approved": True,
        "visual_quality_review_executed": True,
        "visual_quality_evidence_admitted": True,
        "composed_visual_approved": False,
        "semantic_approved": False,
        "human_visual_review_approved": False,
        "genuine_golden_png_created": False,
        "publication_ready": False,
        "policy": {
            "request_id_not_user_supplied": True,
            "seed_not_user_supplied": True,
            "sealed_cs303_contract_required": True,
            "exact_cs263_to_cs272_lineage_required": True,
            "exact_cs272_to_cs275_lineage_required": True,
            "zero_cost_local_generation_required": True,
            "existing_golden_selector_reused": True,
            "golden_quality_does_not_replace_human_review": True,
            "golden_quality_does_not_replace_semantic_publication": True,
            "golden_quality_approval_is_not_genuine_golden_png_creation": True,
        },
    }
    receipt["receipt_sha256"] = sha256_json(receipt)
    output_dir.mkdir(mode=0o700)
    path = output_dir / "composed_candidate_golden_quality_adjudication.json"
    tmp = output_dir / ".composed_candidate_golden_quality_adjudication.json.tmp"
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, ensure_ascii=False, separators=(",", ":")) + "\n")
            handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        if tmp.exists(): tmp.unlink()
        if output_dir.exists() and not any(output_dir.iterdir()): output_dir.rmdir()
        raise
    return path


def verify_composed_candidate_golden_quality_adjudication(receipt_path: Path, *, repo_root: Path) -> dict[str, Any]:
    if receipt_path.is_symlink() or not receipt_path.is_file():
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_RECEIPT_INVALID")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_RECEIPT_INVALID") from exc
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA or receipt.get("status") != STATUS:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_RECEIPT_INVALID")
    unsigned = dict(receipt); claimed = unsigned.pop("receipt_sha256", None)
    if not _is_sha256(claimed) or claimed != sha256_json(unsigned):
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_RECEIPT_DIGEST_MISMATCH")
    verifiers = (
        ("source_cs263_receipt", verify_canonical_candidate_byte_admission),
        ("source_cs272_receipt", verify_composed_candidate_byte_admission),
        ("source_cs275_receipt", verify_composed_candidate_visual_quality_review_evidence),
    )
    bindings: list[Mapping[str, Any]] = []
    verified: list[dict[str, Any]] = []
    for field, verifier in verifiers:
        binding = receipt.get(field)
        if not isinstance(binding, Mapping):
            raise ValueError("QWEN_GOLDEN_ADJUDICATION_SOURCE_BINDING_INVALID")
        source = verifier(_reopen(repo_root, binding, "QWEN_GOLDEN_ADJUDICATION_SOURCE_INVALID"), repo_root=repo_root)
        if binding.get("receipt_sha256") != source.get("receipt_sha256"):
            raise ValueError("QWEN_GOLDEN_ADJUDICATION_SOURCE_RECEIPT_DRIFT")
        bindings.append(binding); verified.append(source)
    cs263, cs272, cs275 = verified
    _assert_inputs(cs263, cs272, cs275)
    _assert_exact_lineage(repo_root=repo_root, cs263_binding=bindings[0], cs263=cs263, cs272_binding=bindings[1], cs272=cs272, cs275=cs275)
    evaluation, selection = _adjudication_values(cs263, cs275)
    canonical_receipt_sha, _ = _generation_context(cs263)
    expected = {
        "story_snapshot_sha256": cs263["story_snapshot_sha256"],
        "source_candidate_png": dict(cs263["candidate_png"]),
        "composed_candidate_png": dict(cs275["composed_candidate_png"]),
        "generation_context": {
            "request_id": evaluation.request_id,
            "request_id_source": "exact_canonical_inference_receipt_sha256",
            "seed": evaluation.seed,
            "seed_source": "sealed_cs303_inference_settings",
            "canonical_inference_receipt_sha256": canonical_receipt_sha,
        },
        "scores": dict(asdict(evaluation.scores)),
        "blockers": dict(asdict(evaluation.blockers)),
        "weighted_score": evaluation.scores.weighted_score,
        "active_blockers": list(evaluation.blockers.active),
        "quality_tier": evaluation.quality_tier,
        "selected_request_id": selection.selected.request_id if selection.selected else None,
        "rejected_request_ids": list(selection.rejected_request_ids),
        "golden_quality_approved": evaluation.approved,
    }
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise ValueError(f"QWEN_GOLDEN_ADJUDICATION_VERDICT_DRIFT:{field}")
    if receipt.get("golden_quality_selector_executed") is not True:
        raise ValueError("QWEN_GOLDEN_ADJUDICATION_SELECTOR_NOT_EXECUTED")
    for field in _FINAL_FALSE:
        if receipt.get(field) is not False:
            raise ValueError(f"QWEN_GOLDEN_ADJUDICATION_PREMATURE_AUTHORITY:{field}")
    return receipt
