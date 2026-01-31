<div align="center">
  <h1>
    Pricing Page A/B Testing: Experiment Design, Statistical Inference & Growth Analytics
  </h1>
</div>

<p align="center">
  <img src="https://img.shields.io/badge/Experimentation-A%2FB%20Testing-blue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Statistics-Causal%20Inference-lightblue?style=flat-square"/>
  <img src="https://img.shields.io/badge/Domain-Growth%20Analytics-success?style=flat-square"/>
</p>

---

## 🧠 Business Problem & Objective

In subscription-based digital products, the pricing page plays a critical role in converting free users into paying customers. Despite a high volume of traffic to the pricing page, only a small fraction of users completes the upgrade to a Premium plan, indicating potential friction or lack of clarity in value communication. 

---

## 🎯 Objective 

The objective of this project was to causally evaluate whether a redesigned pricing page improves the Free-to-Premium conversion rate, while ensuring that user experience and long-term business health (e.g., refunds and churn) are not negatively impacted. 

---

## 📊 Data & Inputs

- Experiment assignment data identifying user exposure to Control (A) or Treatment (B) </br>
- User-level event logs capturing funnel interactions (pricing page views, CTA clicks, checkout starts) </br>
- Subscription lifecycle data including activation, cancellation, and refund signals </br>
- Time-based exposure and conversion windows to ensure correct attribution </br>
- Experiment metadata such as assignment timestamps and variant identifiers renewal

---

## ⚙️ Technical Approach

⭕ Designed a full A/B testing framework with clearly defined population, exposure rules, and attribution logic </br>
⭕ Defined and operationalized primary, secondary, and guardrail metrics to evaluate both success and risk </br>
⭕ Formulated statistical hypotheses and selected appropriate one-tailed tests aligned with business expectations </br>
⭕ Calculated Minimum Detectable Effect, sample size, significance level, and statistical power prior to analysis </br>
⭕ Conducted extensive sanity checks (by SQL) including sample ratio mismatch (SRM), temporal balance, variant exclusivity, and event ordering validation </br>
⭕ Applied z-tests and confidence interval analysis (by Python) to assess statistical significance of observed uplifts </br>
⭕ Analyzed funnel-level metrics to diagnose why the experiment succeeded or failed

---

## 🛠 Key Skills Demonstrated

✅ Experiment design and causal inference using A/B testing </br>
✅ Hypothesis testing, statistical significance, confidence intervals, and power analysis </br>
✅ Metric design (primary, secondary, guardrails) for product experimentation </br>
✅ Funnel analysis and behavioral diagnostics using event-level data </br>
✅ Translating statistical results into clear, decision-oriented product recommendations

---

## 🎥 YouTube Walkthrough
 
https://youtu.be/VppP0DyTpyU
