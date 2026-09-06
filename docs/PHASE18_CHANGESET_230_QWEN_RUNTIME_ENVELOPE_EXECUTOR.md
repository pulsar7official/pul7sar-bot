# Phase 18 Change Set 230 — Qwen Image 2512 Runtime Envelope Executor

## Purpose

Change Set 230 turns the immutable Change Set 229 measurement matrix into a deterministic future execution protocol for a compatible self-hosted `$0-local` NVIDIA CUDA host. It does **not** execute CUDA in CI, establish a production runtime floor, authorize canonical generation, or create Golden/publication evidence.

The executor exists so that the first compatible GPU session cannot improvise parameters after observing results. It must consume the locked Change Set 229 plan and execute only these engineering probes in order:

1. `512x512 / 4 steps`
2. `768x768 / 6 steps`
3. `1024x1024 / 8 steps`

It uses the same identity-neutral probe prompt family, fixed seed, BF16 contract, and `sequential_cpu` offload requirement. It stops after the first failed probe.

## Baseline

Change Set 229 was verified green before this change was started. On baseline head `de875d362ca51fd2df02c02dedd3d2903edfea69`, Phase 18 Story Intelligence Verification completed successfully for both the push and pull-request workflow paths, including PR Run `33149468106 / 3656` and push Run `33149463896 / 3655`.

`main` remained separate and was not modified.

## Added runtime-envelope execution contract

`engine/intelligence/qwen_image_runtime_envelope_executor.py` adds a fail-closed evidence schema:

`pul7sar-phase18-qwen-image-2512-runtime-envelope-execution-v1`

The contract:

- replays and binds the locked Change Set 229 plan;
- requires the exact pinned Qwen Image 2512 model revision;
- enforces probe order and exact width/height/step parameters;
- enforces the fixed seed, guidance scale, BF16 contract, and identity-neutral prompt hash;
- rejects continuation after the first failure;
- rejects an incomplete successful sequence that ends without an explicit failure;
- validates successful probe telemetry;
- byte-verifies every successful engineering PNG by repository-bound path, PNG signature, file size, and SHA-256;
- rejects a failed probe that claims output PNG evidence;
- emits a SHA-bound aggregate execution receipt.

A fully successful three-probe execution remains engineering evidence only. It explicitly leaves all canonical and publication authority closed.

## Added future GPU executor CLI

`tools/phase18_execute_qwen_runtime_envelope.py` is the executable counterpart for a future compatible `$0-local` GPU host.

The parent process verifies the Change Set 229 plan and the Change Set 228 admission binding. Each engineering probe runs in a fresh isolated subprocess. The child loads only the exact local pinned snapshot using `local_files_only=True`, requests `torch.bfloat16`, activates sequential CPU offload, executes one locked probe, records telemetry, and writes a byte-addressed engineering PNG on success.

On CUDA OOM, timeout, process termination, missing output, or any other failure, the parent stops and does not attempt the remaining higher-cost probes.

The CLI never mutates the canonical generation queue and never marks its engineering PNGs reusable as canonical pixels.

## Evidence hardening during implementation

The first implementation prefilled `offload_mode=sequential_cpu` before the child had actually activated offload. That could overstate positive evidence if a probe failed earlier during import, CUDA inspection, model load, or pipeline setup.

This was hardened before Change Set 230 documentation was finalized:

- `offload_mode` starts as `null`;
- it becomes `sequential_cpu` only after `enable_sequential_cpu_offload()` returns successfully;
- failed probes may retain `offload_mode=null`;
- a successful probe is rejected unless observed offload is exactly `sequential_cpu`;
- any non-null incompatible observed offload fails closed.

The prompt SHA is also calculated from the normalized, validated identity-neutral prompt rather than from an unchecked raw string.

## Regression coverage

`tests/test_phase18_qwen_image_runtime_envelope_executor.py` uses canonical `unittest` discovery and covers:

- three ordered successful probes while all authority remains false;
- first-probe failure as valid stopped engineering evidence without falsely claiming observed offload;
- rejection of continuation after failure;
- rejection of an incomplete success sequence;
- rejection of a successful probe without observed sequential offload;
- byte-level PNG tamper detection during replay;
- probe-order drift rejection;
- authority forgery rejection even after recomputing the execution digest;
- incompatible observed offload rejection.

The tests are CPU-only simulations. They do not claim that Qwen Image 2512 ran on CUDA.

## Preserved authority boundaries

Even when all planned probes succeed, the execution receipt must keep:

- `observed_envelope_only = true`
- `engineering_evidence_only = true`
- `runtime_floor_proven = false`
- `local_runtime_qualified = false`
- `canonical_generation_authorized = false`
- `canonical_pixels_reusable = false`
- `queue_mutated = false`
- `semantic_approved = false`
- `human_visual_review_approved = false`
- `golden_quality_approved = false`
- `publication_ready = false`

Therefore Change Set 230 cannot bypass Fact Lock, Entity/Identity Verification, Sentiment/Neutrality, `$0-local` canonical cost, pinned-model provenance, semantic/layer ownership, generated-text/branding/exact-fact/entity-mark/exact-sport-geometry restrictions, byte-bound Visual Critic, Human Review, Golden quality thresholds, Exact Brand Integrity, Typography Integrity, or SemanticPublicationGate.

## Golden Visual status and blocker

No genuine accepted Golden Visual PNG was generated in this change set. No compatible CUDA execution is fabricated.

The remaining execution blocker is the absence, in the currently accessible execution environment, of a self-hosted compatible NVIDIA host that can prove together:

- CUDA availability;
- native BF16 support;
- sufficient live VRAM;
- sufficient system RAM;
- the exact pinned Qwen Image 2512 snapshot;
- a compatible Diffusers `QwenImagePipeline` runtime;
- successful sequential CPU offload;
- `$0-local` execution.

When such a host becomes available, Change Set 230 allows the locked 512/768/1024 envelope to be executed deterministically before any canonical Golden candidate is attempted.
