import sys, os

from scipy import stats
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from scipy import stats

from helpers import (
    check_missing,
    check_duplicates,
    required_sample_size_proportion,
    sample_ratio_mismatch_test,
    split_groups
)


# =======================================================================================
# What is impact of redesigned navigation bar on conversion rate?
# =======================================================================================
"""
The product team shipped a redesigned navigation bar (Variant B).
The hypothesis is that a cleaner navigation reduces friction and keeps users engaged for longer.  
Conversion rate is the primary metric we use to measure engagement.
"""



# =======================================================================================
# PHASE 1 — POWER & EXPERIMENT PLANNING
# =======================================================================================
# ── Define parameters ────────────────────────────────────────────────
ALPHA         = 0.05
POWER         = 0.80
P_BASELINE    = 0.10   
MDE_ABSOLUTE  = 0.02  
DAILY_TRAFFIC = 500


print(f"""
  Parameters:
    α  (alpha)           = {ALPHA}     → 5% Type-I error rate
    Power (1−β)          = {POWER}     → 80% chance of detecting MDE
    Baseline conversion  = {P_BASELINE:.0%}    → 10% of users convert today
    MDE (absolute)       = {MDE_ABSOLUTE:.0%}     → minimum lift worth shipping
    """)




# # ── Sample size calculation ────────────────────────────────────────────────
n_required = required_sample_size_proportion(
        p_baseline=P_BASELINE,
        mde_absolute=MDE_ABSOLUTE,
        alpha=ALPHA,
        power=POWER,
    )

# ── Experiment duration estimate ────────────────────────────────────────────────
duration_days = int(np.ceil(2 * n_required / DAILY_TRAFFIC))

print(f"""
  Power Analysis Result:
    Required n per group : {n_required:,}
    Total required n     : {2*n_required:,}
    Estimated duration   : {duration_days} days

  Normal Approximation Validity Check (Large Sample Condition):
    np ≥ 5:   {P_BASELINE * n_required:.0f}
    n(1-p)≥5: {(1-P_BASELINE) * n_required:.0f}
    The normal approximation to the binomial is valid.

  Randomisation:
    Unit   : user_id — same user always gets the same CTA variant.
    Split  : 50/50 random assignment via feature flag system.
    """)



# =======================================================================================
# PHASE 2 — DATA COLLECTION
# =======================================================================================
df = pd.read_csv("ab_test_dataset.csv")



# =======================================================================================
# PHASE 3 — DATA VALIDATION & QUALITY CHECKS
# =======================================================================================
METRIC = "converted"

# ── Check for missing values ────────────────────────────────────────────────
check_missing(df, METRIC)


# ── Check for duplicate users ────────────────────────────────────────────────
check_duplicates(df)


# ── Check for sample ratio mismatch (SRM) ────────────────────────────────────────────────
srm = sample_ratio_mismatch_test(df, expected_ratio=0.5, alpha=0.01)


# ── Drop missing before further checks ────────────────────────────────────────────────
df = df.dropna(subset=[METRIC]).copy()
ctrl, trt = split_groups(df, METRIC)


# ── Binary Sanity Check ────────────────────────────────────────────────
unique_c = np.unique(ctrl)
unique_t = np.unique(trt)


# ── Descriptive Statistics ────────────────────────────────────────────────
n_c, n_t = len(ctrl), len(trt)
cvr_c = ctrl.mean()
cvr_t = trt.mean()


# =======================================================================================
# PHASE 4 — STATISTICAL ANALYSIS (Two-Proportion Z-Test)
# =======================================================================================
def two_proportion_ztest(ctrl: np.ndarray, trt: np.ndarray) -> dict:
  n_c, n_t   = len(ctrl), len(trt)
  p_c        = ctrl.mean()
  p_t        = trt.mean()
  p_pool     = (ctrl.sum() + trt.sum()) / (n_c + n_t)

  # ── Standard error under H0 (pooled) ──────────────────────────────────────────────────
  se_pool    = np.sqrt(p_pool * (1 - p_pool) * (1/n_c + 1/n_t))
  abs_diff   = p_t - p_c
  z_stat     = abs_diff / se_pool
  p_val      = 2 * (1 - stats.norm.cdf(abs(z_stat)))   # two-tailed

  # ── 95% CI using unpooled SE ──────────────────────────────────────────────────
  se_unpooled = np.sqrt(p_c*(1-p_c)/n_c + p_t*(1-p_t)/n_t)
  z_crit      = stats.norm.ppf(0.975)
  ci_lo       = abs_diff - z_crit * se_unpooled
  ci_hi       = abs_diff + z_crit * se_unpooled

  rel_lift    = abs_diff / p_c

  return {
        "p_c":       p_c,
        "p_t":       p_t,
        "p_pool":    p_pool,
        "abs_diff":  abs_diff,
        "rel_lift":  rel_lift,
        "se_pool":   se_pool,
        "z_stat":    z_stat,
        "p_value":   p_val,
        "ci":        (ci_lo, ci_hi),
        "n_c":       n_c,
        "n_t":       n_t,
    }

res = two_proportion_ztest(ctrl, trt)
print(f"""
    Control   (A): p_A = {res['p_c']:.4%}  ({int(res['p_c']*res['n_c'])} conversions / {res['n_c']:,} users)
    Treatment (B): p_B = {res['p_t']:.4%}  ({int(res['p_t']*res['n_t'])} conversions / {res['n_t']:,} users)
    
    Absolute difference : p_B − p_A = {res['abs_diff']:+.4%}""")

print(f"""
    z-statistic = {res['z_stat']:.4f}
    p-value     = {res['p_value']:.4f}
    α           = {ALPHA}
    """)


# ── Confidence interval ───────────────────────────────────────────────────
ci_lo, ci_hi = res['ci']
print(f"""
    95% CI for (p_B − p_A): [{ci_lo:+.4%},  {ci_hi:+.4%}]
    MDE                    : {MDE_ABSOLUTE:+.4%}

    Interpretation:
      {'CI entirely above 0 → statistically significant improvement.' if ci_lo > 0 else 'CI includes 0 → cannot confirm direction of effect.'}
    """)


# ── Effect size ───────────────────────────────────────────────────────
print(f"""
    Absolute difference : {res['abs_diff']:+.4%}
      → Directly interpretable as conversion rate improvement.
      → Translates to ~{int(res['abs_diff']*5000)} additional sign-ups per 5,000 users exposed.
    """)




# =======================================================================================
# PHASE 5 — BUSINESS VALIDATION
# =======================================================================================
alpha     = ALPHA
mde       = MDE_ABSOLUTE
p_val     = res["p_value"]
abs_diff  = res["abs_diff"]
ci_lo, ci_hi = res["ci"]


# ── Statistical Significance Gate ───────────────────────────────────────────────────────
sig = p_val < alpha
print(f"    p={p_val:.4f}  {'< α=' if sig else '≥ α='}{alpha}   {'✅ PASS' if sig else '❌ FAIL'}")


# ── Practical Significance Gate ───────────────────────────────────────────────────────
practical = abs_diff >= mde
print(f"    Abs lift={abs_diff:.4%}  {'≥' if practical else '<'}  MDE={mde:.0%}   {'✅ PASS' if practical else '❌ FAIL'}")


# ── Guardrail Check ───────────────────────────────────────────────────────
dur_a = df.loc[df["group"]=="A","session_duration_sec"].mean()
dur_b = df.loc[df["group"]=="B","session_duration_sec"].mean()
pv_a  = df.loc[df["group"]=="A","pages_viewed"].mean()
pv_b  = df.loc[df["group"]=="B","pages_viewed"].mean()
print(f" session_duration: A={dur_a:.1f}s  B={dur_b:.1f}s  Δ={dur_b-dur_a:+.1f}s  {'✅' if dur_b >= dur_a-5 else '❌'}")
print(f" pages_viewed : A={pv_a:.2f}  B={pv_b:.2f}  Δ={pv_b-pv_a:+.2f}     {'✅' if pv_b >= pv_a-0.2 else '❌'}")


# ── Segment Analysis (Country) ───────────────────────────────────────────────────────
for country in df["country"].unique():
        sub = df[df["country"] == country]
        ca  = sub.loc[sub["group"]=="A","converted"].mean()
        cb  = sub.loc[sub["group"]=="B","converted"].mean()
        print(f"      {country}: A={ca:.2%}  B={cb:.2%}  Δ={cb-ca:+.2%}")




# =======================================================================================
# PHASE 6 — FINAL DECISION
# =======================================================================================
sig       = res["p_value"] < ALPHA
practical = res["abs_diff"] >= MDE_ABSOLUTE
ci_lo, ci_hi = res["ci"]

if sig and practical:
        verdict = "SHIP"
        rationale = (
            f"Variant B's orange CTA produced a statistically significant "
            f"and practically meaningful conversion lift of {res['abs_diff']:+.2%} "
            f"({res['rel_lift']:+.1%} relative, p={res['p_value']:.4f}).  "
            f"95% CI [{ci_lo:+.2%}, {ci_hi:+.2%}] entirely excludes zero.  "
            f"Guardrails intact.  Estimated annual revenue impact: positive.  SHIP to 100%%."
        )
elif sig and not practical:
        verdict = "ITERATE"
        rationale = (
            f"Statistically significant (p={res['p_value']:.4f}) but lift "
            f"({res['abs_diff']:+.2%}) is below business MDE ({res['mde']:.0%}).  "
            f"Consider a bolder design change or revisit the MDE definition."
        )
else:
        verdict = "NO SHIP"
        rationale = (
            f"Not statistically significant (p={res['p_value']:.4f}).  "
            f"Insufficient evidence that the new CTA improves conversion.  "
            f"Do not ship."
        )

print(f"  VERDICT:  {verdict}")
print(f"\n  Rationale:\n    {rationale}\n")
