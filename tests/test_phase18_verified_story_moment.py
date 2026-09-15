import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.verified_story_moment import (
    StoryMomentKind,
    StoryMomentRights,
    VerifiedStoryMomentAsset,
    VerifiedStoryMomentGate,
)


class VerifiedStoryMomentTests(unittest.TestCase):
    def _image(self, root: Path) -> Path:
        path = root / "moment.jpg"
        Image.new("RGB", (640, 420), (22, 34, 52)).save(path, quality=92)
        return path

    def test_person_bearing_moment_requires_verified_identity_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "REQUIRES_VERIFIED_IDENTITIES"):
                VerifiedStoryMomentAsset(
                    asset_id="goal-moment",
                    path=str(path),
                    sha256=digest,
                    source_reference="test://goal",
                    moment_kind=StoryMomentKind.DECISIVE_ACTION,
                    rights_basis=StoryMomentRights.OWNER_SUPPLIED,
                    contains_people=True,
                )

    def test_verified_moment_is_admitted_with_rights_identity_and_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            asset = VerifiedStoryMomentAsset(
                asset_id="goal-moment",
                path=str(path),
                sha256=digest,
                source_reference="test://goal",
                moment_kind=StoryMomentKind.DECISIVE_ACTION,
                rights_basis=StoryMomentRights.OWNER_SUPPLIED,
                contains_people=True,
                verified_identity_ids=("player:verified-001", "player:verified-002"),
            )
            receipt = VerifiedStoryMomentGate().admit(asset)
            self.assertEqual(receipt.moment_kind, "decisive_action")
            self.assertTrue(receipt.event_evidence)
            self.assertEqual(len(receipt.verified_identity_ids), 2)
            self.assertFalse(receipt.generator_used)

    def test_checksum_and_rights_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._image(Path(tmp))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            bad = VerifiedStoryMomentAsset(
                asset_id="moment",
                path=str(path),
                sha256="0" * 64,
                source_reference="test://moment",
                moment_kind=StoryMomentKind.CELEBRATION,
                rights_basis=StoryMomentRights.OWNER_SUPPLIED,
                contains_people=False,
            )
            with self.assertRaisesRegex(ValueError, "CHECKSUM_MISMATCH"):
                VerifiedStoryMomentGate().admit(bad)

            blocked = VerifiedStoryMomentAsset(
                asset_id="moment",
                path=str(path),
                sha256=digest,
                source_reference="test://moment",
                moment_kind=StoryMomentKind.VERIFIED_OBJECT_DETAIL,
                rights_basis=StoryMomentRights.LICENSED,
                contains_people=False,
                publication_allowed=False,
            )
            with self.assertRaisesRegex(ValueError, "NOT_AUTHORIZED"):
                VerifiedStoryMomentGate().admit(blocked)


if __name__ == "__main__":
    unittest.main()
