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

1. `tests/test_phase18_qwen_precomposition_to_composed_byte_admission.py`
   - regression fixture only;
   - aligned the mocked CS272 evidence with the already-enforced CS336 production
     requirement that `source_cs271_receipt` bind the exact fake CS271 receipt
     bytes, size and `receipt_sha256`;
   - no production authority or production gate was weakened.

2. `docs/PHASE18_IMPLEMENTATION_LOG_337.md`
   - records the initial CI failure, exact regression-fixture cause, corrective
     change and terminal-green code/test CI result.

Existing production gates: none modified.

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

The first CS337 branch CI on commit
`4225e0e37b616cc3d9838394ab50a53efcf0a197` reached GitHub Actions run
`33856312286` and failed during `Syntax and discover validation`.

The failure exposed a stale CS336 test fixture rather than a production-gate
failure: the fixture's mocked CS272 receipt omitted `source_cs271_receipt`, while
CS336 production code correctly requires that field to match the exact CS271
receipt byte digest and the CS271 signed `receipt_sha256`.

The regression fixture was corrected on code/test commit
`1e4ca46a30558e5d5ddfad97926b8a126dac72b1` by binding the exact fake
`one_shot_composition_execution.json` bytes (`271\n`), byte size and the mocked
CS271 `receipt_sha256`. Production CS336 code was not changed.

GitHub Actions re-ran that corrected code/test commit. `Phase 18 Story
Intelligence Verification` run `33856660753` completed successfully, including
syntax/discovery, production isolation, visual-study handoffs, composition
matrix, publication-blocking verification, project-native editorial study,
brand ownership checks, Golden editorial v6 verification and legacy-logo
non-canonical assertion. The nine other visible Phase 18 workflows on the same
commit also completed successfully.

The current HEAD after this entry is documentation-only relative to that
terminal-green code/test commit; no executable production/test change follows the
green result in this log update.

## Genuine Golden execution blocker

No genuine Golden PNG is claimed by CS337.

The execution environment requalification in this change set reported:

- PyTorch `2.10.0+cpu`;
- CUDA available: `false`;
- `torch.version.cuda`: `None`;
- CUDA device count: `0`;
- native CUDA BF16: unavailable;
- `nvidia-smi`: unavailable.

A genuine canonical candidate requires a zero-cost host with compatible NVIDIA
CUDA, CUDA-enabled PyTorch, native BF16 support, sufficient RAM/VRAM, the
approved Qwen-Image/Diffusers runtime, the exact approved already-local pinned
Qwen model snapshot, and local verifier assets. Paid or network fallback is not
permitted.

## What remains

On a genuine candidate, the safe production path is now:

`CS336 exact composed-byte admission -> CS337 exact CS273 semantic QA -> CS274 visual-quality review request -> CS275 genuine visual-quality evidence -> CS276 Golden-quality adjudication -> Human Visual Review -> final presentation/brand review -> final composed approval -> final semantic approval -> SemanticPublicationGate -> CS285 Genuine Golden PNG -> CS286 readiness`

CS337 materially removes the receipt-selection/lineage handoff between CS336 and
CS273 while intentionally leaving every later authority independent.
