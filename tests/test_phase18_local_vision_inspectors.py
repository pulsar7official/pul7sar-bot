import tempfile
import unittest
from pathlib import Path
import struct

from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.image_evidence_extraction import GeneratedImageObservation
from engine.intelligence.local_vision_inspectors import (
    FailClosedForbiddenVisualProbe,
    FailClosedIdentityProbe,
    FailClosedSemanticDefectProbe,
    FailClosedSubjectFramingProbe,
    GeometrySafeCropProbe,
    LocalImageInspectionError,
    PngFileObserver,
    detect_local_vision_capabilities,
)


class LocalVisionInspectorTests(unittest.TestCase):
    def package(self, **metadata):
        return GenerationPackage(
            platform="instagram_story",
            canvas="1080x1920",
            scene_prompt="clean sports editorial base scene",
            negative_constraints=("no fake signing",),
            asset_ids=(),
            factual_constraints=("transfer not completed",),
            layout_boxes={
                "hero": {"x": 100, "y": 250, "width": 800, "height": 1000},
                "logo": {"x": 80, "y": 80, "width": 250, "height": 100},
                "headline": {"x": 100, "y": 1350, "width": 880, "height": 260},
            },
            metadata=metadata,
        )

    def write_png_header(self, path: Path, width: int, height: int):
        data = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height)
        path.write_bytes(data)

    def test_png_observer_reads_exact_dimensions_without_heavy_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "scene.png"
            self.write_png_header(path, 1080, 1920)
            observed = PngFileObserver().observe(str(path))
            self.assertEqual((observed.width, observed.height), (1080, 1920))
            self.assertEqual(observed.aspect_ratio, "9:16")

    def test_png_observer_rejects_remote_reference(self):
        with self.assertRaises(LocalImageInspectionError):
            PngFileObserver().observe("https://example.com/scene.png")

    def test_identity_probe_fails_closed_when_identity_is_required(self):
        image = GeneratedImageObservation("scene.png", 1080, 1920, "9:16")
        evidence = FailClosedIdentityProbe().inspect(
            image,
            self.package(identity_required=True, identity_reference_ids=("ref-1",)),
        )
        self.assertTrue(evidence.required)
        self.assertFalse(evidence.matched)
        self.assertEqual(evidence.confidence, 0.0)

    def test_identity_probe_does_not_block_when_identity_is_not_required(self):
        image = GeneratedImageObservation("scene.png", 1080, 1920, "9:16")
        evidence = FailClosedIdentityProbe().inspect(image, self.package())
        self.assertFalse(evidence.required)
        self.assertTrue(evidence.matched)

    def test_subject_framing_is_not_invented(self):
        image = GeneratedImageObservation("scene.png", 1080, 1920, "9:16")
        evidence = FailClosedSubjectFramingProbe().inspect(image, self.package())
        self.assertFalse(evidence.subject_present)
        self.assertEqual(evidence.confidence, 0.0)

    def test_semantic_defect_check_fails_closed_when_unavailable(self):
        image = GeneratedImageObservation("scene.png", 1080, 1920, "9:16")
        evidence = FailClosedSemanticDefectProbe().inspect(image, self.package())
        self.assertFalse(evidence.defect_free)
        self.assertIn("semantic defect inspection unavailable", evidence.defects)

    def test_forbidden_visual_verification_does_not_silently_pass(self):
        image = GeneratedImageObservation("scene.png", 1080, 1920, "9:16")
        detected = FailClosedForbiddenVisualProbe().inspect(image, self.package())
        self.assertIn("forbidden-visual verification unavailable", detected)

    def test_geometry_safe_crop_accepts_boxes_inside_canvas(self):
        image = GeneratedImageObservation("scene.png", 1080, 1920, "9:16")
        self.assertTrue(GeometrySafeCropProbe().inspect(image, self.package()))

    def test_geometry_safe_crop_rejects_box_outside_canvas(self):
        package = GenerationPackage(
            platform="instagram_story",
            canvas="1080x1920",
            scene_prompt="scene",
            negative_constraints=(), asset_ids=(), factual_constraints=(),
            layout_boxes={"headline": {"x": 1000, "y": 1800, "width": 200, "height": 200}},
        )
        image = GeneratedImageObservation("scene.png", 1080, 1920, "9:16")
        self.assertFalse(GeometrySafeCropProbe().inspect(image, package))

    def test_capability_report_never_claims_unimplemented_semantic_checks(self):
        report = detect_local_vision_capabilities()
        self.assertTrue(report.png_observation)
        self.assertFalse(report.semantic_subject_framing)
        self.assertFalse(report.identity_similarity)
        self.assertFalse(report.semantic_defect_detection)
        self.assertFalse(report.forbidden_visual_detection)
        self.assertFalse(report.publication_grade)


if __name__ == "__main__":
    unittest.main()
