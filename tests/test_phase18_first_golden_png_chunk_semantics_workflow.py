from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/phase18-first-genuine-golden-v6-fresh.yml"


class FirstGoldenChunkSemanticsWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = WORKFLOW.read_text(encoding="utf-8")

    def test_chunk_semantics_is_immutable_source_checked(self) -> None:
        self.assertIn(
            "test -f tools/phase18_verify_first_genuine_golden_png_chunk_semantics.py",
            self.text,
        )
        self.assertIn(
            "test -f tools/phase18_bind_png_chunk_semantics_to_review_bundle.py",
            self.text,
        )

    def test_chunk_semantics_verification_is_between_structure_and_canonical(self) -> None:
        structure = self.text.index("Prove complete Candidate 1 PNG structure before review packaging")
        semantics = self.text.index("Prove Candidate 1 PNG chunk semantics before review packaging")
        canonical = self.text.index("Prove canonical RGB8 Candidate 1 PNG encoding before review packaging")
        package = self.text.index("Package exact Golden v6 Candidate 1 review bundle")
        self.assertIn(
            "python tools/phase18_verify_first_genuine_golden_png_chunk_semantics.py",
            self.text,
        )
        self.assertIn(
            "--structure output/phase18_gpu_smoke/first-genuine-golden-v6-png-structure.json",
            self.text,
        )
        self.assertIn(
            "--output output/phase18_gpu_smoke/first-genuine-golden-v6-png-chunk-semantics.json",
            self.text,
        )
        self.assertLess(structure, semantics)
        self.assertLess(semantics, canonical)
        self.assertLess(canonical, package)

    def test_chunk_semantics_evidence_is_bound_between_structure_and_canonical(self) -> None:
        structure_bind = self.text.index("Bind verified PNG structure evidence into exact review bundle")
        semantics_bind = self.text.index("Bind verified PNG chunk-semantics evidence into exact review bundle")
        canonical_bind = self.text.index("Bind canonical RGB8 PNG evidence into exact review bundle")
        bundle_replay = self.text.index("Replay exact Golden v6 review bundle before upload")
        self.assertIn(
            "python tools/phase18_bind_png_chunk_semantics_to_review_bundle.py bind",
            self.text,
        )
        self.assertIn(
            "--semantic-evidence output/phase18_gpu_smoke/first-genuine-golden-v6-png-chunk-semantics.json",
            self.text,
        )
        self.assertLess(structure_bind, semantics_bind)
        self.assertLess(semantics_bind, canonical_bind)
        self.assertLess(canonical_bind, bundle_replay)

    def test_chunk_semantics_binding_is_replayed_before_canonical_and_source_upload_gate(self) -> None:
        structure_replay = self.text.index("Replay PNG structure binding before upload")
        semantics_replay = self.text.index("Replay PNG chunk-semantics binding before upload")
        canonical_replay = self.text.index("Replay canonical RGB8 PNG binding before upload")
        source_replay = self.text.index("Replay immutable tracked source immediately before upload")
        upload = self.text.index("Upload exact Golden v6 Candidate 1 review bundle")
        self.assertIn(
            "python tools/phase18_bind_png_chunk_semantics_to_review_bundle.py verify",
            self.text,
        )
        self.assertIn(
            "--output output/phase18_gpu_smoke/first-genuine-golden-v6-png-chunk-semantics-review-binding.json",
            self.text,
        )
        self.assertLess(structure_replay, semantics_replay)
        self.assertLess(semantics_replay, canonical_replay)
        self.assertLess(canonical_replay, source_replay)
        self.assertLess(source_replay, upload)

    def test_success_and_failure_artifact_boundaries_remain_closed(self) -> None:
        self.assertIn("if: success()", self.text)
        self.assertIn("if: failure()", self.text)
        self.assertIn(
            "path: output/phase18_golden_review/${{ github.run_id }}-${{ github.run_attempt }}/**",
            self.text,
        )
        self.assertIn("path: output/phase18_gpu_smoke/**", self.text)
        self.assertNotIn("output/phase18_generated/**", self.text)
        self.assertNotIn("output/phase18_handoffs/golden-batch/**", self.text)


if __name__ == "__main__":
    unittest.main()
