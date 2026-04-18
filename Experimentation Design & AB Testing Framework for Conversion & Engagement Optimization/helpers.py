import numpy as np
import pandas as pd
from scipy import stats


# ─── Power analysis ───────────────────────────────────────────────────────────
def required_sample_size_ttest(baseline_mean: float,
                                mde_absolute: float,
                                std_dev: float,
                                alpha: float = 0.05,
                                power: float = 0.80) -> int:

    z_alpha = stats.norm.ppf(1 - alpha / 2)   # two-tailed
    z_beta  = stats.norm.ppf(power)
    d = mde_absolute / std_dev 
    n = 2 * ((z_alpha + z_beta) / d) ** 2
    return int(np.ceil(n))


def required_sample_size_proportion(p_baseline: float,
                                     mde_absolute: float,
                                     alpha: float = 0.05,
                                     power: float = 0.80) -> int:
    p1      = p_baseline
    p2      = p_baseline + mde_absolute
    p_pool  = (p1 + p2) / 2
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta  = stats.norm.ppf(power)

    numerator   = (z_alpha * np.sqrt(2 * p_pool * (1 - p_pool)) +
                   z_beta  * np.sqrt(p1*(1-p1) + p2*(1-p2))) ** 2
    denominator = (p2 - p1) ** 2
    n = numerator / denominator
    return int(np.ceil(n))



# ─── Data quality checks ──────────────────────────────────────────────────────
def split_groups(df: pd.DataFrame, metric: str) -> tuple:
    ctrl = df.loc[df["group"] == "A", metric].dropna().values
    trt  = df.loc[df["group"] == "B", metric].dropna().values
    return ctrl, trt


def check_missing(df: pd.DataFrame, metric: str) -> None:
    total = len(df)
    n_miss = df[metric].isna().sum()
    pct = 100 * n_miss / total
    status = "WARNING" if pct > 1 else "OK"
    print(f" Missing '{metric}': {n_miss:,} / {total:,} ({pct:.2f}%)  {status}")
    if pct > 1:
        print("Investigate whether missingness is random (MCAR) or group-related.")


def check_duplicates(df: pd.DataFrame) -> None:
    n_dup = df.duplicated(subset="user_id").sum()
    status = "WARNING" if n_dup > 0 else "OK"
    print(f"Duplicate user_ids: {n_dup:,}  {status}")
    if n_dup > 0:
        print("Deduplicate before analysis.")


def sample_ratio_mismatch_test(df: pd.DataFrame,
                                expected_ratio: float = 0.5,
                                alpha: float = 0.01) -> bool:
    n_total = len(df)
    n_ctrl  = (df["group"] == "A").sum()
    n_trt   = (df["group"] == "B").sum()

    expected_ctrl = n_total * expected_ratio
    expected_trt  = n_total * (1 - expected_ratio)

    chi2, p_val = stats.chisquare(
        f_obs=[n_ctrl, n_trt],
        f_exp=[expected_ctrl, expected_trt]
    )

    observed_ratio = n_ctrl / n_total
    print(f"Expected split : {expected_ratio:.1%} / {1-expected_ratio:.1%}")
    print(f"Observed split : {observed_ratio:.2%} / {1-observed_ratio:.2%}")
    print(f"x² = {chi2:.4f},  p = {p_val:.4f}")

    if p_val < alpha:
        print(f"SRM DETECTED (p < {alpha}) -> HALT analysis; fix randomisation. (H1)")
        return True
    else:
        print(f"No SRM detected (p ≥ {alpha}) -> Proceed. (H0)")
        return False


def detect_outliers_iqr(values: np.ndarray,
                         iqr_multiplier: float = 3.0) -> np.ndarray:
    q1, q3  = np.percentile(values, [25, 75])
    iqr     = q3 - q1
    lo      = q1 - iqr_multiplier * iqr
    hi      = q3 + iqr_multiplier * iqr
    return (values < lo) | (values > hi)


def report_outliers(ctrl: np.ndarray,
                    trt:  np.ndarray,
                    metric_name: str) -> None:
    out_c = detect_outliers_iqr(ctrl)
    out_t = detect_outliers_iqr(trt)
    print(f"Outliers in Control (3×IQR): {out_c.sum():,} ({100*out_c.mean():.2f}%)")
    print(f"Outliers in Treatment (3×IQR): {out_t.sum():,} ({100*out_t.mean():.2f}%)")
    if out_c.mean() > 0.02 or out_t.mean() > 0.02:
        print(f">2% outliers — consider winsorising at 99th percentile.")
    else:
        print(f"Outlier rate acceptable.")



# ─── Distribution helpers ─────────────────────────────────────────────────────
def describe_groups(ctrl: np.ndarray, trt: np.ndarray, metric: str) -> None:
    stats_dict = {}
    for label, arr in [("Control (A)", ctrl), ("Treatment (B)", trt)]:
        stats_dict[label] = {
            "n"       : len(arr),
            "mean"    : arr.mean(),
            "median"  : np.median(arr),
            "std"     : arr.std(ddof=1),
            "skew"    : stats.skew(arr),
            "min"     : arr.min(),
            "max"     : arr.max(),
        }
    summary = pd.DataFrame(stats_dict).T
    print(summary.round(4).to_string())


def normality_test(arr: np.ndarray, label: str, alpha: float = 0.05) -> bool:
    n = len(arr)
    if n <= 5000:
        stat, p = stats.shapiro(arr[:5000])  
        test_name = "Shapiro-Wilk"
    else:
        stat, p = stats.normaltest(arr)
        test_name = "D'Agostino-Pearson"

    is_normal = p > alpha
    flag = "Normal" if is_normal else "Non-Normal"
    print(f" {label:20s} — {test_name}: stat={stat:.4f}, p={p:.4f}  [{flag}]")
    return is_normal


def levene_test(ctrl: np.ndarray, trt: np.ndarray, alpha: float = 0.05) -> bool:
    stat, p = stats.levene(ctrl, trt, center="median")
    equal_var = p > alpha
    flag = "Equal variances -> Student t (HO)" if equal_var else " Unequal -> Welch t (H1)"
    print(f"Levene's test: stat={stat:.4f}, p={p:.4f}  [{flag}]")
    return equal_var


# ─── Confidence intervals ─────────────────────────────────────────────────────
def mean_ci_analytical(ctrl: np.ndarray,
                        trt:  np.ndarray,
                        confidence: float = 0.95,
                        equal_var: bool = False) -> tuple:
    
    mean_diff = trt.mean() - ctrl.mean()
    se_diff   = np.sqrt(trt.var(ddof=1)/len(trt) + ctrl.var(ddof=1)/len(ctrl))

    if equal_var:
        # Pooled variance t-distribution
        df_ = len(ctrl) + len(trt) - 2
    else:
        # Welch-Satterthwaite df
        num   = (trt.var(ddof=1)/len(trt) + ctrl.var(ddof=1)/len(ctrl))**2
        denom = ((trt.var(ddof=1)/len(trt))**2 / (len(trt)-1) +
                 (ctrl.var(ddof=1)/len(ctrl))**2 / (len(ctrl)-1))
        df_   = num / denom

    t_crit = stats.t.ppf((1 + confidence) / 2, df=df_)
    lo     = mean_diff - t_crit * se_diff
    hi     = mean_diff + t_crit * se_diff
    return lo, hi

def bootstrap_ci(ctrl: np.ndarray,
                 trt:  np.ndarray,
                 statistic = np.mean,
                 n_boot: int = 10_000,
                 ci: float = 0.95,
                 seed: int = 42) -> tuple:
    
    rng   = np.random.default_rng(seed)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        sample_c = rng.choice(ctrl, size=len(ctrl), replace=True)
        sample_t = rng.choice(trt,  size=len(trt),  replace=True)
        diffs[i] = statistic(sample_t) - statistic(sample_c)

    alpha = 1 - ci
    lo    = np.percentile(diffs, 100 * alpha / 2)
    hi    = np.percentile(diffs, 100 * (1 - alpha / 2))
    return lo, hi

# ─── Effect size ──────────────────────────────────────────────────────────────
def cohens_d(ctrl: np.ndarray, trt: np.ndarray) -> float:
    """
    Interpretation (Cohen, 1988):
      |d| < 0.2  → negligible
      |d| < 0.5  → small
      |d| < 0.8  → medium
      |d| ≥ 0.8  → large

    """
    pooled_std = np.sqrt((ctrl.var(ddof=1) + trt.var(ddof=1)) / 2)
    return (trt.mean() - ctrl.mean()) / pooled_std












# ─── Effect size ──────────────────────────────────────────────────────────────

def rank_biserial_r(u_stat: float, n1: int, n2: int) -> float:
    """
    Rank-biserial correlation r from Mann-Whitney U statistic.

    Interpretation: same scale as Cohen's d thresholds (roughly).
      r = 0.1 → small, 0.3 → medium, 0.5 → large

    WHY:  For non-parametric tests, Cohen's d is inappropriate.
          The rank-biserial r provides an effect size on the [−1, 1] scale
          that is directly interpretable: r=0.3 means treatment observations
          rank higher 65% of the time.
    """
    return 1 - (2 * u_stat) / (n1 * n2)

