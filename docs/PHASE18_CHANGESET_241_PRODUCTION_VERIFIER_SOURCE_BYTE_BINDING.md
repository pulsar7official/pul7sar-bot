# Phase 18 Change Set 241 — Production Verifier Source Object + Byte Binding

## Purpose

Change Set 240 required every future production gate-replay adapter to declare a gate ID, stable verifier identity/version, literal production-backed status, and source module/callable provenance. That closed weak metadata cases, but the source provenance was still string-only.

Change Set 241 closes that gap without pretending the six production semantic adapters already exist. A readiness binding is now valid only when the adapter binds the actual source callable object it delegates to and that object's repository source file can be byte-bound.

## New fail-closed requirements

Every future production adapter must provide all Change Set 240 metadata plus:

- `PUL7SAR_SOURCE_CALLABLE_OBJECT`: the actual callable source object;
- exact agreement between that object's `__module__` / `__qualname__` or `__name__` and the declared source module/callable;
- a source callable signature that accepts the Phase 18 replay call shape `(evidence_path, story_snapshot_sha256, receipt)`;
- a source file that resolves inside the PUL7SAR repository;
- a source path that is not under test/fixture/mock/stub/fake/dummy/placeholder locations;
- a non-empty source file whose byte size and SHA-256 are recorded in the readiness receipt.

A string declaration that points to no bound source object is therefore no longer structurally ready.

## Receipt schema

The readiness schema is advanced to:

`pul7sar-phase18-qwen-image-2512-production-gate-verifier-readiness-v3`

Each binding now records, in addition to the Change Set 240 fields:

- `source_object_bound`;
- `source_object_matches_declaration`;
- `source_signature_compatible`;
- `source_repository_relative_path`;
- `source_file_byte_size`;
- `source_file_sha256`;
- `source_file_byte_bound`.

The aggregate receipt also records:

- `all_source_objects_bound`;
- `all_source_files_byte_bound`.

`verify_production_gate_verifier_readiness()` re-audits the live registry and source bytes and requires exact receipt equivalence, so changing a source file or merely rewriting the outer receipt digest cannot preserve an old readiness claim.

## Authority boundary

This Change Set does **not** execute production semantic replay. It does **not** prove that a source callable implements correct Fact Lock, identity, sentiment, semantic, zero-cost, or layer-ownership logic. Those semantics must still be replayed through Change Set 238 against the byte-bound fresh-story evidence and matching receipts.

The following remain false at this layer:

- `production_semantic_replay_executed`;
- `fresh_story_gates_passed`;
- `controlled_trial_preflight_valid`;
- `runtime_floor_proven`;
- `local_runtime_qualified`;
- `canonical_generation_authorized`;
- `canonical_pixels_reusable`;
- `model_weights_loaded`;
- `inference_executed`;
- `genuine_golden_png_created`;
- `semantic_approved`;
- `human_visual_review_approved`;
- `golden_quality_approved`;
- `publication_ready`.

## Canonical registry status

`engine/intelligence/qwen_image_production_gate_verifier_registry.py` remains intentionally empty. No fixture, stub, receipt echo, or synthetic verifier was registered to satisfy readiness.

Six genuine production-backed adapters are still required for:

1. Fact Lock;
2. Entity/Identity Verification;
3. Sentiment/Neutrality;
4. Story Semantic Preflight;
5. canonical `$0-local` policy;
6. Semantic/Layer Ownership.

## Test coverage

The Change Set extends canonical `unittest` coverage for:

- string-only provenance rejection;
- source-object/declaration mismatch;
- incompatible source callable signature;
- repository-external source files;
- source file byte-size/SHA binding;
- source digest tampering even after outer receipt re-hashing;
- all previous Change Set 239/240 missing/extra/duplicate/authority-drift cases.

## Golden path impact

The path remains fail-closed:

`230 real GPU envelope → 231 same-runtime candidate → 232 host-bound qualification → 233 controlled Golden preflight → 234 live same-host recheck → 235 byte-bound story evidence → 236 same-story gate contract → 237 immutable fresh bundle → 238 actual semantic replay → 239 production verifier readiness → 240 declared production provenance → 241 source-object + source-byte binding → six genuine adapters + fresh semantic replay → explicit canonical generation authorization → genuine Qwen PNG → Semantic/Layer QA → byte-bound Visual Critic → Human Review → Golden ≥8.5 / elite ≥9.0 → Exact Brand/Typography → SemanticPublicationGate`

## GPU status

No CUDA/Qwen inference is performed by this Change Set. The first genuine Golden Visual PNG remains blocked until a compatible `$0-local` NVIDIA host is available with native BF16, sufficient live VRAM/system RAM, the exact pinned `Qwen/Qwen-Image-2512` revision, compatible `Diffusers/QwenImagePipeline`, and successful sequential CPU offload.
