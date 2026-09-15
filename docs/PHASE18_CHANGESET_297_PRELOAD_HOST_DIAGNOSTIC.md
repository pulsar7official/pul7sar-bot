# Phase 18 Change Set 297 — Pre-Model-Load Host Diagnostic

## Purpose

CS297 adds an aggregate, fail-closed diagnostic for the exact GPU host that will be used by the existing CS296 pre-model-load identity gate. CS296 intentionally stops at the first mismatch. CS297 reports all currently observable blockers in one pass so a zero-cost host can be corrected before Qwen weights are loaded.

## Boundaries

The diagnostic first replays the existing GPU Host Launch Manifest, resolves the same story authorization and CS260 live-pipeline receipt, reuses CS287 static readiness, and compares the observable pre-load runtime identity against the CS260-authorized identity. It does not load model weights, call the pipeline, create pixels, consume a generation authorization, or change downstream authority.

The report always leaves model-load, inference, semantic approval, human visual review, Golden quality, Genuine Golden PNG creation, and publication readiness false. No VRAM minimum or new inference threshold is introduced.

## Operator entry point

`tools/phase18_qwen_image_preload_host_diagnostic.py --launch-manifest <path> --require-ready`

Exit code 2 means the host has one or more blockers. A zero exit with `--require-ready` means only that the host is eligible to proceed to the real model-load attempt; it is not proof that model loading or inference will succeed.

## Preserved gates

Fact/freshness, entity/identity, sentiment neutrality and loser respect, zero-cost/local-only execution, story-bound semantic ownership, generated-layer QA, composition, visual quality, Human Review, Exact Brand/Typography, SemanticPublicationGate, Genuine Golden materialization, and publication readiness remain independent and unchanged.
