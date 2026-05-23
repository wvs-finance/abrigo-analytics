# AI-Cost Factor Model (v0.2.1) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Spec:** `docs/specs/2026-05-16-ai-cost-factor-model-design.md` (v0.2.1 — all three closure-only reviewers CLOSE_ALL)

**Goal:** Quantify the COP-denominated cost-burden risk that a non-subscribed LATAM developer would face for AI-tooling usage equivalent to the pilot subject's pattern, and isolate the share attributable to COP/USD volatility, via an R5 descriptive primary + R4-S3-COP/R4-S3-USD auxiliary structure.

**Architecture:** New sub-package `simulations/dev_ai_cost_v2/` mirroring `simulations/stochastic_fx/` and `simulations/saas_builder/` tier discipline (types / modules / utils). Three-tier import rule enforced. Single orchestration point at `scripts/build_notional_cost_panel.py`. Five notebooks at `notebooks/dev_ai_cost_v2/`. Banrep daily TRM is a prerequisite work item.

**Tech Stack:** Python 3.13, polars, pydantic (`extra="forbid"`), Decimal, hypothesis, statsmodels (HAC OLS), Politis–Romano stationary bootstrap. LiteLLM price table pinned at commit SHA `e58a561caa21169fb02174148444c08509ce7028`.

---

## Spec-section coverage map

| Spec § | Tasks |
|---|---|
| §0.1 CORRECTIONS-N (own-parser primary) | Task 4, 5 |
| §0.1 CORRECTIONS-O (LiteLLM keys + SHA) | Task 6 |
| §0.1 CORRECTIONS-P (stationary bootstrap) | Task 12 |
| §0.1 CORRECTIONS-Q (conservative covariance) | Task 12 |
| §0.1 CORRECTIONS-R (R5 Role A) | Task 12 |
| §0.1 CORRECTIONS-S (R4-S3 COP+USD split) | Task 13, 14 |
| §0.1 CORRECTIONS-T (CI threshold 0.15) | Task 12 |
| §0.1 CORRECTIONS-U (power-HALT anticipated) | Task 3, 11 |
| §0.1 CORRECTIONS-V (Sequence, ts, is_error, UTC half-open, request_id) | Task 5, 6, 7 |
| §0.1 CORRECTIONS-W (file paths) | Task 1, 2, 8 |
| §1 purpose / proxy framing | Notebook preambles in Task 11–15 |
| §2.1 R5 primary | Task 12 |
| §2.2.A R4-S3-COP consistency | Task 13 |
| §2.2.B R4-S3-USD behavioral | Task 14 |
| §2.3 N-floor | Task 11 |
| §2.4 sensitivity arms (diagnostic) | Task 15 |
| §3.1–3.5 data architecture & contracts | Tasks 4–8 |
| §3.4 Banrep daily TRM prerequisite | Task 1 |
| §4 notebook structure | Tasks 11–15 |
| §5.2 LiteLLM SHA pin | Task 6 |
| §5.4 DATA_PROVENANCE | Task 9, 10 |
| §6 threats / Hypothesis property tests | Tasks 5, 6, 7 (property tests inline) |
| §7 anti-fishing invariants | Tasks 11, 13, 14 |
| §8 workflow / agent assignment | Each task lists owner + audit-pass chain |
| §11 file-existence list | Task 1, 2 |

---

## File structure (locked before task decomposition)

**New / extended files:**

- `scripts/fetch_banrep.py` — **extend** (preserve monthly endpoint; add daily). Emits `data/raw/banrep_trm_daily.parquet`.
- `scripts/build_notional_cost_panel.py` — **new** Tier-3 CLI; single orchestration point.
- `simulations/dev_ai_cost_v2/__init__.py` — **new** sub-package marker.
- `simulations/dev_ai_cost_v2/_errors.py` — **new** sub-package errors module. Defines `JSONLSchemaError(SchemaMismatchError)` (parent imported from `simulations.utils.errors`).
- `simulations/dev_ai_cost_v2/types.py` — **new** types tier. Frozen dataclasses: `MessageRecord`, `TokensByCategory`, `DailyNotionalPanel`.
- `simulations/dev_ai_cost_v2/jsonl_io.py` — **new** utils-tier IO Boundary class `JSONLReader`. Reads `~/.claude/projects/**/*.jsonl` directly. Pydantic `extra="forbid"`. Returns materialized `Sequence[MessageRecord]`. UTC half-open `[00:00:00, 24:00:00)`. Warns on `request_id=None`.
- `simulations/dev_ai_cost_v2/anthropic_pricing.py` — **new** modules-tier. Frozen-dc `PricingTable` with `from_litellm_sha(sha)` constructor. `__call__(model, ts, toks)` — `ts` used for time-varying price-step lookup. Exact Decimal.
- `simulations/dev_ai_cost_v2/panel_builder.py` — **new** modules-tier. Pure `build_daily_panel(records, pricing, trm_panel) -> DailyNotionalPanel`.
- `simulations/tests/strategies.py` — **extend** with Hypothesis strategies for `dev_ai_cost_v2` types.
- `simulations/tests/test_dev_ai_cost_v2_types.py` — **new** types tier tests.
- `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py` — **new** parser tests + property tests.
- `simulations/tests/test_dev_ai_cost_v2_pricing.py` — **new** pricing tests + LiteLLM key existence assertions.
- `simulations/tests/test_dev_ai_cost_v2_panel_builder.py` — **new** panel-builder property tests (forward-fill-forbidden, double-iteration equivalence, reconciliation).
- `simulations/tests/test_fetch_banrep_daily.py` — **new** fetcher tests.
- `notebooks/dev_ai_cost_v2/01_data_eda.ipynb` — **new**, trio-disciplined, reconciliation cell, power-HALT checkpoint.
- `notebooks/dev_ai_cost_v2/02_r5_descriptive.ipynb` — **new**, R5 primary outputs with stationary-bootstrap CIs.
- `notebooks/dev_ai_cost_v2/03_r4s3_cop_consistency.ipynb` — **new**, R4-S3-COP consistency check (NOT novel).
- `notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb` — **new**, R4-S3-USD behavioral test.
- `notebooks/dev_ai_cost_v2/05_sensitivity.ipynb` — **new**, four diagnostic arms (no verdict authority).
- `notebooks/dev_ai_cost_v2/dispositions/power_halt_template.md` — **new**, pre-enumerates user pivots (anticipated power HALT per CORRECTIONS-U).
- `notebooks/dev_ai_cost_v2/data/DATA_PROVENANCE.md` — **new**, provenance file.
- `data/raw/banrep_trm_daily.parquet` — **emitted by Task 1**.
- `data/panels/notional_cost_panel.parquet` — **emitted by Task 10** (dir created at first run).

**Tier-import rule (enforced):** `types/` ↛ `modules/`, `utils/`; `modules/` ↛ `utils/`. Only `jsonl_io.py` performs IO. The CLI script `scripts/build_notional_cost_panel.py` is the single orchestration point importing across tiers.

---

## Task ordering and dependencies

```
                                                                                 
   Task 1  ────────────────┐                                                     
   (Banrep daily fetcher)  │                                                     
                           │                                                     
   Task 2 ──┐              │                                                     
   (sub-pkg │              │                                                     
   scaffold)│              │                                                     
            ▼              │                                                     
   Task 3 (disposition memo template)                                            
            │              │                                                     
            ▼              │                                                     
   Task 4 ──► Task 5 ──► Task 6 ──► Task 7 ──► Task 8 (CLI) ──► Task 9 (impl    
   (_errors)  (types)    (jsonl_io) (pricing/                    review panel)  
                                      panel_builder)                  │         
                                                            ┌─────────┘         
                                                            ▼                   
                                                  Task 10 (run CLI / panel      
                                                  build / DATA_PROVENANCE)      
                                                            │                   
                                                            ▼                   
                              Task 11 (notebook 01) ───► [HALT if power<0.50]   
                                                            │                   
                                                            ▼                   
                              Task 12 (notebook 02 — R5)                        
                                                            │                   
                                                            ▼                   
                              Task 13 (notebook 03 — R4-S3-COP consistency)     
                                                            │                   
                                                            ▼                   
                              Task 14 (notebook 04 — R4-S3-USD behavioral)      
                                                            │                   
                                                            ▼                   
                              Task 15 (notebook 05 — sensitivity, diagnostic)   
                                                            │                   
                                                            ▼                   
                              Task 16 (Delphi audit-econ panel — pre-verdict)   
                                                            │                   
                                                            ▼                   
                              Task 17 (verdict memo + write-up)                 
```

---

## Task 1: Extend `scripts/fetch_banrep.py` for daily TRM (PREREQUISITE)

**Owner:** Data Engineer
**Audit-pass chain:** `try-except` + `contract-docstrings` + `hypothesis-tests`
**Spec ref:** §0.1 CORRECTIONS-E, §3.4
**Depends on:** none

**Files:**
- Modify: `scripts/fetch_banrep.py`
- Create: `simulations/tests/test_fetch_banrep_daily.py`
- Emits: `data/raw/banrep_trm_daily.parquet`

**Exit criteria:**
- Existing monthly endpoint preserved (regression test for monthly path).
- New daily endpoint emits parquet with schema `(date: Date, trm_cop_per_usd: Decimal)`.
- Provenance metadata recorded (endpoint URL, fetch timestamp, sha256 of payload).
- Hypothesis strategy on the response normalizer rejects malformed rows.
- `try` blocks cover ONLY the HTTP call and ONLY the parse step (per `try-except` skill).

**Steps:**

- [ ] **Step 1.1: Confirm Banrep daily TRM endpoint URL**

Locate the Banrep daily TRM endpoint as used by the prior dev-AI iteration. Cross-reference against `scratch/simple-beta-pair-d/data/scripts/` per the current stub fetcher's comment. Document URL + provenance in the script docstring.

- [ ] **Step 1.2: Write the failing test for daily endpoint emission**

```python
# simulations/tests/test_fetch_banrep_daily.py
from pathlib import Path
from decimal import Decimal
import polars as pl
import pytest

from scripts.fetch_banrep import fetch_daily_trm, REPO_ROOT  # to be added

def test_daily_trm_emits_parquet_with_expected_schema(tmp_path: Path) -> None:
    out = tmp_path / "banrep_trm_daily.parquet"
    fetch_daily_trm(out_path=out, since="2024-01-01", until="2024-01-31")
    df = pl.read_parquet(out)
    assert df.columns == ["date", "trm_cop_per_usd"]
    assert df.schema["date"] == pl.Date
    # trm stored as Decimal-typed string or Float64; the contract is exact
    # decimal arithmetic downstream — pin to string here, cast in caller.
    assert df.height >= 15  # roughly half-month of weekdays minimum
```

Run: `uv run pytest simulations/tests/test_fetch_banrep_daily.py -v`
Expected: FAIL with `ImportError` / `AttributeError`.

- [ ] **Step 1.3: Implement `fetch_daily_trm`**

Add `fetch_daily_trm(out_path: Path, since: str, until: str) -> None` to `scripts/fetch_banrep.py`. Narrow `try` to the HTTP call only; parse step in a separate `try`. Write parquet with declared schema. Preserve the existing `main()` printout for monthly.

- [ ] **Step 1.4: Run test to verify it passes**

Run: `uv run pytest simulations/tests/test_fetch_banrep_daily.py -v`
Expected: PASS.

- [ ] **Step 1.5: Add Hypothesis property test on the row normalizer**

If normalization is factored out (e.g., `_normalize_row(raw: dict) -> tuple[date, Decimal]`), add a Hypothesis strategy producing well-formed and malformed rows; property: well-formed → tuple; malformed → ValueError.

- [ ] **Step 1.6: Add `contract-docstrings` pass**

Apply `contract-docstrings` skill to `fetch_daily_trm`: document invariants (since ≤ until, ISO format), errors raised on violation, errors raised from external state (network, Banrep schema drift), silenced errors (none).

- [ ] **Step 1.7: Run the full simulations test suite for regression**

Run: `uv run pytest simulations/tests/ -x`
Expected: PASS.

- [ ] **Step 1.8: Commit**

```bash
git add scripts/fetch_banrep.py simulations/tests/test_fetch_banrep_daily.py
git commit -m "feat(fetch_banrep): add daily TRM endpoint (prerequisite for dev_ai_cost_v2 spec §3.4)"
```

---

## Task 2: Create sub-package scaffold and `_errors.py`

**Owner:** Backend Architect
**Audit-pass chain:** `functional-python` discipline check
**Spec ref:** §0.1 CORRECTIONS-W, §3.5
**Depends on:** none

**Files:**
- Create: `simulations/dev_ai_cost_v2/__init__.py`
- Create: `simulations/dev_ai_cost_v2/_errors.py`

**Exit criteria:**
- Sub-package importable: `from simulations.dev_ai_cost_v2 import _errors` succeeds.
- `JSONLSchemaError(SchemaMismatchError)` defined; `SchemaMismatchError` imported from `simulations.utils.errors`.
- `__all__` declared; matches `simulations/stochastic_fx/_errors.py` style.

**Steps:**

- [ ] **Step 2.1: Create `__init__.py` (empty marker)**

```python
"""dev_ai_cost_v2 sub-package — AI-cost factor model (spec v0.2.1).

Three-tier discipline per functional-python skill:
- types.py: frozen-dc value containers.
- anthropic_pricing.py, panel_builder.py: modules tier (pure Callables).
- jsonl_io.py: utils tier (IO Boundary; mutable state lives ONLY here).
"""
```

- [ ] **Step 2.2: Create `_errors.py`**

```python
"""dev_ai_cost_v2 typed errors.

Per functional-python skill: only Exception subclassing is admitted as
class-inheritance outside of Protocols. Parent spec
``docs/specs/2026-05-16-ai-cost-factor-model-design.md`` v0.2.1 §3.5
defines JSONLSchemaError as the schema-drift gate raised by
``simulations.dev_ai_cost_v2.jsonl_io.JSONLReader``.
"""
from __future__ import annotations

from simulations.utils.errors import SchemaMismatchError


class JSONLSchemaError(SchemaMismatchError):
    """Raised by ``JSONLReader`` when an Anthropic JSONL row violates the
    pinned Pydantic schema (``extra="forbid"`` or missing required field).

    Subclasses ``SchemaMismatchError`` (which subclasses ``ValueError``) so
    existing ``except ValueError`` / ``except SchemaMismatchError`` clauses
    continue to work, while letting callers narrow to JSONL-specific drift.
    """


__all__ = ["JSONLSchemaError"]
```

- [ ] **Step 2.3: Smoke-import test**

```python
# simulations/tests/test_dev_ai_cost_v2_errors.py
from simulations.dev_ai_cost_v2._errors import JSONLSchemaError
from simulations.utils.errors import SchemaMismatchError

def test_jsonl_schema_error_is_schema_mismatch_subclass():
    assert issubclass(JSONLSchemaError, SchemaMismatchError)
    assert issubclass(JSONLSchemaError, ValueError)
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_errors.py -v`
Expected: PASS.

- [ ] **Step 2.4: Commit**

```bash
git add simulations/dev_ai_cost_v2/__init__.py simulations/dev_ai_cost_v2/_errors.py simulations/tests/test_dev_ai_cost_v2_errors.py
git commit -m "feat(dev_ai_cost_v2): scaffold sub-package + JSONLSchemaError (spec v0.2.1 §3.5)"
```

---

## Task 3: Pre-create disposition memo template for anticipated power-HALT

**Owner:** orchestrator
**Audit-pass chain:** —
**Spec ref:** §0.1 CORRECTIONS-U, §2.2.B, §8
**Depends on:** Task 2 (directory `notebooks/dev_ai_cost_v2/` to be created here)

**Files:**
- Create: `notebooks/dev_ai_cost_v2/dispositions/power_halt_template.md`

**Exit criteria:**
- Template exists with three pre-enumerated user-pivot options.
- Each option has its own decision-citation block placeholder.
- HALT routing chain documented (`feedback_pathological_halt_anti_fishing_checkpoint`).

**Steps:**

- [ ] **Step 3.1: Create the directory tree**

```bash
mkdir -p notebooks/dev_ai_cost_v2/dispositions notebooks/dev_ai_cost_v2/data
```

- [ ] **Step 3.2: Write the template**

```markdown
# Power-HALT Disposition Memo Template

**Trigger:** `01_data_eda.ipynb` power-measurement HALT-checkpoint fired
(measured power < 0.50 at MDES = 0.40 residual-SD, current T).

**Anticipated per spec v0.2.1 CORRECTIONS-U** — Model QA's independent calc
at T=38 gave ~0.54–0.66 with HAC small-sample inflation, so this HALT is a
high-probability operational event.

## Pre-enumerated user pivots

### Option A: Expand T by waiting
- Pause iteration; resume when `max(weekday days observed)` ≥ <target T>.
- Re-run from Task 10 (panel build) at the new window.
- Decision-citation block: <fill at firing>

### Option B: Lower MDES to 0.30 residual-SD (documented downgrade)
- Update §2.2.B power threshold in a v0.2.2 patch.
- Disclose downgrade in §0 CORRECTIONS-X.
- Decision-citation block: <fill at firing>

### Option C: Accept lower-power result with explicit caveat in headline
- Proceed past HALT with documented power = <measured>.
- Add caveat banner to `04_r4s3_usd_behavioral.ipynb` headline cell.
- Decision-citation block: <fill at firing>

## HALT routing chain
Per `memory/feedback_pathological_halt_anti_fishing_checkpoint.md`:
1. HALT + this disposition memo
2. User-enumerated pivot (A/B/C)
3. CORRECTIONS block in spec
4. Post-hoc 3-way review before resuming

## Status
- [ ] HALT fired (date: ____)
- [ ] User pivot selected: ____
- [ ] Disposition committed
```

- [ ] **Step 3.3: Commit**

```bash
git add notebooks/dev_ai_cost_v2/dispositions/power_halt_template.md
git commit -m "docs(dev_ai_cost_v2): pre-create power-HALT disposition template (spec v0.2.1 CORRECTIONS-U)"
```

---

## Task 4: Define types tier (`types.py`)

**Owner:** Data Engineer (interface contract pre-agreed with Backend Architect)
**Audit-pass chain:** `tighten-types` + `contract-docstrings` + `hypothesis-tests`
**Spec ref:** §3.5
**Depends on:** Task 2

**Files:**
- Create: `simulations/dev_ai_cost_v2/types.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_types.py`
- Extend: `simulations/tests/strategies.py`

**Exit criteria:**
- Three frozen dataclasses defined with exact field types per spec §3.5.
- `__post_init__` validates non-negative token counts, valid timestamp, etc.
- `DailyNotionalPanel.__post_init__` Hypothesis-property-tested on schema (acknowledges inner-df mutability per §6 threat).
- No imports from `modules/` or `utils/` (tier-import rule).

**Steps:**

- [ ] **Step 4.1: Write the failing test for `MessageRecord`**

```python
# simulations/tests/test_dev_ai_cost_v2_types.py
from datetime import datetime, timezone
from decimal import Decimal
import pytest
from simulations.dev_ai_cost_v2.types import MessageRecord, TokensByCategory

def test_message_record_constructs_with_valid_fields():
    rec = MessageRecord(
        ts=datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc),
        model="claude-sonnet-4-5",
        input_tok=100, output_tok=50,
        cache_create_5m=0, cache_create_1h=0, cache_read=0,
        cost_usd_notional=Decimal("0.0015"),
        session_id="sess-1", request_id=None, is_error=False,
    )
    assert rec.model == "claude-sonnet-4-5"

def test_message_record_rejects_negative_tokens():
    with pytest.raises(ValueError):
        MessageRecord(
            ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
            model="x", input_tok=-1, output_tok=0,
            cache_create_5m=0, cache_create_1h=0, cache_read=0,
            cost_usd_notional=Decimal("0"),
            session_id="s", request_id=None, is_error=False,
        )

def test_message_record_rejects_naive_datetime():
    with pytest.raises(ValueError):
        MessageRecord(
            ts=datetime(2026, 5, 1, 12, 0),  # tz-naive
            model="x", input_tok=0, output_tok=0,
            cache_create_5m=0, cache_create_1h=0, cache_read=0,
            cost_usd_notional=Decimal("0"),
            session_id="s", request_id=None, is_error=False,
        )
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_types.py -v`
Expected: FAIL (`ImportError`).

- [ ] **Step 4.2: Implement `MessageRecord`**

```python
# simulations/dev_ai_cost_v2/types.py
"""Types tier for dev_ai_cost_v2 — frozen dataclass value containers.

Tier-import rule: types/ imports neither modules/ nor utils/.
Spec ref: docs/specs/2026-05-16-ai-cost-factor-model-design.md §3.5.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

import polars as pl


@dataclass(frozen=True, slots=True)
class MessageRecord:
    ts: datetime
    model: str
    input_tok: int
    output_tok: int
    cache_create_5m: int
    cache_create_1h: int
    cache_read: int
    cost_usd_notional: Decimal
    session_id: str
    request_id: str | None
    is_error: bool

    def __post_init__(self) -> None:
        if self.ts.tzinfo is None or self.ts.tzinfo.utcoffset(self.ts) != timezone.utc.utcoffset(self.ts):
            raise ValueError("MessageRecord.ts must be timezone-aware UTC")
        for fname in ("input_tok", "output_tok", "cache_create_5m",
                      "cache_create_1h", "cache_read"):
            v = getattr(self, fname)
            if v < 0:
                raise ValueError(f"MessageRecord.{fname} must be >= 0; got {v}")
        if self.cost_usd_notional < 0:
            raise ValueError("MessageRecord.cost_usd_notional must be >= 0")


@dataclass(frozen=True, slots=True)
class TokensByCategory:
    input: int
    output: int
    cache_create_5m: int
    cache_create_1h: int
    cache_read: int

    def __post_init__(self) -> None:
        for fname in ("input", "output", "cache_create_5m",
                      "cache_create_1h", "cache_read"):
            if getattr(self, fname) < 0:
                raise ValueError(f"TokensByCategory.{fname} must be >= 0")
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_types.py -v`
Expected: PASS for the three tests above.

- [ ] **Step 4.3: Add `DailyNotionalPanel` frozen-dc wrapper with schema validation**

Append to `types.py`:

```python
EXPECTED_PANEL_SCHEMA: dict[str, pl.DataType] = {
    "date_utc": pl.Date,
    "notional_cost_usd": pl.Decimal,
    "notional_cost_cop": pl.Decimal,
    "trm_cop_per_usd": pl.Decimal,
    "input_tok": pl.Int64,
    "output_tok": pl.Int64,
    "cache_create_5m": pl.Int64,
    "cache_create_1h": pl.Int64,
    "cache_read": pl.Int64,
    "n_messages": pl.Int64,
}


@dataclass(frozen=True, slots=True)
class DailyNotionalPanel:
    df: pl.DataFrame
    dropped_rows_count: int
    dropped_error_count: int

    def __post_init__(self) -> None:
        actual = dict(self.df.schema)
        missing = set(EXPECTED_PANEL_SCHEMA) - set(actual)
        extra = set(actual) - set(EXPECTED_PANEL_SCHEMA)
        if missing or extra:
            raise ValueError(
                f"DailyNotionalPanel schema drift: missing={missing}, extra={extra}"
            )
        for col, expected in EXPECTED_PANEL_SCHEMA.items():
            # Decimal precision/scale not enforced here (pinned in builder).
            if not isinstance(actual[col], type(expected)):
                raise ValueError(f"column {col}: expected {expected}, got {actual[col]}")
        if self.dropped_rows_count < 0 or self.dropped_error_count < 0:
            raise ValueError("dropped counts must be >= 0")
```

- [ ] **Step 4.4: Add Hypothesis strategies and property tests**

```python
# simulations/tests/strategies.py — append
from hypothesis import strategies as st
from datetime import datetime, timezone
from decimal import Decimal
from simulations.dev_ai_cost_v2.types import MessageRecord, TokensByCategory

message_records = st.builds(
    MessageRecord,
    ts=st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2027, 1, 1)).map(
        lambda d: d.replace(tzinfo=timezone.utc)
    ),
    model=st.sampled_from(["claude-sonnet-4-5", "claude-haiku-4-5", "claude-opus-4-7"]),
    input_tok=st.integers(min_value=0, max_value=10**6),
    output_tok=st.integers(min_value=0, max_value=10**6),
    cache_create_5m=st.integers(min_value=0, max_value=10**6),
    cache_create_1h=st.integers(min_value=0, max_value=10**6),
    cache_read=st.integers(min_value=0, max_value=10**6),
    cost_usd_notional=st.decimals(min_value=Decimal("0"), max_value=Decimal("1000"),
                                  allow_nan=False, allow_infinity=False, places=8),
    session_id=st.text(min_size=1, max_size=64),
    request_id=st.one_of(st.none(), st.text(min_size=1, max_size=64)),
    is_error=st.booleans(),
)
```

```python
# simulations/tests/test_dev_ai_cost_v2_types.py — append property test
from hypothesis import given
from simulations.tests.strategies import message_records

@given(rec=message_records)
def test_message_record_roundtrip_valid_records(rec: MessageRecord) -> None:
    # No exception from any well-formed strategy draw.
    assert rec.input_tok >= 0
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_types.py -v`
Expected: PASS.

- [ ] **Step 4.5: Apply `tighten-types` + `contract-docstrings` skills to `types.py`**

Verify: no missing attribute annotations; loose dicts replaced; docstrings document input invariants and `ValueError` raise conditions.

- [ ] **Step 4.6: Commit**

```bash
git add simulations/dev_ai_cost_v2/types.py simulations/tests/test_dev_ai_cost_v2_types.py simulations/tests/strategies.py
git commit -m "feat(dev_ai_cost_v2): types tier — MessageRecord, TokensByCategory, DailyNotionalPanel (spec v0.2.1 §3.5)"
```

---

## Task 5: Implement `jsonl_io.py` (utils tier, IO Boundary)

**Owner:** Data Engineer (interface contract from Backend Architect)
**Audit-pass chain:** `tighten-types` + `contract-docstrings` + `hypothesis-tests` + `try-except`
**Spec ref:** §3.1, §3.5, §0.1 CORRECTIONS-N, CORRECTIONS-V
**Depends on:** Task 4

**Files:**
- Create: `simulations/dev_ai_cost_v2/jsonl_io.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_jsonl_io.py`

**Exit criteria:**
- `JSONLReader` is a class (utils tier — mutable state allowed ONLY here).
- `__call__(since, until, projects_root=Path("~/.claude/projects").expanduser()) -> Sequence[MessageRecord]` returns a **materialized list**, NOT an Iterator (CORRECTIONS-V).
- UTC boundaries half-open `[00:00:00, 24:00:00)`.
- Pydantic schema `extra="forbid"` mirrors Anthropic's documented JSONL fields per §3.1.
- `JSONLSchemaError` raised on drift.
- `warnings.warn` emitted when `request_id is None` (CORRECTIONS-V legacy compat).
- Hypothesis property test: double-iteration of returned `Sequence` yields equal contents (CR FLAG A closure).

**Steps:**

- [ ] **Step 5.1: Write the failing JSONL parsing test**

```python
# simulations/tests/test_dev_ai_cost_v2_jsonl_io.py
import json
import warnings
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from simulations.dev_ai_cost_v2._errors import JSONLSchemaError
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader
from simulations.dev_ai_cost_v2.types import MessageRecord


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _valid_row(ts: str = "2026-05-01T12:00:00Z") -> dict:
    return {
        "timestamp": ts,
        "sessionId": "s1",
        "requestId": "r1",
        "isApiErrorMessage": False,
        "message": {
            "model": "claude-sonnet-4-5",
            "usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "cache_creation": {
                    "ephemeral_5m_input_tokens": 0,
                    "ephemeral_1h_input_tokens": 0,
                },
                "cache_read_input_tokens": 0,
            },
        },
        "costUSD": "0.0015",
    }


def test_jsonlreader_emits_sequence_not_iterator(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    _write_jsonl(proj / "session.jsonl", [_valid_row()])
    reader = JSONLReader()
    out = reader(since=date(2026, 5, 1), until=date(2026, 5, 2),
                 projects_root=tmp_path / "projects")
    # Sequence, not Iterator (CR FLAG A / CORRECTIONS-V).
    assert isinstance(out, list)
    assert len(out) == 1
    # Double-iteration property: second pass must equal first.
    first = list(out)
    second = list(out)
    assert first == second


def test_jsonlreader_utc_boundary_half_open(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    _write_jsonl(proj / "s.jsonl", [
        _valid_row("2026-05-01T00:00:00Z"),  # included
        _valid_row("2026-05-01T23:59:59Z"),  # included
        _valid_row("2026-05-02T00:00:00Z"),  # EXCLUDED — half-open upper
    ])
    out = JSONLReader()(since=date(2026, 5, 1), until=date(2026, 5, 2),
                        projects_root=tmp_path / "projects")
    assert len(out) == 2


def test_jsonlreader_raises_on_extra_field(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    bad = _valid_row()
    bad["unknown_extra_field"] = "drift"
    _write_jsonl(proj / "s.jsonl", [bad])
    with pytest.raises(JSONLSchemaError):
        JSONLReader()(since=date(2026, 5, 1), until=date(2026, 5, 2),
                      projects_root=tmp_path / "projects")


def test_jsonlreader_warns_on_null_request_id(tmp_path: Path) -> None:
    proj = tmp_path / "projects" / "p1"
    row = _valid_row()
    row["requestId"] = None
    _write_jsonl(proj / "s.jsonl", [row])
    with pytest.warns(UserWarning, match="request_id"):
        JSONLReader()(since=date(2026, 5, 1), until=date(2026, 5, 2),
                      projects_root=tmp_path / "projects")
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_jsonl_io.py -v`
Expected: FAIL (`ImportError`).

- [ ] **Step 5.2: Implement `JSONLReader`**

```python
# simulations/dev_ai_cost_v2/jsonl_io.py
"""utils-tier IO Boundary for dev_ai_cost_v2.

Reads ~/.claude/projects/**/*.jsonl directly with a Pydantic schema mirroring
Anthropic's documented JSONL fields (extra="forbid"). Spec ref:
docs/specs/2026-05-16-ai-cost-factor-model-design.md §3.1, §3.5.

Tier rule: this is the ONLY module in dev_ai_cost_v2 permitted to perform IO.
"""
from __future__ import annotations

import json
import warnings
from collections.abc import Sequence
from datetime import date, datetime, time, timezone
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from simulations.dev_ai_cost_v2._errors import JSONLSchemaError
from simulations.dev_ai_cost_v2.types import MessageRecord


class _CacheCreation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ephemeral_5m_input_tokens: int = 0
    ephemeral_1h_input_tokens: int = 0


class _Usage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input_tokens: int
    output_tokens: int
    cache_creation: _CacheCreation = Field(default_factory=_CacheCreation)
    cache_read_input_tokens: int = 0


class _Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str
    usage: _Usage


class _Row(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timestamp: datetime
    sessionId: str
    requestId: str | None
    isApiErrorMessage: bool
    message: _Message
    costUSD: Decimal


class JSONLReader:
    """IO Boundary: reads Anthropic Claude Code JSONL transcripts.

    Returns a materialized ``Sequence[MessageRecord]`` (not an Iterator) so
    downstream consumers may iterate multiple times (e.g., reconciliation
    cell + panel-builder aggregation). See spec §3.5 / CORRECTIONS-V FLAG A.
    """

    def __call__(
        self,
        since: date,
        until: date,
        projects_root: Path = Path("~/.claude/projects").expanduser(),
    ) -> Sequence[MessageRecord]:
        """Parse all JSONL files under ``projects_root`` within ``[since, until)``.

        Boundaries are UTC half-open ``[00:00:00, 24:00:00)``: a row at
        timestamp ``until 00:00:00Z`` is EXCLUDED (CORRECTIONS-V NIT).

        Raises
        ------
        JSONLSchemaError
            On any Pydantic validation failure (``extra="forbid"`` or missing
            required field).
        FileNotFoundError
            If ``projects_root`` does not exist.
        """
        if not projects_root.exists():
            raise FileNotFoundError(projects_root)

        lo = datetime.combine(since, time.min, tzinfo=timezone.utc)
        hi = datetime.combine(until, time.min, tzinfo=timezone.utc)

        out: list[MessageRecord] = []
        for jsonl_path in projects_root.rglob("*.jsonl"):
            with jsonl_path.open("r") as f:
                for line_no, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        raw = json.loads(line)
                    except json.JSONDecodeError as e:
                        raise JSONLSchemaError(
                            f"{jsonl_path}:{line_no} invalid JSON: {e}"
                        ) from e
                    try:
                        row = _Row.model_validate(raw)
                    except ValidationError as e:
                        raise JSONLSchemaError(
                            f"{jsonl_path}:{line_no} schema drift: {e}"
                        ) from e
                    ts = row.timestamp.astimezone(timezone.utc)
                    if not (lo <= ts < hi):
                        continue
                    if row.requestId is None:
                        warnings.warn(
                            f"{jsonl_path}:{line_no} legacy row: request_id is None",
                            UserWarning,
                            stacklevel=2,
                        )
                    out.append(MessageRecord(
                        ts=ts,
                        model=row.message.model,
                        input_tok=row.message.usage.input_tokens,
                        output_tok=row.message.usage.output_tokens,
                        cache_create_5m=row.message.usage.cache_creation.ephemeral_5m_input_tokens,
                        cache_create_1h=row.message.usage.cache_creation.ephemeral_1h_input_tokens,
                        cache_read=row.message.usage.cache_read_input_tokens,
                        cost_usd_notional=row.costUSD,
                        session_id=row.sessionId,
                        request_id=row.requestId,
                        is_error=row.isApiErrorMessage,
                    ))
        return out
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_jsonl_io.py -v`
Expected: PASS (all four tests).

- [ ] **Step 5.3: Apply `try-except` skill audit**

Verify each `try:` block covers ONLY the operation that can fail (`json.loads`; `model_validate`). No bare `except`. No `except Exception:`.

- [ ] **Step 5.4: Apply `contract-docstrings` skill audit**

Document for `__call__`: input invariants (since ≤ until, projects_root exists), errors raised on violation (`FileNotFoundError`, `JSONLSchemaError`), errors from external state (none — Pydantic handles all), silenced errors (none).

- [ ] **Step 5.5: Commit**

```bash
git add simulations/dev_ai_cost_v2/jsonl_io.py simulations/tests/test_dev_ai_cost_v2_jsonl_io.py
git commit -m "feat(dev_ai_cost_v2): jsonl_io — own-parser primary substrate (spec v0.2.1 §3.1 / CORRECTIONS-N)"
```

---

## Task 6: Implement `anthropic_pricing.py` (modules tier)

**Owner:** Data Engineer
**Audit-pass chain:** `functional-python` + `hypothesis-tests` + `contract-docstrings`
**Spec ref:** §3.2, §3.5, §5.2, §0.1 CORRECTIONS-O, CORRECTIONS-V
**Depends on:** Task 4

**Files:**
- Create: `simulations/dev_ai_cost_v2/anthropic_pricing.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_pricing.py`

**Exit criteria:**
- `PricingTable` is a frozen dataclass (modules tier — pure callable).
- `from_litellm_sha(sha)` constructor loads the cached LiteLLM JSON; refuses to load if hash drift detected.
- **Load-time assertion** (per Wave 1 RC hint): all five corrected keys (`input_cost_per_token`, `output_cost_per_token`, `cache_creation_input_token_cost`, `cache_creation_input_token_cost_above_1hr`, `cache_read_input_token_cost`) exist for every `claude-*` model in the file. Missing key → raise.
- `__call__(model, ts, toks)` returns Decimal; `ts` is consulted for time-varying step lookups.
- Hypothesis property test: cost is monotone non-decreasing in each token category.

**Steps:**

- [ ] **Step 6.1: Write the failing test for load-time key assertion**

```python
# simulations/tests/test_dev_ai_cost_v2_pricing.py
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from simulations.dev_ai_cost_v2.anthropic_pricing import PricingTable
from simulations.dev_ai_cost_v2.types import TokensByCategory

LITELLM_SHA = "e58a561caa21169fb02174148444c08509ce7028"


def test_pricing_table_load_requires_all_five_keys(tmp_path: Path) -> None:
    """Per Wave 1 RC hint: every claude-* model must carry all five keys."""
    fake_table = {
        "claude-sonnet-4-5": {
            "input_cost_per_token": 3e-06,
            "output_cost_per_token": 15e-06,
            "cache_creation_input_token_cost": 3.75e-06,
            # MISSING: cache_creation_input_token_cost_above_1hr
            "cache_read_input_token_cost": 0.30e-06,
        }
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    with pytest.raises(KeyError, match="cache_creation_input_token_cost_above_1hr"):
        PricingTable.from_litellm_sha(
            sha=LITELLM_SHA, cached_json_path=p, skip_sha_check=True
        )


def test_pricing_table_call_uses_correct_keys(tmp_path: Path) -> None:
    fake_table = {
        "claude-sonnet-4-5": {
            "input_cost_per_token": 3e-06,
            "output_cost_per_token": 15e-06,
            "cache_creation_input_token_cost": 3.75e-06,
            "cache_creation_input_token_cost_above_1hr": 6e-06,
            "cache_read_input_token_cost": 0.30e-06,
        }
    }
    p = tmp_path / "litellm.json"
    p.write_text(json.dumps(fake_table))
    pt = PricingTable.from_litellm_sha(
        sha=LITELLM_SHA, cached_json_path=p, skip_sha_check=True
    )
    toks = TokensByCategory(input=1000, output=500, cache_create_5m=200,
                            cache_create_1h=100, cache_read=300)
    cost = pt(model="claude-sonnet-4-5",
              ts=datetime(2026, 5, 1, tzinfo=timezone.utc),
              toks=toks)
    expected = (Decimal("1000") * Decimal("3e-06")
                + Decimal("500") * Decimal("15e-06")
                + Decimal("200") * Decimal("3.75e-06")
                + Decimal("100") * Decimal("6e-06")
                + Decimal("300") * Decimal("0.30e-06"))
    assert cost == expected
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_pricing.py -v`
Expected: FAIL.

- [ ] **Step 6.2: Implement `PricingTable`**

```python
# simulations/dev_ai_cost_v2/anthropic_pricing.py
"""modules-tier pure Callable: notional USD cost from token counts.

Spec ref: docs/specs/2026-05-16-ai-cost-factor-model-design.md §3.2, §3.5,
§5.2 (LiteLLM SHA pin), §0.1 CORRECTIONS-O (key names),
CORRECTIONS-V (ts policy).

Tier rule: modules/ may import types/ but NOT utils/.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from simulations.dev_ai_cost_v2.types import TokensByCategory

_REQUIRED_KEYS: tuple[str, ...] = (
    "input_cost_per_token",
    "output_cost_per_token",
    "cache_creation_input_token_cost",
    "cache_creation_input_token_cost_above_1hr",
    "cache_read_input_token_cost",
)

LITELLM_SHA_PINNED = "e58a561caa21169fb02174148444c08509ce7028"


@dataclass(frozen=True, slots=True)
class PricingTable:
    rates: Mapping[str, Mapping[str, Decimal]]
    sha: str

    @classmethod
    def from_litellm_sha(
        cls,
        sha: str,
        cached_json_path: Path,
        *,
        skip_sha_check: bool = False,
    ) -> "PricingTable":
        """Load LiteLLM model_prices_and_context_window.json at the pinned SHA.

        Per spec §5.2 + CORRECTIONS-O, every ``claude-*`` model must carry all
        five required keys; missing key raises KeyError at load time (Wave 1
        RC hint).

        Per CORRECTIONS-V, ``ts`` is used downstream for time-varying lookups;
        the pinned SHA captures the historical step structure at the lookup
        timestamp.
        """
        raw = cached_json_path.read_bytes()
        if not skip_sha_check:
            digest = hashlib.sha256(raw).hexdigest()
            # Production path: hash check against a pinned content hash stored
            # in DATA_PROVENANCE.md. The SHA arg here is the *commit* SHA;
            # we sanity-check that the requested commit matches the pin.
            if sha != LITELLM_SHA_PINNED:
                raise ValueError(
                    f"PricingTable refuses load: requested SHA {sha} != pinned "
                    f"{LITELLM_SHA_PINNED}"
                )

        table = json.loads(raw)
        out: dict[str, Mapping[str, Decimal]] = {}
        for model, rates in table.items():
            if not model.startswith("claude-"):
                continue
            if not isinstance(rates, dict):
                continue
            for k in _REQUIRED_KEYS:
                if k not in rates:
                    raise KeyError(
                        f"LiteLLM SHA {sha}: model {model} missing required "
                        f"key {k!r}"
                    )
            out[model] = MappingProxyType({
                k: Decimal(str(rates[k])) for k in _REQUIRED_KEYS
            })
        return cls(rates=MappingProxyType(out), sha=sha)

    def __call__(
        self,
        model: str,
        ts: datetime,
        toks: TokensByCategory,
    ) -> Decimal:
        """Notional USD cost for one message.

        ``ts`` is currently used as a sentinel for time-varying price-step
        lookups; the pinned LiteLLM SHA represents one snapshot. When the
        table is upgraded to multi-step (effective-from dated entries), this
        method dispatches based on ``ts``. For the v0.2.1 single-snapshot
        load, ``ts`` is accepted but does not alter the lookup.
        """
        if model not in self.rates:
            raise KeyError(f"PricingTable has no rates for model {model!r}")
        r = self.rates[model]
        return (
            Decimal(toks.input) * r["input_cost_per_token"]
            + Decimal(toks.output) * r["output_cost_per_token"]
            + Decimal(toks.cache_create_5m) * r["cache_creation_input_token_cost"]
            + Decimal(toks.cache_create_1h) * r["cache_creation_input_token_cost_above_1hr"]
            + Decimal(toks.cache_read) * r["cache_read_input_token_cost"]
        )
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_pricing.py -v`
Expected: PASS.

- [ ] **Step 6.3: Add Hypothesis monotonicity property test**

```python
# Append to test_dev_ai_cost_v2_pricing.py
from hypothesis import given, strategies as st

@given(
    input_tok=st.integers(0, 10_000),
    extra_input=st.integers(0, 10_000),
)
def test_pricing_monotone_in_input_tokens(input_tok: int, extra_input: int,
                                          tmp_path_factory) -> None:
    tmp = tmp_path_factory.mktemp("pricing")
    fake = {"claude-sonnet-4-5": {k: 1e-06 for k in _REQUIRED_KEYS}}
    p = tmp / "litellm.json"
    p.write_text(json.dumps(fake))
    pt = PricingTable.from_litellm_sha(LITELLM_SHA, p, skip_sha_check=True)
    base = pt("claude-sonnet-4-5",
              datetime(2026, 5, 1, tzinfo=timezone.utc),
              TokensByCategory(input_tok, 0, 0, 0, 0))
    more = pt("claude-sonnet-4-5",
              datetime(2026, 5, 1, tzinfo=timezone.utc),
              TokensByCategory(input_tok + extra_input, 0, 0, 0, 0))
    assert more >= base
```

(Note: import `_REQUIRED_KEYS` from the module.)

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_pricing.py -v`
Expected: PASS.

- [ ] **Step 6.4: Commit**

```bash
git add simulations/dev_ai_cost_v2/anthropic_pricing.py simulations/tests/test_dev_ai_cost_v2_pricing.py
git commit -m "feat(dev_ai_cost_v2): anthropic_pricing — LiteLLM SHA-pinned PricingTable (spec v0.2.1 §5.2 / CORRECTIONS-O)"
```

---

## Task 7: Implement `panel_builder.py` (modules tier)

**Owner:** Backend Architect designs ‖ Data Engineer implements
**Audit-pass chain:** `pre-mortem` + `mutation-testing` + `hypothesis-tests` + `try-except` + `contract-docstrings`
**Spec ref:** §3.3, §3.5, §0.1 CORRECTIONS-V (is_error, UTC half-open)
**Depends on:** Tasks 4, 5, 6

**Files:**
- Create: `simulations/dev_ai_cost_v2/panel_builder.py`
- Create: `simulations/tests/test_dev_ai_cost_v2_panel_builder.py`

**Exit criteria:**
- `build_daily_panel(records, pricing, trm_panel) -> DailyNotionalPanel` is pure (no IO).
- Drops `is_error=True` from cost aggregation; counts as `dropped_error_count`.
- Weekends dropped on both sides; inner join on weekday subset; emits `dropped_rows_count`.
- **Forward-fill is forbidden**: Hypothesis property test raises if any output day lacks source rows on either side (§6 threats, CORRECTIONS-M).
- Double-iteration property: re-iterating `records` produces identical panel (CR FLAG A closure).
- Reconciliation property: sum of per-message `cost_usd_notional` over non-error rows equals panel `notional_cost_usd` exactly under `Decimal`.

**Steps:**

- [ ] **Step 7.1: Write the failing reconciliation test**

```python
# simulations/tests/test_dev_ai_cost_v2_panel_builder.py
from datetime import date, datetime, timezone
from decimal import Decimal

import polars as pl
import pytest
from hypothesis import given, settings, strategies as st

from simulations.dev_ai_cost_v2.panel_builder import build_daily_panel
from simulations.dev_ai_cost_v2.anthropic_pricing import PricingTable
from simulations.dev_ai_cost_v2.types import MessageRecord


def _toy_pricing(tmp_path) -> PricingTable:
    import json
    from simulations.dev_ai_cost_v2.anthropic_pricing import _REQUIRED_KEYS, LITELLM_SHA_PINNED
    fake = {"claude-sonnet-4-5": {k: 1e-06 for k in _REQUIRED_KEYS}}
    p = tmp_path / "lite.json"
    p.write_text(json.dumps(fake))
    return PricingTable.from_litellm_sha(LITELLM_SHA_PINNED, p, skip_sha_check=True)


def _toy_trm() -> pl.DataFrame:
    # 5 weekdays 2026-05-04..2026-05-08
    from datetime import date
    return pl.DataFrame({
        "date": [date(2026, 5, d) for d in (4, 5, 6, 7, 8)],
        "trm_cop_per_usd": [Decimal("4100"), Decimal("4105"),
                            Decimal("4090"), Decimal("4110"),
                            Decimal("4120")],
    })


def _rec(day: int, hour: int = 12, is_error: bool = False) -> MessageRecord:
    return MessageRecord(
        ts=datetime(2026, 5, day, hour, tzinfo=timezone.utc),
        model="claude-sonnet-4-5",
        input_tok=1000, output_tok=500,
        cache_create_5m=0, cache_create_1h=0, cache_read=0,
        cost_usd_notional=Decimal("0.0015"),
        session_id="s", request_id="r", is_error=is_error,
    )


def test_reconciliation_exact_decimal(tmp_path) -> None:
    pricing = _toy_pricing(tmp_path)
    records = [_rec(4), _rec(5), _rec(5)]
    panel = build_daily_panel(records, pricing, _toy_trm())
    raw_total = sum((r.cost_usd_notional for r in records), Decimal("0"))
    panel_total = panel.df["notional_cost_usd"].sum()
    assert Decimal(str(panel_total)) == raw_total


def test_is_error_rows_dropped_from_cost_counted_separately(tmp_path) -> None:
    pricing = _toy_pricing(tmp_path)
    records = [_rec(4), _rec(4, is_error=True), _rec(5)]
    panel = build_daily_panel(records, pricing, _toy_trm())
    assert panel.dropped_error_count == 1
    # 2026-05-04 should reflect only 1 message, not 2.
    may4 = panel.df.filter(pl.col("date_utc") == date(2026, 5, 4))
    assert may4["n_messages"].item() == 1


def test_forward_fill_forbidden_property(tmp_path) -> None:
    """No output day should lack source rows on EITHER side (records OR TRM)."""
    pricing = _toy_pricing(tmp_path)
    # Records on May 5 only; TRM has May 4..8. May 4,6,7,8 must NOT appear in panel.
    records = [_rec(5)]
    panel = build_daily_panel(records, pricing, _toy_trm())
    out_dates = set(panel.df["date_utc"].to_list())
    assert out_dates == {date(2026, 5, 5)}


def test_weekends_dropped(tmp_path) -> None:
    pricing = _toy_pricing(tmp_path)
    # 2026-05-02 = Saturday, 2026-05-03 = Sunday
    records = [_rec(2), _rec(3), _rec(4)]
    # extend TRM to include weekends (will be filtered)
    trm = pl.DataFrame({
        "date": [date(2026, 5, d) for d in (2, 3, 4)],
        "trm_cop_per_usd": [Decimal("4100"), Decimal("4100"), Decimal("4100")],
    })
    panel = build_daily_panel(records, pricing, trm)
    assert set(panel.df["date_utc"].to_list()) == {date(2026, 5, 4)}
    assert panel.dropped_rows_count >= 2  # the two weekend records


def test_double_iteration_equivalence(tmp_path) -> None:
    """records is a Sequence — building twice must yield identical panels."""
    pricing = _toy_pricing(tmp_path)
    records: list[MessageRecord] = [_rec(4), _rec(5)]
    p1 = build_daily_panel(records, pricing, _toy_trm())
    p2 = build_daily_panel(records, pricing, _toy_trm())
    assert p1.df.equals(p2.df)
```

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_panel_builder.py -v`
Expected: FAIL (`ImportError`).

- [ ] **Step 7.2: Implement `build_daily_panel`**

```python
# simulations/dev_ai_cost_v2/panel_builder.py
"""modules-tier pure function: per-message records -> DailyNotionalPanel.

Spec ref: docs/specs/2026-05-16-ai-cost-factor-model-design.md §3.3, §3.5,
CORRECTIONS-V (is_error, UTC half-open), CORRECTIONS-M (forward-fill forbidden).

Tier rule: modules/ may import types/ but NOT utils/.
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from decimal import Decimal

import polars as pl

from simulations.dev_ai_cost_v2.anthropic_pricing import PricingTable
from simulations.dev_ai_cost_v2.types import (
    DailyNotionalPanel,
    EXPECTED_PANEL_SCHEMA,
    MessageRecord,
)


def build_daily_panel(
    records: Sequence[MessageRecord],
    pricing: PricingTable,  # accepted for signature parity; values are pre-computed in MessageRecord.cost_usd_notional
    trm_panel: pl.DataFrame,
) -> DailyNotionalPanel:
    """Aggregate per-message records to a daily UTC panel joined with TRM.

    Contract
    --------
    * ``is_error=True`` rows are DROPPED from cost aggregation; their count
      is exposed as ``dropped_error_count`` (spec CORRECTIONS-V).
    * Weekends (Sat/Sun) are dropped on BOTH sides before the inner join;
      their count is included in ``dropped_rows_count`` (§3.5).
    * Forward-fill is FORBIDDEN: a day with no records OR no TRM observation
      does NOT appear in the output (spec §6 threat / CORRECTIONS-M).
    * All arithmetic is exact ``Decimal`` (spec §3.5 rationale).
    """
    dropped_error = sum(1 for r in records if r.is_error)
    kept = [r for r in records if not r.is_error]

    # Per-message frame
    rows = [{
        "date_utc": r.ts.date(),
        "weekday": r.ts.weekday(),
        "cost_usd": r.cost_usd_notional,
        "input_tok": r.input_tok,
        "output_tok": r.output_tok,
        "cache_create_5m": r.cache_create_5m,
        "cache_create_1h": r.cache_create_1h,
        "cache_read": r.cache_read,
    } for r in kept]
    msg_df = pl.DataFrame(rows) if rows else pl.DataFrame(schema={
        "date_utc": pl.Date, "weekday": pl.Int8,
        "cost_usd": pl.Decimal, "input_tok": pl.Int64,
        "output_tok": pl.Int64, "cache_create_5m": pl.Int64,
        "cache_create_1h": pl.Int64, "cache_read": pl.Int64,
    })

    weekend_records = msg_df.filter(pl.col("weekday") >= 5).height
    daily = (
        msg_df.filter(pl.col("weekday") < 5)
              .group_by("date_utc")
              .agg([
                  pl.col("cost_usd").sum().alias("notional_cost_usd"),
                  pl.col("input_tok").sum(),
                  pl.col("output_tok").sum(),
                  pl.col("cache_create_5m").sum(),
                  pl.col("cache_create_1h").sum(),
                  pl.col("cache_read").sum(),
                  pl.len().alias("n_messages"),
              ])
    )

    trm_weekday = trm_panel.filter(
        pl.col("date").dt.weekday() < 5  # polars: Mon=0..Sun=6 if using chrono;
                                          # adjust per polars version
    ).rename({"date": "date_utc"})
    weekend_trm = trm_panel.height - trm_weekday.height

    joined = daily.join(trm_weekday, on="date_utc", how="inner")
    joined = joined.with_columns([
        (pl.col("notional_cost_usd") * pl.col("trm_cop_per_usd"))
            .alias("notional_cost_cop"),
    ])
    joined = joined.select(list(EXPECTED_PANEL_SCHEMA.keys()))

    dropped_rows = weekend_records + weekend_trm + (daily.height - joined.height)

    return DailyNotionalPanel(
        df=joined,
        dropped_rows_count=int(dropped_rows),
        dropped_error_count=int(dropped_error),
    )
```

> **Note:** polars' `dt.weekday()` semantics vary by version. Verify Mon=0/Sun=6 in this repo's pin and adjust the `< 5` filter accordingly. Add a unit test that explicitly checks a known Monday/Saturday before merging.

Run: `uv run pytest simulations/tests/test_dev_ai_cost_v2_panel_builder.py -v`
Expected: PASS.

- [ ] **Step 7.3: Add `pre-mortem` skill audit**

Run the `pre-mortem` skill on `panel_builder.py`. Surface failure modes (silent weekend mis-filter, Decimal precision loss in polars sum, TRM-side gaps masquerading as panel gaps). Add property tests for each surfaced mode.

- [ ] **Step 7.4: Run mutation testing on `panel_builder.py`**

```bash
uv run mutmut run --paths-to-mutate simulations/dev_ai_cost_v2/panel_builder.py
uv run mutmut results
```

Address surviving mutants by adding tests until coverage meets the project's existing mutation-testing bar.

- [ ] **Step 7.5: Commit**

```bash
git add simulations/dev_ai_cost_v2/panel_builder.py simulations/tests/test_dev_ai_cost_v2_panel_builder.py
git commit -m "feat(dev_ai_cost_v2): panel_builder — daily aggregation + forward-fill-forbidden property (spec v0.2.1 §3.3)"
```

---

## Task 8: CLI orchestration script `scripts/build_notional_cost_panel.py`

**Owner:** Data Engineer
**Audit-pass chain:** `try-except` + `contract-docstrings`
**Spec ref:** §3.3, §0.1 CORRECTIONS-W
**Depends on:** Tasks 1, 5, 6, 7

**Files:**
- Create: `scripts/build_notional_cost_panel.py`
- Create: `simulations/tests/test_build_notional_cost_panel_cli.py`

**Exit criteria:**
- Single orchestration point: imports both utils-tier (`jsonl_io`) and modules-tier (`anthropic_pricing`, `panel_builder`).
- **`data/panels/` is created with `mkdir(parents=True, exist_ok=True)` on first run** (Wave 1 RC implementation hint).
- Reads daily TRM from `data/raw/banrep_trm_daily.parquet`.
- Writes `data/panels/notional_cost_panel.parquet`.
- Exits non-zero on any reconciliation or schema-drift failure.
- CLI args: `--since`, `--until`, `--projects-root`, `--litellm-cache`, `--out`.

**Steps:**

- [ ] **Step 8.1: Write the failing CLI smoke test**

```python
# simulations/tests/test_build_notional_cost_panel_cli.py
import subprocess
import sys
from pathlib import Path

def test_cli_help_runs() -> None:
    r = subprocess.run(
        [sys.executable, "-m", "scripts.build_notional_cost_panel", "--help"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0
    assert "--since" in r.stdout
    assert "--until" in r.stdout
```

Run: `uv run pytest simulations/tests/test_build_notional_cost_panel_cli.py -v`
Expected: FAIL.

- [ ] **Step 8.2: Implement the CLI**

```python
# scripts/build_notional_cost_panel.py
"""Tier-3 CLI: build data/panels/notional_cost_panel.parquet.

Single orchestration point that imports across utils + modules tiers
(spec v0.2.1 §3.3, §3.5).
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

import polars as pl

from simulations.dev_ai_cost_v2.anthropic_pricing import LITELLM_SHA_PINNED, PricingTable
from simulations.dev_ai_cost_v2.jsonl_io import JSONLReader
from simulations.dev_ai_cost_v2.panel_builder import build_daily_panel

REPO_ROOT = Path(__file__).resolve().parent.parent


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--since", type=date.fromisoformat, required=True)
    p.add_argument("--until", type=date.fromisoformat, required=True)
    p.add_argument("--projects-root",
                   default=Path("~/.claude/projects").expanduser(), type=Path)
    p.add_argument("--litellm-cache",
                   default=REPO_ROOT / "data" / "raw" / "litellm_model_prices.json",
                   type=Path)
    p.add_argument("--trm-path",
                   default=REPO_ROOT / "data" / "raw" / "banrep_trm_daily.parquet",
                   type=Path)
    p.add_argument("--out",
                   default=REPO_ROOT / "data" / "panels" / "notional_cost_panel.parquet",
                   type=Path)
    return p.parse_args()


def main() -> int:
    args = _parse_args()

    # CORRECTIONS-W: data/panels/ does not exist yet at first run.
    args.out.parent.mkdir(parents=True, exist_ok=True)

    pricing = PricingTable.from_litellm_sha(
        LITELLM_SHA_PINNED, cached_json_path=args.litellm_cache
    )
    trm = pl.read_parquet(args.trm_path)
    reader = JSONLReader()
    records = reader(args.since, args.until, projects_root=args.projects_root)
    panel = build_daily_panel(records, pricing, trm)

    panel.df.write_parquet(args.out)
    print(f"[OK] wrote {args.out} ({panel.df.height} rows; "
          f"dropped_rows={panel.dropped_rows_count}, "
          f"dropped_error={panel.dropped_error_count})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 8.3: Run the smoke test**

Run: `uv run pytest simulations/tests/test_build_notional_cost_panel_cli.py -v`
Expected: PASS.

- [ ] **Step 8.4: Commit**

```bash
git add scripts/build_notional_cost_panel.py simulations/tests/test_build_notional_cost_panel_cli.py
git commit -m "feat(scripts): build_notional_cost_panel CLI (spec v0.2.1 §3.3 / CORRECTIONS-W)"
```

---

## Task 9: Implementation-review checkpoint (Code Reviewer + Reality Checker + Backend Architect)

**Owner:** orchestrator dispatching three reviewers in parallel
**Audit-pass chain:** —
**Spec ref:** §8 row "Implementation review", per `memory/feedback_implementation_review_agents.md`
**Depends on:** Tasks 1–8

**Files:**
- Create: `scratch/2026-05-16-ai-cost-impl-review/code_reviewer.md`
- Create: `scratch/2026-05-16-ai-cost-impl-review/reality_checker.md`
- Create: `scratch/2026-05-16-ai-cost-impl-review/backend_architect.md`

**Exit criteria:**
- Three independent review reports filed.
- All BLOCKs from any reviewer are closed in a CORRECTIONS-Y patch to the spec OR resolved by code changes before proceeding.
- Disposition memo signed off in the impl-review scratch directory.

**Steps:**

- [ ] **Step 9.1: Dispatch reviewers**

Per `feedback_implementation_review_agents.md`, send each reviewer the implementation diff (Tasks 1–8), the spec v0.2.1, and the three v0.2.1 closure-only reports. Reviewers verify:
- **Code Reviewer:** tier-import rule held; frozen-dc semantics; `Sequence` not `Iterator`; UTC half-open boundary; `is_error` policy; Decimal exactness in panel-builder.
- **Reality Checker:** LiteLLM SHA actually loaded at `e58a561c...`; `data/raw/banrep_trm_daily.parquet` actually produced; CLI runs end-to-end on the maintainer's `~/.claude/projects/`.
- **Backend Architect:** API surface stable; double-iteration property test exists and passes; mutation-testing report shows zero unkilled mutants in `panel_builder.py`'s cost path.

- [ ] **Step 9.2: Address all BLOCKs**

For any BLOCK: fix code, add tests, re-run. If a BLOCK requires spec change, draft CORRECTIONS-Y in §0.1.

- [ ] **Step 9.3: Commit review reports**

```bash
git add scratch/2026-05-16-ai-cost-impl-review/
git commit -m "review(dev_ai_cost_v2): impl-review checkpoint (Tasks 1–8)"
```

---

## Task 10: Run the panel build + record provenance

**Owner:** Data Engineer
**Audit-pass chain:** —
**Spec ref:** §5.4
**Depends on:** Task 9 sign-off

**Files:**
- Create: `notebooks/dev_ai_cost_v2/data/DATA_PROVENANCE.md`
- Emits: `data/panels/notional_cost_panel.parquet`

**Exit criteria:**
- `notional_cost_panel.parquet` produced for the maintainer's actual JSONL window.
- DATA_PROVENANCE.md records every field listed in spec §5.4 (LiteLLM SHA, Banrep daily file sha256, panel sha256, since/until window, projects-root scope, `dropped_rows_count`, `dropped_error_count`, own-parser git SHA).

**Steps:**

- [ ] **Step 10.1: Run the fetcher**

```bash
uv run python scripts/fetch_banrep.py --daily --out data/raw/banrep_trm_daily.parquet \
    --since 2024-01-01 --until $(date -I)
```

- [ ] **Step 10.2: Run the CLI**

```bash
uv run python scripts/build_notional_cost_panel.py \
    --since 2024-01-01 --until $(date -I)
```

Verify the printed `dropped_rows_count` and `dropped_error_count` against expectation from JSONL inspection.

- [ ] **Step 10.3: Compute sha256 hashes and write DATA_PROVENANCE.md**

```bash
sha256sum data/raw/banrep_trm_daily.parquet data/panels/notional_cost_panel.parquet
git rev-parse HEAD
```

Populate the file per §5.4.

- [ ] **Step 10.4: Commit**

```bash
git add notebooks/dev_ai_cost_v2/data/DATA_PROVENANCE.md
# Do NOT commit data/panels/*.parquet or data/raw/*.parquet (gitignored).
git commit -m "data(dev_ai_cost_v2): record provenance for first panel build (spec v0.2.1 §5.4)"
```

---

## Task 11: Notebook 01 — `01_data_eda.ipynb` (trio + power HALT)

**Owner:** orchestrator (trio-checkpoints with human reviewer)
**Audit-pass chain:** `python-panel-data` + `statsmodels`
**Spec ref:** §4, §0.1 CORRECTIONS-J + CORRECTIONS-U
**Depends on:** Tasks 3, 10

**Files:**
- Create: `notebooks/dev_ai_cost_v2/01_data_eda.ipynb`

**Exit criteria:**
- Every (why-markdown, code-cell, interpretation-markdown) trio is a HALT-checkpoint (`feedback_notebook_trio_checkpoint`).
- Decision-citation block (4-part) precedes every test or spec choice (`feedback_notebook_citation_block`).
- **Reconciliation cell**: re-sums panel-builder daily aggregates back to per-message totals from `JSONLReader`; asserts exact-Decimal match. Any drift → HALT to disposition.
- **Power-measurement HALT-checkpoint**: residual SD of $|\Delta\ln\text{NotionalCost}^{USD}|$ partialling out $|\Delta\ln\text{Tokens}|$; Monte-Carlo power at MDES=0.40 residual-SD with current T. If power < 0.50 → fill `dispositions/power_halt_template.md` + HALT.

**Steps:**

- [ ] **Step 11.1: Build the notebook skeleton (trios)**

Cells, in order:
1. Title + spec citation (§1, §2.1, §2.3).
2. Trio 1 — "Load panel" (why / code / interpretation).
3. Trio 2 — "Reconciliation gate" (why / **exact-Decimal sum compare** / pass-or-HALT).
4. Trio 3 — "Univariate distributions" (notional cost USD, COP, TRM, tokens).
5. Trio 4 — "Serial correlation diagnostics" (ACF on $|\Delta\ln\text{NotionalCost}^{USD}|$ — informs bootstrap block length).
6. Trio 5 — "Power measurement" (residual SD computation + Monte-Carlo power at MDES=0.40 with HAC L=⌊T^(1/3)⌋).
7. **Power HALT-checkpoint cell** — if power < 0.50, route to `dispositions/power_halt_template.md` and stop.
8. Trio 6 — "Sample inventory" (N weekday days observed; per §2.3 floor).

- [ ] **Step 11.2: Execute headlessly**

```bash
uv run jupyter nbconvert --to notebook --execute notebooks/dev_ai_cost_v2/01_data_eda.ipynb --inplace
```

If power HALT fires, fill the template, commit the disposition, and STOP. Do not proceed to Task 12.

- [ ] **Step 11.3: Commit**

```bash
git add notebooks/dev_ai_cost_v2/01_data_eda.ipynb
git commit -m "notebook(dev_ai_cost_v2): 01_data_eda — trio + reconciliation + power HALT (spec v0.2.1 §4)"
```

---

## Task 12: Notebook 02 — `02_r5_descriptive.ipynb` (R5 PRIMARY)

**Owner:** orchestrator
**Audit-pass chain:** `python-panel-data` + `statsmodels`
**Spec ref:** §2.1, §0.1 CORRECTIONS-P + CORRECTIONS-Q + CORRECTIONS-R + CORRECTIONS-T
**Depends on:** Task 11 PASS

**Files:**
- Create: `notebooks/dev_ai_cost_v2/02_r5_descriptive.ipynb`

**Exit criteria:**
- 90% **stationary bootstrap** (Politis & Romano 1994) implemented with expected block length $\lceil T^{1/3} \rceil$; **B = 10,000**.
- Variance decomposition emits FX share, usage share, AND covariance term as **separately-reported diagnostic** (CORRECTIONS-Q).
- Headline output formatted per spec §2.1 output 5; explicit Role A framing per CORRECTIONS-R.
- CI half-width on FX-vol share threshold **≤ 0.15** (CORRECTIONS-T); cell records pass/fail of this quality threshold (NOT verdict-bearing — informs M-design usability).

**Steps:**

- [ ] **Step 12.1: Notebook cells (trios)**

1. Title + spec citation (§2.1 + CORRECTIONS-P/Q/R/T).
2. Trio — "Load panel + compute Δln series".
3. Trio — "Realized vol of Δln NotionalCost^COP" + bootstrap CI.
4. Trio — "Empirical 5% monthly VaR" + bootstrap CI.
5. Trio — "Variance decomposition" — emit three numbers: FX share (excluding covariance), usage share (excluding covariance), 2·Cov reported separately with its own bootstrap CI. **Headline = FX share / total var EXCLUDING covariance** (CORRECTIONS-Q).
6. Trio — "Counterfactual: FX held constant" → token-only vol path.
7. Trio — "Counterfactual: Tokens held constant" → FX-only vol path (Role A individual-sizing, CORRECTIONS-R; cell preamble disclaims channel-existence claim).
8. Quality-threshold cell: assert CI half-width on FX share ≤ 0.15 (CORRECTIONS-T). If breached, document in headline output cell ("M-design hedge sizing is provisional; tighten by enlarging T").
9. Headline output cell — exact formatting per spec §2.1 output 5.

- [ ] **Step 12.2: Use `arch.bootstrap.StationaryBootstrap` (or hand-implementation)**

```python
from arch.bootstrap import StationaryBootstrap
import numpy as np

T = len(delta_ln_cop)
block_len = int(np.ceil(T ** (1/3)))
sb = StationaryBootstrap(block_len, delta_ln_cop, delta_ln_usd, delta_ln_trm,
                          seed=20260516)
# 10000 reps, 90% CI on FX share excluding covariance:
def fx_share_excl_cov(c, u, x):
    return np.var(x) / (np.var(c))
ci = sb.conf_int(fx_share_excl_cov, reps=10_000, size=0.90, method="basic")
```

(Confirm `arch` is pinned in `requirements.txt`; if not, add it.)

- [ ] **Step 12.3: Execute headlessly + commit**

```bash
uv run jupyter nbconvert --to notebook --execute notebooks/dev_ai_cost_v2/02_r5_descriptive.ipynb --inplace
git add notebooks/dev_ai_cost_v2/02_r5_descriptive.ipynb
git commit -m "notebook(dev_ai_cost_v2): 02_r5_descriptive — stationary bootstrap + cov-separate (spec v0.2.1 §2.1)"
```

---

## Task 13: Notebook 03 — `03_r4s3_cop_consistency.ipynb` (R4-S3-COP consistency check)

**Owner:** orchestrator
**Audit-pass chain:** `python-panel-data` + `statsmodels`
**Spec ref:** §2.2.A, §0.1 CORRECTIONS-S
**Depends on:** Task 11 PASS

**Files:**
- Create: `notebooks/dev_ai_cost_v2/03_r4s3_cop_consistency.ipynb`

**Exit criteria:**
- **Cell preamble explicitly disclaims framework-graduation authority** (CORRECTIONS-S).
- OLS with HAC bandwidth $L = \lfloor T^{1/3} \rfloor$ (CORRECTIONS-I).
- $k=1$ primary, $k=5$ sensitivity.
- One-sided pre-pinned: $\alpha_1^{COP} > 0$.
- Verdict labels: CONSISTENCY-PASS / CONSISTENCY-FAIL. A FAIL HALTs the pipeline (suspect data corruption), not the framework.

**Steps:**

- [ ] **Step 13.1: Notebook cells (trios)**

1. Title + **CORRECTIONS-S preamble disclaiming novelty**.
2. Trio — "Construct |Δln NotionalCost^COP|, |Δln USDCOP|, |Δln Tokens|".
3. Trio — "OLS with Newey-West HAC L=⌊T^(1/3)⌋" using `statsmodels.OLS(...).fit(cov_type='HAC', cov_kwds={'maxlags': L})`.
4. Trio — "$k=5$ sensitivity".
5. Verdict cell — CONSISTENCY-PASS if $\hat\alpha_1^{COP}>0$ at $p_{1\text{-sided}}<0.05$, else CONSISTENCY-FAIL.

- [ ] **Step 13.2: Execute + commit**

```bash
uv run jupyter nbconvert --to notebook --execute notebooks/dev_ai_cost_v2/03_r4s3_cop_consistency.ipynb --inplace
git add notebooks/dev_ai_cost_v2/03_r4s3_cop_consistency.ipynb
git commit -m "notebook(dev_ai_cost_v2): 03_r4s3_cop_consistency — pipeline consistency check (spec v0.2.1 §2.2.A)"
```

---

## Task 14: Notebook 04 — `04_r4s3_usd_behavioral.ipynb` (R4-S3-USD behavioral test)

**Owner:** orchestrator
**Audit-pass chain:** `python-panel-data` + `statsmodels`
**Spec ref:** §2.2.B, §0.1 CORRECTIONS-S
**Depends on:** Task 13

**Files:**
- Create: `notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb`

**Exit criteria:**
- Two-sided $\alpha_1^{USD} = 0$ null pinned (CORRECTIONS-S).
- HAC $L = \lfloor T^{1/3} \rfloor$.
- $k=1$ primary, $k=5$ sensitivity.
- Verdict labels: REJECT_NULL / FAIL_TO_REJECT / HALT — per §2.2.B verdict logic.
- Decision-citation block precedes every test choice.
- Inverted-test interpretation explicitly documented (REJECT = behavioral channel exists; FAIL_TO_REJECT = subscription inelasticity confirmed).

**Steps:**

- [ ] **Step 14.1: Notebook cells (trios)**

1. Title + preamble explaining the **test-inversion logic** (CORRECTIONS-S).
2. Decision-citation block (4-part) for the two-sided test choice.
3. Trio — "Construct |Δln NotionalCost^USD|, |Δln USDCOP|, |Δln Tokens|".
4. Trio — "Primary regression $k=1$ with HAC".
5. Trio — "Sensitivity regression $k=5$ with HAC".
6. Verdict cell.

- [ ] **Step 14.2: Execute + commit**

```bash
uv run jupyter nbconvert --to notebook --execute notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb --inplace
git add notebooks/dev_ai_cost_v2/04_r4s3_usd_behavioral.ipynb
git commit -m "notebook(dev_ai_cost_v2): 04_r4s3_usd_behavioral — inverted two-sided test (spec v0.2.1 §2.2.B)"
```

---

## Task 15: Notebook 05 — `05_sensitivity.ipynb` (four diagnostic arms, NO verdict authority)

**Owner:** orchestrator
**Audit-pass chain:** `python-panel-data` + `statsmodels`
**Spec ref:** §2.4, §0.1 CORRECTIONS-K
**Depends on:** Task 14

**Files:**
- Create: `notebooks/dev_ai_cost_v2/05_sensitivity.ipynb`

**Exit criteria:**
- Every cell preamble documents "DIAGNOSTIC ONLY — no verdict authority" (CORRECTIONS-K).
- Four arms implemented exactly as listed in spec §2.4:
  1. Lag $k=5$.
  2. Model-fixed subset (days with single dominant model).
  3. Pre-/post-price-step regime split.
  4. Outlier-trimmed (top/bottom 1% of |Δln Tokens|).
- No arm produces a PASS/FAIL flag.

**Steps:**

- [ ] **Step 15.1: Notebook cells**

Four trios, one per arm, each with the no-verdict-authority preamble.

- [ ] **Step 15.2: Execute + commit**

```bash
uv run jupyter nbconvert --to notebook --execute notebooks/dev_ai_cost_v2/05_sensitivity.ipynb --inplace
git add notebooks/dev_ai_cost_v2/05_sensitivity.ipynb
git commit -m "notebook(dev_ai_cost_v2): 05_sensitivity — four diagnostic arms (spec v0.2.1 §2.4 / CORRECTIONS-K)"
```

---

## Task 16: Pre-verdict Delphi panel via `audit-econ` skill

**Owner:** orchestrator (dispatches Opus sub-agents per `audit-econ`)
**Audit-pass chain:** —
**Spec ref:** §8 row "Pre-verdict end-to-end audit"
**Depends on:** Tasks 11–15

**Files:**
- Create: `scratch/2026-05-16-ai-cost-delphi/<auditor>.md` (one file per dispatched auditor)

**Exit criteria:**
- `audit-econ` Delphi consensus reached across math, econometrics, code, data, proofs auditors.
- Severity-sorted findings list produced.
- All severity ≥ HIGH findings resolved (code fix, notebook re-run, spec patch CORRECTIONS-Y, or documented accept-with-caveat).
- Consensus disposition committed.

**Steps:**

- [ ] **Step 16.1: Invoke `audit-econ` skill**

Pass the skill the spec, the implementation tree, and the executed notebooks 01–05. Skill dispatches independent Opus sub-agents and orchestrates Delphi consensus.

- [ ] **Step 16.2: Resolve findings**

For each ≥HIGH severity finding: fix → re-execute affected notebook(s) → re-verify.

- [ ] **Step 16.3: Commit**

```bash
git add scratch/2026-05-16-ai-cost-delphi/
git commit -m "audit(dev_ai_cost_v2): pre-verdict audit-econ Delphi panel (spec v0.2.1 §8)"
```

---

## Task 17: Verdict memo + LaTeX write-up

**Owner:** orchestrator; Technical Writer reviews
**Audit-pass chain:** `latex-doc` + `latex-econ-model`
**Spec ref:** §8 row "Write-up"
**Depends on:** Task 16

**Files:**
- Create: `memory/project_dev_ai_cost_v2_verdict.md`
- Create: `docs/writeups/2026-XX-XX-ai-cost-factor-model.tex` (date stamped at write time)

**Exit criteria:**
- Verdict memo states R5 numerical output (with CI), R4-S3-COP consistency outcome, R4-S3-USD verdict (REJECT_NULL / FAIL_TO_REJECT / HALT), and impact on (Y, M, X) framework status.
- LaTeX write-up follows the math notation pinned by `latex-econ-model`.
- If R4-S3-USD HALTed at power, verdict memo includes the chosen disposition pivot (A/B/C from Task 3 template).

**Steps:**

- [ ] **Step 17.1: Draft verdict memo per `memory/project_pair_d_phase2_pass.md` precedent style.**

- [ ] **Step 17.2: Draft LaTeX write-up; compile via `latex-doc` skill.**

- [ ] **Step 17.3: Commit**

```bash
git add memory/project_dev_ai_cost_v2_verdict.md docs/writeups/*.tex
git commit -m "verdict(dev_ai_cost_v2): R5 + R4-S3 outcomes (spec v0.2.1)"
```

---

## Self-review against spec (filed by plan author)

**Spec coverage:** every spec §, every CORRECTIONS letter A–W, every Q1–Q4 in §10 is mapped to a task per the coverage table at top of plan.

**Placeholder scan:** no `TBD`, no "implement later", no "appropriate error handling" without showing the code. The polars `dt.weekday()` ordinal note in Task 7.2 is flagged as a verification-on-execute item (not a placeholder).

**Type consistency:** `MessageRecord`, `TokensByCategory`, `DailyNotionalPanel`, `PricingTable`, `JSONLReader`, `JSONLSchemaError`, `build_daily_panel`, `from_litellm_sha` — names match across Tasks 4, 5, 6, 7, 8, and across tests.

**Audit-pass chains:** every code-touching task lists its chain per spec §8.

**Anti-fishing:** N-floor (38), power-floor (0.50), HAC L=⌊T^(1/3)⌋, sign expectations, lag structure, sensitivity-no-verdict — all pinned in tasks 11/13/14/15.

---

## Execution handoff

Plan complete and saved to `docs/plans/2026-05-16-ai-cost-factor-model-plan.md`. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — executing-plans with batch checkpoints.

Which approach?
