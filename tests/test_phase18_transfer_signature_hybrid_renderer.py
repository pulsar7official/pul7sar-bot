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
from engine.intelligence.models import IdentityPlan, IdentityStatus
from engine.intelligence.platform_profiles import PlatformProfileRegistry, SocialPlatform
from engine.intelligence.transfer_signature_composition import TransferSignatureComposer
from engine.intelligence.transfer_signature_hybrid_renderer import TransferSignatureHybridRenderer
from engine.intelligence.verified_subject_compositor import VerifiedSubjectAsset, VerifiedSubjectMode
from engine.intelligence.visual_layer_qa import LayerLeakageEvidence
from engine.intelligence.zero_cost_models import ImageQualityTier


class TransferSignatureHybridRendererTests(unittest.TestCase):
    def setUp(self):
        self.profile = PlatformProfileRegistry().get(SocialPlatform.INSTAGRAM_FEED)
        self.composition = TransferSignatureComposer().plan(self.profile)
        self.font = next((p for p in (
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
            Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
        ) if p.is_file()), None)
        if self.font is None:
            self.skipTest('DejaVu font unavailable')

    def _fixture(self, root: Path):
        base = root/'base.png'
        Image.new('RGB',(self.profile.width,self.profile.height),(15,24,39)).save(base)
        prov = LocalGenerationProvenance('local-qwen-image-2512','Qwen/Qwen-Image-2512','diffusers',2512,'transfer-base',self.profile.width,self.profile.height,{'image_quality_tier':'elite'})
        admission = BaseSceneCompositionAdmissionCompiler().compile(
            png_path=str(base), provenance=prov,
            execution_decision=BaseSceneExecutionDecision(True,True,(),LayerLeakageEvidence()),
            quality_tier=ImageQualityTier.ELITE,
        )
        hero_path = root/'hero.png'
        hero_img = Image.new('RGBA',(300,700),(0,0,0,0))
        d = ImageDraw.Draw(hero_img)
        d.ellipse((85,20,215,150),fill=(220,180,150,255))
        d.rounded_rectangle((55,145,245,650),radius=70,fill=(45,95,175,255))
        hero_img.save(hero_path)
        hero_sha = sha256(hero_path.read_bytes()).hexdigest()
        hero = VerifiedSubjectAsset('verified-hero','TEST PLAYER',str(hero_path),hero_sha,'fixture://verified-player',VerifiedSubjectMode.TRANSPARENT_CUTOUT)
        identity = IdentityPlan(entity_name='TEST PLAYER',status=IdentityStatus.VERIFIED,sport='football',role='player',confidence=0.99,depiction_allowed=True,reason='unit-test fixture')
        crest_path = root/'crest.png'
        crest = Image.new('RGBA',(160,160),(0,0,0,0)); cd=ImageDraw.Draw(crest); cd.ellipse((8,8,152,152),fill=(200,30,40,255)); crest.save(crest_path)
        crest_sha = sha256(crest_path.read_bytes()).hexdigest()
        crest_ref = AssetReference('destination-crest',AssetRole.TEAM_CREST,AssetTreatment.EXACT,display_name='DESTINATION FC')
        return admission, hero, identity, ExactRasterAsset(crest_ref,str(crest_path),crest_sha)

    def test_transfer_hybrid_uses_elite_base_verified_hero_exact_crest_and_safe_brand_lane(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            admission,hero,identity,crest=self._fixture(root)
            receipt=TransferSignatureHybridRenderer().render(
                self.composition,admission=admission,profile=self.profile,output_path=str(root/'transfer.png'),
                hero=hero,identity=identity,destination_crest=crest,headline='A NEW CHAPTER',destination_name='DESTINATION FC',
                accent_hex='#C71925',brand_accent_hex='#C71925',font_path=str(self.font),
            )
            self.assertEqual(receipt.contract,'pul7sar-transfer-signature-hybrid-renderer-v1-cinematic-exact')
            self.assertEqual(receipt.base_quality_tier,'elite')
            self.assertFalse(receipt.generator_owns_identity or receipt.generator_owns_crest or receipt.generator_owns_readable_text or receipt.generator_owns_brand)
            self.assertFalse(receipt.full_pitch_used or receipt.hero_text_overlap or receipt.hero_brand_overlap)
            self.assertFalse(receipt.publication_ready)
            self.assertTrue((root/'transfer.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))

    def test_unverified_identity_is_rejected_by_subject_compositor(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            admission,hero,_,crest=self._fixture(root)
            identity=IdentityPlan(entity_name='TEST PLAYER',status=IdentityStatus.UNVERIFIED,sport='football',role='player',confidence=0.2,depiction_allowed=False,reason='not verified')
            with self.assertRaisesRegex(ValueError,'requires VERIFIED'):
                TransferSignatureHybridRenderer().render(
                    self.composition,admission=admission,profile=self.profile,output_path=str(root/'transfer.png'),hero=hero,identity=identity,
                    destination_crest=crest,headline='A NEW CHAPTER',destination_name='DESTINATION FC',accent_hex='#C71925',brand_accent_hex='#C71925',font_path=str(self.font),
                )


if __name__=='__main__': unittest.main()
