# Phase 18 Implementation Log — CS394

## Scope

CS394 hardens the CPU-safe replay verifier for the first genuine Golden Editorial v6 Candidate 1 artifact. It does not generate pixels, load a model, authorize Human Review, authorize Golden Quality, or authorize publication.

## Branch isolation

- Working branch: `phase18/story-intelligence` only.
- Branch HEAD at review start: `401e195783a2bbb349399d54b8371dbb4e8ecc7b`.
- `main` was reviewed read-only at `064fd78cefdf033722e1ca81353a617a3753c43d`.
- No write, merge, rebase, reset, or force-update was performed on `main`.

## Verified gap

The CS393 replay verifier assumed that the `png` path stored in the v6 resource-lock receipt could be resolved directly beneath the extracted artifact root. That assumption is not true for the real producer/archive seam:

1. `tools/phase18_colab_first_genuine_resources_locked.py` writes the generated PNG path from the live repository/runner filesystem into the final receipt; this path can be absolute.
2. `.github/workflows/phase18-first-genuine-golden-v6.yml` uploads multiple `output/...` trees in one `actions/upload-artifact@v4` invocation.
3. For multiple upload paths, upload-artifact uses their least common ancestor as the artifact root. The common `output` directory can therefore be stripped from extracted archive member paths.

Without explicit safe rebasing, the independent replay verifier could reject a genuine v6 artifact solely because the original runner path no longer exists after download.

## Code changes

### Modified `tools/phase18_verify_first_genuine_golden_v6_artifact.py`

- Added fail-closed `_artifact_png(...)` resolution.
- Never trusts an arbitrary absolute runner path.
- Requires the recorded path to contain the literal `output` path segment.
- Reconstructs only the suffix beneath `output` inside the caller-supplied extracted artifact root.
- Supports both legitimate archive layouts:
  - native upload-artifact least-common-ancestor layout where `output/` is stripped;
  - explicitly rewrapped extraction where `output/` is retained.
- Rejects path traversal / `..` escape.
- Rejects non-`output`-rooted recorded paths.
- Rejects ambiguous bundles when both legal rebased locations contain a PNG.
- Preserves PNG signature and SHA-256 byte binding.
- Adds independent `png_bytes` validation against the final resource-lock receipt.
- Keeps Human Review, Golden Quality, publication, and Seeds 2–4 authority fail-closed.

Production hardening commit: `10df0e7cea24720715ad9978031cce7903381a5c`.

### Modified `tests/test_phase18_verify_first_genuine_golden_v6_artifact.py`

Regression coverage now includes:

- existing retained-`output/` extraction succeeds;
- native upload-artifact LCA layout succeeds when the receipt contains an absolute self-hosted-runner path;
- PNG byte tampering fails;
- receipt `png_bytes` drift fails even when SHA-256 still matches;
- illegal publication authority fails;
- arbitrary absolute path not rooted at the producer `output` tree fails;
- ambiguous rebased PNG locations fail closed.

Exact code-and-test-bearing commit: `0925964e6a6f1221dd2cf3f7a442b5e996c7769f`.

## Added / modified / deleted

- Added: `docs/PHASE18_IMPLEMENTATION_LOG_394.md`.
- Modified: `tools/phase18_verify_first_genuine_golden_v6_artifact.py`.
- Modified: `tests/test_phase18_verify_first_genuine_golden_v6_artifact.py`.
- Deleted: none.
- Dependency changes: none.
- Generation workflow behavior: unchanged.
- Model revisions: unchanged.

## Tests / verification

A `Phase 18 Story Intelligence Verification` run was automatically created for exact code-and-test commit `0925964e6a6f1221dd2cf3f7a442b5e996c7769f`:

- run id: `34544090719`
- run number: `5426`
- state at documentation time: `queued`

CS394 must not be called terminal-green until that exact code-and-test run completes successfully.

## Golden PNG status

No Genuine Golden PNG was created or claimed in CS394. This change is execution-preparatory and post-execution verification hardening only.

The genuine-generation blocker remains the same: execution requires the dedicated self-hosted runner labels `gpu`, `cuda`, `bf16`, and `pul7sar-phase18`, CUDA-enabled PyTorch, native BF16 support, sufficient live VRAM/RAM/storage headroom, and the approved pinned Qwen2.5-VL and FLUX.2 snapshots already available under the `$0-local` / offline-only contract.

## Gates preserved

CS394 does not weaken or bypass factual/freshness, entity/identity, sentiment neutrality / loser-respect, zero-cost, semantic, generated-layer, visual-quality, Human Review, Golden Quality, SemanticPublicationGate, or publication gates. It grants no downstream authority.

## Remaining gap

1. Obtain a compatible `$0-local` NVIDIA CUDA/native-BF16 self-hosted execution host with approved local pinned model caches.
2. Dispatch `.github/workflows/phase18-first-genuine-golden-v6.yml` from `phase18/story-intelligence` with the required explicit confirmation.
3. Let the workflow produce Candidate 1 and its bound resource-lock/evidence artifact.
4. Download/extract that immutable artifact and run the CS394 replay verifier against the real receipt and PNG bytes.
5. Only after successful replay proceed to the independent Human Visual Review / Golden Quality stages; publication remains closed until its own downstream gates pass.
