# Phase 18 Change Set 294 — Canonical Postflight Seal

## Purpose

Change Set 294 repairs the CS293 CPU-CI incompatibility and makes the existing CS293 launch-to-output attestation mandatory at the successful production inference edge.

The change does not add a new approval gate. It removes two execution-quality gaps:

1. CS293's regression module depended on `pytest` even though the repository's canonical Phase 18 CPU validation uses standard-library `unittest` discovery and does not install pytest.
2. CS293 launch-to-output attestation existed as a standalone build/verify tool, but the genuine one-shot production inference CLI could finish successfully after CS290 provenance without automatically materializing and replaying that postflight join.

## Execution contract

A successful `tools/phase18_run_one_shot_canonical_inference.py` run must now complete, in order:

1. CS292 launch-manifest execution replay before model work.
2. Story-bound prompt derivation from the exact CS257 evidence and CS261 authorization.
3. Exact local Qwen snapshot load under `$0-local`, BF16, no-network execution policy.
4. One-shot canonical inference and canonical receipt replay.
5. CS290 local inference provenance build and replay.
6. CS293 `launch_to_output_attestation.json` build and replay.
7. Only then may the CLI return exit success.

If postflight attestation build or replay fails, the command fails closed. No retry or alternate candidate is introduced.

## Authority boundaries

CS294 grants no semantic, visual-quality, Human Review, Golden-quality, Genuine Golden, or publication authority. A successful postflight seal proves only that the genuine canonical candidate and its local-only provenance are joined to the exact pre-launch manifest that governed the attempt.

The following remain independent and mandatory downstream:

- factual truth and fresh-story replay;
- entity/identity verification;
- sentiment neutrality and loser-respect;
- semantic layer ownership and generated-layer QA;
- composition and exact deterministic overlays;
- strict visual-quality adjudication;
- Human Review;
- exact PUL7SAR brand and typography;
- SemanticPublicationGate;
- CS285 exact-byte Genuine Golden materialization;
- CS286 publication readiness.

## Zero-cost and network policy

No paid provider or network fallback is added. The production edge remains bound to the exact already-local approved Qwen snapshot with `$0-local`, `network_allowed=false`, and `local_files_only=true`.
