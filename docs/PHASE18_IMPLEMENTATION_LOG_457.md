# Phase 18 Implementation Log — CS457

## Scope

Advance `phase18/story-intelligence` toward the first genuine Golden Visual PNG without modifying `main` and without weakening factual, identity, sentiment, zero-cost, semantic-publication, native-BF16, visual-quality, or human-review gates.

## Starting state

- Starting branch HEAD: `7b9260adec862f7ae8bd7fa48761bc9fe639b96e` (CS456).
- CS456 central Phase 18 checks visible on the exact starting HEAD were successful before this change set.
- CS456 already replayed the content-bound GPU attempt contract before invoking the resource-locked Candidate 1 subprocess.
- Remaining gap: after that subprocess returned successfully, the canonical wrapper treated existence of the resource-lock JSON as sufficient readiness and did not independently replay the resource-lock contract and PNG before returning `ready=true`.

## Changes

### Modified

`tools/phase18_run_first_genuine_golden_v6_canonical_attested.py`

- Advanced canonical launch schema to `pul7sar-phase18-first-genuine-golden-v6-canonical-attested-launch-v4`.
- Added independent post-generation replay of the resource-lock receipt before canonical readiness can become true.
- The replay requires the exact resource-lock schema/status, `phase18/story-intelligence`, Candidate 1, `$0-local`, GPU eligibility, native BF16, local-only/no-network state, semantic preflight binding, and runtime stability.
- The replay explicitly requires Human Review to remain required and unapproved, Golden quality to remain unapproved, publication to remain false, and Seeds 2–4 to remain unauthorized.
- The replay validates that the PNG path remains inside the repository, exists, has the PNG signature, matches the recorded SHA-256, and matches the recorded byte count.
- Canonical return evidence now includes the resource-lock SHA-256 plus the independently replayed PNG path and PNG SHA-256.
- A successful subprocess can therefore no longer cause `ready=true` if it leaves a stale, malformed, authority-drifted, or content-drifted output receipt.
- All closed authorities remain explicitly false in every canonical return path.

`tests/test_phase18_first_genuine_golden_v6_canonical_attested_launcher.py`

- Updated the successful-generation fixture to emit a valid resource-lock receipt and PNG fixture so the new output replay is exercised rather than bypassed.
- Added assertions that the replayed PNG path and SHA-256 are surfaced by the canonical launcher.
- Added regression coverage proving that a subprocess returning successfully while leaving an unverified `{}` resource-lock does not make the canonical run ready.
- Preserved existing coverage for invalid commit, pre-GPU failure, authority drift, GPU-handoff failure, and output path collisions.

### Added

`docs/PHASE18_IMPLEMENTATION_LOG_457.md`

### Deleted

None.

## Gates deliberately unchanged

No changes were made to:

- factual verification/fact locks;
- real-person/entity identity verification;
- sentiment and loser-respect policy;
- `SemanticPublicationGate`;
- visual-quality or Human Review approval authority;
- Candidate 1 prompt, seed, dimensions, steps, guidance, or composition policy;
- Qwen2.5-VL or FLUX.2 approved model identities/revisions;
- native BF16 requirement;
- CUDA requirement;
- `$0-local` requirement;
- `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` policy;
- network-download prohibition;
- publication authority;
- Seeds 2–4 authority.

## Why this materially reduces the remaining gap

Before CS457, all pre-generation gates could be correct while the outer canonical wrapper still trusted a successful subprocess plus output-file existence. The resource-locked subprocess itself performs strong checks, but the outer boundary should independently prove that the artifact it is about to report is the exact validated Candidate 1 receipt and PNG. CS457 adds that replay at the final machine boundary. This narrows the remaining work from orchestration correctness toward actual compatible GPU execution and genuine artifact production.

## Testing state

The modified unit tests are committed with this change set. Repository-wide authoritative status remains the existing Phase 18 central verification and CPU diagnostic workflows on the final CS457 HEAD. Do not describe CS457 as terminal-green until those runs complete successfully.

## Remaining blocker to a genuine PNG

A genuine PNG still requires an available compatible self-hosted NVIDIA execution host satisfying all existing fail-closed preconditions simultaneously: CUDA-enabled PyTorch, a real CUDA device, native BF16, approved GPU/compute capability, sufficient live-free VRAM/RAM/cache/filesystem headroom, coherent Qwen2.5-VL semantic runtime, compatible FLUX runtime, and the exact approved local model snapshots. Network model download and FP16/FP32 quality substitution remain prohibited.

No PNG is claimed by this change set.
