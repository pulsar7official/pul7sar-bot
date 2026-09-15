import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.golden_original_scene_admission import GoldenOriginalSceneAdmissionGate
from engine.intelligence.golden_smoke import GoldenSmokeCandidate
from engine.intelligence.local_generation_handoff import LocalGenerationHandoff
from engine.intelligence.local_readiness_report import LocalGenerationReadinessReport
from engine.intelligence.zero_cost_models import FLUX2_KLEIN_4B_LOCAL
from tools.phase18_build_golden_handoff import build_request


def readiness(*, ready=True, provider_id=None, model_id=None, runtime_kind="local_cuda"):
    return LocalGenerationReadinessReport(
        ready=ready,
        provider_id=provider_id or FLUX2_KLEIN_4B_LOCAL.provider_id,
        model_id=model_id or FLUX2_KLEIN_4B_LOCAL.model_id,
        backend="diffusers",
        runtime_kind=runtime_kind,
        gpu_name="test-cuda" if runtime_kind == "local_cuda" else None,
        gpu_vram_gb=16.0 if runtime_kind == "local_cuda" else None,
        blockers=() if ready else ("not-ready",),
        warnings=(),
    )


class GoldenOriginalSceneAdmissionTests(unittest.TestCase):
    def _candidate(self, root: Path, *, candidate_number=1):
        handoff_path = root / "candidate-01.json"
        request = build_request(seed=7007001, request_id="golden-season-opener-editorial-v6-001")
        LocalGenerationHandoff.write(request, str(handoff_path))
        raw = json.loads(handoff_path.read_text(encoding="utf-8"))
        return GoldenSmokeCandidate(
            manifest_path=root / "manifest.json",
            handoff_path=handoff_path,
            candidate=candidate_number,
            seed=request.seed,
            request_id=request.request_id,
            payload_sha256=raw["payload_sha256"],
            provider_id=request.provider_id,
            model_id=request.model_id,
        )

    def test_candidate_1_is_admitted_only_to_matching_zero_cost_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            receipt = GoldenOriginalSceneAdmissionGate().admit(
                candidate=self._candidate(Path(temp)),
                readiness=readiness(),
            )
        self.assertEqual(receipt.candidate, 1)
        self.assertEqual(receipt.cost_mode, "$0-local")
        self.assertEqual(receipt.original_scene_runtime_kind, "atmosphere")
        self.assertTrue(receipt.semantic_inspection_required)
        self.assertFalse(receipt.generated_branding_allowed)
        self.assertFalse(receipt.generated_exact_facts_allowed)
        self.assertFalse(receipt.generated_sport_geometry_allowed)
        self.assertFalse(receipt.queue_mutated)
        self.assertFalse(receipt.png_created)
        self.assertFalse(receipt.semantic_approved)
        self.assertFalse(receipt.golden_quality_approved)
        self.assertFalse(receipt.publication_ready)
        self.assertEqual(len(receipt.compiled_prompt_sha256), 64)

    def test_candidate_other_than_one_is_rejected_before_runtime_admission(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "REQUIRES_CANDIDATE_1"):
                GoldenOriginalSceneAdmissionGate().admit(
                    candidate=self._candidate(Path(temp), candidate_number=2),
                    readiness=readiness(),
                )

    def test_cpu_or_unready_runtime_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate = self._candidate(Path(temp))
            with self.assertRaisesRegex(ValueError, "ORIGINAL_SCENE_LOCAL_RUNTIME_NOT_ADMITTED"):
                GoldenOriginalSceneAdmissionGate().admit(
                    candidate=candidate,
                    readiness=readiness(runtime_kind="local_cpu"),
                )

    def test_provider_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            candidate = self._candidate(Path(temp))
            with self.assertRaisesRegex(ValueError, "ORIGINAL_SCENE_LOCAL_RUNTIME_NOT_ADMITTED"):
                GoldenOriginalSceneAdmissionGate().admit(
                    candidate=candidate,
                    readiness=readiness(provider_id="wrong-provider"),
                )


class FirstPngOriginalSceneEntrypointTests(unittest.TestCase):
    def setUp(self):
        self.path = Path("tools/phase18_first_png_original_scene.py")
        self.text = self.path.read_text(encoding="utf-8")

    def test_admission_is_executed_before_canonical_first_png(self):
        admission = self.text.index("phase18_admit_golden_original_scene.py")
        generation = self.text.index("phase18_first_png.py")
        self.assertLess(admission, generation)

    def test_wrapper_does_not_mutate_queue_or_authorize_quality(self):
        self.assertNotIn("FilesystemGenerationJobStore", self.text)
        self.assertIn('"semantic_approved": False', self.text)
        self.assertIn('"golden_quality_approved": False', self.text)
        self.assertIn('"publication_ready": False', self.text)

    def test_admission_receipt_is_sha_bound_before_and_after_generation(self):
        self.assertIn("import hashlib", self.text)
        self.assertIn("admission_sha256 = _sha256(receipt)", self.text)
        self.assertIn("admission_bytes = receipt.stat().st_size", self.text)
        self.assertIn("replayed_admission = _load_admission_receipt(receipt)", self.text)
        self.assertIn("GOLDEN_ORIGINAL_SCENE_ADMISSION_RECEIPT_TAMPERED_DURING_GENERATION", self.text)
        self.assertIn('"original_scene_admission_sha256": admission_sha256', self.text)
        self.assertIn('"original_scene_admission_replayed": True', self.text)
        generation = self.text.index("phase18_first_png.py")
        prebind = self.text.index("admission_sha256 = _sha256(receipt)")
        replay = self.text.index("replayed_admission = _load_admission_receipt(receipt)")
        self.assertLess(prebind, generation)
        self.assertLess(generation, replay)

    def test_admission_receipt_must_stay_inside_repository(self):
        self.assertIn("_inside_root(repository_root, Path(args.admission_receipt))", self.text)
        self.assertIn("GOLDEN_ORIGINAL_SCENE_ADMISSION_RECEIPT_ESCAPES_REPOSITORY", self.text)


if __name__ == "__main__":
    unittest.main()
