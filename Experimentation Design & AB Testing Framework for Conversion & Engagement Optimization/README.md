<div align="center"> <h1> Pricing Page A/B Testing: Experiment Design, Statistical Inference & Growth Analytics </h1> </div> <p align="center"> <img src="https://img.shields.io/badge/Experimentation-A%2FB%20Testing-blue?style=flat-square"/> <img src="https://img.shields.io/badge/Statistics-Causal%20Inference-lightblue?style=flat-square"/> <img src="https://img.shields.io/badge/Domain-Growth%20Analytics-success?style=flat-square"/> </p>
🧠 Business Problem & Objective

In subscription-based digital products, the pricing page plays a critical role in converting free users into paying customers. Despite high traffic, conversion rates often remain low due to friction in navigation, unclear value propositions, or suboptimal user experience.

Without a rigorous experimentation framework, product decisions are frequently driven by intuition rather than evidence, increasing the risk of shipping ineffective or harmful changes.

🎯 Objective

The objective of this project was to design and implement a robust A/B testing framework to evaluate whether a redesigned pricing experience improves Free-to-Premium conversion, while ensuring no negative impact on user engagement or key behavioral metrics.

Specifically, the project aimed to:

Quantify the causal impact of design changes on conversion rate
Ensure statistical validity through proper experiment design (power, MDE, sample size)
Monitor guardrail metrics (e.g., session duration, engagement) to prevent regressions
Support data-driven product decisions using both statistical and practical significance
📊 Data & Inputs
Experiment assignment data identifying user exposure to Control (A) or Treatment (B)
User-level metrics including conversion outcome (binary), session duration, and pages viewed
Behavioral attributes such as device type and geographic segmentation
Time-based experiment data ensuring consistent exposure and attribution
Cleaned and validated dataset after handling missing values and duplicate users
⚙️ Technical Approach
Designed experiment planning framework including Minimum Detectable Effect (MDE), statistical power (80%), and sample size estimation
Implemented data validation pipelines including missing value checks, duplicate detection, and Sample Ratio Mismatch (SRM) testing
Applied two-proportion z-tests to evaluate differences in conversion rates between control and treatment groups
Conducted t-tests for continuous engagement metrics (e.g., session duration) with variance checks (Levene’s test)
Computed confidence intervals (analytical and bootstrap) to quantify uncertainty and validate assumptions
Integrated guardrail metrics (session duration, pages viewed) to ensure no degradation in user experience
Performed segmentation analysis (e.g., by country and device) to validate consistency of treatment effects
Built a decision framework combining p-values, confidence intervals, and MDE thresholds to determine SHIP / ITERATE / NO-SHIP outcomes
🛠 Key Skills Demonstrated
Experimentation & Statistics: A/B testing, hypothesis testing, power analysis, confidence intervals, effect size estimation
Data Validation: SRM detection, data quality checks, outlier handling, and sanity validation
Python & SQL: Statistical analysis pipelines and data processing
Product Analytics: Conversion optimization, engagement measurement, and guardrail design
Decision Science: Translating statistical outputs into actionable business decisions
🎥 YouTube Walkthrough

.......
