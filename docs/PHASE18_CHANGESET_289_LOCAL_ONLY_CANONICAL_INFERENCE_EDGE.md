# Phase 18 Change Set 289 — Local-Only Canonical Inference Edge

## Purpose

CS289 hardens the already-existing story-bound one-shot Qwen Image inference path. The canonical inference CLI previously loaded `Qwen/Qwen-Image-2512` by mutable repository identifier plus revision, which could still permit a Hugging Face cache miss to use network access. That no longer matches the stricter local-only execution contract established by CS287/CS288.

CS289 therefore makes the actual inference edge consume the exact already-local approved `snapshots/<revision>` directory and forbids download fallback.

## Invariants preserved

- branch work remains limited to `phase18/story-intelligence`.
- Fact Lock and story replay remain upstream requirements through CS257/CS261.
- no free-form prompt is accepted by the production inference CLI.
- entity/identity and sentiment constraints remain bound through the canonical prompt/authorization chain.
- required cost mode remains `$0-local`.
- approved model remains `Qwen/Qwen-Image-2512` at revision `2ce1c28560fbc62c9f5531e076b237d3575330a9`.
- native BF16 and sequential CPU offload remain mandatory.
- one authorization still permits exactly one canonical inference attempt; there is no retry loop.
- successful inference produces only a canonical candidate. Semantic QA, visual-quality, Human Review, Brand/Typography, SemanticPublication, Golden materialization, and publication readiness remain downstream and independent.

## Runtime hardening

`engine/intelligence/qwen_image_local_inference_runtime.py`:

1. requires `$0-local` before any preflight/import/model load;
2. re-runs CS287 static preflight against the supplied local snapshot;
3. requires the snapshot path to resolve to the exact approved full revision;
4. loads `QwenImagePipeline.from_pretrained(local_snapshot, torch_dtype=torch.bfloat16, local_files_only=True)`;
5. enables sequential CPU offload;
6. reconstructs the live runtime identity and compares it to the CS260 evidence used by the CS261 authorization chain;
7. returns the loaded runtime to the existing one-shot executor but performs no inference itself.

## CLI change

`tools/phase18_run_one_shot_canonical_inference.py` now requires:

`--snapshot-path <already-local snapshots/2ce1c28560fbc62c9f5531e076b237d3575330a9>`

The former model-id/revision load at the inference edge was removed. The command cannot silently download weights when the approved snapshot is absent.

## Authority limits

CS289 does not change the authority of `qwen_image_one_shot_canonical_inference` or any downstream gate. A produced PNG remains only a canonical candidate and cannot become a Genuine Golden PNG until the existing semantic, visual-quality, human, brand/typography, semantic-publication, CS285 materialization, and CS286 readiness chain succeeds.

## Testing

Regression coverage proves:

- a non-`$0-local` cost mode fails before preflight;
- a failed static preflight prevents imports/model loading;
- a successful load uses the exact supplied snapshot path, BF16, `local_files_only=True`, and sequential CPU offload;
- runtime-identity drift still fails closed.

No test fixture is represented as a production Qwen inference or Golden Visual.
