# Phase 18 Implementation Log 293 — Launch-to-Output Attestation

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Starting HEAD: `31c0add763ab40dfca859a275d6a85f71d889708` (CS292).

`main` was read-only and was not committed to, merged, rebased, force-updated, or otherwise modified.

## Review before change

CS292 was verified terminal-green before this change set. Its production inference edge requires `--launch-manifest` and replays the launch contract before prompt extraction, model load, authorization consumption, or inference.

Review identified one remaining audit gap: CS290 post-inference provenance proves the genuine local-only candidate, but does not itself prove which CS292 launch manifest was replayed for that candidate. CS293 adds that missing join without introducing a new approval gate.

## Added

- `engine/intelligence/qwen_image_launch_to_output_attestation.py`
  - builds an exclusive JSON attestation only after both CS292 launch-manifest verification and CS290 local-inference-provenance verification succeed;
  - independently re-verifies the canonical inference receipt;
  - requires exact story/model/revision/cost/snapshot/inference-setting equality across launch and output evidence;
  - byte-binds the launch manifest, provenance receipt, canonical inference receipt, and candidate PNG;
  - keeps semantic, human-review, Golden-quality, Genuine Golden, and publication authorities false;
  - verifier reopens all bound files and reruns the upstream verifiers fail-closed.

- `tests/test_phase18_qwen_image_launch_to_output_attestation.py`
  - exact launch/output join acceptance;
  - seed drift rejection;
  - cross-story rejection;
  - network-enabled provenance rejection;
  - snapshot path drift rejection;
  - premature Genuine Golden authority rejection.

- `tools/phase18_qwen_image_launch_to_output_attestation.py`
  - explicit `build` and `verify` commands only;
  - no prompt, network, model-revision, Golden, semantic, or publication override.

- `docs/PHASE18_CHANGESET_293_LAUNCH_TO_OUTPUT_ATTESTATION.md`
  - formal contract and authority boundaries.

- `docs/PHASE18_IMPLEMENTATION_LOG_293.md`
  - this implementation record.

## Modified

None.

## Deleted

None.

## Gates preserved

CS293 does not weaken or bypass factual truth, entity/identity verification, sentiment neutrality, loser-respect, `$0-local` execution, semantic replay, composition/visual-quality checks, Human Review, exact brand/typography, SemanticPublicationGate, Genuine Golden materialization, or publication readiness.

A successful CS293 receipt can assert only that a genuine canonical inference already verified by the existing upstream contracts is cryptographically joined to the exact pre-launch manifest. It cannot assert that the candidate is visually acceptable or Golden.

## Testing

The new regression file is discoverable by the existing `tests/test_phase18_*.py` CPU validation pattern. GitHub Actions status must be checked on the final CS293 SHA before claiming terminal-green completion.

## Genuine Golden blocker

No production inference or PNG was fabricated. The available runtime still lacks a compatible NVIDIA CUDA execution environment. A real Qwen load/inference requires, on one zero-cost host, CUDA-enabled PyTorch, an NVIDIA device with native BF16 support, compatible `QwenImagePipeline`, sequential CPU offload, the exact already-local approved Qwen snapshot, and sufficient RAM/VRAM demonstrated by the real load/inference attempt.

## Remaining path

CS292 verified launch -> real compatible zero-cost GPU host -> local model load -> one-shot story-bound Qwen inference -> CS290 local provenance -> CS293 launch-to-output attestation -> existing factual/identity/sentiment/semantic/composition/visual-quality gates -> Human Review -> exact brand/typography -> SemanticPublicationGate -> CS285 exact-byte Genuine Golden materialization -> CS286 publication readiness.
