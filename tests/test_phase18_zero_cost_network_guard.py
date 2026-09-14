from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest

from engine.intelligence import zero_cost_network_guard as guard

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "phase18-first-genuine-golden-v6-fresh.yml"


class ZeroCostNetworkGuardTests(unittest.TestCase):
    def test_guard_contract_requires_all_existing_offline_assertions(self) -> None:
        good = {
            "PUL7SAR_PHASE18_COST_MODE": "$0-local",
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
        }
        self.assertTrue(guard.contract_requests_guard(good))
        for key in tuple(good):
            drifted = dict(good)
            drifted.pop(key)
            self.assertFalse(guard.contract_requests_guard(drifted), key)

    def test_policy_allows_only_loopback_and_unix_destinations(self) -> None:
        import socket

        self.assertTrue(guard._address_is_local(("127.0.0.1", 1), socket.AF_INET))
        self.assertTrue(guard._address_is_local(("::1", 1, 0, 0), socket.AF_INET6))
        self.assertTrue(guard._address_is_local("/tmp/pul7sar.sock", socket.AF_UNIX))
        self.assertFalse(guard._address_is_local(("8.8.8.8", 53), socket.AF_INET))
        self.assertFalse(guard._address_is_local(("example.com", 443), socket.AF_INET))

    def test_sitecustomize_blocks_external_socket_before_network_io(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "PYTHONPATH": str(ROOT),
                "PUL7SAR_PHASE18_COST_MODE": "$0-local",
                "HF_HUB_OFFLINE": "1",
                "TRANSFORMERS_OFFLINE": "1",
            }
        )
        code = r'''
import os
import socket
assert os.environ.get("PUL7SAR_PHASE18_NETWORK_GUARD_ACTIVE") == "1"
try:
    socket.create_connection(("example.com", 443), timeout=0.01)
except PermissionError as exc:
    assert "PUL7SAR_PHASE18_ZERO_COST_NETWORK_BLOCKED" in str(exc)
else:
    raise SystemExit("external socket was not blocked")
'''
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

    def test_golden_workflow_guarantees_sitecustomize_activation_contract(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("PYTHONPATH: .", text)
        self.assertIn("PUL7SAR_PHASE18_COST_MODE: $0-local", text)
        self.assertIn('HF_HUB_OFFLINE: "1"', text)
        self.assertIn('TRANSFORMERS_OFFLINE: "1"', text)
        self.assertIn("python tools/phase18_run_first_genuine_golden_v6_canonical_fresh.py", text)


if __name__ == "__main__":
    unittest.main()
