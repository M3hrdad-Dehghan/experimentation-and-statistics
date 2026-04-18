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

In subscription-based digital products, the pricing page plays a critical role in converting free users into paying customers. Despite high traffic, conversion rates often remain low due to friction in navigation, unclear value propositions, or suboptimal user experience.  

Without a rigorous experimentation framework, product decisions are often driven by intuition rather than evidence, increasing the risk of shipping ineffective or harmful changes.

---

## 🎯 Objective 

The objective of this project was to design and implement a robust A/B testing framework to evaluate whether a redesigned pricing experience improves Free-to-Premium conversion, while ensuring no negative impact on user engagement or key behavioral metrics.

Specifically, the project aimed to:

- Quantify the causal impact of design changes on conversion rate  
- Ensure statistical validity through proper experiment design (power, MDE, sample size)  
- Monitor guardrail metrics (e.g., session duration, engagement) to prevent regressions  
- Support data-driven product decisions using both statistical and practical significance  

---

## 📊 Data & Inputs

- Experiment assignment data identifying user exposure to Control (A) or Treatment (B)  
- User-level metrics including:
  - Conversion outcome (binary: converted / not converted)  
  - Session duration (seconds)  
  - Pages viewed  
- Behavioral attributes such as:
  - Device type  
  - Country  
- Cleaned and validated dataset after:
  - Handling missing values  
  - Removing duplicate users  
- Experiment structure ensuring consistent exposure and attribution  

---

## ⚙️ Technical Approach

- Designed experiment planning framework including:
  - Minimum Detectable Effect (MDE)  
  - Statistical power (80%)  
  - Sample size estimation  

- Implemented data validation and quality checks:
  - Missing value detection  
  - Duplicate user validation  
  - Sample Ratio Mismatch (SRM) testing  

- Conducted statistical analysis:
  - Two-proportion z-test for conversion rate comparison  
  - Independent t-test for engagement metrics (session duration)  
  - Variance testing using Levene’s test  

- Estimated uncertainty and effect size:
  - Analytical confidence intervals  
  - Bootstrap confidence intervals  
  - Effect size (Cohen’s d)  

- Integrated guardrail metrics:
  - Session duration  
  - Pages viewed  
  - Ensured no negative impact on engagement  

- Performed segmentation analysis:
  - Country-level comparison  
  - Device-level behavior differences  

- Developed decision framework:
  - Statistical significance (p-value < α)  
  - Practical significance (lift ≥ MDE)  
  - Final decision: SHIP / ITERATE / NO-SHIP  

---

## 🛠 Key Skills Demonstrated

- **Experimentation & Statistics**
  - A/B testing, hypothesis testing, power analysis  
  - Confidence intervals and effect size estimation  

- **Data Validation**
  - SRM detection, data quality checks, outlier handling  

- **Python & SQL**
  - Data processing and statistical analysis pipelines  

- **Product Analytics**
  - Conversion optimization and engagement measurement  
  - Guardrail metric design  

- **Decision Science**
  - Translating statistical outputs into actionable business decisions  

---

## 🎥 YouTube Walkthrough

https://youtu.be/tJMI38cwYRw
