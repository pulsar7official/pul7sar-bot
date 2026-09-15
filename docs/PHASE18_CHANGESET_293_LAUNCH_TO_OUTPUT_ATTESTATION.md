# Phase 18 Change Set 293 — Launch-to-Output Attestation

## Purpose

CS293 closes the remaining provenance gap between CS292 pre-launch attestation and CS290 post-inference provenance. A future successful genuine Qwen run can now produce an independent receipt proving that the exact verified launch manifest, exact local-only provenance, exact canonical inference receipt, and exact candidate PNG belong to one execution.

This change set does **not** execute inference and grants no semantic, visual-quality, human-review, Golden, or publication authority.

## Contract

The attestation replays both upstream verifiers and requires exact equality for:

- story snapshot SHA-256;
- Qwen model ID and pinned revision;
- `$0-local` cost mode;
- immutable local snapshot path/revision;
- width, height, seed, inference steps, and guidance scale;
- `network_allowed=false` and `local_files_only=true`;
- successful genuine canonical inference;
- all downstream authorities still false.

It byte-binds the launch manifest, CS290 provenance, canonical inference receipt, and canonical candidate PNG. Verification reopens all four files and reruns the upstream verifiers before accepting the receipt.

## Safety properties preserved

Fact Lock, entity/identity verification, sentiment neutrality and loser-respect, zero-cost execution, visual-quality adjudication, Human Review, exact brand/typography, SemanticPublicationGate, Genuine Golden materialization, and publication readiness remain separate downstream authorities.

## Runtime status

No production GPU inference is claimed by CS293. The current execution environment still lacks a compatible NVIDIA CUDA runtime, so a genuine Qwen candidate and Genuine Golden PNG remain blocked until a compatible zero-cost host is available.
