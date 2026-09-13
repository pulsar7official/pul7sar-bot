"""Unified local readiness service for the first real $0 PUL7SAR generation."""

from __future__ import annotations

from dataclasses import dataclass

from engine.intelligence.local_backend import LocalBackendReadinessGate, LocalBackendSnapshot
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.local_runtime import LocalRuntimeProbe, RuntimeHardwareSnapshot
from engine.intelligence.local_vision_inspectors import LocalVisionCapabilityReport, detect_local_vision_capabilities
from engine.intelligence.zero_cost_models import LocalModelCandidate


@dataclass(frozen=True)
class LocalReadinessBundle:
    generation: LocalGenerationReadinessReport
    vision: LocalVisionCapabilityReport

    @property
    def generation_ready(self) -> bool:
        return self.generation.ready

    @property
    def publication_ready(self) -> bool:
        return self.generation.ready and self.vision.publication_grade

    def as_dict(self) -> dict[str, object]:
        return {
            "generation": self.generation.as_dict(),
            "vision": {
                "png_observation": self.vision.png_observation,
                "protected_region_clutter": self.vision.protected_region_clutter,
                "semantic_subject_framing": self.vision.semantic_subject_framing,
                "identity_similarity": self.vision.identity_similarity,
                "semantic_defect_detection": self.vision.semantic_defect_detection,
                "forbidden_visual_detection": self.vision.forbidden_visual_detection,
                "publication_grade": self.vision.publication_grade,
            },
            "generation_ready": self.generation_ready,
            "publication_ready": self.publication_ready,
            "cost_mode": "$0-local",
        }


class LocalReadinessService:
    """Produce one truthful readiness snapshot without installing anything."""

    def __init__(self, runtime_probe: LocalRuntimeProbe | None = None) -> None:
        self._runtime_probe = runtime_probe or LocalRuntimeProbe()
        self._gate = LocalBackendReadinessGate()

    def evaluate(
        self,
        *,
        model: LocalModelCandidate,
        backend: LocalBackendSnapshot,
        runtime: RuntimeHardwareSnapshot | None = None,
        vision: LocalVisionCapabilityReport | None = None,
    ) -> LocalReadinessBundle:
        runtime = runtime or self._runtime_probe.detect()
        decision = self._gate.evaluate(model=model, runtime=runtime, backend=backend)
        generation = LocalGenerationReadinessReport.build(
            model=model,
            runtime=runtime,
            backend=backend,
            readiness=decision,
        )
        return LocalReadinessBundle(generation, vision or detect_local_vision_capabilities())
