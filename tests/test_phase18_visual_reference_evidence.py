import unittest

from engine.intelligence.visual_reference_evidence import CHELSEA_REFERENCE_7_OF_10


class VisualReferenceEvidenceTests(unittest.TestCase):
    def test_reference_sha_and_score_are_locked(self):
        ref = CHELSEA_REFERENCE_7_OF_10
        self.assertEqual(ref.sha256, "ab5f2e7b58d29153427837b08080c39a2912952ca251ef0c3cb29f437c489e60")
        self.assertEqual(ref.score_out_of_10, 7.0)

    def test_reference_preserves_identity_and_contextual_visual_strengths(self):
        ref = CHELSEA_REFERENCE_7_OF_10
        self.assertIn("fixed metallic PUL7SAR wordmark body", ref.preserve)
        self.assertIn("enlarged dynamic number 7", ref.preserve)
        self.assertIn("small football signature near R", ref.preserve)
        self.assertIn("verified club-linked accent color", ref.preserve)
        self.assertIn("subtle tactical drawing as contextual texture when relevant", ref.preserve)

    def test_reference_does_not_become_universal_template(self):
        ref = CHELSEA_REFERENCE_7_OF_10
        self.assertIn("using this composition as a fixed template for all news", ref.improve_or_avoid)
        self.assertIn("forcing stadium or pitch motifs into unrelated stories", ref.improve_or_avoid)
        self.assertIn("headline copy that is too long or visually crowded", ref.improve_or_avoid)


if __name__ == "__main__":
    unittest.main()
