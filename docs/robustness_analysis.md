# Registered robustness analysis

All 26 planned secondary fits ran. The table reports the partial coefficient scaled to a **+0.10** increase in the concentration measure except in the partner-count row, which uses one additional positive non-U.S. destination. Intervals use each fit’s province-clustered CR1 standard error. The outcome is absolute annual log change unless the table specifies another transformation. The intervals are unadjusted, apply to different samples or outcomes in several rows, and serve as specification diagnostics. [Registered protocol](phase4b_preregistered_specification.md) · [Complete estimates and covariance variants](../data/phase4b/robustness_regressions.csv) · [Sensitivity chart](../figures/phase4b/en/02_specification_sensitivity.png)

| Check | Cells | Groups | Scaled estimate | 95% interval |
| --- | ---: | ---: | ---: | --- |
| Primary, CAD 1m floor | 1,454 | 108 | +0.0128 | [−0.0690, +0.0947] |
| A · Exclude C14 | 1,321 | 98 | +0.0145 | [−0.0764, +0.1054] |
| B · Positive lagged portfolio, no extra floor | 1,512 | 109 | −0.0015 | [−0.0934, +0.0905] |
| B · CAD 100,000 floor | 1,505 | 108 | +0.0124 | [−0.0674, +0.0923] |
| B · CAD 10m floor | 1,270 | 99 | +0.0113 | [−0.0593, +0.0820] |
| C · Complete 14-year groups | 1,372 | 98 | +0.0259 | [−0.0566, +0.1085] |
| D · Lagged-value weights | 1,454 | 108 | −0.0275 | [−0.0567, +0.0016] |
| E · Signed annual growth | 1,454 | 108 | +0.0564 | [−0.0422, +0.1550] |
| F · Downside magnitude | 1,454 | 108 | −0.0218 | [−0.0815, +0.0379] |
| G · Largest non-U.S. share | 1,454 | 108 | +0.0074 | [−0.0461, +0.0609] |
| G · Top-three non-U.S. share | 1,454 | 108 | +0.0111 | [−0.0420, +0.0642] |
| G · HHI including the U.S. | 1,454 | 108 | −0.0032 | [−0.1112, +0.1049] |
| G · One more positive non-U.S. destination | 1,454 | 108 | +0.0009 | [−0.0064, +0.0081] |
| H · Outcome endpoints through 2024 | 1,349 | 107 | +0.0126 | [−0.0693, +0.0944] |
| J · Non-overlap, even start years | 726 | 106 | −0.0057 | [−0.0828, +0.0714] |
| J · Non-overlap, odd start years | 724 | 106 | +0.0355 | [−0.0787, +0.1497] |
| J · Non-overlap, two-year annualized log magnitude | 517 | 106 | −0.0399 | [−0.1288, +0.0491] |

The sections C14 and 2025 endpoint exclusions give similar point estimates to the primary model. That comparison does not separately remove the price, quantity or destination effects of gold. At the alternative portfolio floors, dropping either very small or more modest portfolios gives estimates near zero, with wide intervals. At the CAD 100,000 and no-extra-floor thresholds, iterative singleton removal takes out the one remaining Prince Edward Island C12 cell. [Sample membership for each fit](../data/phase4b/robustness_membership.csv) · [Primary sample diagnostics](../data/phase4b/preflight.json)

The largest notable change in the weighting sensitivity is from +0.0128 to −0.0275 log points. This sample is identical and the weighting changes the estimand toward larger initial portfolios. The sign difference is descriptive evidence of weighting sensitivity. The weighted interval contains zero and its p-value (0.06134, unadjusted) does not change the primary conclusion. Signed growth and downside ask distinct questions. Their different signs, plus the wider intervals in non-overlapping windows, leave the mechanisms unresolved.

## I · Leave-one-province-out

| Province omitted | Cells | Scaled estimate | 95% interval |
| --- | ---: | ---: | --- |
| Alberta | 1,300 | +0.0154 | [−0.0699, +0.1006] |
| British Columbia | 1,301 | +0.0162 | [−0.0699, +0.1024] |
| Manitoba | 1,315 | +0.0291 | [−0.0557, +0.1138] |
| New Brunswick | 1,300 | +0.0329 | [−0.0600, +0.1258] |
| Newfoundland and Labrador | 1,309 | +0.0213 | [−0.0782, +0.1208] |
| Nova Scotia | 1,300 | −0.0075 | [−0.0863, +0.0712] |
| Ontario | 1,301 | +0.0104 | [−0.0781, +0.0989] |
| Prince Edward Island | 1,348 | −0.0077 | [−0.0811, +0.0658] |
| Quebec | 1,300 | +0.0114 | [−0.0716, +0.0945] |
| Saskatchewan | 1,312 | +0.0074 | [−0.0832, +0.0979] |

Dropping Nova Scotia or Prince Edward Island makes the point estimate slightly negative. The range is **−0.0077 to +0.0329** per 0.10 HHI. Every omission leaves a broad interval covering both signs. The main model retains all ten provinces. [Influence and leverage data](../data/phase4b/province_influence.csv) · [Provincial influence chart](../figures/phase4b/en/03_province_influence.png)

## Selection check

The expected grid has nine genuine zero ends. Among the 1,454 cells with a valid HHI and controls, a lagged portfolio of at least CAD 1m, a positive start and an observed end, there are **zero verified exits** by the next annual endpoint. The protocol’s minimum support for a linear probability fit was unmet, so coverage only is reported. This cannot assess destinations or exporters that disappear inside a continuing product portfolio. [Exclusion ledger](../data/phase4b/sample_exclusion_ledger.csv)
