from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase18-first-genuine-golden-v6-fresh.yml"


class FirstGoldenFreshWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_runner_zero_cost_offline_and_branch_are_locked(self) -> None:
        for token in (
            "runs-on: [self-hosted, linux, x64, gpu, cuda, bf16, pul7sar-phase18]",
            "PUL7SAR_PHASE18_COST_MODE: $0-local",
            'HF_HUB_OFFLINE: "1"',
            'TRANSFORMERS_OFFLINE: "1"',
            'refs/heads/phase18/story-intelligence',
            "git diff --name-only",
            "main.py",
        ):
            self.assertIn(token, self.text)

    def test_fresh_wrapper_is_the_only_direct_canonical_execution_entrypoint(self) -> None:
        self.assertIn("python tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py", self.text)
        self.assertNotIn("python tools/phase18_run_first_genuine_golden_v6_canonical_attested.py", self.text)
        self.assertIn("--freshness-baseline", self.text)
        self.assertIn("--freshness-verification", self.text)
        self.assertIn("--attempt-contract", self.text)
        self.assertIn("--handoff", self.text)

    def test_tracked_source_integrity_wraps_the_entire_attempt(self) -> None:
        baseline = self.text.index("Capture immutable tracked source baseline before preflight")
        probe = self.text.index("Record first-Golden execution blocker probe before CUDA preflight")
        generation = self.text.index("Run freshness-bound canonical Candidate 1")
        bundle_replay = self.text.index("Replay exact Golden v6 review bundle before upload")
        source_replay = self.text.index("Replay immutable tracked source immediately before upload")
        upload = self.text.index("Upload exact Golden v6 Candidate 1 review bundle")
        self.assertIn("python tools/phase18_verify_first_golden_tracked_source_integrity.py capture", self.text)
        self.assertIn("python tools/phase18_verify_first_golden_tracked_source_integrity.py verify", self.text)
        self.assertIn("first-genuine-golden-v6-tracked-source-baseline.json", self.text)
        self.assertIn("first-genuine-golden-v6-tracked-source-verification.json", self.text)
        self.assertLess(baseline, probe)
        self.assertLess(probe, generation)
        self.assertLess(generation, bundle_replay)
        self.assertLess(bundle_replay, source_replay)
        self.assertLess(source_replay, upload)

    def test_snapshot_inventory_is_required_before_candidate_generation(self) -> None:
        probe = self.text.index("Record first-Golden execution blocker probe before CUDA preflight")
        inventory = self.text.index("Capture approved local model snapshot inventory")
        generation = self.text.index("Run freshness-bound canonical Candidate 1")
        self.assertIn("python tools/phase18_capture_approved_snapshot_inventory.py", self.text)
        self.assertIn("first-genuine-golden-v6-approved-snapshot-inventory.json", self.text)
        self.assertLess(probe, inventory)
        self.assertLess(inventory, generation)

    def test_snapshot_and_runtime_are_replayed_after_generation_before_upload(self) -> None:
        generation = self.text.index("Run freshness-bound canonical Candidate 1")
        final_binding = self.text.index("Bind execution, runner, fresh attempt, source provenance, and PNG bytes")
        snapshot_replay = self.text.index("Replay and bind approved model snapshots and runtime after generation")
        package = self.text.index("Package exact Golden v6 Candidate 1 review bundle")
        bundle_replay = self.text.index("Replay exact Golden v6 review bundle before upload")
        upload = self.text.index("Upload exact Golden v6 Candidate 1 review bundle")
        self.assertIn("python tools/phase18_verify_first_genuine_golden_v6_snapshot_bound.py", self.text)
        self.assertIn("--snapshot-inventory output/phase18_gpu_smoke/first-genuine-golden-v6-approved-snapshot-inventory.json", self.text)
        self.assertIn("--execution-probe output/phase18_gpu_smoke/first-genuine-golden-v6-execution-blocker-probe.json", self.text)
        self.assertIn("first-genuine-golden-v6-snapshot-bound-manifest.json", self.text)
        self.assertLess(generation, final_binding)
        self.assertLess(final_binding, snapshot_replay)
        self.assertLess(snapshot_replay, package)
        self.assertLess(package, bundle_replay)
        self.assertLess(bundle_replay, upload)

    def test_png_structure_evidence_is_bound_and_replayed_before_upload(self) -> None:
        structure = self.text.index("Prove complete Candidate 1 PNG structure before review packaging")
        package = self.text.index("Package exact Golden v6 Candidate 1 review bundle")
        network_bind = self.text.index("Bind zero-cost network guard evidence into exact review bundle")
        png_bind = self.text.index("Bind verified PNG structure evidence into exact review bundle")
        bundle_replay = self.text.index("Replay exact Golden v6 review bundle before upload")
        network_replay = self.text.index("Replay zero-cost network guard binding before upload")
        png_replay = self.text.index("Replay PNG structure binding before upload")
        source_replay = self.text.index("Replay immutable tracked source immediately before upload")
        upload = self.text.index("Upload exact Golden v6 Candidate 1 review bundle")
        self.assertIn("test -f tools/phase18_bind_png_structure_to_review_bundle.py", self.text)
        self.assertIn("python tools/phase18_bind_png_structure_to_review_bundle.py bind", self.text)
        self.assertIn("--structure-evidence output/phase18_gpu_smoke/first-genuine-golden-v6-png-structure.json", self.text)
        self.assertIn("python tools/phase18_bind_png_structure_to_review_bundle.py verify", self.text)
        self.assertIn("first-genuine-golden-v6-png-structure-review-binding.json", self.text)
        self.assertLess(structure, package)
        self.assertLess(package, network_bind)
        self.assertLess(network_bind, png_bind)
        self.assertLess(png_bind, bundle_replay)
        self.assertLess(bundle_replay, network_replay)
        self.assertLess(network_replay, png_replay)
        self.assertLess(png_replay, source_replay)
        self.assertLess(source_replay, upload)

    def test_canonical_png_evidence_is_verified_bound_and_replayed_before_upload(self) -> None:
        structure = self.text.index("Prove complete Candidate 1 PNG structure before review packaging")
        canonical = self.text.index("Prove canonical RGB8 Candidate 1 PNG encoding before review packaging")
        package = self.text.index("Package exact Golden v6 Candidate 1 review bundle")
        structure_bind = self.text.index("Bind verified PNG structure evidence into exact review bundle")
        canonical_bind = self.text.index("Bind canonical RGB8 PNG evidence into exact review bundle")
        bundle_replay = self.text.index("Replay exact Golden v6 review bundle before upload")
        structure_replay = self.text.index("Replay PNG structure binding before upload")
        canonical_replay = self.text.index("Replay canonical RGB8 PNG binding before upload")
        source_replay = self.text.index("Replay immutable tracked source immediately before upload")
        upload = self.text.index("Upload exact Golden v6 Candidate 1 review bundle")
        self.assertIn("test -f tools/phase18_verify_first_genuine_golden_png_canonical_encoding.py", self.text)
        self.assertIn("test -f tools/phase18_bind_png_canonical_encoding_to_review_bundle.py", self.text)
        self.assertIn("python tools/phase18_verify_first_genuine_golden_png_canonical_encoding.py", self.text)
        self.assertIn("--structure output/phase18_gpu_smoke/first-genuine-golden-v6-png-structure.json", self.text)
        self.assertIn("first-genuine-golden-v6-png-canonical-encoding.json", self.text)
        self.assertIn("python tools/phase18_bind_png_canonical_encoding_to_review_bundle.py bind", self.text)
        self.assertIn("--canonical-evidence output/phase18_gpu_smoke/first-genuine-golden-v6-png-canonical-encoding.json", self.text)
        self.assertIn("python tools/phase18_bind_png_canonical_encoding_to_review_bundle.py verify", self.text)
        self.assertIn("first-genuine-golden-v6-png-canonical-review-binding.json", self.text)
        self.assertLess(structure, canonical)
        self.assertLess(canonical, package)
        self.assertLess(structure_bind, canonical_bind)
        self.assertLess(canonical_bind, bundle_replay)
        self.assertLess(structure_replay, canonical_replay)
        self.assertLess(canonical_replay, source_replay)
        self.assertLess(source_replay, upload)

    def test_freshness_replay_precedes_source_binding_and_upload(self) -> None:
        run_fresh = self.text.index("Run freshness-bound canonical Candidate 1")
        replay = self.text.index("Replay freshness result before source binding")
        source = self.text.index("Bind and replay exact source commit provenance")
        upload = self.text.index("Upload exact Golden v6 Candidate 1 review bundle")
        self.assertLess(run_fresh, replay)
        self.assertLess(replay, source)
        self.assertLess(source, upload)

    def test_success_upload_replays_exact_review_bundle_and_failures_are_diagnostics_only(self) -> None:
        package = self.text.index("Package exact Golden v6 Candidate 1 review bundle")
        bundle_replay = self.text.index("Replay exact Golden v6 review bundle before upload")
        success_upload = self.text.index("Upload exact Golden v6 Candidate 1 review bundle")
        failure_upload = self.text.index("Upload failed-attempt diagnostics only")
        self.assertIn("python tools/phase18_package_first_genuine_golden_v6_review_bundle.py", self.text)
        self.assertIn("python tools/phase18_verify_first_genuine_golden_v6_review_bundle.py", self.text)
        self.assertIn("--bundle-dir output/phase18_golden_review/${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}", self.text)
        self.assertIn("first-genuine-golden-v6-review-bundle-replay.json", self.text)
        self.assertIn("if: success()", self.text)
        self.assertIn("if-no-files-found: error", self.text)
        self.assertIn("output/phase18_golden_review/${{ github.run_id }}-${{ github.run_attempt }}/**", self.text)
        self.assertIn("if: failure()", self.text)
        self.assertNotIn("output/phase18_generated/**", self.text)
        self.assertNotIn("output/phase18_handoffs/golden-batch/**", self.text)
        self.assertLess(package, bundle_replay)
        self.assertLess(bundle_replay, success_upload)
        self.assertLess(success_upload, failure_upload)

    def test_authorities_remain_closed_and_native_bf16_is_required(self) -> None:
        self.assertIn("torch.cuda.is_bf16_supported()", self.text)
        self.assertIn("refusing FP16/FP32 substitution", self.text)
        for field in (
            '"authoritative_gate"',
            '"network_download_authorized"',
            '"generation_authorized"',
            '"publication_ready"',
            '"seeds_2_to_4_authorized"',
        ):
            self.assertIn(field, self.text)


if __name__ == "__main__":
    unittest.main()
