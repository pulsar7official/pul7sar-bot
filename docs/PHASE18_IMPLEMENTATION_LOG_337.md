# Phase 18 Implementation Log 337 — Composed-Byte Admission → Hybrid-Surface Semantic QA

## Scope

Branch: `phase18/story-intelligence` only.

`main` was reviewed read-only. No merge, rebase, reset, force-update, or content
write to `main` is part of CS337.

## Baseline review

The current production chain after CS336 was re-read before implementation.

The repository already contains the correct post-composition semantic authority:
CS273 `qwen_image_composed_candidate_hybrid_surface_semantic_qa.py`. CS273
consumes exact CS272 composed bytes, runs the pinned Qwen2.5-VL verifier in
`HYBRID_SURFACE` mode, reuses `SemanticVisualVerdictGate` and
`SemanticLayerEvidenceAdapter`, and deliberately keeps global
`semantic_approved=false`.

CS274/275/276 remain downstream for visual-quality request/evidence/Golden
adjudication. CS337 therefore does not jump to those gates.

## Added

1. `engine/intelligence/qwen_image_composed_byte_admission_to_hybrid_surface_semantic_qa.py`
   - independently reverifies CS336;
   - reopens and independently reverifies the exact CS272 receipt selected by CS336;
   - requires exact Story, source-candidate and composed-byte continuity;
   - forces local/offline semantic-verifier execution;
   - runs and independently reverifies CS273;
   - binds CS273 back to the exact CS272 receipt bytes and receipt digest;
   - records pass or rejection without requesting CS274;
   - remains non-authoritative.

2. `tests/test_phase18_qwen_composed_byte_admission_to_hybrid_surface_semantic_qa.py`
   - scoped pass path;
   - semantic rejection path;
   - cross-story CS272 rejection;
   - exact CS273→CS272 receipt-binding enforcement;
   - premature global semantic-authority rejection;
   - static guards against Qwen generation, composition, network, CS274, Golden,
     Human Review, semantic-publication, or publication shortcuts.

3. `tools/phase18_continue_composed_byte_admission_to_hybrid_surface_semantic_qa.py`
   - operator CLI for the exact CS336→CS273 continuation;
   - exits nonzero when scoped semantic QA rejects;
   - does not advance to CS274.

4. `docs/PHASE18_CHANGESET_337_COMPOSED_BYTE_ADMISSION_TO_HYBRID_SURFACE_SEMANTIC_QA.md`

5. `docs/PHASE18_IMPLEMENTATION_LOG_337.md`

## Modified

Existing production gates: none.

This implementation log may receive a documentation-only follow-up containing
terminal CI status after the code-bearing commit is exercised by GitHub Actions.

## Deleted

None.

## Gates preserved

No Fact/Freshness, Entity/Identity, manual identity evidence, sentiment
neutrality, loser-respect, zero-cost/local-only, generated-layer, composition,
semantic, visual-quality, Human Review, brand/presentation, Golden,
SemanticPublicationGate, Genuine Golden, or publication gate is weakened or
bypassed.

A scoped CS273 semantic pass is explicitly not global semantic-publication
authority.

## Testing

Local pre-write syntax compilation was performed for the new production module,
test module and operator CLI.

GitHub Actions status: pending code-bearing branch execution at the time this
initial log entry is created.

## Genuine Golden execution blocker

No genuine Golden PNG is claimed by CS337.

The current execution environment must be requalified before genuine Qwen-Image
inference. A genuine canonical candidate requires a zero-cost host with
compatible NVIDIA CUDA, CUDA-enabled PyTorch, native BF16 support, sufficient
RAM/VRAM, the approved Qwen-Image/Diffusers runtime, the exact approved
already-local pinned Qwen model snapshot, and local verifier assets. Paid or
network fallback is not permitted.

## What remains

On a genuine candidate, the safe production path is now:

`CS336 exact composed-byte admission -> CS337 exact CS273 semantic QA -> CS274 visual-quality review request -> CS275 genuine visual-quality evidence -> CS276 Golden-quality adjudication -> Human Visual Review -> final presentation/brand review -> final composed approval -> final semantic approval -> SemanticPublicationGate -> CS285 Genuine Golden PNG -> CS286 readiness`

CS337 materially removes the receipt-selection/lineage handoff between CS336 and
CS273 while intentionally leaving every later authority independent.
