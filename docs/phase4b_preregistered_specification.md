# Phase 4B preregistered specification

This document fixes Design C before coefficient estimation. It follows the scientifically approved Phase 4A design. The primary estimand is a conditional historical association for active Canadian non-U.S. domestic merchandise export portfolios. The protocol fixes a two-sided test of zero association, with a positive directional hypothesis, at the 5% level. The regression outcome is expressed in log points. [Design C](econometric_design_C.md)

## Panel and variables

- Source. Use the pinned November 18, 2026 Toronto-time snapshot of Statistics Canada 12-10-0173-01, with annual reference years 2010–2025. Recalculate Phase 3 exposure from the raw archive and cross-check the hashed Phase 3 extract and the hashed Phase 4A eligibility grid. Partner and world lines follow the same product, customs, flow and producer-geography definitions. The official HHI is a separate aggregate benchmark and cannot replace product-cell HHI. [Annual trade](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017301) · [HHI audit](hhi_reconciliation.md)
- Unit. Ten Canadian provinces × NAPCS sections C11–C19, C21 and C22 × outcome-start years 2011–2024. National, territorial, all-product and special-transaction C23 aggregates are outside the primary universe.
- Outcome. For a province–product portfolio with positive, valid non-U.S. nominal domestic exports at both endpoints, use `abs(log(X[t+1]) − log(X[t]))`. Derive `X` from world minus U.S. exports, in current CAD. Exports dated `t+1` and `t` form the outcome. Regressors are dated `t−1`.
- Predictor. Reconstruct `HHI_exUS[t−1]` as the sum of squared shares of identified non-U.S. partners. Use the world-minus-U.S. denominator. Apply the existing strict reconciliation rules, including a complete, numeric and nonnegative destination partition, the publisher’s rounding tolerance and a zero unallocated residual. Do not replace suppressed or missing flows with zero. A zero reported for a genuinely inactive portfolio stays zero. Rounding-consistent positive amounts retain their published precision.
- Controls and weights. Include `log(X[t−1])` and the U.S. share of world exports at `t−1`, and absorb province×product, product×outcome-start year and province×outcome-start year. Weight cells equally. Fixed effects use the observed cell universe, with a rank-revealing decomposition and redundant indicator columns removed. Report each fixed-effect level count and their combined identified rank.

```
abs(log X[g,k,t+1] − log X[g,k,t]) =
  a[g,k] + b[k,t] + c[g,t] + beta * HHI_exUS[g,k,t−1]
  + gamma1 * log X[g,k,t−1] + gamma2 * US_share[g,k,t−1] + error[g,k,t]
```

## Eligibility and pre-estimation gates

1. Preserve the full expected 1,540-cell ledger with flags for every defect, including missing/trade-unavailable endpoints, genuine zeros, lag portfolio/HHI and control availability. At each source year audit world, U.S. and component statuses, numeric counts, zeros, negative values, unallocated amounts and reconciliation. Record explicit model exclusion reasons. At the outcome endpoints require valid numeric world and U.S. totals and valid differences. Strict partner reconciliation is required at the predictor date to construct HHI.
2. Before estimation the Phase 4A grid contains 1,513 cells with the required HHI and positive endpoints. Within those, the lagged non-U.S. portfolio is CAD 33,900 at the minimum, CAD 211,404 at the 1st percentile, CAD 473,340 at the 2.5th, CAD 1,282,900 at the 5th and CAD 229.87 million at the median (linear sample quantiles). Apply a **CAD 1 million lagged** non-U.S. export floor. It removes 59 thin portfolios before singleton removal and retains all ten provinces. The floor limits the influence of small base years and single shipments without screening on the size of the subsequent outcome. Its level is a design judgment, with explicit sensitivities. In historic Canadian dollars it is a nominal screen.
3. The unequally observed primary panel keeps all otherwise eligible rows. Iteratively remove singleton levels of any absorbed fixed effect and record the iteration and all singleton terms at the time of removal. The balanced sensitivity keeps province–product groups with all 14 start years after the primary floor and eligibility filters. Report its retained groups and rows separately.
4. Before computing coefficients, verify the three slopes add rank after fixed effects and standardization, projected HHI has positive residual sum of squares and standard deviation above 1e-8, the standardized slope matrix condition number is below 1e8, and all ten province clusters retain measured variation. Validate rank using pivoted QR at the standard machine precision cutoff and SVD on the three residualized, scaled slopes. Report partial HHI variation and partial leverage by province. Stop if primary rank, support or the primary inference validation fails. Report high leverage without deleting influential provinces from the primary fit.

## Estimation and statistical inference

Fit least squares by projecting out the fixed-effect space, with SciPy QR for the projection and statsmodels OLS for the residualized fit. Verify against an explicit full-rank dummy regression. Report overall and adjusted R², within R² relative to the fixed-effects-only fit, RMSE using residual degrees of freedom, and exact fixed-effect dimensions.

Use one-way province-clustered CR1 with multiplier `G/(G−1) × (n−1)/(n−rank)` and Student t with `G−1` degrees of freedom. This accounts for within-province serial dependence and multiple products. The companion small-cluster result is a restricted wild cluster bootstrap-t with null imposed, common province multiplier per draw, classic CR1 studentization, six-point Webb weights `±sqrt(1/2), ±1, ±sqrt(3/2)`, 9,999 draws from seed 20261118, and the add-one two-sided tail probability. Keep the same draws for all candidate nulls. For the two-sided 95% confidence set, invert the test using a 481-point scan at the coefficient plus or minus 12 CR1 standard errors and refine each detected boundary with 18 bisections. Report an open or disconnected set if detected in the scanned range. Validate the optimized calculation against literal restricted pseudo-outcome refits and their CR1 t statistics on the genuine panel. Report bootstrap Monte Carlo error near the decision threshold.

Product×year effects absorb common product-year means. Check covariance sensitivity by product clustering and two-way province and product clustering with province×product intersection subtraction and degrees of freedom equal to the smaller marginal cluster count minus one. Check province×product clusters only as a comparison and describe their stronger assumptions. Report invalid or negative sandwich variances transparently. Report province cluster partial leverage, outcome-conditioned influence from full leave-one-province-out refits, and effective support as inverse sum of squared province partial leverage shares. No sign or significance claim depends on a secondary specification. [Cluster inference guide](https://doi.org/10.1016/j.jeconom.2022.04.001) · [Webb weights](https://doi.org/10.1111/caje.12661)

## Prespecified secondary analyses

Each model inherits the primary data and controls unless described below. Report estimates and province-clustered 95% intervals without multiple-testing adjustments or significance claims. A failed design check is reported, with no substitution of another specification after looking at results.

| Check | Prespecified implementation |
| --- | --- |
| A | Remove C14 (the broad metal and non-metallic mineral products section). |
| B | Repeat with a strictly positive lagged portfolio and no extra floor, and with CAD 100,000 and CAD 10 million floors. |
| C | Restrict to complete 14-year province–product panels after primary eligibility and floor. |
| D | Weighted least squares with weights proportional to each observation’s lagged non-U.S. export value, scaled to average one. |
| E | Replace the outcome with signed `log(X[t+1]) − log(X[t])`. |
| F | Use downside magnitude `max(0, −signed growth)` on the full primary sample, keeping genuine zero downside in nondeclining years. |
| G | Replace lagged ex-U.S. HHI individually with the largest non-U.S. share, share of the top three non-U.S. destinations, all-destination HHI, and the number of positive non-U.S. partners. Use the same partner definitions and eligible universe. Interpret share indices per +0.10 and counts per +1 destination. |
| H | End the outcome window in 2024 (start years through 2023). |
| I | Refit once omitting each province. Rebuild the same fixed-effect design and inference for the resulting nine-province panel. |
| J | Use even and odd outcome-start years separately, so no adjacent outcome intervals share a reference year within each fit. Also use two-year outcomes starting in 2011, 2014, 2017, 2020 and 2023, with log-change magnitude divided by two and predictors dated one year before each start. |
| Additional selection check | Report the frequency of a verified zero final observation among portfolios with otherwise eligible lag information and a valid positive start. If there are at least 20 exits across at least five provinces, a linear probability sensitivity uses the same fixed-effect structure. If support is too thin, report coverage only. |

The coefficient is a conditional association for observed merchandise export values. A larger coefficient can reflect output prices, destination demand, firm composition, shipment timing and quantity movements, among other factors. Predictive validity requires a separate out-of-sample exercise. Policy-induced diversification, effects of the United States tariffs, value added and real export risk are outside this estimand.

Design A is a separate legal and mapping pilot with no estimation. Design B remains deferred.
