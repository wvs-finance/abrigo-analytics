"""Pytest conftest for the E10 GSPS test suite (plan v0.2 Phase 0).

Registers Hypothesis profiles compatible with the SIM-INFRA-0 reference
(``simulations/tests/conftest.py``) so mutation-testing runs (mutmut) do
not flake on ``differing_executors``. Profile is activated via:

    HYPOTHESIS_PROFILE=mutation_safe  pytest simulations/e10_gsps/tests
"""

from __future__ import annotations

import os

from hypothesis import HealthCheck, settings

settings.register_profile(
    "mutation_safe",
    suppress_health_check=[
        HealthCheck.differing_executors,
        HealthCheck.too_slow,
    ],
    deadline=None,
)

settings.register_profile(
    "e10_default",
    deadline=None,
    max_examples=50,
)

_in_mutmut = "mutants" in os.path.abspath(os.getcwd()).split(os.sep)
if (
    _in_mutmut
    or os.environ.get("HYPOTHESIS_MUTATION")
    or os.environ.get("HYPOTHESIS_PROFILE") == "mutation_safe"
):
    settings.load_profile("mutation_safe")
else:
    settings.load_profile("e10_default")
