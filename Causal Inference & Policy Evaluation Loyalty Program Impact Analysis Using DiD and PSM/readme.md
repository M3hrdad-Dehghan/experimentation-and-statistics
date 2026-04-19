<div align="center">
  <h1>
    Loyalty Program Impact Evaluation: Causal Inference with DiD & Propensity Score Matching
  </h1>
</div>
<p align="center">
  <img src="https://img.shields.io/badge/Causal%20Inference-DiD%20%26%20PSM-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Statistics-ATT%20Estimation-lightblue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Domain-Telecom%20%26%20Churn%20Analytics-success?style=flat-square"/>
</p>

---

## 🧠 Business Problem & Objective

In subscription-based telecom services, customer churn directly impacts revenue and long-term growth. Retention initiatives such as loyalty programs are commonly deployed — but measuring their **true causal impact** is rarely straightforward.

When program enrollment is not random, treated and control customers differ systematically across tenure, spending behavior, and complaint history. This means naive before/after or treated/untreated comparisons are **biased by design**, and can lead to overestimating or underestimating the program's actual effectiveness.

---

## 🎯 Objective

The objective of this project was to build a rigorous causal inference pipeline to estimate the true effect of a loyalty program rollout on customer churn — going beyond simple comparisons to properly account for confounding and selection bias.

Specifically, the project aimed to:

- Identify and control for confounders that bias naive churn comparisons
- Apply quasi-experimental methods suitable for non-randomized program rollouts
- Estimate the Average Treatment Effect on the Treated (ATT) using two complementary approaches
- Validate robustness by cross-checking estimates across methods

---

## 📊 Data & Inputs

- Panel dataset with **pre and post** observations per customer, enabling longitudinal causal analysis
- Customer-level records including:
  - Program enrollment status (treated / control)
  - Churn outcome (binary: churned / retained)
  - Loyalty score (composite eligibility score, 0–100)
- Behavioral and account attributes:
  - Tenure in months
  - Monthly spend ($)
  - Number of service complaints
- Period indicator (pre / post rollout) to support DiD estimation
- Cleaned dataset after handling missing values and ensuring consistent customer-level attribution

---

## ⚙️ Technical Approach

- Constructed a **panel dataset** with pre/post observations per customer to support longitudinal analysis
- Applied **Difference-in-Differences (DiD)**:
  - Modeled churn with OLS regression using `post × treatment` interaction term
  - Isolated program effect from pre-existing group differences and shared time trends
  - Validated parallel trends assumption visually across both groups
- Implemented **Propensity Score Matching (PSM)**:
  - Estimated propensity scores via logistic regression on observed confounders
  - Performed 1:1 nearest-neighbor matching without replacement
  - Assessed covariate balance using Standardized Mean Differences (SMD) before and after matching
  - Confirmed bias reduction across tenure, spend, and complaint variables
- Estimated **ATT** on the matched sample by directly comparing churn rates between treated and matched control customers
- Cross-validated results across DiD and PSM to assess consistency and robustness of causal estimates

---

## 🛠 Key Skills Demonstrated

- **Causal Inference & Quasi-Experimentation**
  - Difference-in-Differences, Propensity Score Matching, ATT estimation
  - Confounding identification and selection bias correction
- **Statistical Modeling**
  - OLS regression with interaction terms, logistic regression for propensity scoring
  - Standardized Mean Difference (SMD) for balance assessment
- **Data Engineering**
  - Panel data construction, longitudinal dataset design, feature engineering
- **Python**
  - End-to-end pipeline: data simulation, regression modeling, matching algorithm, visualization
- **Decision Science**
  - Translating causal estimates into business conclusions about program effectiveness
- **Communication**
  - YouTube walkthrough explaining methodology, assumptions, and results to a technical audience

---

## 🎥 YouTube Walkthrough

......
