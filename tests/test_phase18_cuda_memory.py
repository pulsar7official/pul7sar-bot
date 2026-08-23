import unittest

from engine.intelligence.cuda_memory import CudaPeakMemoryTracker


class _FakeCuda:
    def __init__(self, *, available=True):
        self.available = available
        self.reset_calls = []

    def is_available(self):
        return self.available

    def current_device(self):
        return 0

    def reset_peak_memory_stats(self, device):
        self.reset_calls.append(device)

    def max_memory_allocated(self, device):
        return 8 * 1024 ** 3

    def max_memory_reserved(self, device):
        return 10 * 1024 ** 3

    def memory_allocated(self, device):
        return 6 * 1024 ** 3

    def memory_reserved(self, device):
        return 7 * 1024 ** 3


class _FakeTorch:
    def __init__(self, *, available=True):
        self.cuda = _FakeCuda(available=available)


class CudaMemoryTelemetryTests(unittest.TestCase):
    def test_reset_and_capture_realistic_counters(self):
        torch = _FakeTorch()
        tracker = CudaPeakMemoryTracker(torch)
        self.assertTrue(tracker.reset())
        self.assertEqual(torch.cuda.reset_calls, [0])

        sample = tracker.capture()
        self.assertTrue(sample.available)
        self.assertEqual(sample.device_index, 0)
        self.assertEqual(sample.peak_allocated_gb, 8.0)
        self.assertEqual(sample.peak_reserved_gb, 10.0)
        self.assertEqual(sample.current_allocated_gb, 6.0)
        self.assertEqual(sample.current_reserved_gb, 7.0)
        self.assertIsNone(sample.blocker)

    def test_unavailable_cuda_returns_truthful_unavailable_snapshot(self):
        tracker = CudaPeakMemoryTracker(_FakeTorch(available=False))
        self.assertFalse(tracker.reset())
        sample = tracker.capture()
        self.assertFalse(sample.available)
        self.assertIsNone(sample.peak_allocated_gb)
        self.assertIn("CUDA is unavailable", sample.blocker)

    def test_capture_failure_does_not_invent_measurements(self):
        class BrokenCuda(_FakeCuda):
            def max_memory_allocated(self, device):
                raise RuntimeError("driver counter unavailable")

        class BrokenTorch:
            cuda = BrokenCuda()

        sample = CudaPeakMemoryTracker(BrokenTorch()).capture()
        self.assertFalse(sample.available)
        self.assertIsNone(sample.peak_reserved_gb)
        self.assertIn("driver counter unavailable", sample.blocker)


if __name__ == "__main__":
    unittest.main()
