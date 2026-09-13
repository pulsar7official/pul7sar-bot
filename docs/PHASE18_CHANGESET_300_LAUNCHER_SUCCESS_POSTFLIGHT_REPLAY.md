# Phase 18 Change Set 300 — Launcher Success Postflight Replay

## Objective

Close the remaining trust gap between a zero exit code from the canonical Qwen child process and the launcher's own success decision.

Before CS300, the manifest-bound launcher enforced the verified launch manifest, the mandatory preload host gate, `$0-local`, the offline child environment, and shell-free execution. The canonical child itself produced and replayed CS290/CS293 postflight evidence before returning zero. The outer launcher, however, propagated a zero child return code without independently replaying the output evidence.

CS300 makes launcher success fail-closed on the exact output bundle.

## Production behavior

After the canonical child returns:

1. Non-zero child exit codes are propagated unchanged. No successful-output replay is attempted.
2. A zero child exit code does **not** immediately become launcher success.
3. The output directory must exist, remain repository-local, and not be a symlink.
4. The following exact files must exist as regular non-symlink files:
   - `canonical_candidate.png`
   - `canonical_inference_receipt.json`
   - `local_inference_provenance.json`
   - `launch_to_output_attestation.json`
5. The launcher replays `verify_launch_to_output_attestation(...)`.
6. That verifier recursively revalidates the launch manifest, local inference provenance, canonical inference receipt, inference settings, local-only/network-disabled contract, and the exact candidate PNG byte binding.
7. The launcher additionally refuses any replay result that prematurely claims semantic, human-review, Golden-quality, Genuine-Golden, or publication authority.
8. Only after all of the above can `execute_manifest_bound_inference(...)` return `0`.

## Authority boundaries

CS300 proves only that a child process which returned zero also left behind a replay-valid genuine canonical candidate bundle tied to the authorized launch.

It does **not** make the candidate a Golden Visual and does not grant:

- semantic approval,
- human visual review approval,
- Golden-quality approval,
- Genuine Golden PNG materialization,
- publication readiness.

Fact/freshness, identity/entity, sentiment/loser-respect, semantic ownership, composition, generated-layer QA, visual-quality, human review, exact brand/typography, `SemanticPublicationGate`, CS285, and CS286 remain independent downstream gates.

## Zero-cost and network policy

No network path or paid service was added. CS299's child environment remains enforced:

- `PUL7SAR_PHASE18_COST_MODE=$0-local`
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`

The canonical model loader continues to require the exact approved local snapshot and `local_files_only=True`.

## GPU blocker

CS300 is safe CPU/control-plane preparation. It does not fabricate Qwen execution. A genuine candidate still requires a compatible zero-cost NVIDIA CUDA host with CUDA-enabled PyTorch, native BF16, the authorized Diffusers/QwenImagePipeline runtime, sequential CPU offload, the exact already-local approved Qwen snapshot, and sufficient RAM/VRAM proven by real load/inference.
