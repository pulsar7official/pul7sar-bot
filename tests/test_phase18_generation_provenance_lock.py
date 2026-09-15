import json
import tempfile
import unittest
from pathlib import Path

from engine.intelligence.approved_model_revisions import FLUX2_KLEIN_4B_REVISION
from engine.intelligence.generation_provenance_lock import GenerationProvenanceLock


class GenerationProvenanceLockTests(unittest.TestCase):
    def _fixture(self, root: Path):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow unavailable")

        proof = root / "output" / "phase18_visual_proof" / "proof.png"
        proof.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (640, 800), (21, 62, 39)).save(proof)
        metadata = proof.with_suffix(".json")
        metadata.write_text(json.dumps({
            "provider": "local-flux2-klein-4b",
            "model": "black-forest-labs/FLUX.2-klein-4B",
            "model_revision": FLUX2_KLEIN_4B_REVISION,
            "backend": "diffusers",
            "seed": 7007001,
            "request_id": "golden-hybrid-v5-001",
            "width": 640,
            "height": 800,
            "output_ref": str(proof),
            "visual_proof": True,
            "cost_mode": "$0-local",
        }), encoding="utf-8")
        executor = root / "output" / "phase18_visual_proof" / "colab-candidate-01-result.json"
        executor.write_text(json.dumps({
            "status": "REAL_VISUAL_PROOF_GENERATED",
            "png": str(proof),
            "metadata": str(metadata),
            "request_id": "golden-hybrid-v5-001",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "payload_sha256": "a" * 64,
            "resolved_dtype": "bfloat16",
            "cost_mode": "$0-local",
        }), encoding="utf-8")
        summary = {
            "candidate": 1,
            "request_id": "golden-hybrid-v5-001",
            "seed": 7007001,
            "model_id": "black-forest-labs/FLUX.2-klein-4B",
            "payload_sha256": "a" * 64,
            "executor_result": str(executor),
            "publication_ready": False,
        }
        return proof, metadata, executor, summary

    def test_verifies_and_hashes_exact_proof_executor_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            proof, metadata, executor, summary = self._fixture(root)
            result = GenerationProvenanceLock().verify(
                repository_root=str(root), summary=summary, base_png=str(proof)
            )
            self.assertEqual(result["status"], "GENERATION_PROVENANCE_LOCK_VERIFIED")
            self.assertEqual(result["model_revision"], FLUX2_KLEIN_4B_REVISION)
            self.assertEqual(len(result["base_png_sha256"]), 64)
            self.assertEqual(len(result["executor_result_sha256"]), 64)
            self.assertEqual(len(result["metadata_sha256"]), 64)
            self.assertEqual(result["resolved_dtype"], "bfloat16")
            self.assertFalse(result["publication_ready"])
            self.assertEqual(Path(result["executor_result"]), executor.resolve())
            self.assertEqual(Path(result["metadata"]), metadata.resolve())

    def test_rejects_executor_identity_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            proof, _, executor, summary = self._fixture(root)
            data = json.loads(executor.read_text(encoding="utf-8"))
            data["seed"] = 9
            executor.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "SEED_MISMATCH"):
                GenerationProvenanceLock().verify(
                    repository_root=str(root), summary=summary, base_png=str(proof)
                )

    def test_rejects_png_path_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            proof, _, executor, summary = self._fixture(root)
            other = proof.with_name("other.png")
            other.write_bytes(proof.read_bytes())
            data = json.loads(executor.read_text(encoding="utf-8"))
            data["png"] = str(other)
            executor.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "PNG_PATH_MISMATCH"):
                GenerationProvenanceLock().verify(
                    repository_root=str(root), summary=summary, base_png=str(proof)
                )

    def test_rejects_metadata_output_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            proof, metadata, _, summary = self._fixture(root)
            data = json.loads(metadata.read_text(encoding="utf-8"))
            data["output_ref"] = str(proof.with_name("wrong.png"))
            metadata.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "METADATA_OUTPUT_MISMATCH"):
                GenerationProvenanceLock().verify(
                    repository_root=str(root), summary=summary, base_png=str(proof)
                )

    def test_rejects_model_revision_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            proof, metadata, _, summary = self._fixture(root)
            data = json.loads(metadata.read_text(encoding="utf-8"))
            data["model_revision"] = "0" * 40
            metadata.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "METADATA_MODEL_REVISION_MISMATCH"):
                GenerationProvenanceLock().verify(
                    repository_root=str(root), summary=summary, base_png=str(proof)
                )

    def test_rejects_precision_or_cost_drift(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            proof, _, executor, summary = self._fixture(root)
            for key, bad, message in (
                ("resolved_dtype", "float16", "DTYPE_DRIFT"),
                ("cost_mode", "paid", "COST_MODE_DRIFT"),
            ):
                data = json.loads(executor.read_text(encoding="utf-8"))
                original = data[key]
                data[key] = bad
                executor.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, message):
                    GenerationProvenanceLock().verify(
                        repository_root=str(root), summary=summary, base_png=str(proof)
                    )
                data[key] = original
                executor.write_text(json.dumps(data), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
