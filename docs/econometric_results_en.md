# Design C · Destination concentration and subsequent export instability

**The preregistered estimate is positive and imprecise.** A 0.10 increase in the previous year’s non-U.S. destination Herfindahl–Hirschman index (HHI) is associated with **0.0128 more log points** of subsequent absolute annual export change. The restricted Webb bootstrap 95% confidence interval is **−0.0605 to +0.1053 log points**, with a two-sided **p-value of 0.7174**. The interval is compatible with economically meaningful movements in either direction. [Preregistered specification](phase4b_preregistered_specification.md) · [Complete regression table](../data/phase4b/primary_regression.md) · [Primary inference figure](../figures/phase4b/en/01_primary_inference.png) · [Version française](econometric_results_fr.md)

## What the model measures

The unit is a province–NAPCS product section–year cell. The panel covers ten provinces, eleven product sections and outcome start years 2011–2024, with trade endpoints through 2025. The outcome is the absolute difference of log non-U.S. domestic merchandise exports in current Canadian dollars between years `t` and `t+1`. The predictor, log export size and U.S. export share use year `t−1`. Province–product, product–year and province–year fixed effects absorb persistent pair differences and common movements at the product-year and province-year levels. Cells have equal weight. [Statistics Canada, table 12-10-0173-01](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017301)

| Primary model result | Estimate |
| --- | ---: |
| Lagged HHI coefficient, full 0–1 scale | +0.12827 |
| Province-clustered standard error, full scale | 0.36183 |
| Province-clustered p-value (9 degrees of freedom) | 0.73112 |
| Association per +0.10 HHI | +0.01283 log points |
| Province-clustered 95% interval per +0.10 | [−0.06903, +0.09468] |
| Restricted Webb 95% interval per +0.10 | [−0.06049, +0.10525] |
| Observations and province–product groups | 1,454 and 108 |
| Fixed-effect levels, province–product / product–year / province–year | 108 / 154 / 140 |
| Combined fixed-effect rank / full design rank | 368 / 371 |
| Overall / adjusted / within R² | 0.51860 / 0.35414 / 0.00862 |

Of 1,540 possible cells, 1,513 had a valid lagged HHI and positive export endpoints. The prespecified CAD 1 million lagged-portfolio floor reduced that set to 1,454, with no primary fixed-effect singletons. A fully balanced sensitivity retains 98 groups and 1,372 cells. [Eligibility ledger](../data/phase4b/sample_exclusion_ledger.csv) · [Preflight checks](../data/phase4b/preflight.json)

## Magnitude and robustness

The point estimate of 0.0128 log points per 0.10 HHI is small relative to the sample’s median absolute annual change of **0.1633 log points**. The uncertainty permits larger effects than the point estimate suggests. The three regressors account for about **0.9%** of the variation remaining after the fixed effects. This in-sample statistic does not establish forecasting performance. [Model diagnostics](../data/phase4b/primary_diagnostics.json)

The estimate stays near its original value when the metal and non-metallic mineral products section (C14) or the 2025 endpoint is removed. Lagged-value weighting reverses the sign to **−0.0275** log points per 0.10 HHI, with a province-clustered interval of **[−0.0567, +0.0016]**. Signed growth is positive and downside magnitude is negative, with wide intervals for both. The non-overlapping windows and individual province omissions also span different signs. Every registered secondary province-clustered interval includes zero. Equal and value weights target different portfolios, and the estimates do not establish a stable direction across them. [Robustness analysis](robustness_analysis.md) · [Sensitivity figure](../figures/phase4b/en/02_specification_sensitivity.png)

## Implications for export dependence

The descriptive record shows that Canada’s U.S. export share can fall while its non-U.S. export portfolio becomes more concentrated. This regression addresses a different question. Within comparable province–product cells, observed non-U.S. concentration has no precisely estimated relationship with the next annual movement in nominal exports. The evidence does not establish how much a diversification policy would stabilize exports. An HHI shift can reflect larger shipments to a bullion hub, market-specific demand, changing exporters, exchange rates or anticipated volatility. Fixed effects absorb common movements and leave province–product-specific price, quantity and destination shocks unresolved. The fit covers continuing positive non-U.S. portfolios above the lagged size floor and assesses changes in customs value. It does not measure physical export volumes, value-added dependence, or the employment and welfare consequences of shifting trade. [Diversification mechanisms](diversification_mechanisms.md) · [Statistical inference audit](statistical_inference_audit.md)

Design A remains at the legal and data-mapping stage. The core-steel codes and public import mirror are usable for descriptive validation, while policy-clean controls and independent variation remain unverified. [Design A pilot](design_A_tariff_pilot.md)
