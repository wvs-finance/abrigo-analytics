# Wave-1 v0.3 Re-Review — Math Quality (MQ) Verdict

**Reviewer**: Math Quality (MQ)
**Spec**: stochastic-FX variant v0.3 (commit `9906ffa`)
**Prior v0.2 verdict**: BLOCK — NEW-BLOCK-MQ-4 (§4.2 GBM `E[σ_T]` missing `− 1` correction)
**Scope (narrow, per my own v0.2 note)**: §4.2 GBM `E[σ_T]` formula correctness + σ→0 trivial-degenerate limit. OU/Merton/architecture/anti-fishing all out of scope.

---

## Verdict: **ACCEPT**

NEW-BLOCK-MQ-4 is **closed**.

## Q1 — Is the corrected §4.2 GBM formula mathematically right?

**Yes.** Spec v0.3 reads:

```
E[σ_T] = (X̄/Ȳ)² · [ (e^{σ²T} − 1)/(σ²T) − 1 ]    (exact)
       ≈ (X̄/Ȳ)² · σ²T/2                          (leading order)
```

Set `u ≔ σ²T`. The bracket factor `B(u) = (e^u − 1)/u − 1` has the elementary power series

```
e^u            = 1 + u + u²/2 + u³/6 + u⁴/24 + …
(e^u − 1)/u    = 1 + u/2 + u²/6 + u³/24 + …
(e^u − 1)/u − 1 =      u/2 + u²/6 + u³/24 + …
```

Therefore `B(u) = u/2 + O(u²)`, exactly matching the spec's leading-order claim `σ²T/2`. The `− 1` correction is present and correct; the formula is consistent with what I recommended in the v0.2 block.

**Numerical sanity** (T = 1):

| σ    | u = σ²T | B(u) exact     | σ²T/2          | rel err |
|------|---------|----------------|----------------|---------|
| 0.01 | 1.0e-04 | 5.000167e-05   | 5.000000e-05   | +0.00%  |
| 0.05 | 2.5e-03 | 1.251042e-03   | 1.250000e-03   | +0.08%  |
| 0.10 | 1.0e-02 | 5.016708e-03   | 5.000000e-03   | +0.33%  |
| 0.30 | 9.0e-02 | 4.638093e-02   | 4.500000e-02   | +3.07%  |

Confirms the `O(u²)` remainder grows monotonically; leading-order approximation is appropriate for the small-σ²T regime the spec invokes it in.

## Q2 — Does the σ→0 trivial-degenerate limit now hold?

**Yes.** From the power series above, `lim_{u→0} B(u) = 0`, hence

```
lim_{σ→0} E[σ_T] = (X̄/Ȳ)² · 0 = 0
```

which is the required degenerate-limit behaviour (FX path collapses to a point mass at `x_0`; realized vol is identically zero). The v0.2 pathology — non-vanishing limit `(X̄/Ȳ)² · 1` driven by the missing `− 1` — is eliminated.

## Out-of-scope items (not re-reviewed)

- OU `E[σ_T]` and Merton-jump `E[σ_T]`: previously APPROVED at v0.2; carried forward unchanged.
- Architecture / pin coverage / anti-fishing posture: preserved per spec preamble; not re-examined.
- FLAG-RC-1-v2 closure: RC's lane.

## Flags raised: **none**

No new MQ findings. v0.2 BLOCK is fully remediated by the single-line correction in §4.2. MQ lane is clean for Wave-1 v0.3.
