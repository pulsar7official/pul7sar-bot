from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from engine.intelligence.generation_job_store import FilesystemGenerationJobStore
from engine.intelligence.generation_jobs import GenerationJobState
from engine.intelligence.golden_smoke import DEFAULT_SMOKE_JOB_ID, load_first_candidate, prepare_smoke_job, smoke_status_payload
from tools.phase18_build_golden_batch import build_batch


class GoldenSmokeCoordinatorTests(unittest.TestCase):
    def _build(self, root: Path) -> Path:
        batch_dir = root / "batch"
        build_batch(str(batch_dir))
        return batch_dir / "manifest.json"

    def test_load_first_candidate_cross_checks_locked_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            candidate = load_first_candidate(manifest)
            self.assertEqual(candidate.candidate, 1)
            self.assertEqual(candidate.seed, 7007001)
            self.assertEqual(candidate.request_id, "golden-season-opener-editorial-v6-001")
            self.assertEqual(len(candidate.payload_sha256), 64)
            self.assertTrue(candidate.handoff_path.is_file())

    def test_manifest_sha_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["candidates"][0]["payload_sha256"] = "0" * 64
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "SHA"):
                load_first_candidate(manifest)

    def test_non_zero_cost_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["cost_mode"] = "paid-api"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "0-local"):
                load_first_candidate(manifest)

    def test_v6_manifest_requires_unified_scene_grammar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["composition_grammar"] = "legacy_collage"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "single_continuous_scene"):
                load_first_candidate(manifest)

    def test_v6_manifest_forbids_generated_exact_sport_geometry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["generated_sport_geometry_allowed"] = True
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "v6 editorial policy mismatch"):
                load_first_candidate(manifest)

    def test_v6_manifest_forbids_pitch_replacement_regression(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["hybrid_surface_replacement_required"] = True
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "v6 editorial policy mismatch"):
                load_first_candidate(manifest)

    def test_v6_manifest_forbids_generated_branding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["generated_branding_allowed"] = True
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "v6 editorial policy mismatch"):
                load_first_candidate(manifest)

    def test_v6_manifest_requires_dynamic_deterministic_branding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["brand_composition_policy"] = "generated_wordmark"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "v6 editorial policy mismatch"):
                load_first_candidate(manifest)

    def test_v6_manifest_requires_story_first_visual_priority(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self._build(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["visual_priority"] = "sport_surface_before_story"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "v6 editorial policy mismatch"):
                load_first_candidate(manifest)

    def test_prepare_creates_exactly_one_durable_smoke_job(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = load_first_candidate(self._build(root))
            store = FilesystemGenerationJobStore(root / "queue")
            first = prepare_smoke_job(store=store, candidate=candidate)
            second = prepare_smoke_job(store=store, candidate=candidate)
            self.assertTrue(first.created)
            self.assertFalse(second.created)
            self.assertTrue(second.reusable_existing)
            self.assertEqual(first.job.job_id, DEFAULT_SMOKE_JOB_ID)
            self.assertEqual(first.job.state, GenerationJobState.QUEUED)
            self.assertEqual(store.snapshot().pending, 1)
            self.assertEqual(first.job.metadata["cost_mode"], "$0-local")
            self.assertEqual(first.job.metadata["smoke_role"], "golden-editorial-base")

    def test_existing_job_with_different_locked_identity_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self._build(root)
            candidate = load_first_candidate(manifest)
            store = FilesystemGenerationJobStore(root / "queue")
            prepared = prepare_smoke_job(store=store, candidate=candidate)
            stored = store.get(prepared.job.job_id)
            self.assertIsNotNone(stored)
            mutated = stored.__class__(
                **{
                    **{name: getattr(stored, name) for name in stored.__dataclass_fields__},
                    "payload_sha256": "f" * 64,
                }
            )
            store.save(mutated)
            with self.assertRaisesRegex(ValueError, "identity"):
                prepare_smoke_job(store=store, candidate=candidate)

    def test_terminal_failure_is_not_silently_requeued(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = load_first_candidate(self._build(root))
            store = FilesystemGenerationJobStore(root / "queue")
            prepared = prepare_smoke_job(store=store, candidate=candidate)
            job = prepared.job.transition(
                GenerationJobState.LEASED,
                lease_owner="worker",
                lease_expires_at=prepared.job.updated_at,
            )
            job = job.transition(
                GenerationJobState.TERMINAL_FAILED,
                failure_code="hard_failure",
                failure_detail="do not retry",
            )
            store.save(job)
            with self.assertRaisesRegex(RuntimeError, "terminal_failed"):
                prepare_smoke_job(store=store, candidate=candidate)

    def test_status_payload_is_explicit_about_job_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = load_first_candidate(self._build(root))
            store = FilesystemGenerationJobStore(root / "queue")
            prepared = prepare_smoke_job(store=store, candidate=candidate)
            payload = smoke_status_payload(prepared)
            self.assertEqual(payload["status"], "SMOKE_JOB_PREPARED")
            self.assertEqual(payload["request_id"], candidate.request_id)
            self.assertEqual(payload["payload_sha256"], candidate.payload_sha256)
            self.assertEqual(payload["cost_mode"], "$0-local")


if __name__ == "__main__":
    unittest.main()
