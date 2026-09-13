"""Bind Visual Brain critic evidence to the exact generated candidate bytes.

A critic decision is useful only if it demonstrably refers to the same concept,
request, seed and PNG that the approved generation handoff produced.  This module
adds that fail-closed binding without granting publication authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

from engine.intelligence.visual_brain import VisualCriticEvidence, VisualCriticGate


VISUAL_BRAIN_BATCH_CONTRACT = "pul7sar-visual-brain-batch-v1"
VISUAL_BRAIN_BENCHMARK = "visual-brain-preview-season-return-v1"
CRITIC_PROVENANCE_CONTRACT = "pul7sar-visual-brain-critic-provenance-v1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _resolve_repo_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("visual critic evidence path escapes repository root") from exc
    return resolved


@dataclass(frozen=True)
class VisualCriticProvenanceReceipt:
    status: str
    candidate: int
    concept_id: str
    request_id: str
    seed: int
    payload_sha256: str
    png: str
    png_sha256: str
    batch_manifest_sha256: str
    generation_result_sha256: str
    critic_evidence_sha256: str
    critic_score: float
    critic_failures: tuple[str, ...]
    critic_accepted: bool
    publication_ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract": CRITIC_PROVENANCE_CONTRACT,
            "status": self.status,
            "candidate": self.candidate,
            "concept_id": self.concept_id,
            "request_id": self.request_id,
            "seed": self.seed,
            "payload_sha256": self.payload_sha256,
            "png": self.png,
            "png_sha256": self.png_sha256,
            "batch_manifest_sha256": self.batch_manifest_sha256,
            "generation_result_sha256": self.generation_result_sha256,
            "critic_evidence_sha256": self.critic_evidence_sha256,
            "critic_contract": VisualCriticGate.CONTRACT,
            "critic_score": self.critic_score,
            "critic_failures": list(self.critic_failures),
            "critic_accepted": self.critic_accepted,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": self.publication_ready,
        }


class VisualCriticProvenanceGate:
    """Replay identity and byte-level evidence before accepting a critic verdict."""

    def verify(
        self,
        *,
        repository_root: str | Path,
        manifest_path: str | Path,
        generation_result_path: str | Path,
        critic_evidence_path: str | Path,
    ) -> VisualCriticProvenanceReceipt:
        root = Path(repository_root).resolve()
        manifest_file = _resolve_repo_path(root, str(manifest_path))
        result_file = _resolve_repo_path(root, str(generation_result_path))
        evidence_file = _resolve_repo_path(root, str(critic_evidence_path))

        manifest = _read_json(manifest_file)
        result = _read_json(result_file)
        supplied = _read_json(evidence_file)

        if manifest.get("manifest_version") != VISUAL_BRAIN_BATCH_CONTRACT:
            raise ValueError("visual critic requires the canonical Visual Brain batch contract")
        if manifest.get("benchmark") != VISUAL_BRAIN_BENCHMARK:
            raise ValueError("visual critic benchmark identity mismatch")
        if manifest.get("publication_ready") is not False:
            raise ValueError("visual-brain manifest cannot grant publication authority")
        if manifest.get("critic_contract") != VisualCriticGate.CONTRACT:
            raise ValueError("visual critic contract drift")

        candidate_number = supplied.get("candidate")
        if not isinstance(candidate_number, int) or candidate_number < 1:
            raise ValueError("critic evidence must identify a positive integer candidate")
        candidates = manifest.get("candidates")
        if not isinstance(candidates, list):
            raise ValueError("visual-brain manifest candidates are missing")
        matches = [item for item in candidates if isinstance(item, dict) and item.get("candidate") == candidate_number]
        if len(matches) != 1:
            raise ValueError("critic candidate is not uniquely present in the manifest")
        candidate = matches[0]

        identity_fields = ("concept_id", "request_id", "seed", "payload_sha256")
        for field in identity_fields:
            expected = candidate.get(field)
            if supplied.get(field) != expected:
                raise ValueError(f"critic evidence {field} does not match the selected concept candidate")
            if result.get(field) != expected:
                raise ValueError(f"generation result {field} does not match the selected concept candidate")

        if result.get("status") != "REAL_VISUAL_PROOF_GENERATED":
            raise ValueError("critic evidence requires a genuine generated visual proof")
        if result.get("publication_ready") is not False:
            raise ValueError("generation result cannot grant publication authority")
        if result.get("cost_mode") != "$0-local":
            raise ValueError("visual-brain critic provenance requires $0-local generation")
        if result.get("model_id") != candidate.get("model_id"):
            raise ValueError("generation result model identity drift")
        if result.get("provider_id") != candidate.get("provider_id"):
            raise ValueError("generation result provider identity drift")

        png_value = result.get("png")
        if not isinstance(png_value, str) or not png_value:
            raise ValueError("generation result is missing its PNG path")
        png = _resolve_repo_path(root, png_value)
        if not png.is_file() or png.stat().st_size <= len(PNG_SIGNATURE):
            raise ValueError("generated PNG is missing or empty")
        if png.read_bytes()[: len(PNG_SIGNATURE)] != PNG_SIGNATURE:
            raise ValueError("generated visual proof does not have a PNG signature")
        png_sha256 = _sha256(png)
        if supplied.get("png_sha256") != png_sha256:
            raise ValueError("critic evidence is not bound to the generated PNG bytes")

        evidence = VisualCriticEvidence(
            concept_id=str(supplied.get("concept_id") or ""),
            geometry_violation=bool(supplied.get("geometry_violation", False)),
            pseudo_text_detected=bool(supplied.get("pseudo_text_detected", False)),
            identity_violation=bool(supplied.get("identity_violation", False)),
            factual_violation=bool(supplied.get("factual_violation", False)),
            generation_defect=bool(supplied.get("generation_defect", False)),
            editorial_specificity=float(supplied.get("editorial_specificity", 0.0)),
            visual_impact=float(supplied.get("visual_impact", 0.0)),
            composition_quality=float(supplied.get("composition_quality", 0.0)),
            photographic_coherence=float(supplied.get("photographic_coherence", 0.0)),
            concept_fidelity=float(supplied.get("concept_fidelity", 0.0)),
            ordinary_stock_risk=float(supplied.get("ordinary_stock_risk", 1.0)),
        )
        decision = VisualCriticGate().evaluate(evidence)
        status = "VISUAL_BRAIN_CRITIC_PROVENANCE_ACCEPTED" if decision.accepted else "VISUAL_BRAIN_CRITIC_PROVENANCE_REJECTED"
        return VisualCriticProvenanceReceipt(
            status=status,
            candidate=candidate_number,
            concept_id=evidence.concept_id,
            request_id=str(candidate["request_id"]),
            seed=int(candidate["seed"]),
            payload_sha256=str(candidate["payload_sha256"]),
            png=str(png),
            png_sha256=png_sha256,
            batch_manifest_sha256=_sha256(manifest_file),
            generation_result_sha256=_sha256(result_file),
            critic_evidence_sha256=_sha256(evidence_file),
            critic_score=decision.score,
            critic_failures=decision.failures,
            critic_accepted=decision.accepted,
            publication_ready=False,
        )
