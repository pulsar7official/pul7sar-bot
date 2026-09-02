# Phase 18 Implementation Log 318 — Qwen Identity-Aware Workflow Continuation

## Scope and branch isolation

- Repository: `pulsar7official/pul7sar-bot`
- Working branch: `phase18/story-intelligence` only.
- Starting HEAD reviewed before writes: `7ebc51fcbebeb3c47b658019b7b720ef53d9c6a8` (CS317).
- CS317 Story Intelligence verification run `33627354897` / #4626 was confirmed `completed/success` before CS318 writes.
- `main` was reviewed read-only and was at `89b69e0972047af615162518dcc32dc1a16cd2dd` at the latest check.
- No write, merge, rebase, reset, force-update, or ref mutation was performed on `main`.

## Review finding

CS317 correctly introduced a deterministic identity-aware router, but the canonical Qwen GPU workflow still stopped after CS304 Semantic Base QA and CS305 Identity Requirement Classification. The router therefore existed only as a separate operator-invoked control-plane command.

That left a material execution gap after a rare genuine GPU inference: an operator still had to locate the exact CS304 and CS305 receipts from the same run and invoke CS317 manually. The repository already contains the safe downstream semantics, so the correct change is workflow orchestration rather than a new approval gate.

## Modified

### `.github/workflows/phase18-qwen-image-canonical-inference.yml`

The canonical Qwen workflow now:

1. proves that `tools/phase18_route_semantic_checkpoint_after_identity_requirement.py` exists on the immutable branch-bound checkout;
2. reads the exact `cs304_receipt` and `cs305_receipt` emitted by the same run's `semantic-checkpoint-result.json`;
3. rejects missing or empty lineage paths before routing;
4. invokes CS317 exactly once into a run-ID-bound output directory;
5. captures the router exit code without losing its receipt;
6. validates the mutually exclusive route state:
   - when human pixel-identity review is required, the route must stop at CS266, create the review request, and prove CS268 did not execute;
   - when review is not required, the route must execute CS268 and the candidate must pass Generated-Layer QA;
7. requires `identity_approved`, `semantic_approved`, `human_visual_review_approved`, `golden_quality_approved`, `genuine_golden_png_created`, and `publication_ready` to remain false;
8. requires a successful router exit only after all route-state assertions pass.

No CS267 manual identity evidence is generated or inferred by the workflow.

### `tests/test_phase18_qwen_image_canonical_inference_workflow.py`

Regression coverage now locks:

- exact CS304/CS305 continuation into CS317;
- one invocation of the identity-aware router;
- CS266 stop behavior when human identity review is required;
- prohibition on CS268 execution before required manual identity evidence;
- mandatory CS268 execution and approval when human review is not required;
- continued closure of identity, semantic-final, Human Review, Golden, materialization, and publication authorities.

## Added

### `docs/PHASE18_CHANGESET_318_QWEN_IDENTITY_AWARE_WORKFLOW_CONTINUATION.md`

Defines CS318's orchestration contract and authority boundaries.

### `docs/PHASE18_IMPLEMENTATION_LOG_318.md`

This implementation record.

## Deleted

None.

## Commits

- `688e8d8fc038b4942b0f759098fc82e76b92903d` — canonical Qwen workflow continuation through CS317.
- `e285e7006f036b1adb712ced252dc327277124b3` — workflow regressions for identity-aware routing.
- `bc8535e908d1bc000d0536061fc77d98ec2fe154` — CS318 contract documentation.
- The commit containing this file records the implementation log.

## Gate preservation

CS318 does not alter thresholds, evidence semantics, or approval ownership for:

- Fact/Freshness locks;
- Entity/Identity evidence;
- source-backed manual identity review;
- sentiment neutrality and loser-respect;
- `$0-local` generation;
- Hugging Face / Transformers offline requirements;
- Semantic Base QA;
- Generated-Layer QA;
- Composition QA;
- Golden Visual Quality;
- Human Visual Review;
- Exact Brand/Typography;
- Final Composed Approval;
- Final Semantic Approval;
- `SemanticPublicationGate`;
- Genuine Golden materialization;
- final publication readiness.

The human-review route deliberately terminates at CS266. CS267 still requires independent manual source comparison. The no-review route may reach CS268 only because CS305 explicitly classified human pixel-identity review as unnecessary.

## Test status

CS317 baseline was confirmed terminal-green before writes. GitHub Actions are expected to run automatically on CS318 commits. Terminal success is not claimed in this log until a workflow run on the final CS318 HEAD reports `completed/success`.

## Genuine Golden PNG status and exact execution blocker

No genuine Qwen candidate PNG, production-composed PNG, or Genuine Golden Visual PNG is claimed by CS318. This change set is control-plane orchestration only.

The currently available execution runtime was probed during this change set and reported:

- PyTorch: `2.10.0+cpu`
- CUDA available: `false`
- `torch.version.cuda`: `null`
- CUDA device count: `0`
- native BF16 support: `false`
- `nvidia-smi`: unavailable

Therefore the canonical Qwen inference cannot be executed here.

A real candidate still requires a proven zero-cost host that simultaneously provides NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, a compatible approved QwenImagePipeline/Diffusers runtime, the exact already-local pinned `Qwen/Qwen-Image-2512` snapshot, pinned local semantic-verifier assets, sequential CPU offload support, and sufficient live RAM/VRAM demonstrated by an actual model load and inference.

No image, identity verdict, Golden score, or publication result is fabricated.

## Remaining path after CS318

`genuine Qwen inference`
→ CS301 sealed candidate handoff
→ CS303 exact-byte admission
→ CS304 Semantic Base QA
→ CS305 Identity Requirement
→ **CS318 invokes CS317 automatically**

If human identity review is required:
`→ CS266 request → stop → independent manual source comparison → CS267 evidence admission → CS268 Generated-Layer QA`

If human identity review is not required:
`→ CS268 Generated-Layer QA in the same workflow`

Then:
`→ Composition/Post-composition → Golden Quality → Human Visual Review → Exact Brand/Typography → Final Composed Approval → Final Semantic Approval → SemanticPublicationGate → CS285 Genuine Golden materialization → CS286 publication readiness`.
