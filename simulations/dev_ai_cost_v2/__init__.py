"""dev_ai_cost_v2 sub-package — AI-cost factor model (spec v0.2.1) + continuous-stream simulation (spec R6 v0.1.3).

Three-tier discipline per functional-python skill:
- types.py: frozen-dc value containers.
- anthropic_pricing.py, panel_builder.py, nhpp_calibration.py, etc.: modules tier (pure Callables).
- jsonl_io.py: utils tier (IO Boundary; mutable state lives ONLY here).
"""
