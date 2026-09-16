"""Fail-closed real-visual validation ledger for Phase 18 canonical benchmarks.

This module deliberately does not grant publication authority. It records the
real PNG evidence and review state needed after engineering completion so that
PUL7SAR can validate every canonical story family without seed cherry-picking.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from engine.intelligence.visual_benchmark_suite import PHASE18_VISUAL_BENCHMARKS

SCHEMA = "pul7sar-phase18-visual-validation-ledger-v1"
BRANCH = "phase18/story-intelligence"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
GOLDEN_MINIMUM = 8.5
_VALID_STATUSES = {"pending_real_visual", "rejected", "accepted"}
_REQUIRED_CHECKS = (
    "factual_integrity_passed",
    "identity_integrity_passed",
    "sentiment_neutrality_passed",
    "sport_geometry_passed",
    "protected_zones_passed",
    "platform_crop_passed",
    "semantic_qa_passed",
    "provenance_passed",
)


class VisualValidationLedgerError(RuntimeError):
    """Raised when a validation ledger tries to weaken a Phase 18 gate."""


def _canonical_cases() -> dict[str, Any]:
    return {case.benchmark_id: case for case in PHASE18_VISUAL_BENCHMARKS}


def candidate_png_evidence(path: str | Path) -> dict[str, Any]:
    """Return immutable evidence for a real PNG candidate.

    The function only accepts a genuine PNG signature and never interprets file
    extension as proof of an image.
    """

    candidate = Path(path)
    if not candidate.is_file():
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANDIDATE_MISSING")
    data = candidate.read_bytes()
    if len(data) <= len(PNG_SIGNATURE) or not data.startswith(PNG_SIGNATURE):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANDIDATE_NOT_PNG")
    return {
        "path": str(candidate),
        "sha256": sha256(data).hexdigest(),
        "bytes": len(data),
    }


def build_canonical_visual_validation_ledger() -> dict[str, Any]:
    """Build a publication-closed ledger containing every canonical benchmark."""

    cases: list[dict[str, Any]] = []
    for case in PHASE18_VISUAL_BENCHMARKS:
        cases.append(
            {
                "benchmark_id": case.benchmark_id,
                "event": case.event.value,
                "review_kind": case.review_kind.value,
                "goal": case.goal,
                "must_show": list(case.must_show),
                "must_avoid": list(case.must_avoid),
                "status": "pending_real_visual",
                "candidate": None,
                "checks": {name: None for name in _REQUIRED_CHECKS},
                "owner_visual_accepted": False,
                "golden_quality_score": None,
                "hard_blockers": [],
                "rejection_reasons": [],
                "publication_ready": False,
            }
        )
    return {
        "schema": SCHEMA,
        "branch": BRANCH,
        "canonical_case_count": len(cases),
        "cases": cases,
        "multi_family_visual_validation_complete": False,
        "ready_for_publication_claim": False,
        "publication_ready": False,
    }


def _validate_candidate(candidate: Mapping[str, Any] | None) -> None:
    if not isinstance(candidate, Mapping):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_REAL_PNG_EVIDENCE_REQUIRED")
    digest = candidate.get("sha256")
    size = candidate.get("bytes")
    path = candidate.get("path")
    if not isinstance(path, str) or not path.strip():
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANDIDATE_PATH_REQUIRED")
    if not isinstance(digest, str) or len(digest) != 64:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANDIDATE_SHA256_REQUIRED")
    try:
        int(digest, 16)
    except ValueError as exc:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANDIDATE_SHA256_INVALID") from exc
    if not isinstance(size, int) or isinstance(size, bool) or size <= len(PNG_SIGNATURE):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANDIDATE_SIZE_INVALID")


def _validate_case(record: Mapping[str, Any], canonical: Any) -> None:
    if record.get("event") != canonical.event.value:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_EVENT_DRIFT")
    if record.get("review_kind") != canonical.review_kind.value:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_REVIEW_KIND_DRIFT")
    if tuple(record.get("must_show", ())) != canonical.must_show:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_MUST_SHOW_DRIFT")
    if tuple(record.get("must_avoid", ())) != canonical.must_avoid:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_MUST_AVOID_DRIFT")
    if record.get("publication_ready") is not False:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANNOT_AUTHORIZE_PUBLICATION")

    status = record.get("status")
    if status not in _VALID_STATUSES:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_STATUS_INVALID")

    checks = record.get("checks")
    if not isinstance(checks, Mapping) or set(checks) != set(_REQUIRED_CHECKS):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CHECK_SET_INVALID")

    blockers = record.get("hard_blockers")
    rejection_reasons = record.get("rejection_reasons")
    if not isinstance(blockers, list) or not all(isinstance(item, str) and item for item in blockers):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_HARD_BLOCKERS_INVALID")
    if not isinstance(rejection_reasons, list) or not all(
        isinstance(item, str) and item for item in rejection_reasons
    ):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_REJECTION_REASONS_INVALID")

    if status == "pending_real_visual":
        if record.get("candidate") is not None:
            raise VisualValidationLedgerError("VISUAL_VALIDATION_PENDING_CASE_HAS_CANDIDATE")
        if record.get("owner_visual_accepted") is not False:
            raise VisualValidationLedgerError("VISUAL_VALIDATION_PENDING_CASE_OWNER_ACCEPTED")
        if record.get("golden_quality_score") is not None:
            raise VisualValidationLedgerError("VISUAL_VALIDATION_PENDING_CASE_HAS_SCORE")
        if any(value is not None for value in checks.values()):
            raise VisualValidationLedgerError("VISUAL_VALIDATION_PENDING_CASE_HAS_CHECK_RESULTS")
        if blockers or rejection_reasons:
            raise VisualValidationLedgerError("VISUAL_VALIDATION_PENDING_CASE_HAS_REVIEW_RESULT")
        return

    _validate_candidate(record.get("candidate"))

    if status == "rejected":
        if record.get("owner_visual_accepted") is not False:
            raise VisualValidationLedgerError("VISUAL_VALIDATION_REJECTED_CASE_OWNER_ACCEPTED")
        if not rejection_reasons and not blockers:
            raise VisualValidationLedgerError("VISUAL_VALIDATION_REJECTION_REASON_REQUIRED")
        return

    # accepted
    if not all(checks.get(name) is True for name in _REQUIRED_CHECKS):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_ACCEPTED_CASE_CHECK_FAILED")
    if blockers:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_ACCEPTED_CASE_HAS_HARD_BLOCKER")
    if rejection_reasons:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_ACCEPTED_CASE_HAS_REJECTION_REASON")
    if record.get("owner_visual_accepted") is not True:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_OWNER_ACCEPTANCE_REQUIRED")
    score = record.get("golden_quality_score")
    if not isinstance(score, (int, float)) or isinstance(score, bool) or float(score) < GOLDEN_MINIMUM:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_GOLDEN_SCORE_BELOW_MINIMUM")


def validate_visual_validation_ledger(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a canonical ledger and return its computed completion summary."""

    if payload.get("schema") != SCHEMA:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_SCHEMA_MISMATCH")
    if payload.get("branch") != BRANCH:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_BRANCH_MISMATCH")
    if payload.get("publication_ready") is not False or payload.get("ready_for_publication_claim") is not False:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_LEDGER_CANNOT_AUTHORIZE_PUBLICATION")

    records = payload.get("cases")
    if not isinstance(records, list):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CASES_REQUIRED")
    canonical = _canonical_cases()
    ids = [record.get("benchmark_id") for record in records if isinstance(record, Mapping)]
    if len(records) != len(canonical) or len(ids) != len(records) or len(set(ids)) != len(ids):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANONICAL_CASE_COUNT_INVALID")
    if set(ids) != set(canonical):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANONICAL_CASE_SET_INVALID")
    if payload.get("canonical_case_count") != len(canonical):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CANONICAL_COUNT_DRIFT")

    accepted = 0
    rejected = 0
    pending = 0
    for record in records:
        if not isinstance(record, Mapping):
            raise VisualValidationLedgerError("VISUAL_VALIDATION_CASE_RECORD_INVALID")
        benchmark_id = record.get("benchmark_id")
        _validate_case(record, canonical[benchmark_id])
        status = record["status"]
        accepted += status == "accepted"
        rejected += status == "rejected"
        pending += status == "pending_real_visual"

    complete = accepted == len(canonical)
    if payload.get("multi_family_visual_validation_complete") is not complete:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_COMPLETION_FLAG_DRIFT")

    return {
        "schema": SCHEMA,
        "canonical_case_count": len(canonical),
        "accepted": accepted,
        "rejected": rejected,
        "pending": pending,
        "multi_family_visual_validation_complete": complete,
        "ready_for_publication_claim": False,
        "publication_ready": False,
    }


def record_visual_review(
    payload: Mapping[str, Any],
    *,
    benchmark_id: str,
    candidate: Mapping[str, Any],
    status: str,
    checks: Mapping[str, bool | None],
    owner_visual_accepted: bool,
    golden_quality_score: float | None,
    hard_blockers: tuple[str, ...] = (),
    rejection_reasons: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Return a new validated ledger with one benchmark review recorded.

    This helper never infers acceptance from a score. ``status='accepted'`` must
    still satisfy every factual/identity/sentiment/geometry/semantic/provenance
    gate and explicit owner acceptance.
    """

    updated = deepcopy(dict(payload))
    records = updated.get("cases")
    if not isinstance(records, list):
        raise VisualValidationLedgerError("VISUAL_VALIDATION_CASES_REQUIRED")
    matches = [record for record in records if record.get("benchmark_id") == benchmark_id]
    if len(matches) != 1:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_BENCHMARK_NOT_UNIQUE")
    if status not in {"accepted", "rejected"}:
        raise VisualValidationLedgerError("VISUAL_VALIDATION_REVIEW_STATUS_REQUIRED")

    record = matches[0]
    record["status"] = status
    record["candidate"] = dict(candidate)
    record["checks"] = dict(checks)
    record["owner_visual_accepted"] = owner_visual_accepted
    record["golden_quality_score"] = golden_quality_score
    record["hard_blockers"] = list(hard_blockers)
    record["rejection_reasons"] = list(rejection_reasons)
    record["publication_ready"] = False

    updated["multi_family_visual_validation_complete"] = all(
        item.get("status") == "accepted" for item in records
    )
    updated["ready_for_publication_claim"] = False
    updated["publication_ready"] = False
    validate_visual_validation_ledger(updated)
    return updated
