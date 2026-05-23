"""Pytest conftest for simulations test suite.

Registers a Hypothesis profile that suppresses the ``differing_executors``
health check for mutation-testing runs. Activated by setting environment
variable ``HYPOTHESIS_PROFILE=mutation_safe`` (or HYPOTHESIS_MUTATION=1).

The differing_executors check is a correctness-flake warning that fires
spuriously when mutmut 3.x re-runs the same test under different worker
processes. It is unrelated to the property under test.
"""

from __future__ import annotations

import os

from hypothesis import HealthCheck, settings

settings.register_profile(
    "mutation_safe",
    suppress_health_check=[HealthCheck.differing_executors, HealthCheck.too_slow],
    deadline=None,
)

_in_mutmut = "mutants" in os.path.abspath(os.getcwd()).split(os.sep)
if (
    _in_mutmut
    or os.environ.get("HYPOTHESIS_MUTATION")
    or os.environ.get("HYPOTHESIS_PROFILE") == "mutation_safe"
):
    settings.load_profile("mutation_safe")
