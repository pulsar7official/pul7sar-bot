import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.visual_brain import VisualCriticGate
from engine.intelligence.visual_brain_critic_provenance import (
    CRITIC_PROVENANCE_CONTRACT,
    VISUAL_BRAIN_BATCH_CONTRACT,
    VISUAL_BRAIN_BENCHMARK,
    VisualCriticProvenanceGate,
)


PNG_BYTES = b"\x89PNG\r\n\x1a\nvisual-brain-test-pixels"


class VisualBrainCriticProvenanceTests(unittest.TestCase):
    def _fixture(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "output").mkdir()
        png = root / "output" / "candidate.png"
        png.write_bytes(PNG_BYTES)
        png_sha = hashlib.sha256(PNG_BYTES).hexdigest()
        payload_sha = "a" * 64
        candidate = {
            "candidate": 1,
            "concept_id": "preview-light-awakening",
            "request_id": "visual-brain-preview-preview-light-awakening-01",
            "seed": 8107101,
            "payload_sha256": payload_sha,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "provider_id": "local-diffusers",
        }
        manifest = {
            "manifest_version": VISUAL_BRAIN_BATCH_CONTRACT,
            "benchmark": VISUAL_BRAIN_BENCHMARK,
            "critic_contract": VisualCriticGate.CONTRACT,
            "publication_ready": False,
            "candidates": [candidate],
        }
        result = {
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "png": "output/candidate.png",
            "publication_ready": False,
            "cost_mode": "$0-local",
            **{key: candidate[key] for key in ("concept_id", "request_id", "seed", "payload_sha256", "model_id", "provider_id")},
        }
        evidence = {
            "candidate": 1,
            "concept_id": candidate["concept_id"],
            "request_id": candidate["request_id"],
            "seed": candidate["seed"],
            "payload_sha256": payload_sha,
            "png_sha256": png_sha,
            "editorial_specificity": 0.90,
            "visual_impact": 0.91,
            "composition_quality": 0.90,
            "photographic_coherence": 0.92,
            "concept_fidelity": 0.93,
            "ordinary_stock_risk": 0.10,
        }
        manifest_path = root / "manifest.json"
        result_path = root / "result.json"
        evidence_path = root / "critic.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        result_path.write_text(json.dumps(result), encoding="utf-8")
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        return temp, root, manifest_path, result_path, evidence_path, png, evidence

    def test_accepts_only_critic_evidence_bound_to_exact_generated_bytes(self):
        temp, root, manifest, result, evidence_path, _, _ = self._fixture()
        self.addCleanup(temp.cleanup)
        receipt = VisualCriticProvenanceGate().verify(
            repository_root=root,
            manifest_path=manifest,
            generation_result_path=result,
            critic_evidence_path=evidence_path,
        ).to_dict()
        self.assertEqual(receipt["contract"], CRITIC_PROVENANCE_CONTRACT)
        self.assertEqual(receipt["status"], "VISUAL_BRAIN_CRITIC_PROVENANCE_ACCEPTED")
        self.assertTrue(receipt["critic_accepted"])
        self.assertGreater(receipt["critic_score"], 0.85)
        self.assertTrue(receipt["human_visual_review_required"])
        self.assertFalse(receipt["golden_quality_approved"])
        self.assertFalse(receipt["publication_ready"])
        for field in ("png_sha256", "batch_manifest_sha256", "generation_result_sha256", "critic_evidence_sha256"):
            self.assertEqual(len(receipt[field]), 64)

    def test_rejects_png_tampering_after_critic_evidence_was_created(self):
        temp, root, manifest, result, evidence_path, png, _ = self._fixture()
        self.addCleanup(temp.cleanup)
        png.write_bytes(PNG_BYTES + b"tamper")
        with self.assertRaisesRegex(ValueError, "not bound to the generated PNG bytes"):
            VisualCriticProvenanceGate().verify(
                repository_root=root,
                manifest_path=manifest,
                generation_result_path=result,
                critic_evidence_path=evidence_path,
            )

    def test_rejects_critic_candidate_identity_drift(self):
        temp, root, manifest, result, evidence_path, _, evidence = self._fixture()
        self.addCleanup(temp.cleanup)
        evidence["seed"] = 9999999
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "seed does not match"):
            VisualCriticProvenanceGate().verify(
                repository_root=root,
                manifest_path=manifest,
                generation_result_path=result,
                critic_evidence_path=evidence_path,
            )

    def test_hard_visual_failure_remains_rejected_and_never_publishable(self):
        temp, root, manifest, result, evidence_path, _, evidence = self._fixture()
        self.addCleanup(temp.cleanup)
        evidence["geometry_violation"] = True
        evidence_path.write_text(json.dumps(evidence), encoding="utf-8")
        receipt = VisualCriticProvenanceGate().verify(
            repository_root=root,
            manifest_path=manifest,
            generation_result_path=result,
            critic_evidence_path=evidence_path,
        ).to_dict()
        self.assertEqual(receipt["status"], "VISUAL_BRAIN_CRITIC_PROVENANCE_REJECTED")
        self.assertFalse(receipt["critic_accepted"])
        self.assertEqual(receipt["critic_score"], 0.0)
        self.assertIn("sport geometry violation", receipt["critic_failures"])
        self.assertFalse(receipt["publication_ready"])

    def test_rejects_paths_outside_repository(self):
        temp, root, manifest, result, evidence_path, _, _ = self._fixture()
        self.addCleanup(temp.cleanup)
        outside = Path(temp.name).parent / "outside-critic.json"
        outside.write_text(evidence_path.read_text(encoding="utf-8"), encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        with self.assertRaisesRegex(ValueError, "escapes repository root"):
            VisualCriticProvenanceGate().verify(
                repository_root=root,
                manifest_path=manifest,
                generation_result_path=result,
                critic_evidence_path=outside,
            )


if __name__ == "__main__":
    unittest.main()
