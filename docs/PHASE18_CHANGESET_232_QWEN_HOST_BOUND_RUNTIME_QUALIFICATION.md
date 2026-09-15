# Phase 18 Change Set 232 — Qwen Image 2512 Host-Bound Runtime Qualification

## Purpose

Change Set 231 normalizes a complete measured 512/768/1024 Qwen Image 2512 runtime envelope into a non-authoritative qualification candidate. Change Set 232 adds the next fail-closed boundary: a CPU-only qualification decision scoped strictly to the exact runtime identity that produced the measured envelope.

This change does **not** claim a portable minimum hardware floor and does **not** authorize canonical generation. Its purpose is to preserve measured evidence so a later controlled Golden-trial gate can require the exact same observed runtime identity instead of treating one successful host as proof that arbitrary hardware is safe.

## Evidence replay

A host-bound qualification cannot be built from the Change Set 231 candidate alone. The builder requires both:

1. the Change Set 231 qualification-candidate receipt; and
2. the Change Set 230 runtime-envelope execution receipt.

The Change Set 230 execution is replayed through the existing verification chain, including byte-level verification of the referenced engineering PNGs. Change Set 231 is then rebuilt from that source execution and must match the supplied candidate exactly. This prevents a later stage from trusting rewritten runtime identity or telemetry metadata without returning to the underlying measured evidence.

## Qualification scope

A successful Change Set 232 receipt records:

- the pinned `Qwen/Qwen-Image-2512` model and approved revision;
- `$0-local` cost mode;
- source candidate and execution SHA-256 anchors;
- the exact coherent runtime identity observed across all locked probes;
- a SHA-256 runtime fingerprint derived from that identity;
- the measured 512/768/1024 envelope summary;
- `host_bound_runtime_qualified=true`;
- `qualification_scope=exact_observed_runtime_only`;
- a mandatory live-host identity recheck before any future controlled Golden trial.

The qualification may not expand the measured envelope. The current locked maximum remains 1024×1024 at 8 engineering steps because that is the largest probe in Change Set 229/230.

## Deliberately unproven / unauthorized

Even after a genuine successful GPU envelope and a valid Change Set 232 receipt, the following remain false:

- `runtime_floor_proven`
- `local_runtime_qualified`
- `canonical_generation_authorized`
- `canonical_pixels_reusable`
- `queue_mutated`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

The engineering PNGs remain non-canonical measurement evidence and cannot be repurposed as Golden pixels.

## Gates preserved

Change Set 232 does not weaken Fact Lock, entity/identity verification, sentiment/neutrality, loser-respect handling, `$0-local`, pinned-model provenance, generated-text/branding/exact-fact/entity-mark/exact-sport-geometry restrictions, Semantic/Layer Ownership, byte-bound Visual Critic, Human Review, Golden 8.5 minimum / 9.0+ elite scoring, Exact Brand Integrity, Typography Integrity, or SemanticPublicationGate.

A future canonical trial must still pass fresh story/fact/identity/sentiment preflight, semantic/layer preflight, a fresh canonical-generation gate, live runtime-identity matching, and all downstream visual/publication gates.

## Files

Added:

- `engine/intelligence/qwen_image_host_bound_runtime_qualification.py`
- `tools/phase18_build_qwen_host_bound_runtime_qualification.py`
- `tests/test_phase18_qwen_image_host_bound_runtime_qualification.py`
- `docs/PHASE18_CHANGESET_232_QWEN_HOST_BOUND_RUNTIME_QUALIFICATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_232.md`

Deleted: none.

No production canonical-generation file, `main`, or `main.py` is modified by this change set.

## GPU status

No GPU execution is fabricated by this change. The current execution environment still does not expose a compatible self-hosted NVIDIA CUDA host with the exact pinned Qwen Image 2512 snapshot, native BF16, sufficient live VRAM/system RAM, compatible Diffusers/QwenImagePipeline, successful sequential CPU offload, and `$0-local` execution. Therefore no Change Set 230 measured envelope, Change Set 232 real qualification receipt, canonical PNG, or Golden score is claimed in this change set.
