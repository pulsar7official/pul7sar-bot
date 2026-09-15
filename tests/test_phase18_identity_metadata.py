import unittest
from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.generation_package import GenerationPackageCompiler
from engine.intelligence.platform_profiles import SocialPlatform
from engine.intelligence.scene_spec import OriginalSceneSpecification, SceneIdentityReference

class IdentityMetadataPropagationTests(unittest.TestCase):
    def assets(self, *, with_identity=False):
        items = [
            AssetReference("pul7sar-logo", AssetRole.PUL7SAR_LOGO, treatment=AssetTreatment.EXACT, source_reference="exact://pul7sar-logo"),
            AssetReference("pul7sar-pulse", AssetRole.PUL7SAR_PULSE, treatment=AssetTreatment.TINTABLE_ACCENT, source_reference="exact://pul7sar-pulse", accent_color="#EF0107"),
        ]
        if with_identity:
            items.append(AssetReference("sam-hickey-ref-1", AssetRole.VERIFIED_IDENTITY_REFERENCE, treatment=AssetTreatment.REFERENCE_ONLY, source_reference="verified://sam-hickey-1"))
        return AssetBundle(tuple(items))
    def specification(self, identity):
        return OriginalSceneSpecification(platform=SocialPlatform.INSTAGRAM_STORY,width=1080,height=1920,aspect_ratio="9:16",safe_area={"top":100,"right":60,"bottom":140,"left":60},family="player_stories",concept="premium athlete portrait",subject=identity.entity_name if identity else None,identity_reference=identity,environment="sport-specific arena",composition="hero portrait",camera_direction="medium portrait",emotional_mood="positive",palette_strategy="#EF0107")
    def test_verified_identity_requirement_survives_into_package_metadata(self):
        identity = SceneIdentityReference("Sam Hickey", sport="boxing", role="middleweight boxer", confidence=0.98)
        package = GenerationPackageCompiler().compile(self.specification(identity), self.assets(with_identity=True))
        self.assertTrue(package.metadata["identity_required"]); self.assertEqual(package.metadata["identity_entity_name"], "Sam Hickey"); self.assertEqual(package.metadata["identity_reference_confidence"], 0.98); self.assertEqual(package.metadata["identity_reference_ids"], ("sam-hickey-ref-1",))
    def test_identity_scene_without_verified_reference_asset_fails_closed(self):
        identity = SceneIdentityReference("Sam Hickey", sport="boxing", role="middleweight boxer", confidence=0.98)
        with self.assertRaises(ValueError): GenerationPackageCompiler().compile(self.specification(identity), self.assets())
    def test_non_identity_scene_is_explicitly_marked(self):
        package = GenerationPackageCompiler().compile(self.specification(None), self.assets())
        self.assertFalse(package.metadata["identity_required"]); self.assertIsNone(package.metadata["identity_entity_name"]); self.assertEqual(package.metadata["identity_reference_ids"], ())

if __name__ == "__main__": unittest.main()
