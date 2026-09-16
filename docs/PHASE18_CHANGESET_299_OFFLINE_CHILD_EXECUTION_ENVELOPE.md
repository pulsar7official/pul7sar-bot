# Phase 18 Change Set 299 — Offline Child Execution Envelope

## Purpose

CS299 closes a remaining zero-cost/local-only execution gap at the manifest-bound GPU launcher edge.

Before CS299, CS295/CS298 already required:

- a verified launch manifest;
- `$0-local` cost mode;
- the CS297 aggregate preload diagnostic;
- exact CS260 host identity replay before model load;
- an immutable local Qwen snapshot;
- `local_files_only=True` inside the canonical model loader;
- the existing CS290 provenance and CS293/294 launch-to-output postflight chain.

However, the canonical subprocess still inherited the parent process network-related library environment unchanged. That did not create a known network call in the canonical path, but it left an avoidable defense-in-depth gap between the launcher and the local-only loader contract.

## Change

The manifest-bound execution module now constructs an explicit child environment before starting the canonical inference subprocess.

The child environment requires:

- `PUL7SAR_PHASE18_COST_MODE=$0-local`
- `HF_HUB_OFFLINE=1`
- `TRANSFORMERS_OFFLINE=1`

Inherited values for the two offline flags are overwritten to `1`.

The executor passes this environment explicitly to `subprocess.run(...)` while preserving the existing shell-free argv execution.

## Security and authority boundary

This change is deliberately narrow.

It is a **library-level offline envelope**, not an operating-system network sandbox. It does not claim that arbitrary code on the host cannot access the network. The stronger production guarantees remain layered:

1. exact immutable local snapshot;
2. `local_files_only=True` in the Qwen loader;
3. `$0-local` cost mode;
4. manifest-bound settings and authorization;
5. pre-model-load host readiness/identity enforcement;
6. post-inference provenance and launch-to-output attestation.

CS299 does not load Qwen, execute inference, create pixels, approve semantics, approve identity, approve sentiment, approve visual quality, create a Golden PNG, or grant publication authority.

## Preserved gates

No thresholds or approvals were weakened or bypassed. The following remain independent and fail-closed:

- factual/freshness lock;
- entity and identity verification;
- sentiment neutrality and loser-respect rules;
- story-bound semantic ownership;
- zero-cost/local-only execution requirements;
- generated-layer and composition quality checks;
- human visual review;
- exact brand/typography requirements;
- `SemanticPublicationGate`;
- CS285 Genuine Golden PNG materialization;
- CS286 publication readiness.

## Regression coverage

CS299 adds tests proving that:

- `$0-local` is mandatory when building the child environment;
- `HF_HUB_OFFLINE` is forced to `1` even if inherited as `0`;
- `TRANSFORMERS_OFFLINE` is forced to `1` even if inherited as `0`;
- unrelated environment values are preserved;
- the successful executor passes the explicit offline environment to the child process;
- the executor remains shell-free and preserves the canonical subprocess exit code;
- the CS298 preload gate still prevents subprocess launch when blockers remain.

These are CPU/control-plane regressions only. They are not evidence of a genuine CUDA model load, Qwen inference, canonical candidate PNG, or Genuine Golden Visual.

## Remaining blocker

A genuine Golden Visual still requires a compatible zero-cost execution host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, the compatible QwenImagePipeline/Diffusers stack, the exact approved local Qwen snapshot, the previously authorized runtime identity, and sufficient RAM/VRAM demonstrated by a real model load and inference.
