from __future__ import annotations

import unittest

from tools.phase18_probe_first_golden_pre_gpu import inspect


HEAD = "a" * 40


def source_report(*, ready=True, network=False, generation=False, publication=False, seeds=False):
    return {
        "source_identity_ready": ready,
        "network_download_authorized": network,
        "generation_authorized": generation,
        "publication_ready": publication,
        "seeds_2_to_4_authorized": seeds,
    }


def execution_report(*, ready=True, network=False, generation=False, publication=False, seeds=False):
    return {
        "ready_for_authoritative_golden_preflight": ready,
        "network_download_authorized": network,
        "generation_authorized": generation,
        "publication_ready": publication,
        "seeds_2_to_4_authorized": seeds,
    }


class FirstGoldenPreGpuProbeTests(unittest.TestCase):
    def test_ready_requires_source_then_execution_and_keeps_authority_closed(self):
        calls: list[str] = []

        def source_inspector(*, expected_commit):
            calls.append(f"source:{expected_commit}")
            return source_report()

        def execution_inspector():
            calls.append("execution")
            return execution_report()

        payload = inspect(
            expected_commit=HEAD,
            source_inspector=source_inspector,
            execution_inspector=execution_inspector,
        )
        self.assertEqual(calls, [f"source:{HEAD}", "execution"])
        self.assertTrue(payload["source_identity_ready"])
        self.assertTrue(payload["execution_environment_evaluated"])
        self.assertTrue(payload["ready_for_authoritative_golden_preflight"])
        self.assertEqual(payload["blockers"], [])
        self.assertFalse(payload["authoritative_gate"])
        self.assertFalse(payload["network_download_authorized"])
        self.assertFalse(payload["generation_authorized"])
        self.assertFalse(payload["publication_ready"])
        self.assertFalse(payload["seeds_2_to_4_authorized"])

    def test_source_failure_prevents_execution_probe(self):
        calls: list[str] = []

        def source_inspector(*, expected_commit):
            calls.append("source")
            return source_report(ready=False)

        def execution_inspector():
            calls.append("execution")
            return execution_report()

        payload = inspect(
            expected_commit=HEAD,
            source_inspector=source_inspector,
            execution_inspector=execution_inspector,
        )
        self.assertEqual(calls, ["source"])
        self.assertFalse(payload["execution_environment_evaluated"])
        self.assertIsNone(payload["execution_environment"])
        self.assertIn("FIRST_GOLDEN_SOURCE_IDENTITY_NOT_READY", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_execution_failure_is_preserved_as_pre_gpu_blocker(self):
        payload = inspect(
            expected_commit=HEAD,
            source_inspector=lambda **_: source_report(),
            execution_inspector=lambda: execution_report(ready=False),
        )
        self.assertIn("FIRST_GOLDEN_EXECUTION_ENVIRONMENT_NOT_READY", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_invalid_expected_commit_fails_closed_without_execution(self):
        calls: list[str] = []

        def execution_inspector():
            calls.append("execution")
            return execution_report()

        payload = inspect(
            expected_commit="phase18/story-intelligence",
            source_inspector=lambda **_: source_report(),
            execution_inspector=execution_inspector,
        )
        self.assertEqual(calls, [])
        self.assertIn("EXPECTED_COMMIT_INVALID", payload["blockers"])
        self.assertFalse(payload["execution_environment_evaluated"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_nested_authority_drift_is_rejected(self):
        payload = inspect(
            expected_commit=HEAD,
            source_inspector=lambda **_: source_report(),
            execution_inspector=lambda: execution_report(generation=True),
        )
        self.assertIn("EXECUTION_GENERATION_AUTHORITY_DRIFT", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])

    def test_source_network_authority_drift_blocks_before_execution(self):
        payload = inspect(
            expected_commit=HEAD,
            source_inspector=lambda **_: source_report(network=True),
            execution_inspector=lambda: execution_report(),
        )
        self.assertIn("SOURCE_NETWORK_AUTHORITY_DRIFT", payload["blockers"])
        self.assertFalse(payload["ready_for_authoritative_golden_preflight"])


if __name__ == "__main__":
    unittest.main()
