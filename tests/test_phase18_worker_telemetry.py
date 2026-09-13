import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from engine.intelligence.worker_telemetry import (
    FilesystemWorkerTelemetryStore,
    GenerationCapacityEstimator,
    GenerationPerformanceSample,
    WorkerHeartbeat,
)


class WorkerTelemetryTests(unittest.TestCase):
    def test_heartbeat_round_trip_preserves_gpu_and_queue_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemWorkerTelemetryStore(tmp)
            now = datetime.now(timezone.utc)
            heartbeat = WorkerHeartbeat(
                worker_id="gpu-1",
                observed_at=now,
                status="idle",
                gpu_name="Example GPU",
                vram_gb=24.0,
                bf16_supported=True,
                queue_counts={"queued": 3, "running": 1},
                metadata={"cost_mode": "$0-local"},
            )
            store.write_heartbeat(heartbeat)
            restored = store.read_heartbeat("gpu-1")
            self.assertIsNotNone(restored)
            self.assertEqual(restored.worker_id, "gpu-1")
            self.assertEqual(restored.gpu_name, "Example GPU")
            self.assertEqual(restored.queue_counts["queued"], 3)
            self.assertEqual(restored.metadata["cost_mode"], "$0-local")

    def test_sample_round_trip_is_append_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FilesystemWorkerTelemetryStore(tmp)
            start = datetime.now(timezone.utc)
            sample = GenerationPerformanceSample(
                worker_id="gpu-1",
                job_id="job-1",
                request_id="request-1",
                started_at=start,
                finished_at=start + timedelta(seconds=30),
                duration_seconds=30.0,
                outcome="succeeded",
                result_path="output/proof.png",
                gpu_name="Example GPU",
                vram_gb=24.0,
            )
            path = store.record_sample(sample)
            self.assertTrue(path.exists())
            restored = list(store.iter_samples())
            self.assertEqual(len(restored), 1)
            self.assertTrue(restored[0].succeeded)
            self.assertEqual(restored[0].duration_seconds, 30.0)

    def test_capacity_estimator_refuses_to_invent_throughput_without_success(self):
        start = datetime.now(timezone.utc)
        failed = GenerationPerformanceSample(
            worker_id="gpu-1",
            job_id="job-1",
            request_id="request-1",
            started_at=start,
            finished_at=start + timedelta(seconds=5),
            duration_seconds=5.0,
            outcome="terminal_failed",
        )
        report = GenerationCapacityEstimator().estimate([failed])
        self.assertEqual(report.confidence, "unproven")
        self.assertIsNone(report.estimated_images_per_day)
        self.assertIn("no real successful GPU generation", report.blocker)

    def test_capacity_estimator_uses_only_real_successful_samples(self):
        start = datetime.now(timezone.utc)
        samples = []
        for index, duration in enumerate((20.0, 30.0, 40.0), start=1):
            samples.append(GenerationPerformanceSample(
                worker_id="gpu-1",
                job_id=f"job-{index}",
                request_id=f"request-{index}",
                started_at=start,
                finished_at=start + timedelta(seconds=duration),
                duration_seconds=duration,
                outcome="succeeded",
                result_path=f"output/{index}.png",
            ))
        samples.append(GenerationPerformanceSample(
            worker_id="gpu-1",
            job_id="job-failed",
            request_id="request-failed",
            started_at=start,
            finished_at=start + timedelta(seconds=1),
            duration_seconds=1.0,
            outcome="terminal_failed",
        ))
        report = GenerationCapacityEstimator().estimate(samples, worker_count=1, utilization=0.5)
        self.assertEqual(report.successful_samples, 3)
        self.assertEqual(report.failed_samples, 1)
        self.assertEqual(report.median_seconds_per_success, 30.0)
        self.assertAlmostEqual(report.estimated_images_per_hour, 60.0)
        self.assertAlmostEqual(report.estimated_images_per_day, 1440.0)
        self.assertEqual(report.confidence, "measured-low")

    def test_invalid_utilization_is_rejected(self):
        with self.assertRaises(ValueError):
            GenerationCapacityEstimator().estimate([], utilization=0)

    def test_unsafe_worker_id_is_rejected(self):
        with self.assertRaises(ValueError):
            WorkerHeartbeat(
                worker_id="../escape",
                observed_at=datetime.now(timezone.utc),
                status="idle",
                gpu_name=None,
                vram_gb=None,
                bf16_supported=False,
            )


if __name__ == "__main__":
    unittest.main()
