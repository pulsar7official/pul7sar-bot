import hashlib
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from engine.intelligence.verified_context_surface import (
    ContextRightsBasis,
    VerifiedContextAsset,
    VerifiedContextSurfaceRenderer,
)


class VerifiedContextSurfaceTests(unittest.TestCase):
    def _fixture(self, root: Path) -> Path:
        path = root / 'context.jpg'
        image = Image.new('RGB', (640, 420), (34, 48, 62))
        image.save(path, format='JPEG', quality=95)
        return path

    def test_rights_known_photo_can_become_deterministic_context_surface(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._fixture(root)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            asset = VerifiedContextAsset(
                asset_id='fixture-context', path=str(source), sha256=digest,
                source_reference='test-fixture', rights_basis=ContextRightsBasis.OWNER_SUPPLIED,
            )
            one = root / 'one.png'
            two = root / 'two.png'
            renderer = VerifiedContextSurfaceRenderer()
            a = renderer.render(asset=asset, output_path=str(one), canvas_size=(1080, 1350), accent_hex='#B21F2D')
            b = renderer.render(asset=asset, output_path=str(two), canvas_size=(1080, 1350), accent_hex='#B21F2D')
            self.assertEqual(a.output_sha256, b.output_sha256)
            self.assertEqual(one.read_bytes(), two.read_bytes())
            self.assertTrue(a.photographic_context_used)
            self.assertFalse(a.generator_used)

    def test_context_asset_cannot_smuggle_person_around_identity_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self._fixture(Path(tmp))
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, 'CONTEXT_SURFACE_MAY_NOT_BYPASS'):
                VerifiedContextAsset(
                    asset_id='bad', path=str(source), sha256=digest,
                    source_reference='test-fixture', rights_basis=ContextRightsBasis.LICENSED,
                    contains_verified_person=True,
                )

    def test_checksum_and_publication_rights_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._fixture(root)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            blocked = VerifiedContextAsset(
                asset_id='blocked', path=str(source), sha256=digest,
                source_reference='test-fixture', rights_basis=ContextRightsBasis.CREATIVE_COMMONS,
                publication_allowed=False,
            )
            with self.assertRaisesRegex(ValueError, 'NOT_AUTHORIZED'):
                VerifiedContextSurfaceRenderer().render(
                    asset=blocked, output_path=str(root/'out.png'), canvas_size=(400, 500), accent_hex='#034694'
                )


if __name__ == '__main__':
    unittest.main()
