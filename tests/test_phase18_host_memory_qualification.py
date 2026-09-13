import unittest

from engine.intelligence.host_memory_qualification import HostMemoryQualificationProbe


class HostMemoryQualificationTests(unittest.TestCase):
    @staticmethod
    def _meminfo(*, total_gib: int, available_gib: int, swap_total_gib: int = 0, swap_free_gib: int = 0) -> str:
        kib = 1024 * 1024
        return "\n".join(
            (
                f"MemTotal: {total_gib * kib} kB",
                f"MemAvailable: {available_gib * kib} kB",
                f"SwapTotal: {swap_total_gib * kib} kB",
                f"SwapFree: {swap_free_gib * kib} kB",
            )
        )

    def test_ready_when_live_available_ram_meets_floor(self):
        report = HostMemoryQualificationProbe(
            minimum_available_ram_gb=10.0,
            meminfo_reader=lambda: self._meminfo(total_gib=24, available_gib=14, swap_total_gib=4, swap_free_gib=4),
        ).inspect()
        self.assertTrue(report.ready)
        self.assertAlmostEqual(report.total_ram_gb, 24.0)
        self.assertAlmostEqual(report.available_ram_gb, 14.0)
        self.assertAlmostEqual(report.used_ram_gb, 10.0)
        self.assertEqual(report.measurement_source, "/proc/meminfo")
        self.assertFalse(report.generation_authorized)
        self.assertFalse(report.publication_ready)

    def test_low_available_ram_fails_closed_even_when_total_ram_is_large(self):
        report = HostMemoryQualificationProbe(
            minimum_available_ram_gb=10.0,
            meminfo_reader=lambda: self._meminfo(total_gib=32, available_gib=6),
        ).inspect()
        self.assertFalse(report.ready)
        self.assertIn("available_system_ram_below_first_golden_floor", report.reasons)

    def test_missing_memavailable_is_not_guessed(self):
        report = HostMemoryQualificationProbe(
            minimum_available_ram_gb=10.0,
            meminfo_reader=lambda: "MemTotal: 25165824 kB\n",
        ).inspect()
        self.assertFalse(report.ready)
        self.assertIsNone(report.available_ram_gb)
        self.assertIn("available_system_ram_unproven", report.reasons)

    def test_measurement_failure_is_fail_closed(self):
        def fail():
            raise OSError("unavailable")

        report = HostMemoryQualificationProbe(
            minimum_available_ram_gb=10.0,
            meminfo_reader=fail,
        ).inspect()
        self.assertFalse(report.ready)
        self.assertIn("host_memory_measurement_unavailable", report.reasons)
        self.assertIn("total_system_ram_unproven", report.reasons)
        self.assertIn("available_system_ram_unproven", report.reasons)

    def test_non_positive_floor_is_rejected(self):
        with self.assertRaises(ValueError):
            HostMemoryQualificationProbe(minimum_available_ram_gb=0)


if __name__ == "__main__":
    unittest.main()
