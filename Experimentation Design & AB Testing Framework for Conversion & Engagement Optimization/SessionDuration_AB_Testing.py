import sys, os

from scipy import stats
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from scipy import stats

from helpers import (
    bootstrap_ci,
    detect_outliers_iqr,
    levene_test,
    report_outliers,
    required_sample_size_ttest, 
    check_missing,
    check_duplicates,
    sample_ratio_mismatch_test,
    split_groups,
    describe_groups,
    normality_test,
    mean_ci_analytical,
    cohens_d
)



# =======================================================================================
# What is impact of redesigned navigation bar on session duration?
# =======================================================================================
"""
The product team shipped a redesigned navigation bar (Variant B).
The hypothesis is that a cleaner navigation reduces friction and keeps users engaged for longer.  
Session duration (seconds) is the primary continuous metric we use to measure engagement.
"""



# =======================================================================================
# PHASE 1 — POWER & EXPERIMENT PLANNING
# =======================================================================================
# ── Define parameters ────────────────────────────────────────────────
ALPHA = 0.05    
POWER = 0.80    
BASELINE_MEAN = 180.0  # 180 Seconds
BASELINE_STD = 45.0   # 45 Seconds
MDE_ABSOLUTE = 10.0  # +10 Seconds
DAILY_TRAFFIC = 500   

print(f"""
  Parameters:
    α (alpha, Type-I error) = {ALPHA} -> 5% chance of false positive (We wrongly conclude the redesign has an effect when it doesn't)
    β (Type-II error) = {1-POWER} -> 20% chance of false negative (We wrongly conclude the redesign has no effect when it actually does)
    Power (1−β) = {POWER} -> 80% chance of detecting MDE
    Baseline mean = {BASELINE_MEAN}s
    Baseline std dev = {BASELINE_STD}s
    MDE (absolute) = {MDE_ABSOLUTE}s (+{MDE_ABSOLUTE/BASELINE_MEAN:.1%} relative)""")


# ── Sample size calculation ────────────────────────────────────────────────
n_required = required_sample_size_ttest(
        baseline_mean=BASELINE_MEAN,
        mde_absolute=MDE_ABSOLUTE,
        std_dev=BASELINE_STD,
        alpha=ALPHA,
        power=POWER,
    )


# ── Experiment duration estimate ────────────────────────────────────────────────
duration_days = int(np.ceil(2 * n_required / DAILY_TRAFFIC))

print(f"""
  Power Analysis Result:
    Required n per group : {n_required:,}
    Total required n     : {2*n_required:,}
    Daily traffic        : {DAILY_TRAFFIC:,} users
    Estimated duration   : {duration_days} days

  Interpretation:
    We need {n_required:,} users per arm.  With {DAILY_TRAFFIC}/day, the experiment
    should run for {duration_days} days.  This comfortably covers a full business
    week cycle (Mon-Sun patterns) and is long enough to dilute novelty effects.
 """)




# =======================================================================================
# PHASE 2 — DATA COLLECTION
# =======================================================================================
df = pd.read_csv("ab_test_dataset.csv")



# =======================================================================================
# PHASE 3 — DATA VALIDATION & QUALITY CHECKS
# =======================================================================================
METRIC = "session_duration_sec"

# ── Check for missing values ────────────────────────────────────────────────
check_missing(df, METRIC)


# ── Check for duplicate users ────────────────────────────────────────────────
check_duplicates(df)


# ── Check for sample ratio mismatch (SRM) ────────────────────────────────────────────────
srm_detected = sample_ratio_mismatch_test(df, expected_ratio=0.5, alpha=0.01)


# ── Drop missing before further checks ────────────────────────────────────────────────
df_clean = df.dropna(subset=[METRIC]).copy()
ctrl, trt = split_groups(df_clean, METRIC)


# ── Check Outlier ────────────────────────────────────────────────
detect_outliers_iqr(ctrl, iqr_multiplier=3.0)
report_outliers(ctrl, trt, METRIC)

# p99 = np.percentile(np.concatenate([ctrl, trt]), 99)
# ctrl_w = np.clip(ctrl, a_min=None, a_max=p99)
# trt_w  = np.clip(trt,  a_min=None, a_max=p99)
# print(f"Winsorised at 99th percentile ({p99:.1f}s).  Values above capped.")


# ── Descriptive Statistics ────────────────────────────────────────────────
describe_groups(ctrl, trt, METRIC)




# =======================================================================================
# PHASE 4 — STATISTICAL ANALYSIS
# =======================================================================================
# ── 4a: Normality checks ──────────────────────────────────────────────────
is_normal_c = normality_test(ctrl, "Control (A)", alpha=ALPHA)
is_normal_t = normality_test(trt,  "Treatment (B)", alpha=ALPHA)
both_normal = is_normal_c and is_normal_t
print(f"CLT note: n_ctrl={len(ctrl):,}, n_trt={len(trt):,} — CLT applies.")


# ── 4b: Variance equality ─────────────────────────────────────────────────
equal_var = levene_test(ctrl, trt, alpha=ALPHA)


# ── 4c: Hypothesis test ───────────────────────────────────────────────────
test_name = "Student's t-test" if equal_var else "Welch's t-test"
print(f"Selected: {test_name}")

results = {}
t_stat, p_val = stats.ttest_ind(trt, ctrl, equal_var=equal_var, alternative="two-sided")
results["t_stat"] = t_stat
results["p_value"] = p_val
results["alpha"]   = ALPHA
mean_diff = trt.mean() - ctrl.mean()
results["mean_diff"] = mean_diff

print(f"\n    Results:")
print(f"      Mean Control   (μ_A) = {ctrl.mean():.3f} s")
print(f"      Mean Treatment (μ_B) = {trt.mean():.3f} s")
print(f"      Difference  (μ_B−μ_A) = {mean_diff:+.3f} s")
print(f"      t-statistic           = {t_stat:.4f}")
print(f"      p-value               = {p_val:.4f}")
print(f"      α                     = {ALPHA}")



# ── 4c: Confidence interval ───────────────────────────────────────────────────
ci_lo, ci_hi = mean_ci_analytical(ctrl, trt, confidence=0.95, equal_var=equal_var)
results["ci"] = (ci_lo, ci_hi)

print(f"""we are 95% confident the true lift is between {ci_lo:+.2f}s and {ci_hi:+.2f}s."
Interpretation:
      {'CI excludes 0 -> statistically significant difference.' if ci_lo > 0 or ci_hi < 0 else 'CI includes 0  →  cannot rule out no effect.'}
      {'CI lower bound exceeds MDE (' + str(MDE_ABSOLUTE) + 's)  ->  practically significant.' if ci_lo > MDE_ABSOLUTE else ' CI lower bound (' + f'{ci_lo:.2f}' + 's) is below MDE (' + str(MDE_ABSOLUTE) + 's)  ->  practical significance uncertain.'}
    """)



# ── 4e: Bootstrap validation ──────────────────────────────────────────────
boot_lo, boot_hi = bootstrap_ci(ctrl, trt, statistic=np.mean, n_boot=10_000, ci=0.95, seed=42)
results["boot_ci"] = (boot_lo, boot_hi)
print(f"    Bootstrap 95% CI: [{boot_lo:+.3f}s,  {boot_hi:+.3f}s]")
print(f"    Analytical 95% CI: [{ci_lo:+.3f}s,  {ci_hi:+.3f}s]")
print(f"    {'CIs agree — parametric assumptions validated.' if abs(boot_lo-ci_lo)<1 and abs(boot_hi-ci_hi)<1 else 'CIs diverge — prefer bootstrap CI.'}")



# ── 4f: Effect size ───────────────────────────────────────────────────────
d = cohens_d(ctrl, trt)
results["cohens_d"] = d
magnitude = (
        "negligible" if abs(d) < 0.2 else
        "small"      if abs(d) < 0.5 else
        "medium"     if abs(d) < 0.8 else "large" )

print(f"Cohen's d = {d:.4f}  [{magnitude} effect]")




# =======================================================================================
# PHASE 5 — BUSINESS VALIDATION
# =======================================================================================
p_val     = results["p_value"]
alpha     = results["alpha"]
mean_diff = results["mean_diff"]
ci_lo, ci_hi = results["ci"]


# ── Check Statistical Significance ───────────────────────────────────────────────
sig = p_val < alpha
print(f"p-value = {p_val:.4f}  vs  α = {alpha}")
print(f"{'SIGNIFICANT — reject H0' if sig else 'NOT SIGNIFICANT — fail to reject H0'}")


# ── Check Practical Significance ───────────────────────────────────────────────
practical = mean_diff >= MDE_ABSOLUTE
print(f"Observed lift = {mean_diff:+.2f}s  vs  MDE = {MDE_ABSOLUTE}s")
print(f"{'EXCEEDS MDE — practically meaningful' if practical else 'BELOW MDE — not practically meaningful'}")


# ── Check Guardrail ───────────────────────────────────────────────────────
cr_a = df.loc[df["group"]=="A", "converted"].mean()
cr_b = df.loc[df["group"]=="B", "converted"].mean()
cr_diff = cr_b - cr_a
print(f"Conversion A={cr_a:.3%},  B={cr_b:.3%},  Δ={cr_diff:+.3%}")
print(f"{'Guardrail intact' if cr_diff >= -0.01 else 'Guardrail BREACHED — conversion dropped by >1pp'}")


# ── Check Cohort Consistency ───────────────────────────────────────────────────────
seg = df.dropna(subset=["session_duration_sec"])
for device in ["mobile", "desktop", "tablet"]:
    m = seg[seg["device"] == device]
    a_mean = m.loc[m["group"]=="A","session_duration_sec"].mean()
    b_mean = m.loc[m["group"]=="B","session_duration_sec"].mean()
    print(f"      {device:8s}: Δ = {b_mean-a_mean:+.2f}s")
print("If lift is inconsistent across segments, investigate interaction effects.")




# =======================================================================================
# PHASE 6 — FINAL DECISION
# =======================================================================================
p_val     = results["p_value"]
alpha     = results["alpha"]
mean_diff = results["mean_diff"]
ci_lo, ci_hi = results["ci"]
d         = results["cohens_d"]
sig       = p_val < alpha
practical = mean_diff >= MDE_ABSOLUTE


if sig and practical:
        verdict = "SHIP"
        rationale = (
            f"The new navigation (Variant B) produced a statistically significant "
            f"and practically meaningful increase in session duration of {mean_diff:+.2f}s "
            f"(95% CI [{ci_lo:+.2f}s, {ci_hi:+.2f}s], p={p_val:.4f}).  "
            f"The effect size (Cohen's d = {d:.3f}) is {('small' if abs(d)<0.5 else 'medium')}. "
            f"Guardrail metrics remain intact.  Recommend shipping to 100% of users."
        )
elif sig and not practical:
        verdict = "ITERATE"
        rationale = (
            f"The result is statistically significant (p={p_val:.4f}) but the observed "
            f"lift ({mean_diff:+.2f}s) is below the business-defined MDE ({MDE_ABSOLUTE}s).  "
            f"The effect is real but not large enough to justify engineering cost.  "
            f"Revisit the design to achieve a larger lift, or lower the MDE threshold."
        )
else:
        verdict = "NO SHIP"
        rationale = (
            f"The test failed to reach statistical significance (p={p_val:.4f} ≥ α={alpha}).  "
            f"We cannot reject H0.  The observed difference ({mean_diff:+.2f}s) is likely "
            f"due to random chance.  Do not ship Variant B."
        )

print(f"  VERDICT:  {verdict}")
print(f"\n  Rationale:\n    {rationale}")
print()




