# Phase 18 Change Set 357 — Inventory-Bound Launch-to-Output Attestation

## Purpose

Close the remaining model-asset integrity gap after genuine canonical inference but before the output is accepted into downstream visual-quality processing.

CS356 made the canonical inference child itself require the CS354 exact local Qwen snapshot-byte inventory. The historical CS293 launch-to-output attestation, however, still replayed only the older launch verifier that proves approved model path/revision and settings. That created an asymmetric postflight contract: execution was byte-bound, while the postflight attestation could still validate through the weaker historical verifier.

CS357 upgrades both construction and verification of `launch_to_output_attestation.json` to replay `verify_inventory_bound_gpu_host_launch_manifest(...)`.

## Contract

The postflight chain is now:

```text
CS354 inventory-bound launch manifest
→ CS355 preload host gate
→ CS356 canonical child exact-byte execution replay
→ CS352 pre-load inventory
→ from_pretrained(local_files_only=True, BF16)
→ CS353 post-load inventory
→ one genuine inference
→ local inference provenance
→ CS357 launch-to-output attestation
   → replay exact launch-manifest bytes
   → replay current snapshot-byte inventory
   → bind canonical receipt + candidate PNG + provenance
   → preserve all downstream authorities as false
```

The attestation stores non-authoritative inventory evidence copied from the already-verified launch manifest:

- `snapshot_inventory_sha256`
- `snapshot_file_count`
- `snapshot_total_bytes`
- `model_revision`

Verification recomputes the live inventory through CS354 and requires exact equality with the recorded evidence.

## Fail-closed behavior

The attestation fails if:

- the launch manifest lacks the CS354 inventory;
- any local model/config/tokenizer byte has drifted;
- the recorded inventory digest/count/byte-size evidence is malformed;
- the recorded inventory revision differs from the approved model revision;
- the attestation inventory evidence differs from the currently replayed CS354 evidence;
- any existing story/model/settings/PNG/provenance binding drifts;
- any downstream semantic, human-review, Golden, or publication authority appears prematurely.

## Authority boundaries

CS357 does not perform or grant:

- factual/freshness approval;
- Entity/Identity approval;
- sentiment or loser-respect approval;
- semantic approval;
- visual-quality approval;
- Golden-quality approval;
- Human Visual Review approval;
- Brand/Typography/Presentation approval;
- Final Composed or Final Semantic approval;
- SemanticPublicationGate approval;
- Genuine Golden PNG materialization;
- publication readiness;
- upload or publication.

It also adds no model download, network fallback, paid fallback, retry loop, or synthetic inference result.

## Runtime requirement unchanged

A first genuine Golden Visual PNG still requires a real zero-cost compatible execution host with NVIDIA CUDA, CUDA-enabled PyTorch, native BF16, sufficient actual RAM/VRAM, the approved Qwen-Image/Diffusers runtime, and exact already-local pinned model/verifier assets. No result may be fabricated when those requirements are absent.