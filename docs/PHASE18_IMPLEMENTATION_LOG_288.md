# Phase 18 Implementation Log 288 — Qwen-Image Model-Load Attestation

## Baseline

- Branch: `phase18/story-intelligence`
- Baseline HEAD: `a4cadeef6bad43defb6a210a81465092d26e6786` (CS287)
- CS287 `Phase 18 Story Intelligence Verification`: terminal `success` before CS288 work began (run `33370357520`, run number `4343`).
- `main` baseline observed read-only at `368e8e07a6c5926a770a75f8fc0c506143845cf2`.
- No merge, rebase, force update, commit, or file write was performed on `main`.

## Goal

CS287 made static host incompatibilities machine-readable but deliberately stopped before loading weights. CS288 reduces the remaining execution gap by adding a genuine, local-only model-load attestation for the exact approved Qwen-Image snapshot, while still refusing to claim inference or image creation.

## Added

1. `engine/intelligence/qwen_image_model_load_attestation.py`
   - requires successful CS287 static preflight before loading.
   - requires exact `$0-local` cost mode.
   - uses the immutable already-local snapshot path, `torch.bfloat16`, and `local_files_only=True`.
   - calls `enable_sequential_cpu_offload()` after a successful real model load.
   - records genuine load failure rather than inferring success from static metadata.
   - never calls the pipeline and cannot create pixels or downstream authority.

2. `tests/test_phase18_qwen_image_model_load_attestation.py`
   - static-preflight failure blocks loading.
   - non-zero-cost mode blocks loading.
   - a mocked successful real-load path proves BF16/local-files-only/sequential-offload configuration while all inference/Golden/publication flags remain false.
   - a mocked real model-load failure is recorded fail-closed.

3. `tools/phase18_qwen_image_model_load_attestation.py`
   - host-execution CLI producing JSON evidence inside the repository.
   - accepts only an already-local snapshot path and output location.
   - `--require-loaded` provides a strict non-zero exit when genuine loading/offload enabling does not succeed.
   - exposes no inference, approval, Golden, publication, network, model-revision, or cost-mode override.

4. `docs/PHASE18_CHANGESET_288_QWEN_IMAGE_MODEL_LOAD_ATTESTATION.md`
   - documents preconditions, local-only behavior, authority limits, and Golden-path relationship.

5. `docs/PHASE18_IMPLEMENTATION_LOG_288.md`
   - this implementation record.

## Modified

- No pre-existing production, policy, workflow, test, or tool file was modified.

## Deleted

- None.

## Authority preserved

CS288 creates no factual, identity, sentiment, semantic, composition, Golden-quality, human-review, brand/typography, final-semantic, SemanticPublication, materialization, or publication-readiness approval.

Even successful model loading emits:

- `genuine_inference_executed=false`
- `png_created=false`
- `semantic_approved=false`
- `genuine_golden_png_created=false`
- `publication_ready=false`

## Zero-cost / immutable execution policy

- required cost mode: `$0-local`.
- approved model: `Qwen/Qwen-Image-2512`.
- approved immutable revision: `2ce1c28560fbc62c9f5531e076b237d3575330a9`.
- the loader receives the canonical already-local `snapshots/<revision>` path, not a mutable model ref.
- `local_files_only=True` is mandatory; download fallback is not authorized.
- native BF16 and sequential CPU offload remain mandatory through the CS287 preflight and CS288 load configuration.

## Commits in this change set

- `9ce11bca8f5861b468fc579d84f2202170f96fd6` — add Qwen model-load attestation engine.
- `2a2360dda918c72366d9b63b8e6d0ad0b04e520f` — add model-load regressions.
- `4b822cca1b4d63837bdd63d6f7cbf5aed75d2584` — add model-load attestation CLI.
- `0c083e5d8d2f20aa45b07e79572a07467b549018` — document CS288 contract.

The implementation-log commit is the final commit in this change set.

## Testing

The repository's discover-based CPU validator automatically runs every `tests/test_phase18_*.py` module, so the CS288 regression file is included in `Phase 18 Story Intelligence Verification`; it is not merely syntax-checked.

Terminal CI status must be verified on the final CS288 HEAD before claiming the change set CI-green.

## Genuine execution status and exact blocker

No production model load or Qwen inference is fabricated in this change set. The currently available execution runtime remains CPU-only / without a compatible CUDA-visible NVIDIA host, so a production CS288 model-load attempt cannot pass its own CS287 preconditions here.

A real execution still requires one zero-cost host that simultaneously provides:

- NVIDIA CUDA visible to CUDA-enabled PyTorch,
- native BF16,
- importable compatible `QwenImagePipeline`,
- sequential CPU offload support,
- exact approved local Qwen snapshot revision,
- sufficient real VRAM and system RAM demonstrated by successful loading/inference rather than an invented threshold.

## Remaining gap

1. Run CS287 on the compatible zero-cost NVIDIA host with the exact local snapshot.
2. If CS287 passes, run CS288 and retain a real `model_loaded=true` / `sequential_cpu_offload_enabled=true` attestation.
3. Execute genuine Qwen inference without weakening the pinned-revision, BF16, local-only, or offload requirements.
4. Pass the real PNG through the existing factual, identity, sentiment, semantic, composition, visual-quality, Human Review, exact Brand/Typography, SemanticPublication, CS285 materialization, and CS286 publication-readiness chain.

No production Genuine Golden PNG is claimed by CS288.
