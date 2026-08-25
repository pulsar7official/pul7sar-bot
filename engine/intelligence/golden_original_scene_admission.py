"""Fail-closed Original Scene admission for the locked Golden Hybrid v5 candidate.

This module binds the provider-neutral OriginalSceneRequest contract to the
existing integrity-hashed Candidate 1 handoff and measured local readiness. It
never generates pixels, mutates the durable queue, or grants publication
readiness. Its only purpose is to prove that the currently selected local runtime
is qualified to execute the same original-first visual concept before the GPU
job may be enqueued.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256

from engine.intelligence.golden_smoke import GoldenSmokeCandidate
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.original_scene_local_bridge import OriginalSceneLocalBridge
from engine.intelligence.original_scene_runtime_contract import OriginalSceneRequest, OriginalSceneRuntimeKind
from engine.intelligence.visual_concept_director import VisualConceptArchetype
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL


EXPECTED_VISUAL_CONCEPT_CONTRACT = "pul7sar-visual-concept-director-v2-original-first"
EXPECTED_ARCHETYPE = VisualConceptArchetype.GENERATIVE_EVENT_ATMOSPHERE
EXPECTED_COST_MODE = "$0-local"
EXPECTED_BACKEND = "diffusers"
_RESERVED = ("readable_text", "pul7sar_brand", "exact_score", "club_crest", "sport_geometry")


@dataclass(frozen=True)
class GoldenOriginalSceneAdmissionReceipt:
    candidate: int
    request_id: str
    payload_sha256: str
    provider_id: str
    model_id: str
    backend: str
    seed: int
    width: int
    height: int
    visual_concept_contract: str
    visual_concept_archetype: str
    original_scene_request_contract: str
    original_scene_runtime_contract: str
    original_scene_execution_gate_contract: str
    original_scene_bridge_contract: str
    original_scene_runtime_id: str
    original_scene_runtime_kind: str
    compiled_prompt_sha256: str
    cost_mode: str
    semantic_inspection_required: bool
    generated_branding_allowed: bool
    generated_exact_facts_allowed: bool
    generated_sport_geometry_allowed: bool
    queue_mutated: bool = False
    png_created: bool = False
    semantic_approved: bool = False
    golden_quality_approved: bool = False
    publication_ready: bool = False
    status: str = "GOLDEN_ORIGINAL_SCENE_RUNTIME_ADMITTED"
    schema: str = "pul7sar-golden-original-scene-admission-v1"

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


class GoldenOriginalSceneAdmissionGate:
    """Admit Candidate 1 to a measured runtime without weakening the handoff."""

    def __init__(self, bridge: OriginalSceneLocalBridge | None = None) -> None:
        self._bridge = bridge or OriginalSceneLocalBridge()

    def admit(
        self,
        *,
        candidate: GoldenSmokeCandidate,
        readiness: LocalGenerationReadinessReport,
    ) -> GoldenOriginalSceneAdmissionReceipt:
        if not isinstance(candidate, GoldenSmokeCandidate):
            raise TypeError("candidate must be GoldenSmokeCandidate")
        if not isinstance(readiness, LocalGenerationReadinessReport):
            raise TypeError("readiness must be LocalGenerationReadinessReport")
        if candidate.candidate != 1:
            raise ValueError("GOLDEN_ORIGINAL_SCENE_ADMISSION_REQUIRES_CANDIDATE_1")

        locked = LocalGenerationHandoff.read(str(candidate.handoff_path))
        metadata = locked.metadata
        failures: list[str] = []
        expected_metadata = {
            "cost_mode": EXPECTED_COST_MODE,
            "visual_concept_contract": EXPECTED_VISUAL_CONCEPT_CONTRACT,
            "visual_concept_archetype": EXPECTED_ARCHETYPE.value,
            "visual_concept_selected_before_renderer": True,
            "generated_branding_allowed": False,
            "generated_sport_geometry_allowed": False,
            "composition_grammar": "single_continuous_scene",
        }
        for key, expected in expected_metadata.items():
            if metadata.get(key) != expected:
                failures.append(f"{key}={metadata.get(key)!r}")
        if locked.provider_id != candidate.provider_id or locked.model_id != candidate.model_id:
            failures.append("candidate_model_identity_drift")
        if locked.request_id != candidate.request_id or locked.seed != candidate.seed:
            failures.append("candidate_request_identity_drift")
        if locked.backend != EXPECTED_BACKEND:
            failures.append(f"backend={locked.backend!r}")
        if failures:
            raise ValueError("GOLDEN_ORIGINAL_SCENE_HANDOFF_CONTRACT_DRIFT:" + "; ".join(failures))

        request = OriginalSceneRequest(
            archetype=EXPECTED_ARCHETYPE,
            runtime_kind=OriginalSceneRuntimeKind.ATMOSPHERE,
            scene_intent=(
                "premium non-identifying football season-opening atmosphere in one continuous photographic world; "
                "stadium atmosphere and depth are the visual hero while turf remains restrained contextual support"
            ),
            emotional_tone="premium anticipatory global-football energy without invented outcome or identity claims",
            safe_negative_space="clean upper editorial region with uncluttered visual breathing room",
            forbidden_visual_claims=(
                "no generated branding, wordmarks, readable text, numerals or pseudo-text",
                "no collage or multi-panel layout",
                "no specific identifiable real venue",
                "no specific real-person depiction",
            ),
            exact_fact_roles_reserved_for_compositor=_RESERVED,
            width=locked.width,
            height=locked.height,
            seed=locked.seed,
        )
        compiled, bridge_receipt = self._bridge.compile(
            request=request,
            model=FLUX2_KLEIN_4B_LOCAL,
            readiness=readiness,
            backend=locked.backend,
            request_id=locked.request_id,
        )

        identity_pairs = (
            ("provider_id", locked.provider_id, compiled.provider_id),
            ("model_id", locked.model_id, compiled.model_id),
            ("backend", locked.backend, compiled.backend),
            ("request_id", locked.request_id, compiled.request_id),
            ("seed", locked.seed, compiled.seed),
            ("width", locked.width, compiled.width),
            ("height", locked.height, compiled.height),
        )
        drift = [name for name, expected, actual in identity_pairs if expected != actual]
        if drift:
            raise ValueError("GOLDEN_ORIGINAL_SCENE_COMPILED_IDENTITY_DRIFT:" + ", ".join(drift))

        for key in ("generated_branding_allowed", "generated_exact_facts_allowed", "generated_sport_geometry_allowed"):
            if compiled.metadata.get(key) is not False:
                raise ValueError("GOLDEN_ORIGINAL_SCENE_LAYER_OWNERSHIP_DRIFT:" + key)
        if compiled.metadata.get("cost_mode") != EXPECTED_COST_MODE:
            raise ValueError("GOLDEN_ORIGINAL_SCENE_ESCAPED_ZERO_COST_POLICY")
        if compiled.metadata.get("semantic_inspection_required") is not True:
            raise ValueError("GOLDEN_ORIGINAL_SCENE_SEMANTIC_INSPECTION_NOT_REQUIRED")
        if compiled.metadata.get("publication_ready") is not False or bridge_receipt.publication_ready:
            raise ValueError("GOLDEN_ORIGINAL_SCENE_ADMISSION_MAY_NOT_AUTHORIZE_PUBLICATION")

        return GoldenOriginalSceneAdmissionReceipt(
            candidate=1,
            request_id=locked.request_id,
            payload_sha256=candidate.payload_sha256,
            provider_id=locked.provider_id,
            model_id=locked.model_id,
            backend=locked.backend,
            seed=locked.seed,
            width=locked.width,
            height=locked.height,
            visual_concept_contract=EXPECTED_VISUAL_CONCEPT_CONTRACT,
            visual_concept_archetype=EXPECTED_ARCHETYPE.value,
            original_scene_request_contract=request.contract,
            original_scene_runtime_contract=bridge_receipt.runtime_contract,
            original_scene_execution_gate_contract=bridge_receipt.execution_gate_contract,
            original_scene_bridge_contract=bridge_receipt.contract,
            original_scene_runtime_id=bridge_receipt.runtime_id,
            original_scene_runtime_kind=bridge_receipt.runtime_kind,
            compiled_prompt_sha256=sha256(compiled.prompt.encode("utf-8")).hexdigest(),
            cost_mode=EXPECTED_COST_MODE,
            semantic_inspection_required=True,
            generated_branding_allowed=False,
            generated_exact_facts_allowed=False,
            generated_sport_geometry_allowed=False,
        )
