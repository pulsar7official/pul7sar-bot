# Phase 18 Implementation Log 232

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

`main` and `main.py` were not modified, merged, rebased, force-updated, or used as a write target.

## Baseline review

Phase 18 baseline before Change Set 232:

`b08750c445a4087b4c2c65579456091a574e202a`

Change Set 231 was confirmed green before this work. Phase 18 Story Intelligence Verification run `33157308975` / run number `3688` completed with conclusion `success`; the companion Phase 18 workflows returned for the same commit were also successful.

During this implementation window, `main` continued to move independently because of posted-history automation. A read-only check observed `main` at:

`dfdba74b6d7b132300eebd3dfe0f9d40d19a20a3`

No attempt was made to synchronize Phase 18 with that branch.

## Problem closed

Change Set 231 proves that a complete locked Qwen Image 2512 engineering envelope came from one coherent runtime and emits a SHA-bound qualification candidate. However, granting even a narrowly scoped runtime qualification from that candidate alone would create an avoidable evidence gap: a downstream stage could trust candidate metadata without replaying the underlying Change Set 230 execution and its byte-bound PNG evidence.

Change Set 232 closes that gap before any controlled Golden-trial work.

## Added

### `engine/intelligence/qwen_image_host_bound_runtime_qualification.py`

Adds a CPU-only, fail-closed host-bound qualification layer.

A successful decision requires both the Change Set 231 qualification candidate and the Change Set 230 execution receipt. The execution is replayed through the existing verification chain; Change Set 231 is rebuilt from it and must equal the supplied candidate. This transitively reopens and hashes the engineering PNG bytes instead of relying on copied metadata.

The resulting receipt records an exact runtime fingerprint and grants only:

`host_bound_runtime_qualified=true`

with:

`qualification_scope=exact_observed_runtime_only`

It explicitly does not infer a portable minimum VRAM/hardware floor.

### `tools/phase18_build_qwen_host_bound_runtime_qualification.py`

Adds a repository-bound CPU-only CLI. It reads the source candidate and execution receipts, hashes both files, replays source evidence, and writes a SHA-bound host qualification receipt.

The CLI never loads Qwen, invokes CUDA, downloads a model, mutates the generation queue, or produces canonical pixels.

### `tests/test_phase18_qwen_image_host_bound_runtime_qualification.py`

Adds canonical `unittest` regressions covering:

- successful exact-host qualification from a complete replayable envelope;
- mandatory 1024×1024 / 8-step measured maximum with no expansion;
- source-candidate metadata forgery rejected by source replay;
- engineering PNG mutation rejected during replay;
- execution-file SHA mismatch rejected;
- attempted portable `runtime_floor_proven`, `local_runtime_qualified`, or canonical-generation authority forgery rejected even after receipt rehash;
- attempted 2048px envelope expansion rejected even after rehash;
- runtime-identity drift rejected even when its fingerprint and outer receipt digest are recomputed.

### Documentation

- `docs/PHASE18_CHANGESET_232_QWEN_HOST_BOUND_RUNTIME_QUALIFICATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_232.md`

## Modified

No pre-existing production/canonical generation module was modified.

No pre-existing semantic-publication, Fact Lock, identity, sentiment, visual-critic, brand, typography, Human Review, or Golden gate was modified.

## Deleted

None.

## Commits

- `5d72ba09a84f9eb2fe7ba7b33d53c6e74805c2d0` — add host-bound Qwen runtime qualification engine.
- `dfb50d7af226b894afaa6d3ee8bfe7a4db3bbf75` — add CPU-only host-bound qualification CLI.
- `330466ddfdd76fa0355767d4b7928dccee33b200` — add host-bound qualification regressions.
- `1ce461baa43cde2c54d5601d4b9b3a24985f85a7` — add Change Set 232 design documentation.
- Implementation-log commit: this document's commit becomes the Change Set 232 HEAD and is recorded by Git history itself.

## Authority boundaries preserved

A valid Change Set 232 receipt keeps all of these false:

- `runtime_floor_proven`
- `local_runtime_qualified`
- `canonical_generation_authorized`
- `canonical_pixels_reusable`
- `queue_mutated`
- `semantic_approved`
- `human_visual_review_approved`
- `golden_quality_approved`
- `publication_ready`

The positive `host_bound_runtime_qualified` field means only that the exact observed model revision + GPU/runtime identity completed the locked engineering envelope represented by the replayed evidence. A future live host must match that identity again before a controlled Golden trial can even be reviewed.

## Preserved PUL7SAR gates

No relaxation was made to:

- Fact Lock and factual correctness;
- entity/identity verification and disambiguation;
- sentiment/neutrality and loser-respect requirements;
- `$0-local` canonical generation policy;
- pinned-model provenance;
- generated text/branding/exact-facts/entity-marks/exact-sport-geometry restrictions;
- Semantic/Layer Ownership;
- byte-bound Visual Critic;
- Human Review;
- Golden threshold of 8.5 minimum / 9.0+ elite;
- Exact Brand Integrity;
- Typography Integrity;
- SemanticPublicationGate.

## Tests / CI status

The Change Set 232 regressions are written as `unittest.TestCase` tests so they participate in the canonical Phase 18 CPU discovery path.

At the time this log is first committed, pushes for Change Set 232 have triggered GitHub Actions. Final Story Intelligence Verification status for the final Change Set 232 HEAD must be checked after this log commit; it is not predeclared as green.

No GPU test is claimed in this implementation log.

## Genuine Golden Visual status

No genuine canonical Golden PNG was produced in this change set.

No Qwen Image inference, runtime envelope, local runtime floor, semantic approval, Human Review score, Golden score, or publication approval is fabricated.

## Exact external blocker

The available execution environment still does not expose a compatible self-hosted NVIDIA host proving all of the following together:

- CUDA execution;
- native BF16;
- sufficient measured live VRAM;
- sufficient system RAM;
- the exact pinned `Qwen/Qwen-Image-2512` snapshot and approved revision;
- compatible Diffusers with `QwenImagePipeline`;
- successful sequential CPU offload;
- `$0-local` execution.

Therefore Change Set 230 cannot yet be executed genuinely here, and Change Set 232 cannot honestly produce a real host-bound qualification receipt from live measurements.

## Remaining path

`230 real locked GPU envelope → 231 same-runtime qualification candidate → 232 byte-replayed host-bound qualification → live host identity recheck + fresh story/fact/identity/sentiment/semantic preflight → controlled canonical Golden-trial gate → genuine canonical PNG → Semantic/Layer QA → byte-bound Visual Critic → Human Review → Golden 8.5/9.0+ → Exact Brand/Typography → SemanticPublicationGate`
