import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.dynamic_renderer_prompt import DynamicRendererPromptCompiler
from engine.intelligence.dynamic_visual_brain_critic_binding import DynamicVisualBrainCriticBindingGate
from engine.intelligence.dynamic_visual_brain_local_admission import DynamicVisualBrainLocalAdmission
from engine.intelligence.dynamic_visual_brain_lock import DynamicVisualBrainConceptLock
from engine.intelligence.visual_brain import VisualCriticGate
from engine.intelligence.visual_brain_critic_provenance import VISUAL_BRAIN_BATCH_CONTRACT, VISUAL_BRAIN_BENCHMARK


class DynamicVisualBrainCriticBindingTests(unittest.TestCase):
    def _fixture(self, root: Path):
        digest = lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest()
        story = digest("story")
        competition = digest("competition")
        concept_hash = digest("concept")
        prompt_hash = digest("prompt")
        renderer_prompt_hash = digest("renderer-safe-prompt")
        original_hash = digest("original")
        payload_hash = digest("payload")
        concept_id = "preview-atmosphere-01"
        request_id = "dynamic-preview-001"
        seed = 42
        png = root / "candidate.png"
        png.write_bytes(b"\x89PNG\r\n\x1a\n" + b"dynamic-visual-brain-candidate")
        png_hash = hashlib.sha256(png.read_bytes()).hexdigest()

        lock = {
            "contract": DynamicVisualBrainConceptLock.CONTRACT,
            "status": "DYNAMIC_VISUAL_BRAIN_CONCEPT_LOCKED",
            "story_fingerprint": story,
            "event": "preview",
            "concept_count": 3,
            "competition_sha256": competition,
            "selected_concept_id": concept_id,
            "selected_concept_sha256": concept_hash,
            "scene_prompt_sha256": prompt_hash,
            "preflight_score": 0.91,
            "provider_agnostic": True,
            "selection_locked_before_rendering": True,
            "generation_authorized": False,
            "human_visual_review_approved": False,
            "golden_quality_approved": False,
            "publication_ready": False,
            "seeds_2_to_4_authorized": False,
        }
        admission = {
            "contract": DynamicVisualBrainLocalAdmission.CONTRACT,
            "status": "DYNAMIC_VISUAL_BRAIN_RENDERER_SAFE_LOCAL_RUNTIME_ADMITTED",
            "story_fingerprint": story,
            "competition_sha256": competition,
            "selected_concept_id": concept_id,
            "selected_concept_sha256": concept_hash,
            "scene_prompt_sha256": prompt_hash,
            "renderer_prompt_contract": DynamicRendererPromptCompiler.CONTRACT,
            "renderer_prompt_sha256": renderer_prompt_hash,
            "renderer_identity_neutral": True,
            "original_scene_request_sha256": original_hash,
            "provider_id": "local-diffusers",
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "backend": "diffusers",
            "request_id": request_id,
            "seed": seed,
            "cost_mode": "$0-local",
            "semantic_inspection_required": True,
            "runtime_qualified": True,
            "generation_request_compiled": True,
            "generated_branding_allowed": False,
            "generated_exact_facts_allowed": False,
            "generated_sport_geometry_allowed": False,
            "human_visual_review_required": True,
            "golden_quality_approved": False,
            "publication_ready": False,
        }
        manifest = {
            "manifest_version": VISUAL_BRAIN_BATCH_CONTRACT,
            "benchmark": VISUAL_BRAIN_BENCHMARK,
            "critic_contract": VisualCriticGate.CONTRACT,
            "publication_ready": False,
            "candidates": [{
                "candidate": 1,
                "concept_id": concept_id,
                "request_id": request_id,
                "seed": seed,
                "payload_sha256": payload_hash,
                "provider_id": "local-diffusers",
                "model_id": "black-forest-labs/FLUX.2-klein-4B",
            }],
        }
        result = {
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "candidate": 1,
            "concept_id": concept_id,
            "request_id": request_id,
            "seed": seed,
            "payload_sha256": payload_hash,
            "provider_id": "local-diffusers",
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "cost_mode": "$0-local",
            "publication_ready": False,
            "png": str(png.relative_to(root)),
            "dynamic_visual_brain_contract": DynamicVisualBrainCriticBindingGate.PLAN_CONTRACT,
            "dynamic_visual_brain_story_fingerprint": story,
            "dynamic_visual_brain_competition_sha256": competition,
            "dynamic_visual_brain_selected_concept_id": concept_id,
            "dynamic_visual_brain_selected_concept_sha256": concept_hash,
            "dynamic_visual_brain_scene_prompt_sha256": prompt_hash,
            "dynamic_renderer_prompt_contract": DynamicRendererPromptCompiler.CONTRACT,
            "dynamic_renderer_prompt_sha256": renderer_prompt_hash,
            "dynamic_renderer_identity_neutral": True,
            "dynamic_visual_brain_original_scene_request_sha256": original_hash,
            "dynamic_visual_brain_selection_locked_before_rendering": True,
        }
        critic = {
            "candidate": 1,
            "concept_id": concept_id,
            "request_id": request_id,
            "seed": seed,
            "payload_sha256": payload_hash,
            "png_sha256": png_hash,
            "geometry_violation": False,
            "pseudo_text_detected": False,
            "identity_violation": False,
            "factual_violation": False,
            "generation_defect": False,
            "editorial_specificity": 0.91,
            "visual_impact": 0.92,
            "composition_quality": 0.93,
            "photographic_coherence": 0.91,
            "concept_fidelity": 0.94,
            "ordinary_stock_risk": 0.1,
        }
        paths = {}
        for name, payload in (("lock", lock), ("admission", admission), ("manifest", manifest), ("result", result), ("critic", critic)):
            path = root / f"{name}.json"
            path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            paths[name] = path
        return paths

    def _verify(self, root: Path, paths):
        return DynamicVisualBrainCriticBindingGate.verify(
            concept_lock_path=str(paths["lock"].relative_to(root)),
            local_admission_path=str(paths["admission"].relative_to(root)),
            batch_manifest_path=str(paths["manifest"].relative_to(root)),
            generation_result_path=str(paths["result"].relative_to(root)),
            critic_evidence_path=str(paths["critic"].relative_to(root)),
            repository_root=str(root),
        )

    def test_exact_locked_concept_renderer_prompt_and_png_can_reach_human_review_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            receipt = self._verify(root, self._fixture(root))
            self.assertTrue(receipt.critic_approved)
            self.assertEqual(receipt.renderer_prompt_contract, DynamicRendererPromptCompiler.CONTRACT)
            self.assertEqual(len(receipt.renderer_prompt_sha256), 64)
            self.assertTrue(receipt.renderer_identity_neutral)
            self.assertTrue(receipt.human_visual_review_required)
            self.assertFalse(receipt.golden_quality_approved)
            self.assertFalse(receipt.publication_ready)

    def test_generation_cannot_swap_selected_concept_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = self._fixture(root)
            result = json.loads(paths["result"].read_text())
            result["dynamic_visual_brain_selected_concept_sha256"] = "0" * 64
            paths["result"].write_text(json.dumps(result), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "selected_concept_sha256"):
                self._verify(root, paths)

    def test_renderer_safe_prompt_cannot_be_swapped_after_admission(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = self._fixture(root)
            result = json.loads(paths["result"].read_text())
            result["dynamic_renderer_prompt_sha256"] = "0" * 64
            paths["result"].write_text(json.dumps(result), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "dynamic_renderer_prompt_sha256"):
                self._verify(root, paths)

    def test_renderer_identity_neutrality_cannot_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = self._fixture(root)
            admission = json.loads(paths["admission"].read_text())
            admission["renderer_identity_neutral"] = False
            paths["admission"].write_text(json.dumps(admission), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "IDENTITY_NEUTRALITY"):
                self._verify(root, paths)

    def test_local_admission_cannot_gain_publication_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = self._fixture(root)
            admission = json.loads(paths["admission"].read_text())
            admission["publication_ready"] = True
            paths["admission"].write_text(json.dumps(admission), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "AUTHORITY_DRIFT"):
                self._verify(root, paths)

    def test_visual_critic_geometry_failure_remains_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = self._fixture(root)
            critic = json.loads(paths["critic"].read_text())
            critic["geometry_violation"] = True
            paths["critic"].write_text(json.dumps(critic), encoding="utf-8")
            receipt = self._verify(root, paths)
            self.assertFalse(receipt.critic_approved)
            self.assertTrue(receipt.critic_rejections)
            self.assertFalse(receipt.publication_ready)

    def test_png_tampering_after_critic_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = self._fixture(root)
            (root / "candidate.png").write_bytes(b"\x89PNG\r\n\x1a\nchanged")
            with self.assertRaisesRegex(ValueError, "PNG bytes"):
                self._verify(root, paths)


if __name__ == "__main__":
    unittest.main()
