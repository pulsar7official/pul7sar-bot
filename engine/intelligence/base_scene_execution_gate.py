"""Fail-closed execution gate between semantic base-scene inspection and hybrid composition.

This combines semantic inspection completeness with hybrid layer-ownership QA so a
FLUX base scene cannot reach deterministic composition merely because inspection
results were logged. Missing/low-confidence required checks and detected leakage
both block execution.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.hybrid_layer_planner import HybridLayerPlan
from engine.intelligence.semantic_layer_evidence import SemanticLayerEvidenceAdapter
from engine.intelligence.semantic_visual_verdict import SemanticVisualVerdict
from engine.intelligence.visual_layer_qa import HybridLayerQualityGate, LayerLeakageEvidence


@dataclass(frozen=True)
class BaseSceneExecutionDecision:
    allowed: bool
    inspection_complete: bool
    blockers: tuple[str, ...]
    evidence: LayerLeakageEvidence


class BaseSceneExecutionGate:
    """Require completed semantic layer evidence and a clean ownership decision."""

    def __init__(self, *, minimum_confidence: float = 0.85) -> None:
        self.adapter = SemanticLayerEvidenceAdapter(minimum_confidence=minimum_confidence)
        self.layer_gate = HybridLayerQualityGate()

    def evaluate(
        self,
        plan: HybridLayerPlan,
        verdict: SemanticVisualVerdict,
        *,
        require_exact_number_check: bool,
        require_sport_geometry_check: bool,
    ) -> BaseSceneExecutionDecision:
        inspection = self.adapter.adapt(
            verdict,
            require_exact_number_check=require_exact_number_check,
            require_sport_geometry_check=require_sport_geometry_check,
        )
        blockers = list(inspection.blockers)
        if inspection.complete:
            ownership = self.layer_gate.evaluate(plan, inspection.evidence)
            blockers.extend(ownership.blockers)
        return BaseSceneExecutionDecision(
            allowed=inspection.complete and not blockers,
            inspection_complete=inspection.complete,
            blockers=tuple(blockers),
            evidence=inspection.evidence,
        )

    def assert_allowed(
        self,
        plan: HybridLayerPlan,
        verdict: SemanticVisualVerdict,
        *,
        require_exact_number_check: bool,
        require_sport_geometry_check: bool,
    ) -> BaseSceneExecutionDecision:
        decision = self.evaluate(
            plan,
            verdict,
            require_exact_number_check=require_exact_number_check,
            require_sport_geometry_check=require_sport_geometry_check,
        )
        if not decision.allowed:
            raise ValueError("BASE_SCENE_EXECUTION_BLOCKED: " + "; ".join(decision.blockers))
        return decision
