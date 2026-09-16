# Phase 18 Change Set 329 — Genuine Golden → Publication Readiness

## Scope

CS329 closes the deterministic handoff from an exact CS328 Genuine Golden checkpoint to the existing CS286 publication-readiness authority. It does not generate, edit, upload, publish, or otherwise mutate any image bytes.

## Preconditions

The continuation accepts only a repository-local CS328 checkpoint with the exact expected schema/state and requires:

- composed visual approval already true;
- final semantic approval already true;
- SemanticPublicationGate already executed and allowed;
- byte identity already proven;
- Genuine Golden PNG already created by CS285;
- publication readiness still false;
- non-authoritative CS328 wrapper state.

It resolves only the exact `cs285_receipt` selected by CS328, independently replays CS285, and proves exact story/source/golden bindings before invoking CS286.

## CS286 execution

The existing CS286 contract is then invoked and independently replayed. CS329 requires CS286 to preserve the same story, composed source bytes, and Genuine Golden bytes while carrying forward all prior authorities and setting only `publication_ready=true`.

CS286 has no publication side effect. CS329 records `publication_side_effect_executed=false` explicitly.

## Fail-closed guarantees

CS329 rejects:

- cross-story CS285/CS286 receipts;
- source or Genuine Golden byte drift;
- missing prior authority;
- premature or malformed CS328 state;
- CS286 responses that drop semantic-publication or Genuine Golden authority;
- output paths outside the repository or pre-existing output directories.

The continuation also forces Hugging Face/Transformers offline environment variables as a defensive zero-cost/no-network posture, although CS286 is deterministic and does not require model inference.

## Authority boundary

A successful CS329 checkpoint is a non-authoritative wrapper around the authoritative CS286 receipt. It records:

- `genuine_golden_png_created=true`;
- `publication_ready=true`;
- `publication_side_effect_executed=false`;
- `authoritative=false`.

No code in CS329 publishes content to any platform.

## Runtime blocker

This change does not solve the upstream genuine-generation blocker. A first real candidate still requires a compatible zero-cost NVIDIA CUDA/BF16 execution host, CUDA-enabled PyTorch, approved local Qwen-Image runtime/model snapshot, local verifier assets, and sufficient RAM/VRAM. Until that exists, no genuine candidate or production-composed PNG is fabricated.
