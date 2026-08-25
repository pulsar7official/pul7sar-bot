import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.hybrid_family_compositor import HybridEditorialFacts, HybridFamilyCompositor
from engine.intelligence.sports_editorial_scene import EditorialSceneFamily


class HybridFamilyCompositorTests(unittest.TestCase):
    def _base(self, root: Path) -> Path:
        p = root / "base.png"
        Image.new("RGB", (512, 640), (26, 34, 47)).save(p)
        return p

    def _assert_receipt(self, receipt, target: Path, family):
        self.assertTrue(target.is_file())
        self.assertEqual(Image.open(target).size, (1080, 1350))
        self.assertEqual(receipt.family, family.value)
        self.assertTrue(receipt.exact_brand_used)
        self.assertTrue(receipt.deterministic_facts_used)
        self.assertFalse(receipt.fabricated_crest_used)
        self.assertFalse(receipt.placeholder_used)
        self.assertFalse(receipt.generated_text_used)
        self.assertFalse(receipt.source_photo_used)
        self.assertFalse(receipt.publication_ready)

    def test_all_generative_families_compose_without_placeholders(self):
        cases = [
            HybridEditorialFacts(EditorialSceneFamily.RESULT_STATEMENT, "MATCH RESULT", home_name="NORTH CITY", away_name="SOUTH UNITED", home_score=3, away_score=1),
            HybridEditorialFacts(EditorialSceneFamily.TRANSFER_SIGNATURE, "NEW DESTINATION", primary="NORTH CITY", secondary="TRANSFER UPDATE"),
            HybridEditorialFacts(EditorialSceneFamily.VERIFIED_SUBJECT_NEWS, "TEAM UPDATE", primary="VERIFIED SUBJECT LAYER RESERVED"),
            HybridEditorialFacts(EditorialSceneFamily.DATA_MONUMENT, "SEASON RECORD", primary="27", secondary="MATCHES UNBEATEN", tertiary="EXACT DATA LAYER"),
            HybridEditorialFacts(EditorialSceneFamily.EVENT_EDITORIAL, "MATCHDAY", primary="NORTH CITY vs SOUTH UNITED", secondary="28 AUG · 20:00"),
        ]
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            base = self._base(root)
            for index, facts in enumerate(cases):
                target = root / f"{index}.png"
                receipt = HybridFamilyCompositor().compose(base_path=str(base), output_path=str(target), facts=facts)
                self._assert_receipt(receipt, target, facts.family)

    def test_result_requires_exact_scores_and_names(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(ValueError):
                HybridFamilyCompositor().compose(
                    base_path=str(self._base(root)),
                    output_path=str(root / "bad.png"),
                    facts=HybridEditorialFacts(EditorialSceneFamily.RESULT_STATEMENT, "RESULT"),
                )

    def test_data_requires_exact_value(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(ValueError):
                HybridFamilyCompositor().compose(
                    base_path=str(self._base(root)),
                    output_path=str(root / "bad.png"),
                    facts=HybridEditorialFacts(EditorialSceneFamily.DATA_MONUMENT, "DATA"),
                )

    def test_tactical_is_not_routed_through_generated_family_compositor(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(ValueError):
                HybridFamilyCompositor().compose(
                    base_path=str(self._base(root)),
                    output_path=str(root / "bad.png"),
                    facts=HybridEditorialFacts(EditorialSceneFamily.TACTICAL_BOARD, "TACTICS"),
                )


if __name__ == "__main__":
    unittest.main()
