# Phase 18 Implementation Log — CS444

## Title
Canonical Golden v6 attested launcher staging

## Scope
Advance the canonical Candidate 1 path toward the same immutable-source / zero-cost host attestation contract already enforced in the JIT and offload paths, without weakening or replacing any existing factual, identity, sentiment, semantic-publication, visual-quality, native-BF16, local-cache, provenance, Human Visual Review, or publication gates.

## Baseline reviewed
- Branch: `phase18/story-intelligence`
- Baseline HEAD: `3c3e0f7c46dace1253d4cd07e11c94d2a94e9179`
- CS443 CI status: terminal green; Story Intelligence Verification and the associated Phase 18 study workflows completed successfully on the baseline SHA.
- Canonical workflow reviewed: `.github/workflows/phase18-first-genuine-golden-v6.yml`.
- The canonical workflow still invokes the existing execution blocker and explicit CUDA/native-BF16 proof before the canonical resource-locked Candidate 1 entrypoint, but unlike JIT/offload it does not yet invoke the CS439 attested pre-GPU runner directly in YAML.

## Added
### `tools/phase18_run_first_genuine_golden_v6_canonical_attested.py`
A narrow fail-closed launcher that:
1. requires an immutable 40-character expected source commit;
2. runs the existing `phase18_run_first_golden_pre_gpu_attested.run(...)` contract;
3. writes the exact pre-GPU summary evidence;
4. refuses to start canonical generation if readiness, receipt attestation, blocker emptiness, exact commit binding, or closed-authority conditions drift;
5. delegates only on success to the existing canonical entrypoint `tools/phase18_colab_first_genuine_resources_locked.py`;
6. keeps network-download, publication, and Seeds 2–4 authority closed;
7. refuses output paths outside the repository and refuses output-path collisions.

The launcher does not replace the canonical generation implementation and does not change model IDs, model revisions, prompts, Candidate 1 seed, generation parameters, precision requirements, semantic gates, or downstream replay/provenance checks.

### `tests/test_phase18_first_genuine_golden_v6_canonical_attested_launcher.py`
Standard-library `unittest` regression coverage proving:
- invalid source SHA fails before any pre-GPU or generation call;
- failed pre-GPU readiness prevents canonical generation;
- authority drift prevents canonical generation;
- fully attested readiness delegates to the existing canonical resource-locked entrypoint;
- output paths must remain distinct.

### `docs/PHASE18_IMPLEMENTATION_LOG_444.md`
This implementation record.

## Modified
None.

## Deleted
None.

## Preserved gates
- branch isolation: `phase18/story-intelligence` only;
- `main` remains untouched;
- `$0-local` contract remains inherited from the canonical workflow and pre-GPU runner;
- `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` remain unchanged in the canonical workflow;
- no model-network download is authorized;
- native BF16 remains required; no FP16/FP32 quality substitution was introduced;
- Qwen2.5-VL and FLUX immutable identities/revisions are unchanged;
- factual, entity/identity, sentiment-neutrality, SemanticPublicationGate, visual-quality, provenance, Human Visual Review, publication, and Seeds 2–4 gates are unchanged.

## Why this materially reduces the remaining gap
The canonical workflow file is large and already contains extensive source-binding, model-cache, runtime-fingerprint, PNG replay, artifact-upload, and transport-attestation logic. CS444 introduces a small, independently testable drop-in launch boundary that composes the already-green attested pre-GPU contract with the existing canonical generator without duplicating or rewriting the downstream generation path.

The remaining integration change is deliberately minimal: replace the canonical workflow's direct invocation of `phase18_colab_first_genuine_resources_locked.py` with this launcher and pass `${{ github.sha }}` as `--expected-commit`, while retaining the existing execution blocker and explicit CUDA/native-BF16 checks as defense-in-depth. Until that YAML wiring is committed and green, CS444 must not be described as full canonical workflow integration.

## First Genuine Golden PNG status
No genuine Golden PNG was produced in CS444 and none is claimed.

The execution blocker remains availability of a compatible self-hosted NVIDIA runner satisfying all existing requirements simultaneously: CUDA-enabled PyTorch, a real approved CUDA device, native BF16, sufficient live-free VRAM, sufficient available RAM and filesystem/cache headroom, compatible generation/semantic runtime, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already resolvable locally under offline `$0-local` execution.

## Commits
- `ac8729cb6cedae1ea6c372aaf6ed266d75455f49` — add canonical Golden v6 attested launcher
- `dfb7345fe46c3e46ad6d118e86e76a21332b1383` — add launcher regression coverage
- final documentation commit: this log
