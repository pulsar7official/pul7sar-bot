# PUL7SAR Phase 18 — Implementation Log 153

## Scope

Branch only: `phase18/story-intelligence`

`main` and `main.py` were not modified, merged, force-updated, or used as write targets.

## Starting state reviewed

- Phase 18 branch HEAD at review start: `25be02ace58319c1d30122a8d073c80be6807a98`
- `main` HEAD at review start: `a94710381bcd6a1cb152672a65b89aee6dcf1bb7`
- Previous Phase 18 HEAD verification was green: Story Intelligence Verification Run `32874471653 / 2647` completed with `success`, and the visible companion Phase 18 CPU workflows on that commit also completed successfully.
- No genuine new Golden Hybrid v5 Candidate 1 PNG existed under the latest architecture because no compatible CUDA/native-BF16 execution host was available to this run.

## Change Set 153 — Early GPU Host Qualification

### Why

The strict first-Golden bootstrap repaired the runtime and could begin cache/model preparation before the existing first-PNG path reached `GpuHostQualificationPolicy`. This left a preventable failure mode: a CUDA machine could consume time/storage downloading Qwen before later proving that its VRAM or native BF16 capability was insufficient for the locked FLUX.2 Klein path.

### Added behavior

`tools/phase18_colab_first_golden_bootstrap.py` now runs `tools/phase18_qualify_gpu_host.py` immediately after runtime repair and before shared cache-budget validation, Qwen prefetch, FLUX prefetch, or queue mutation.

The qualification must prove all of the following:

- eligible host
- exact `black-forest-labs/FLUX.2-klein-4B` identity
- `local_cuda`
- CUDA-enabled PyTorch
- native BF16 support
- sufficient VRAM under the existing host policy
- `$0-local`
- no install/download/queue/paid-API authority in the qualification receipt

The host receipt is then SHA/size-bound into the strict bootstrap evidence set.

### Bootstrap contract update

Strict bootstrap receipt moved from:

`pul7sar-first-golden-colab-bootstrap-v2`

to:

`pul7sar-first-golden-colab-bootstrap-v3`

New explicit facts:

- `gpu_host_qualification`
- `gpu_host_eligible=true`
- `native_bf16_proven=true`
- `bootstrap_evidence.gpu_host_qualification`

The canonical GitHub first-Golden workflow was updated to replay the new host evidence before accepting the Candidate 1 review artifact.

## Files modified

- `tools/phase18_colab_first_golden_bootstrap.py`
- `tests/test_phase18_colab_first_golden_bootstrap.py`
- `.github/workflows/phase18-first-golden-review.yml`
- `tests/test_phase18_first_golden_review_workflow.py`

## Files added

- `docs/PHASE18_CHANGESET_153_EARLY_GPU_HOST_QUALIFICATION.md`
- `docs/PHASE18_IMPLEMENTATION_LOG_153.md`

## Files deleted

None.

## Regression coverage added/expanded

- Exact ordering: repository integrity → runtime repair → GPU host qualification → shared cache budget → Qwen runtime/prefetch → sealed staging.
- Host qualification blocks before any model download when native BF16/eligibility is not proven.
- Qualification-policy drift that grants download/install/queue/paid-API authority is rejected.
- Bootstrap v3 evidence contains the host receipt.
- Canonical workflow replays host receipt SHA/size and rechecks exact model, CUDA runtime, native BF16, and `$0-local`.
- Human review, Golden approval, publication readiness, and Seeds 2–4 authority remain closed.

## Test status

Code/test HEAD after the runtime/workflow/test changes: `eb1b49ecf38f6c4eb0995360b2c1a421027b4b0d`.

GitHub Actions started automatically. At the time this log was written, Story Intelligence Verification Run `32880682561 / 2671` and the companion Phase 18 workflows were still queued, so Change Set 153 is **not** claimed CI-green yet.

The preceding branch HEAD `25be02ace58319c1d30122a8d073c80be6807a98` is confirmed green via Story Intelligence Verification Run `32874471653 / 2647`.

## Gates preserved without weakening

- Fact Lock
- Entity/Identity Verification
- Sentiment/Neutrality
- `$0-local`
- FLUX.2 Klein 4B identity
- native BF16 requirement
- Candidate/request/seed/canvas/SHA locks
- generated text/branding/exact facts/entity marks/sport-geometry prohibitions
- Original Scene runtime admission
- Qwen `BASE_SCENE` and `HYBRID_SURFACE`
- deterministic football geometry
- provenance/evidence replay
- Golden 8.5 minimum / 9.0+ elite
- Exact Brand Integrity
- Typography Integrity
- SemanticPublicationGate

## Remaining blocker

The first genuine Golden Hybrid v5 Candidate 1 still requires a real NVIDIA CUDA host that satisfies the existing VRAM/native-BF16 policy and can run both FLUX.2 Klein 4B and the locked Qwen semantic path.

No PNG, benchmark, or visual success is fabricated when compatible execution hardware is unavailable.

## Remaining path to first genuine Golden Visual

`immutable Phase 18 source → repository integrity → runtime repair → early GPU/native-BF16 qualification → shared cache budget → Qwen readiness → Original Scene admission → FLUX Candidate 1 → provenance replay → BASE_SCENE ownership QA → deterministic football Hybrid → HYBRID_SURFACE QA → sealed human review → explicit human acceptance → Golden 8.5/9.0 → exact brand/typography → SemanticPublicationGate`

Seeds 2–4 remain unauthorized until Candidate 1 is genuinely generated and accepted visually.
