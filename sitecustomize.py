"""Repository startup hook for strict Phase 18 zero-cost network isolation.

Python imports ``sitecustomize`` automatically when this repository is present on
``PYTHONPATH``. The Golden workflow already exports ``PYTHONPATH=.``. The guard
itself activates only when the existing $0-local + Hugging Face offline contract
is fully asserted, so ordinary development and CI remain unaffected.
"""
from engine.intelligence.zero_cost_network_guard import install_zero_cost_network_guard

install_zero_cost_network_guard()
