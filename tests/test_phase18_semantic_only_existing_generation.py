import unittest
from pathlib import Path


class Phase18SemanticOnlyExistingGenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("tools/phase18_colab_one_command.py").read_text(encoding="utf-8")

    def test_cli_exposes_explicit_semantic_only_existing_mode(self):
        self.assertIn('"--semantic-only-existing"', self.source)
        self.assertIn("SEMANTIC_ONLY_CANNOT_FORCE_GENERATION", self.source)
        self.assertIn("SEMANTIC_ONLY_CANNOT_PREPARE_GENERATION", self.source)
        self.assertIn("SEMANTIC_ONLY_REQUIRES_QWEN", self.source)

    def test_semantic_only_mode_requires_durable_generation_provenance(self):
        self.assertIn("def _require_existing_generation_for_semantic", self.source)
        self.assertIn("GenerationProvenanceLock().verify", self.source)
        self.assertIn("SEMANTIC_ONLY_GENERATION_PROVENANCE_NOT_VERIFIED", self.source)
        self.assertIn("SEMANTIC_ONLY_PROVENANCE_PNG_MISMATCH", self.source)
        self.assertIn("SEMANTIC_ONLY_CANDIDATE_MISMATCH", self.source)

    def test_semantic_only_branch_never_enters_generation_runner(self):
        semantic_branch = self.source.index("if args.semantic_only_existing:\n        print(\"4/9 Reusing provenance-verified saved Candidate")
        runner_branch = self.source.index("else:\n        print(\"4/9 Entering story-first Golden editorial runner")
        runner_call = self.source.index('str(ROOT / "tools" / "phase18_colab_runner.py")', runner_branch)
        review_stage = self.source.index('print("5/9 Confirming PREVIEW stayed context-only')
        self.assertLess(semantic_branch, runner_branch)
        self.assertLess(runner_branch, runner_call)
        self.assertLess(runner_call, review_stage)
        semantic_block = self.source[semantic_branch:runner_branch]
        self.assertNotIn("phase18_colab_runner.py", semantic_block)
        self.assertIn("_require_existing_generation_for_semantic(args.candidate)", semantic_block)

    def test_publication_authority_remains_closed(self):
        self.assertIn("SEMANTIC_ONLY_REQUIRES_UNPUBLISHED_GENERATION", self.source)
        self.assertIn("SEMANTIC_ONLY_PROVENANCE_CANNOT_AUTHORIZE_PUBLICATION", self.source)
        self.assertIn('"publication_ready": False', self.source)


if __name__ == "__main__":
    unittest.main()
