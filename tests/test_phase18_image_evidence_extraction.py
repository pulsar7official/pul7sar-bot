import unittest

from engine.intelligence.base_scene_quality import (
    GenerationDefectEvidence, IdentityVisualEvidence, ProtectedRegionEvidence, SubjectFramingEvidence,
)
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.image_evidence_extraction import (
    BaseSceneEvidenceExtractor, GeneratedImageObservation, ImageEvidenceProbeSet,
)
from engine.intelligence.local_generation_provenance import LocalGenerationProvenance


class _Framing:
    def inspect(self, image, package):
        return SubjectFramingEvidence(True, True, True, 0.96)


class _Identity:
    def inspect(self, image, package):
        return IdentityVisualEvidence(True, True, 0.97, ("identity-ref-1",))


class _Regions:
    def inspect(self, image, package):
        return (
            ProtectedRegionEvidence("logo", True, 0.03),
            ProtectedRegionEvidence("headline", True, 0.05),
        )


class _Defects:
    def inspect(self, image, package):
        return GenerationDefectEvidence(True)


class _Forbidden:
    def inspect(self, image, package):
        return ()


class _SafeCrop:
    def inspect(self, image, package):
        return True


class ImageEvidenceExtractionTests(unittest.TestCase):
    def setUp(self):
        self.package = GenerationPackage(
            platform="instagram_feed",
            canvas="1080x1350",
            scene_prompt="clean editorial scene",
            negative_constraints=("no humiliation",),
            asset_ids=(),
            factual_constraints=(),
            layout_boxes={
                "hero": {"x": 0, "y": 0, "width": 800, "height": 1000},
                "logo": {"x": 30, "y": 30, "width": 200, "height": 70},
                "headline": {"x": 80, "y": 1080, "width": 920, "height": 180},
            },
        )
        self.image = GeneratedImageObservation("file:///tmp/scene.png", 1080, 1350, "4:5")
        self.provenance = LocalGenerationProvenance(
            provider_id="local-flux",
            model_id="model",
            backend="diffusers",
            seed=123,
            request_id="req-1",
            width=1080,
            height=1350,
            metadata={"output_ref": "file:///tmp/scene.png"},
        )
        self.extractor = BaseSceneEvidenceExtractor(ImageEvidenceProbeSet(
            _Framing(), _Identity(), _Regions(), _Defects(), _Forbidden(), _SafeCrop()
        ))

    def test_extracts_domain_owned_base_scene_evidence(self):
        evidence = self.extractor.extract(image=self.image, package=self.package, provenance=self.provenance)
        self.assertEqual(evidence.provider_id, "local-flux")
        self.assertTrue(evidence.identity.matched)
        self.assertEqual(evidence.provenance["seed"], 123)
        self.assertTrue(evidence.safe_crop_possible)

    def test_image_dimensions_must_match_provenance(self):
        bad = GeneratedImageObservation("file:///tmp/scene.png", 1024, 1350, "4:5")
        with self.assertRaises(ValueError):
            self.extractor.extract(image=bad, package=self.package, provenance=self.provenance)

    def test_output_ref_cannot_conflict_with_provenance(self):
        bad = GeneratedImageObservation("file:///tmp/other.png", 1080, 1350, "4:5")
        with self.assertRaises(ValueError):
            self.extractor.extract(image=bad, package=self.package, provenance=self.provenance)

    def test_invalid_probe_evidence_is_rejected(self):
        class BadIdentity:
            def inspect(self, image, package):
                return {"matched": True}
        extractor = BaseSceneEvidenceExtractor(ImageEvidenceProbeSet(
            _Framing(), BadIdentity(), _Regions(), _Defects(), _Forbidden(), _SafeCrop()
        ))
        with self.assertRaises(TypeError):
            extractor.extract(image=self.image, package=self.package, provenance=self.provenance)


if __name__ == "__main__":
    unittest.main()
