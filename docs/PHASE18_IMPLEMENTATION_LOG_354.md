# Phase 18 Implementation Log — CS354

## Scope

Repository: `pulsar7official/pul7sar-bot`

Branch: `phase18/story-intelligence` only.

Starting branch HEAD reviewed before changes: `24d9d076b2ff83ced2ae60ee1c2942aaa3638c1d`.

`main` was reviewed separately at `219ba9aa51d206cb2407e7d9b649023e5c02f44d` and was not modified, merged, rebased, reset, force-updated, or otherwise written by this change set.

## Gap identified

The existing CS291/292 GPU-host launch manifest bound the approved model id/revision and resolved snapshot path, while CS352/353 protected exact snapshot bytes immediately around `from_pretrained`. The manifest itself did not bind the deterministic snapshot byte inventory, leaving an authorization-to-execution interval where a different local snapshot content set could occupy the same approved revision path before later runtime checks.

## Added

- `engine/intelligence/qwen_image_inventory_bound_launch_manifest.py`
  - composes the existing CS291/292 builder/verifier;
  - computes the deterministic CS352 snapshot inventory;
  - seals that inventory into the final manifest digest;
  - replays the original manifest verifier and the live inventory;
  - removes the private unbound temporary manifest after construction;
  - grants no downstream authority.
- `tests/test_phase18_qwen_image_inventory_bound_launch_manifest.py`
  - verifies inventory sealing;
  - verifies private temporary cleanup;
  - verifies byte drift rejection;
  - verifies rejection of a manifest lacking inventory;
  - verifies all downstream authorities stay false.
- `docs/PHASE18_CHANGESET_354_INVENTORY_BOUND_GPU_HOST_LAUNCH_MANIFEST.md`.
- `docs/PHASE18_IMPLEMENTATION_LOG_354.md`.

## Modified

- `tools/phase18_qwen_image_gpu_host_launch_manifest.py`
  - build and verify commands now use the inventory-bound manifest contract.
- `engine/intelligence/qwen_image_manifest_bound_execution.py`
  - the launcher now replays the inventory-bound verifier before deriving the canonical subprocess argv;
  - the historical verifier symbol remains as a test seam alias so existing regression mocks keep exercising the launcher logic without semantic change.

## Deleted

None.

## Commit sequence

- `2ba7571aac234c686e6ec8c8c1649e070aaab18b` — add inventory-bound launch manifest.
- `f5ae1f9e701867f36d82f8d279cfe2190cebf6ad` — route manifest CLI through byte binding.
- `f47126eeae4edda277941bd8178ae535bd95e295` — enforce snapshot bytes before subprocess.
- `e5b4b9f13372c4892e20a4be0ac411bfe600c7af` — preserve launcher regression test seam while using the byte verifier.
- `4405a5eabbb4cf5e30132469225e692f6acec0a6` — add inventory-bound manifest regressions.
- `770a4b6cbaf7ad8ef1f04501b4425230889bbaea` — document CS354 contract.

## Gate preservation

CS354 does not download models, allow network fallback, load Qwen, execute inference, create pixels, or grant factual/freshness, identity, sentiment/loser-respect, semantic, visual-quality, Golden-quality, human-review, brand, typography, Final Composed, Final Semantic, SemanticPublicationGate, Genuine Golden, publication-readiness, authoritative-publication, upload, or external-publication authority.

The production ordering is now:

`manifest build -> exact snapshot inventory sealed -> manifest/inventory replay -> preload host gate -> canonical subprocess -> CS352 pre-load inventory -> from_pretrained(local_files_only=True, BF16) -> CS353 post-load inventory -> inference`.

## Tests / CI

Code-and-test-bearing SHA: `4405a5eabbb4cf5e30132469225e692f6acec0a6`.

Terminal CI was subsequently observed: `Phase 18 Story Intelligence Verification` run `34017688235` (#5018) completed with conclusion `success`. The companion Phase 18 workflows visible for the same SHA also completed successfully.

## Runtime blocker

No Genuine Golden PNG is claimed by CS354. Genuine Qwen inference remains blocked in the currently available execution environment unless a zero-cost host provides all of the following simultaneously:

- NVIDIA CUDA GPU;
- CUDA-enabled PyTorch;
- native CUDA BF16 support;
- sufficient real host RAM and GPU VRAM proven by model load/inference, not guessed;
- approved Qwen-Image/Diffusers runtime;
- exact approved already-local pinned Qwen model snapshot and verifier assets;
- no paid or network fallback.

When that host exists, CS354 materially narrows the remaining gap by ensuring the launch authorization is already bound to the exact model/config/tokenizer bytes that CS352/353 will recheck at model load.
