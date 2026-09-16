# Phase 18 Implementation Log — CS505

## Scope
Branch: `phase18/story-intelligence` only. `main` was not modified.

## State reviewed
CS504 HEAD was `260388d8a5899bd939e42227ba58c512beba8341`. Its Story Intelligence Verification and CPU Diagnostics runs completed successfully. CS504 provides a fail-closed orchestrator that captures and binds the four authoritative pre-generation evidence files. The canonical-fresh launcher already enforces immutable binder proof, semantic/cryptographic evidence binding, freshness baseline, canonical Candidate 1 attempt, and post-attempt freshness replay.

## Gap closed
The two safe components still required an explicit composition point. CS505 adds a single authoritative entrypoint that first performs CS504 evidence capture/binding and only then delegates to the CS500 canonical-fresh launcher. This materially reduces the remaining workflow change to selecting one tested entrypoint rather than reproducing security-sensitive orchestration in YAML.

## Added
- `tools/phase18_run_first_genuine_golden_v6_authoritative_entrypoint.py`
- `tests/test_phase18_authoritative_entrypoint.py`
- this implementation log

## Modified
None.

## Deleted
None.

## Gate preservation
The entrypoint fails closed on malformed immutable source SHA, non-`$0-local` mode, or either offline-model flag not being `1`. A non-ready evidence capture prevents the fresh canonical launcher from being called. It does not grant authoritative, download, generation, publication, or Seeds 2-4 authority. Existing factual/source-consensus, identity/entity, sentiment/loser-respect, semantic-publication, CUDA/native-BF16, exact-model snapshot, PNG integrity, Human Visual Review, and Golden-quality gates remain delegated to the already-locked lower layers and are not bypassed or reimplemented here.

## Tests added
Stdlib `unittest` regression coverage verifies:
1. evidence capture happens before the fresh canonical launcher;
2. exact four evidence filenames are passed into the fresh launcher;
3. capture failure prevents Candidate-1 path delegation;
4. offline-contract failure occurs before evidence capture;
5. malformed SHA failure occurs before evidence capture;
6. authority fields remain closed in the composition result.

## Remaining
The live authoritative GitHub Actions workflow still needs to invoke this new single entrypoint instead of the older direct canonical-attested launcher. That workflow edit must preserve every existing pre/post gate and should be made only from a complete, non-truncated workflow source. After CPU CI proves CS505, genuine PNG execution remains blocked until a compatible self-hosted NVIDIA runner is available with CUDA-enabled PyTorch, native BF16, sufficient GPU/RAM/cache/filesystem resources, and the exact approved Qwen2.5-VL and FLUX.2 snapshots already present locally under the `$0-local` offline-only contract. No PNG was fabricated.
