import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw

from engine.intelligence.assets import AssetReference, AssetRole, AssetTreatment
from engine.intelligence.base_scene_composition_admission import BaseSceneCompositionAdmissionCompiler
from engine.intelligence.base_scene_execution_gate import BaseSceneExecutionDecision
from engine.intelligence.exact_raster_asset import ExactRasterAsset
from engine.intelligence.local_generation_provenance import LocalGenerationProvenance
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.result_statement_composition import ResultStatementComposer
from engine.intelligence.result_statement_hybrid_renderer import ResultStatementHybridRenderer
from engine.intelligence.visual_layer_qa import LayerLeakageEvidence
from engine.intelligence.zero_cost_models import ImageQualityTier


class ResultStatementHybridRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = ResultStatementComposer().plan(self.profile)
        self.font = next((p for p in (
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ) if p.is_file()), None)
        if self.font is None:
            self.skipTest('DejaVu font unavailable')

    @staticmethod
    def _png(path: Path, size, color, mark=False):
        image = Image.new('RGBA', size, color)
        if mark:
            draw = ImageDraw.Draw(image)
            draw.ellipse((8, 8, size[0]-8, size[1]-8), fill=(255,255,255,255), outline=(30,30,30,255), width=3)
            draw.ellipse((size[0]//2-8, size[1]//2-8, size[0]//2+8, size[1]//2+8), fill=color)
        image.save(path)
        return sha256(path.read_bytes()).hexdigest()

    def _fixture(self, root: Path):
        base = root/'base.png'
        self._png(base, (self.profile.width, self.profile.height), (12, 25, 42, 255))
        provenance = LocalGenerationProvenance(
            provider_id='local-qwen-image-2512', model_id='Qwen/Qwen-Image-2512', backend='diffusers',
            seed=2512, request_id='elite-result-base', width=self.profile.width, height=self.profile.height,
            metadata={'image_quality_tier': 'elite'},
        )
        decision = BaseSceneExecutionDecision(True, True, (), LayerLeakageEvidence())
        admission = BaseSceneCompositionAdmissionCompiler().compile(
            png_path=str(base), provenance=provenance, execution_decision=decision, quality_tier=ImageQualityTier.ELITE,
        )
        home_path, away_path = root/'home.png', root/'away.png'
        home_sha = self._png(home_path, (160,160), (3,70,148,255), True)
        away_sha = self._png(away_path, (160,160), (178,31,45,255), True)
        home_ref = AssetReference('home-crest', AssetRole.TEAM_CREST, AssetTreatment.EXACT, display_name='HOME CLUB')
        away_ref = AssetReference('away-crest', AssetRole.TEAM_CREST, AssetTreatment.EXACT, display_name='AWAY CLUB')
        return admission, ExactRasterAsset(home_ref, str(home_path), home_sha), ExactRasterAsset(away_ref, str(away_path), away_sha)

    def test_elite_base_exact_crests_score_and_brand_compose_without_generator_ownership(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            admission, home, away = self._fixture(root)
            receipt = ResultStatementHybridRenderer().render(
                self.composition, admission=admission, profile=self.profile, output_path=str(root/'result.png'),
                home_crest=home, away_crest=away, home_name='HOME CLUB', away_name='AWAY CLUB',
                home_score=3, away_score=1, headline='FULL TIME', home_accent_hex='#034694', away_accent_hex='#B21F2D',
                brand_accent_hex='#034694', font_path=str(self.font), winner='home',
            )
            self.assertEqual(receipt.contract, 'pul7sar-result-statement-hybrid-renderer-v1-cinematic-exact')
            self.assertEqual(receipt.base_quality_tier, 'elite')
            self.assertTrue(receipt.exact_crests_used and receipt.exact_score_used)
            self.assertFalse(receipt.generated_score_used or receipt.generated_brand_used or receipt.loser_degraded)
            self.assertFalse(receipt.publication_ready)
            self.assertTrue((root/'result.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))

    def test_tampered_admitted_base_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            admission, home, away = self._fixture(root)
            Path(admission.png_path).write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'BYTES_CHANGED'):
                ResultStatementHybridRenderer().render(
                    self.composition, admission=admission, profile=self.profile, output_path=str(root/'result.png'),
                    home_crest=home, away_crest=away, home_name='HOME', away_name='AWAY', home_score=1, away_score=0,
                    headline='FULL TIME', home_accent_hex='#034694', away_accent_hex='#B21F2D', brand_accent_hex='#034694',
                    font_path=str(self.font), winner='home',
                )

    def test_tampered_exact_crest_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            admission, home, away = self._fixture(root)
            Path(home.path).write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                ResultStatementHybridRenderer().render(
                    self.composition, admission=admission, profile=self.profile, output_path=str(root/'result.png'),
                    home_crest=home, away_crest=away, home_name='HOME', away_name='AWAY', home_score=1, away_score=0,
                    headline='FULL TIME', home_accent_hex='#034694', away_accent_hex='#B21F2D', brand_accent_hex='#034694',
                    font_path=str(self.font), winner='home',
                )


if __name__ == '__main__':
    unittest.main()
