import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from engine.intelligence.models import IdentityPlan, IdentityStatus
from engine.intelligence.verified_subject_compositor import (
    SubjectPlacement,
    VerifiedSubjectAsset,
    VerifiedSubjectCompositor,
    VerifiedSubjectMode,
)


class VerifiedSubjectCompositorTests(unittest.TestCase):
    def identity(self, *, name="Verified Player", status=IdentityStatus.VERIFIED, confidence=0.97, allowed=True):
        return IdentityPlan(
            entity_name=name,
            status=status,
            sport="football",
            role="player",
            confidence=confidence,
            depiction_allowed=allowed,
            reason="test evidence",
            metadata={"evidence_source": "trusted-test-source"},
        )

    @staticmethod
    def cutout(path: Path):
        image = Image.new("RGBA", (220, 420), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((70, 20, 150, 100), fill=(190, 150, 120, 255))
        draw.polygon([(45, 115), (175, 115), (205, 395), (15, 395)], fill=(20, 50, 90, 255))
        image.save(path)

    def test_verified_cutout_composes_exact_subject_and_receipts_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.png"
            subject_path = root / "subject.png"
            out = root / "out.png"
            Image.new("RGB", (1080, 1350), (5, 10, 18)).save(base)
            self.cutout(subject_path)
            digest = hashlib.sha256(subject_path.read_bytes()).hexdigest()
            asset = VerifiedSubjectAsset(
                "verified-player-visual", "Verified Player", str(subject_path), digest,
                "trusted:test:asset", VerifiedSubjectMode.TRANSPARENT_CUTOUT,
            )
            receipt = VerifiedSubjectCompositor().compose(
                base_path=str(base), output_path=str(out), subject=asset,
                identity=self.identity(), placement=SubjectPlacement(270, 260, 540, 760),
                accent_hex="#034694",
            )
            self.assertTrue(out.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(receipt.subject_sha256, digest)
            self.assertEqual(receipt.entity_name, "Verified Player")
            self.assertTrue(receipt.identity_verified)
            self.assertFalse(receipt.generator_used)
            self.assertFalse(receipt.subject_placeholder_used)
            self.assertFalse(receipt.publication_ready)

    def test_checksum_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.png"
            subject_path = root / "subject.png"
            Image.new("RGB", (300, 400)).save(base)
            self.cutout(subject_path)
            asset = VerifiedSubjectAsset(
                "verified-player-visual", "Verified Player", str(subject_path), "0" * 64,
                "trusted:test:asset", VerifiedSubjectMode.TRANSPARENT_CUTOUT,
            )
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                VerifiedSubjectCompositor().compose(
                    base_path=str(base), output_path=str(root / "out.png"), subject=asset,
                    identity=self.identity(), placement=SubjectPlacement(10, 10, 200, 300),
                )

    def test_unverified_or_low_confidence_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.png"
            subject_path = root / "subject.png"
            Image.new("RGB", (300, 400)).save(base)
            self.cutout(subject_path)
            digest = hashlib.sha256(subject_path.read_bytes()).hexdigest()
            asset = VerifiedSubjectAsset(
                "verified-player-visual", "Verified Player", str(subject_path), digest,
                "trusted:test:asset", VerifiedSubjectMode.TRANSPARENT_CUTOUT,
            )
            compositor = VerifiedSubjectCompositor()
            with self.assertRaisesRegex(ValueError, "VERIFIED"):
                compositor.compose(
                    base_path=str(base), output_path=str(root / "bad1.png"), subject=asset,
                    identity=self.identity(status=IdentityStatus.PARTIAL, confidence=0.85, allowed=False),
                    placement=SubjectPlacement(10, 10, 200, 300),
                )
            with self.assertRaisesRegex(ValueError, "below composition threshold"):
                compositor.compose(
                    base_path=str(base), output_path=str(root / "bad2.png"), subject=asset,
                    identity=self.identity(confidence=0.89), placement=SubjectPlacement(10, 10, 200, 300),
                )

    def test_entity_name_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.png"
            subject_path = root / "subject.png"
            Image.new("RGB", (300, 400)).save(base)
            self.cutout(subject_path)
            digest = hashlib.sha256(subject_path.read_bytes()).hexdigest()
            asset = VerifiedSubjectAsset(
                "verified-player-visual", "Verified Player", str(subject_path), digest,
                "trusted:test:asset", VerifiedSubjectMode.TRANSPARENT_CUTOUT,
            )
            with self.assertRaisesRegex(ValueError, "does not match"):
                VerifiedSubjectCompositor().compose(
                    base_path=str(base), output_path=str(root / "out.png"), subject=asset,
                    identity=self.identity(name="Different Person"), placement=SubjectPlacement(10, 10, 200, 300),
                )

    def test_same_inputs_produce_same_png_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "base.png"
            subject_path = root / "subject.png"
            Image.new("RGB", (1080, 1350), (6, 11, 18)).save(base)
            self.cutout(subject_path)
            digest = hashlib.sha256(subject_path.read_bytes()).hexdigest()
            asset = VerifiedSubjectAsset(
                "verified-player-visual", "Verified Player", str(subject_path), digest,
                "trusted:test:asset", VerifiedSubjectMode.TRANSPARENT_CUTOUT,
            )
            c = VerifiedSubjectCompositor()
            a = c.compose(base_path=str(base), output_path=str(root / "a.png"), subject=asset, identity=self.identity(), placement=SubjectPlacement(270,260,540,760), accent_hex="#034694")
            b = c.compose(base_path=str(base), output_path=str(root / "b.png"), subject=asset, identity=self.identity(), placement=SubjectPlacement(270,260,540,760), accent_hex="#034694")
            self.assertEqual(a.output_sha256, b.output_sha256)


if __name__ == "__main__":
    unittest.main()
