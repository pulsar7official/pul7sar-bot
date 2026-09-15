# Phase 18 Implementation Log — CS393

## Scope
CS393 adds a CPU-safe, fail-closed post-run verifier for the First Genuine Golden Editorial v6 artifact bundle. The goal is to reduce the remaining gap between a future compatible CUDA/BF16 execution and trustworthy acceptance of the resulting Candidate 1 PNG without weakening any factual, identity, sentiment, zero-cost, semantic-publication, visual-quality, Human Review, Golden Quality, or publication gate.

## Branch isolation
- Working branch only: `phase18/story-intelligence`.
- Starting HEAD reviewed before changes: `3356e176ec83f5f739b5bd6b2b21b454aacd4007`.
- Starting HEAD Phase 18 Story Intelligence Verification: run `34534036336`, conclusion `success`.
- `main` was read only; observed HEAD during this run: `064fd78cefdf033722e1ca81353a617a3753c43d`.
- No merge, rebase, reset, force update, commit, or other write was performed against `main`.

## Verified execution blocker
No Genuine Golden PNG was created or claimed in CS393. The actual Golden v6 workflow still requires a self-hosted runner labeled `self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18`, CUDA-enabled PyTorch, native BF16, sufficient live VRAM/RAM/storage, and the approved pinned Qwen/FLUX snapshots already available locally under the `$0-local` / offline model-resolution contract. The currently available execution host for this work does not provide compatible CUDA GPU execution, so genuine inference cannot be truthfully performed here.

## Gap addressed
The v6 workflow already replays evidence before its artifact-upload step and keeps downstream authorities fail-closed. CS393 adds a reusable verifier for the extracted artifact itself so the exact PNG bytes can be independently replayed after workflow transport/download. This materially reduces the operational gap after the first real GPU run: a downloaded artifact can now be checked without model loading, GPU access, network access, pixel mutation, or publication authority.

## Added
### `tools/phase18_verify_first_genuine_golden_v6_artifact.py`
CPU-safe verifier that:
- requires schema `pul7sar-first-genuine-golden-v6-resource-lock-v4`;
- requires status `FIRST_GENUINE_GOLDEN_V6_MODEL_CACHE_RESOURCE_RUNTIME_SEMANTIC_LOCK_VERIFIED`;
- binds Candidate 1 to `phase18/story-intelligence` and `$0-local`;
- requires GPU eligibility, native BF16 proof, semantic-preflight binding, and runtime stability;
- requires `human_visual_review_approved=false`, `golden_quality_approved=false`, `publication_ready=false`, and `seeds_2_to_4_authorized=false`;
- resolves repository/artifact-relative PNG paths only inside the selected artifact root;
- requires a valid PNG signature;
- recomputes SHA-256 from the actual PNG bytes and rejects digest drift;
- returns only a replay-verification receipt and does not grant downstream authority.

### `tests/test_phase18_verify_first_genuine_golden_v6_artifact.py`
Regression coverage for:
1. valid bound PNG replay while downstream authority remains closed;
2. PNG byte tampering detection;
3. illegal publication authority rejection;
4. artifact-root path-escape rejection.

## Modified
- None in production/workflow files for CS393.

## Deleted
- Nothing.

## Dependencies
- No dependency additions, removals, or version changes.

## Tests performed before repository write
Executed the new test module in an isolated local copy:

`python -m unittest discover -s /tmp/cs393/tests -p 'test_phase18_verify_first_genuine_golden_v6_artifact.py' -v`

Result: `Ran 4 tests ... OK`.

## Repository commits
- `4a0903e514bc93bd810bbaf42c11fec8880080b7` — add fail-closed Golden v6 artifact verifier.
- `d001f4a8575e30d7cc50f12db39cb0fa28bbe5b3` — add verifier regression tests.

## Gate preservation
CS393 does not perform model loading, network model fallback, generation, composition, upload, publication, Human Review, Golden Quality approval, or Seed 2–4 authorization. It does not alter factual/freshness, Entity/Identity, sentiment/loser-respect, semantic-publication, generated-layer, visual-quality, or publication policy. All downstream authorities remain fail-closed.

## Remaining work
1. Let repository CI verify the exact branch HEAD containing CS393.
2. On the first compatible `$0-local` CUDA/BF16 self-hosted host, run `phase18-first-genuine-golden-v6.yml` from the immutable `phase18/story-intelligence` SHA.
3. Extract the resulting artifact and replay `tools/phase18_verify_first_genuine_golden_v6_artifact.py` against the actual resource-lock receipt and PNG bytes.
4. Only after byte/evidence replay succeeds should the candidate proceed to independent Human Visual Review, Golden Quality decision, and later publication gates. No such downstream approval is granted by CS393.
