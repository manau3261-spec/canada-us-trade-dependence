# Canada Is Trading Less with the U.S. — But Is It Really Becoming Less Dependent?

**Manau Salaun** · Graduate Student in Economics, Université de Sherbrooke  
Independent Applied Economics Research · Academic affiliation provided for identification  
Working paper · November 2026

Annual domestic merchandise trade, 2010–2025 · Verified monthly update through September 2026

## Abstract

Canada’s United States share of domestic merchandise exports declined from **{{US24}}% in 2024 to {{US25}}% in 2025**. The exports that gained weight outside the United States became less evenly distributed across destinations. Non-U.S. exports grew by CAD {{NON_US_CHANGE}} billion in current dollars. Unwrought non-monetary gold and crude petroleum accounted for **{{GOLD_CRUDE_PCT}}%** of that net increase. The reconstructed non-U.S. destination Herfindahl–Hirschman index (HHI) rose from {{HHI24}} to {{HHI25}}. Excluding unwrought gold, it rose only from {{EX_GOLD24}} to {{EX_GOLD25}}. The United Kingdom’s importance is particularly sensitive to this exclusion.

A preregistered, three-way fixed-effect model relates lagged non-U.S. destination concentration to the subsequent absolute annual log change in nominal non-U.S. exports. It covers {{N}} province–product–year cells in {{G}} groups. A 0.10 higher HHI is associated with **+{{SCALED}} log points**, with a restricted Webb bootstrap 95% interval of **[{{LOW}}, +{{HIGH}}]** and **p = {{P}}**. Value weighting and alternative outcomes change the sign of the point estimate. A separate March 2025 steel tariff mapping pilot verifies legal scope and import data, and finds insufficient comparison support for estimation. The evidence establishes a reallocation of nominal export value and leaves the effect of diversification on economic vulnerability unresolved.

*Keywords:* Canada, United States, trade dependence, export concentration, nominal volatility, commodity composition.  
*JEL:* F14, F15, F40, C23.

## Executive summary

- **The change in the U.S. share was {{US_DPP}} percentage points.** Canada exported CAD {{WORLD25}} billion of domestic merchandise in 2025, including CAD {{US25_CAD}} billion to the U.S. and CAD {{NON_US25}} billion to other destinations. In the separate monthly series, the U.S. share fell from {{MONTH25}}% to {{MONTH26}}% between the same January–September windows in 2025 and 2026. U.S.-bound value grew in that matched comparison.
- **Less weight on one dominant market can coexist with greater concentration among the alternatives.** The United Kingdom’s share of Canada’s non-U.S. exports increased from {{UK24}}% to {{UK25}}%. Its CAD {{UK_CHANGE}} billion increase included CAD {{UK_GOLD}} billion from unwrought gold. Removing that line largely attenuates the increase in non-U.S. HHI and makes the U.K. share edge down.
- **Exposure varies with the denominator.** New Brunswick leads by the U.S. share of gross exports in 2025, while Ontario leads by the dollar value exposed. Gross exports, gross exports divided by GDP, and domestic value added attributable to U.S. demand answer different economic questions.
- **Uncertainty dominates the estimated relationship.** The HHI coefficient is +{{BETA}} on the full 0–1 scale. The confidence interval spans both signs. The regression is associational, and its membership rules apply to active, adequately measured merchandise portfolios. It leaves policy effects, real quantities, output and welfare open.
- **A tariff schedule is insufficient for realized exposure.** The steel pilot maps {{PILOT_LINES}} U.S. reporting lines, with just two complete post months in the original regime. Preference treatment, stacking, overlapping trade remedies and sparse comparison trade prevent a defensible effect estimate.

## 1. Introduction and motivation

A decrease in the fraction of exports sold to a dominant partner often reads as progress toward diversification. The denominator can make this interpretation misleading. If a boom in one high-value commodity raises shipments to a single alternative destination, the U.S. share falls even as the remaining portfolio becomes more concentrated. Prices and trading hubs can shift customs values without a proportional relocation of final demand or production. The economic question is therefore which exposures have diminished, for which provinces and products, and whether the remaining allocation of export markets is associated with a more stable path.

We address three questions. First, how broad and durable is the fall in the U.S. share when measured using comparable domestic merchandise exports? Second, how do products, destinations and selected physical quantities explain the 2024–2025 movement? Third, is past concentration within non-U.S. markets associated with subsequent export instability within comparable province–product portfolios? A separate steel pilot asks whether a major 2025 tariff can be mapped into a defensible future research design. It does not estimate a tariff effect.

The paper contributes a consistent customs-vintage analysis of the dominant-partner share and the conditional non-U.S. HHI. It reconstructs both country weights and detailed commodity contributions, checking where the concentration benchmark agrees with published statistics and where it does not. The econometric exercise prespecifies the sample, controls and inference and makes weak and contradictory results visible. Together, these steps separate measurable changes in recorded trade values from stronger claims about resilience.

## 2. Canadian economic and trade context

Canadian merchandise production and shipment decisions respond to customer proximity, border logistics, product specialization and integrated production across the U.S. and Canada. A single high national share can therefore reflect very different relationships. Energy and transport equipment may depend on destination-specific infrastructure, standards or production linkages. Other products can be routed through major overseas hubs. These distinctions affect the time and cost of redirecting shipments and the interpretation of partner labels.

The U.S. domestic merchandise export share was about 74.7% in 2010 and reached {{US23}}% in 2023, the highest year in the project window. The 2025 observation is the lowest year in that window. In annual current-dollar terms, exports to the U.S. declined by 5.8% from 2024 to 2025, non-U.S. exports grew by 16.5%, and world exports declined by 0.4%. This combination distinguishes a change in market weights from an across-the-board Canadian export expansion.

The monthly follow-up offers a different decomposition. In January–September 2026, U.S.-bound current-dollar shipments rose about 3.4% from the same months of 2025 while shipments elsewhere rose about 33.6%. Both sides grew in the monthly comparison. Monthly estimates are unadjusted for seasonality and drawn from a different source table; the matched windows support a like-month comparison. It would be inappropriate to combine the monthly total with the annual series to construct a substitute 2025 or partial 2026 annual observation. Policy timing, invoicing, commodity prices and changing demand remain plausible explanations for the recent mix.

{{fig:monthly}}

## 3. Literature and economic mechanism

Portfolio logic helps explain why destination shares matter. If receipts in different destinations face partly independent shocks, distributing sales more evenly can reduce exposure to a shock in any one market. Under an illustrative model with common variances and independent market shocks, the normalized portfolio variance is proportional to the sum of squared market weights. With heterogeneous risks or correlated destination shocks, it is proportional instead to a quadratic form in the weights and the covariance matrix. Two portfolios with identical HHI can therefore carry very different risks. The index summarizes the allocation of realized nominal values; it cannot recover the covariance matrix of future demand shocks.

Koren and Tenreyro (2007) distinguish different sources of aggregate volatility, including sector composition and country-specific shocks. Di Giovanni and Levchenko (2010) develop a risk-content measure that combines export specialization with sector risk. Haddad et al. (2013) find that diversification conditions the relationship between trade openness and growth volatility in cross-country data. These findings motivate heterogeneity and the possibility of stabilizing effects. Their outcomes, observation units and identification differ from this paper’s annual nominal customs portfolio. They do not imply a particular coefficient for Canada’s province–product panel.

Cadot, Carrère and Strauss-Kahn (2011) distinguish reallocations among existing export lines from adding new lines. The distinction is useful here. A larger value going to a known partner, an additional reporting line and an increase in exports spread evenly across partners are different margins. A destination count can rise while the HHI rises if a dominant partner takes a larger share. The paper therefore shows largest and top-three shares, the number of positive partners and a commodity exclusion alongside HHI.

A second distinction concerns production. Hummels, Ishii and Yi (2001) document the use of imported inputs in exported goods. Along a production chain the gross value of a shipment can exceed the domestic value created at the production stage. That observation motivates use of domestic value-added benchmarks with a separate denominator. It also cautions against interpreting a customs measure as the contribution of trade to GDP or the share of Canadian employment exposed to a U.S. policy.

Finally, fixed effects can reduce some exposure to omitted common shocks, and clustered inference can address specified residual dependence. Neither element by itself turns past concentration into exogenous assignment. MacKinnon, Nielsen and Webb (2023) emphasize choosing meaningful clusters and examining leverage; Webb (2023) describes a six-point alternative for few-cluster bootstrap inference. Those methods discipline the uncertainty reported here. Their assumptions remain substantive, especially with ten provinces and shared product markets.

## 4. Data sources and construction

The annual core is Statistics Canada table 12-10-0173-01, at producing province or territory, NAPCS product section and partner. The analysis filters to domestic merchandise exports and uses world and U.S. controls from the same reference period and cell. Re-exports are excluded. Values are current Canadian dollars on a customs basis. Province of production differs from port of exit, and country of last known destination can differ from place of use or end buyer.

The annual extract runs from 2010 to 2025. The dedicated recent table 12-10-0175-01 is used from January 2025 through September 2026. The project keeps the two frequencies separate. An archived 2020 comparison reproduced annual-to-monthly additivity where a newer active monthly vintage did not. The evidence ties the 2020 discrepancy to the newer monthly vintage, with the exact publisher operation unresolved. The annual dataset anchors historical inference. Recent monthly data are used for like-month descriptive comparisons.

Table 12-10-0129-01 supplies published destination concentration ratios. We compare those ratios with a reconstruction from annual bilateral trade using the same reported period. Rebased index series are excluded from that comparison. The granular 2024 and 2025 CIMT domestic export archives cover 2,556,556 monthly HS8 records across national subgroups and are aggregated only once to HS6 and destination. The 2024 and 2025 world and U.S. aggregates from this detail match the four corresponding annual controls to within CAD 169. Comparable HS8 quantities require positive quantities for every positive-value line and one common nonblank unit across years.

Current-price provincial GDP in table 36-10-0711-01 supports gross-export-intensity ratios through 2023 in the pinned data. Values for later years are left blank in that calculation. Table 12-10-0100-01 supplies a separate domestic value-added and employment attribution to foreign demand. Its national comparison is available through 2024; the comparable subnational series covers 2013–2022. Canada’s 2023–2024 benchmarks use advanced modelled estimates. Table 14-10-0022-01 supplies employment coverage diagnostics; it is not used to estimate an employment model. NAICS industry classifications and NAPCS shipped-product sections cannot be equated without a verified concordance.

All results use a locked research vintage. Data provenance records fix the archive hashes and preserve the Phase 3–4B source outputs. Unavailable, invalid or suppressed values remain unavailable. Genuine reported zeros retain their meaning. A missing entry in the detailed CIMT change file contributes no published amount to reconciled changes, and this arithmetic convention does not demonstrate that the actual trade flow was zero or support imputing an econometric observation.

{{table:sources}}

## 5. Definitions of dependence and diversification

Let X(g,k,d,t) be domestic merchandise exports in current CAD from geography g, for product k and recorded destination d in reference period t. The U.S. share divides X destined for the U.S. by the world total at the same grain. Its complement is the non-U.S. share of world exports. The level of gross shipments provides a separate scale measure. The value of exports divided by GDP describes gross exposure relative to economic size, even though the numerator includes embodied inputs. It has neither the accounting identity nor the denominator of a domestic value-added share.

Destination HHI is the sum of squared destination shares. The all-destination HHI uses world exports; the non-U.S. HHI removes the U.S. from both the sum and the denominator. If the published partners form a complete partition, the two have an exact relationship.

`HHI(all) = s(US)² + (1 − s(US))² × HHI(ex-US).`

This identity shows how a falling U.S. share can reduce all-destination concentration while concentration among the alternatives rises. The measures retain the exact U.S. label; sensitivity tests for separately listed U.S. areas are reported in the reconciliation. A positive unallocated destination prevents a strict reconstruction. The measure is on the unit scale, and larger values indicate greater concentration. It is sensitive to large values and complements the count of partners with positive trade and the shares of the largest markets.

The phase 4B outcome differs from both HHI measures. It is a realized absolute annual log change, a proxy for instability that captures both large positive movements and contractions. It does not recover a conditional variance, endpoint quantity change, or probability of a future shock. The signed and downside specifications help show what is lost when the magnitude is used alone.

## 6. Provincial and product exposure

The national trend makes the decline in the U.S. share visible. Its regional distribution is uneven. In 2025, New Brunswick leads by share (90.4%), followed by Yukon (87.4%) and Alberta (85.4%). Ontario leads in U.S.-bound value at CAD 189.5 billion, followed by Alberta at CAD 152.0 billion. Together they supply approximately 66.2% of national U.S.-bound domestic exports. A province can rank highly in dollars without ranking first in the local share; each comparison answers a different exposure question.

Newfoundland and Labrador’s share declined from 50.4% in 2024 to 34.2% in 2025. Small territorial portfolios are particularly sensitive to individual large shipments. The far lower reported shares in the Northwest Territories and Nunavut in 2025 cannot be generalized to stable insulation from U.S. demand. National results and subnational charts include territories where coverage allows. The estimation universe excludes them under the approved protocol and keeps the ten provinces.

The product contrast is equally sizeable. In 2025 national U.S. shares were 93.4% for motor vehicles and parts, 84.9% for chemicals, plastics and rubber, and 84.4% for energy. Shares of metal ores and non-metallic minerals (22.0%) and farm, fishing and intermediate food (46.4%) were much lower. Energy was the largest broad merchandise category by world value at CAD 188.6 billion. A high exposure share in an important product group can magnify a border shock, while substitution possibilities and input sourcing determine its practical consequences.

In 2023, New Brunswick’s gross U.S. exports were 37.2% of provincial current-dollar GDP, followed by Alberta at 35.5% and Saskatchewan at 26.2%. In the 2022 supply-and-use comparison, Alberta’s domestic value-added share attributable to U.S. demand was 33.7%, Saskatchewan’s 25.0% and Ontario’s 14.2%. Nationally in 2024 the corresponding value-added share was 15.9%, and approximately 12.1% of jobs were attributable in the modelled benchmark. Each number reflects a different reference year, scope and denominator. Policy analysis should maintain that distinction when prioritizing regional support or evaluating trade risk.

{{fig:national}}

{{fig:ranking}}

{{fig:province_heat}}

{{fig:product}}

## 7. Decomposing the 2024–2025 change

A midpoint identity decomposes the annual U.S. share into changes in product weights and changes in U.S. shares within product sections. Across all sections, the {{US_DPP}} percentage-point movement consists of −3.21 points from within-section U.S. shares and −0.90 points from product composition. Energy has the largest net contribution at −1.64 points. The midpoint averages allocate the interaction symmetrically. This is an accounting decomposition of a share, separate from the contribution of HS goods to the growth of non-U.S. value.

The latter exercise sums the 2024–2025 changes at the detailed HS6 level across non-U.S. destinations. Unwrought non-monetary gold (HS 710812) added CAD {{GOLD}} billion, crude petroleum (HS 270900) CAD {{CRUDE}} billion, and the net of other products CAD {{REMAINDER}} billion. Large contributions also include unwrought non-alloyed aluminium, copper ores and concentrates, and potassium chloride. Bituminous coal made a sizeable negative contribution. The two leading codes generated {{GOLD_CRUDE_PCT}}% of the net increase. Some negative changes elsewhere raised the fraction accounted for by the two positive contributions.

The United Kingdom provides the clearest destination case. Its CAD {{UK_CHANGE}} billion increase included CAD {{UK_GOLD}} billion in unwrought gold. Gold exports to Switzerland and Hong Kong moved in the opposite direction. In a midpoint decomposition of the U.K.’s share within non-U.S. destinations, 3.165 of approximately 6.707 percentage points came from increasing U.K. shares within HS6 products and 3.542 from changing product weights. Reported product entry and exit contributed a negligible amount to this comparison. Gold on its own added about 6.910 points. London’s trading and storage role offers a plausible interpretation of destination attribution, with customs records unable to track a final purchaser beyond the reported market.

Same-unit quantities add useful context. For the primary U.K. unwrought gold line (HS8 71081210), the reported quantity rose from 207.20 to 252.13 million grams (+21.7%). The nominal unit value rose from CAD 107.38 to CAD 158.62 per gram (+47.7%). Within the matched line, midpoint arithmetic attributes roughly CAD 5.976 billion of nominal change to quantity and CAD 11.768 billion to unit value. For China’s heavier crude line (HS8 27090010), quantities rose from 4.074 to 12.656 million cubic metres while unit value fell from CAD 600.97 to CAD 543.53 per cubic metre. A unit value also responds to quality, timing, contractual mix and currency movement. Global Affairs Canada’s separate aggregate gold assessment reports higher prices and lower volume across all destinations in 2025. This is compatible with rising U.K. line quantities and reinforces the importance of the aggregation level.

{{fig:commodity}}

{{fig:dest_change}}

## 8. Destination concentration and measurement reconciliation

Across all destinations, the national reconstructed HHI fell from about 0.579 in 2024 to 0.521 in 2025. Within the non-U.S. portfolio, it increased from {{HHI24}} to {{HHI25}}. The five largest non-U.S. destinations, ranked separately each year, represented 50.0% of the non-U.S. portfolio in 2024 and 54.9% in 2025. Growth in the U.K., which overtook China, is central to the less even distribution. China’s share remained near 16.9% in both years after rounding.

The commodity exclusion recalculates numerator and denominator for each alternative portfolio. Without HS 710812, the non-U.S. HHI moves from {{EX_GOLD24}} to {{EX_GOLD25}}. The U.K. share edges down from 3.626% to 3.555% on that basis. Excluding the larger HS chapter 71 yields a similar attenuation of the HHI increase. The counterfactual is a transparent accounting exclusion, and is not a simulation of trade or purchasing behaviour in the absence of gold. Because HHI is nonlinear, differences between the index levels do not sum into a causal decomposition.

The official and reconstructed indices are retained in parallel. The archived annual trade table reproduces the published 2022 national ratio of 0.59 (reconstructed 0.587571 in the archive, 0.581086 in the active series). The same check reproduces Ontario’s 0.62. The 2013, 2016 and 2018 national comparisons fall just outside the allowable rounding range, and the 2025 national non-U.S. index remains materially different relative to the displayed 0.10; a value of {{HHI25}} is below the 0.095 rounding boundary. Alternative denominator normalization and regrouping U.S. areas fail to reconcile these cases.

Both the annual and the independent detailed reconstruction reproduce the current 2024–2025 HHI closely, including discrepancies for Yukon and Prince Edward Island. Their small or concentrated portfolios can amplify a change in accounting, but this is not a verified explanation of the published differences. The national 2020 reconstruction is withheld because a positive Canada-labelled destination amount prevents full identification of the market partition. We display that gap and use the independently published value as a benchmark. The empirical model requires its own cell-level quality check at the predictor date.

{{fig:hhi}}

{{table:gold_hhi}}

## 9. Econometric methodology

Design C is a conditional historical projection. Let X(g,k,t) denote positive non-U.S. domestic merchandise exports for a province–product portfolio. For outcome start t, define Y(g,k,t) as the absolute difference between log X(g,k,t+1) and log X(g,k,t). The regression uses the non-U.S. HHI at t−1, log exports at t−1 and the U.S. share of world exports at t−1. It uses ten provinces and eleven NAPCS sections, omitting national totals, territories and special transactions. Start years run from 2011 to 2024 using annual source years 2010 to 2025.

`Y(g,k,t) = a(g,k) + b(k,t) + c(g,t) + β HHI(g,k,t−1) + γ₁ log X(g,k,t−1) + γ₂ USshare(g,k,t−1) + u(g,k,t).`

Province–product effects absorb time-invariant local specialization. Product–year effects absorb common movements in a merchandise section; province–year effects absorb disturbances common to all sectors in a province-year. The one-year separation between the predictor and the start of the outcome avoids sharing a measured time point. It cannot remove anticipated demand, persistence, selection into continued trade, or local exposure to differential prices within broad sections. The design estimates an unweighted conditional association per province–product–year cell, reported per 0.10 HHI.

The expected grid has 1,540 cells. Of these, 1,513 pass lag and endpoint eligibility. The CAD 1 million floor on lagged non-U.S. export value removes 59 otherwise eligible observations, limiting the role of very small base portfolios. The pre-estimation first and fifth percentiles of eligible lagged exports were about CAD 0.211 million and CAD 1.283 million, respectively. Threshold and balanced-panel sensitivities were specified before seeing the coefficient. The 1,454 primary cells have no fixed-effect singleton after the floor. The primary design keeps all other valid observations rather than enforcing balance. Positive endpoints reflect the log transformation and limit inference about portfolios that stop exporting.

The fixed-effect level counts are 108, 154, and 140. Their combined rank is 368, and the three slopes yield full rank 371. The HHI standard deviation after fixed effects and controls is 0.08359 compared with 0.16126 before adjustment. All provinces retain identifying variation; the effective support based on leverage is approximately 7.89 equally leveraged provinces. Least squares after projecting out the effects agrees with an explicit full-rank dummy regression. This supports the numerical calculation; statistical interpretation still depends on the error structure.

Inference uses province-clustered CR1 and a restricted wild cluster bootstrap-t. The bootstrap imposes the candidate null, draws one of six Webb weights per province, refits the full design, and studentizes with province CR1. The analysis uses 9,999 draws and obtains the 95% interval by inverting the tests. Alternative one- and two-way covariance estimators and province omissions show sensitivity. Adjacent outcome intervals share endpoint years, so they can be dependent. Province clustering accommodates serial and cross-product dependence within provinces. Product-year effects address common means; shared residual shocks across provinces remain possible.

## 10. Primary estimation and uncertainty

The HHI coefficient is **+{{BETA}}** on the full 0–1 index scale. At a +0.10 change in concentration, this gives **+{{SCALED}} log points** relative to the median absolute annual log change of 0.1633. The 95% province-CR1 interval per +0.10 is [−0.06903, +0.09468], and the restricted Webb interval is [{{LOW}}, +{{HIGH}}] with p = {{P}}. An effect of economically relevant magnitude in either direction remains compatible with the estimates. The point estimate alone cannot establish the direction of the population association.

Overall R² is 0.51860 and adjusted R² is 0.35414; within R² is 0.00862. The three regressors jointly explain less than one per cent of the variation left after the fixed effects in this sample. The fit is an in-sample measure. An out-of-sample prediction exercise would need a benchmark that can operate when future fixed effects are unknown. It is outside the registered exercise.

All cluster variants yield intervals that cover zero. With ten provincial clusters and partly shared destination shocks, neither a bootstrap nor another covariance choice removes limited effective information. The maximum provincial HHI leverage share is 17.85% in New Brunswick; some individual observations have appreciable leverage where local portfolios are small or irregular. Leaving out Nova Scotia or Prince Edward Island reverses the sign. These results are reported as part of the evidence.

{{table:regression}}

{{fig:intervals}}

## 11. Robustness and sensitivity

Excluding broad metals and minerals (C14) yields +0.0145 log points per +0.10 HHI. Ending the outcome window in 2024 yields +0.0126. Those comparisons are close to the primary estimate. Removing the extra lag floor gives −0.0015; alternative CAD 100,000 and CAD 10 million floors give +0.0124 and +0.0113. The balanced sensitivity retains 1,372 rows in 98 groups and gives +0.0259.

Value weighting places greater emphasis on larger initial portfolios and yields **−0.0275** with a 95% province-clustered interval of [−0.0567, +0.0016]. The signed growth outcome gives +0.0564 and the downside magnitude gives −0.0218. The outcome contrasts ask different questions and their signs need not align. Changing the concentration measure also changes its economic meaning. The top-partner and top-three shares produce small positive estimates, all-destination HHI a small negative estimate, and the positive-partner count a near-zero estimate per additional partner.

Non-overlapping samples use even and odd start years separately and a two-year annualized change with non-overlapping windows. Point estimates alternate in sign. The leave-one-province-out results span −0.0077 to +0.0329 per 0.10 HHI. All 26 registered secondary province-clustered intervals include zero. The interval comparisons are diagnostic and the specifications can target different populations and outcomes. The registered selection check found zero verified exits among portfolios meeting lag eligibility with positive start and observed end, so the proposed exit regression was not estimable under its support requirement. This check does not assess exporter or destination exits within continuing portfolios.

{{fig:robust}}

{{fig:loo}}

## 12. The steel tariff pilot and identification limits

The February 10, 2025 announcement and March 12 effective date for the Section 232 steel measure create a potential event window. The March rule specifies a 25% additional rate on ordinary entries of covered core products under Chapter 99 note 16(j), subject to other rules and verified exceptions. The June 4 increase to 50% changes the regime. February is an anticipation month and March mixes policy states. The comparison uses 37 complete pre-event months and leaves only April and May as full post months in the original regime.

The archived U.S. schedule and legal annex yield {{PILOT_LINES}} HTS10 reporting lines across 301 HTS8 subheadings, {{PILOT_HS6}} HS6 products and {{PILOT_HS4}} nominal HS4 families. The Canadian HS8 and U.S. HTS10 national suffixes differ. The pilot retains all U.S. child lines under each candidate HS6 and checks treatment homogeneity and Canadian descriptions. Twenty-four core HS4 families contain a stable HS6 with complete U.S. positive-flow support. All identified families share one legal effective date. Nominal families are not verified independent policy shocks.

The U.S. Census import-for-consumption mirror provides customs values and calculated duties for January, April and May. The core basket’s calculated duty ratios are 0.00%, 22.83% and 22.60%. These figures describe the observed import basket, and can combine applicable duty authorities and claims. They do not capture net payments after refunds, the Section 232-only levy, or how border costs are distributed between exporters, importers and consumers. The March northern-border measures, CUSMA preference, April stacking guidance and Canadian countermeasures create overlapping changes that cannot be assigned from an HS code alone.

Mexico is the most feasible of the screened alternative destinations by continuous positive-flow support, with only four core HS6 products in common with the U.S. One overlaps a corrosion-resistant steel antidumping proceeding with a U.S. Commerce preliminary determination on Canadian goods applicable April 10. The near upstream candidates differ economically and only one has full common U.S.–Mexico support. Diversion itself could affect comparison destinations. With short post coverage, unresolved eligibility at entry and sparse independent comparison support, the pilot remains descriptive. No tariff coefficient is estimated.

## 13. Interpretation and policy implications

The evidence supports three increasingly demanding measurements. The gross U.S. export share shows where the current value of merchandise is recorded. The conditional HHI shows how those values are distributed among alternative destinations. Exposure of Canadian output and employment requires value-added and jobs data, with attention to imported inputs, supply linkages and final demand. A change in the first measurement does not imply proportional changes in the others.

From a monitoring perspective, the simultaneous decline in the U.S. share and rise in non-U.S. HHI warrants tracking both axes. Product-exclusion scenarios provide a transparent view of whether a movement depends on a small commodity set. A quantity or deflator panel would be more informative than a broad current-value reclassification when the policy objective concerns real activity. Denominators should match decisions: gross dollar exposure for trade-flow monitoring; regional GDP for scale; value-added measures for domestic production; and firm or worker data for adjustment and distribution. These are measurement implications, independent of any estimate of a policy treatment.

The regression offers no dependable conversion from a proposed HHI reduction to an expected stabilization of exports. A policy that changes market access might simultaneously alter intensive and extensive margins, investments, pricing and the variance of demand. The accounting exclusion of gold describes a different observed basket and offers no evidence about substituting markets or goods under an intervention. The steel mapping illustrates a related operational lesson. A nominal statutory rate can be a useful starting point, and effective exposure depends on entry date, eligibility, content, overlap and exemptions.

## 14. Limitations and future research

First, the customs basis obscures final demand routed through market hubs, and current-dollar valuations combine prices, quantities and composition. A next empirical extension would obtain concorded physical units or suitable price deflators across matched destination and product cells, with explicit coverage thresholds. If reliable quantities are unavailable, a narrower product analysis would be more defensible than extrapolating from the selected HS8 lines.

Second, historical destination portfolios may reflect anticipated volatility, trade finance, technology, logistics and firm-level selection. Fixed effects remove common patterns while allowing heterogeneous local shocks to remain. Research on real resilience could explicitly incorporate correlated destination demand and trade-route substitution. A predictive reading would require a reserved validation period and a feasible benchmark for unknown future effects.

Third, concentration can lag revisions in underlying bilateral values. Additional archived snapshots and publisher metadata could help resolve the 2025 and regional discrepancies and the remaining pre-2020 rounding-edge cases. Separate indicators should stay separately versioned, even when similarly named. Fourth, a future tariff project needs a verified HTS-to-Canadian product concordance, preference and exclusion information at relevant entry grain, and uncontaminated comparison variation. This study supplies the feasibility evidence; it cannot determine tariff incidence. Finally, merchandise values do not cover services or the full range of household and business adjustments, so broad economic dependence remains beyond what the customs ratios alone can establish.

## 15. Conclusion

Canada’s U.S. share of domestic merchandise exports fell from {{US24}}% to {{US25}}% between 2024 and 2025. The alternative portfolio became more concentrated, with gold and crude petroleum accounting for {{GOLD_CRUDE_PCT}}% of its nominal increase. Removing unwrought gold materially changes the destination picture. Some matched lines show quantity growth, while other evidence identifies a large unit-value component and different aggregate volume movements.

The preregistered concentration coefficient is small and statistically inconclusive relative to its uncertainty. The pattern does not establish that reducing concentration would stabilize nominal or real exports. The steel policy mapping validates statutory scope and mirror data while exposing gaps in the counterfactual. The evidence supports a more precise description of Canada’s changing exposure, with the question of economically meaningful resilience still open.

## References

- Cadot, O., Carrère, C., and Strauss-Kahn, V. (2011). Export Diversification: What’s behind the Hump? *Review of Economics and Statistics*, 93(2), 590–605. [Journal article](https://doi.org/10.1162/REST_a_00078).
- Di Giovanni, J., and Levchenko, A. A. (2010). The Risk Content of Exports: A Portfolio View of International Trade. *NBER Working Paper 16005*. [NBER](https://www.nber.org/papers/w16005).
- Global Affairs Canada (2026). *Canada’s State of Trade 2026*, box 1.4.1, gold exports. [Report](https://international.canada.ca/en/global-affairs/corporate/reports/chief-economist/state-trade/2026).
- Haddad, M., Lim, J. J., Pancaro, C., and Saborowski, C. (2013). Trade openness reduces growth volatility when countries are well diversified. *Canadian Journal of Economics*, 46(2), 765–790. [Journal article](https://doi.org/10.1111/caje.12031).
- Hummels, D., Ishii, J., and Yi, K.-M. (2001). The nature and growth of vertical specialization in world trade. *Journal of International Economics*, 54(1), 75–96. [Journal article](https://doi.org/10.1016/S0022-1996(00)00093-3).
- Koren, M., and Tenreyro, S. (2007). Volatility and Development. *Quarterly Journal of Economics*, 122(1), 243–287. [Journal article](https://doi.org/10.1162/qjec.122.1.243).
- MacKinnon, J. G., Nielsen, M. Ø., and Webb, M. D. (2023). Cluster-robust inference: A guide to empirical practice. *Journal of Econometrics*, 232(2), 272–299. [Journal article](https://doi.org/10.1016/j.jeconom.2022.04.001).
- Statistics Canada. Annual and monthly merchandise trade, tables 12-10-0173-01 and 12-10-0175-01. Pinned November 18, 2026 Toronto time. [Annual data](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017301) · [Monthly data](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017501).
- Statistics Canada. Export market concentration, table 12-10-0129-01. [Published HHI](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210012901) · [Provincial methodology discussion](https://www150.statcan.gc.ca/n1/daily-quotidien/250506/dq250506a-eng.htm).
- Statistics Canada. Canadian International Merchandise Trade (CIMT), domestic export HS archives. [Open data](https://open.canada.ca/data/en/dataset/2909a648-5753-4924-878a-b069392d9cde) · [Reference guide](https://www150.statcan.gc.ca/n1/pub/13-605-x/2025001/article/00003-eng.htm).
- Statistics Canada. Provincial and territorial GDP (36-10-0711-01), value added and jobs due to exports and foreign demand (12-10-0100-01), and Labour Force Survey employment (14-10-0022-01). [GDP](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610071101) · [Value added and jobs](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210010001) · [Employment](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410002201).
- United States. Proclamation 10896 and implementation at 90 FR 11249. [Legal implementation and scope](https://www.govinfo.gov/content/pkg/FR-2025-03-05/html/2025-03598.htm) · [CBP stacking guidance](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3e0a63e) · [June rate change](https://www.govinfo.gov/content/pkg/DCPD-202500655/html/DCPD-202500655.htm) · [Preliminary antidumping determination](https://www.govinfo.gov/content/pkg/FR-2025-04-10/html/2025-06135.htm).
- U.S. Census Bureau and USITC. Merchandise Trade Imports detailed files and 2025 HTS Revision 4. [Census imports](https://www.census.gov/foreign-trade/data/IMDB.html) · [HTS edition](https://www.usitc.gov/2025_hts_revision_4).
- Webb, M. D. (2023). Reworking wild bootstrap-based inference for clustered errors. *Canadian Journal of Economics*, 56(3), 839–858. [Journal article](https://doi.org/10.1111/caje.12661).

## Appendix A. Primary sample and robustness outputs

The 1,540-cell exclusion ledger records overlapping defects and fixed-effect singleton removals. The 24 unavailable lagged HHIs include invalid or unallocated destinations. Eight rows lack lagged controls. Nine starts and nine ends have genuine zero non-U.S. trade in the full grid. A lagged floor failure can coexist with any of these other flags. Zero and missing classifications are retained in the ledger, with no fabricated values. Imposing the floor after the other eligibility rules leaves 1,454 distinct estimation cells.

{{table:robustness}}

The one-additional-partner row uses a count increment, while share and concentration specifications use 0.10. Two-year log movements are annualized by division by two. All intervals for these secondary specifications use one-way provincial CR1. Full machine-readable estimates, the sample membership of each alternative and the scope of the steel pilot are retained in the release.

## Appendix B. Data and reproducibility

The following table supplies the exact geographic comparison underlying the 2025 ranking at displayed precision. All values are in current Canadian dollars, and the regional share divides U.S. by world exports in the same geography. Source: Statistics Canada 12-10-0173-01.

{{table:regions}}

This paper and the Streamlit monitor read the same locked Phase 3–4B outputs. Reports render from language-specific source Markdown and common, programmatically inserted headline values and tables. Figure inputs include the verified annual and monthly CSVs, the CIMT-derived product bridge, and the independent checked regression and uncertainty files. The release provides a source lock, hashes, a reproducible rendering command and test logs.

© 2026 Manau Salaun. Original research text and figures are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source data retain the terms cited below.

Adapted from Statistics Canada, tables 12-10-0173-01 and 12-10-0129-01 (2010–2025), 12-10-0175-01 (January 2025–September 2026), 12-10-0100-01 (national to 2024 and subnational 2013–2022), 36-10-0711-01 (2010–2023) and CIMT domestic export archives (2022–2025). This does not constitute an endorsement by Statistics Canada of this product. U.S. sources are credited to the Census Bureau, USITC and the relevant legal notices. [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/terms-conditions/open-licence)

## Appendix C. Monthly comparison and estimation eligibility

The table reports January through September of each year from the separate unadjusted monthly series. The monetary columns are CAD billions in current dollars. The share is a ratio of nine-month sums. Statistics Canada table 12-10-0175-01.

{{table:monthly}}

The main model uses the annual series. The following audit lists the construction checks that operate before estimation. For example, a zero lagged portfolio can make the HHI unavailable, invalidate the log control and fail the size floor. Summing the flagged rows would double-count such observations. The archived ledger is the authoritative list of the unique 86 exclusions.

{{table:sample}}

These data checks preserve the distinction between a valid zero in observed trade and missing or unusable values. Because the outcome uses logarithms, zero endpoints are outside the main estimation sample. Stronger inference about extinction of markets would require a different outcome, data grain and research design.
