# Final scientific audit

> Historical review. The Phase 7A checklist records current approval and licensing status. [Current checklist](final_approval_checklist.md)

**Review date:** 18 November 2026 (Toronto). **Decision:** NO-GO for public release pending the owner's authorization, attribution and original-work licence. The statistical and descriptive evidence supports private scientific sign-off for this release candidate. The March 2025 steel exercise remains a feasibility pilot. The Phase 6 edits clarify that the April 10 preliminary antidumping determination was issued by U.S. Commerce and applied to certain Canadian goods. [Antidumping notice](https://www.govinfo.gov/content/pkg/FR-2025-04-10/html/2025-06135.htm)

## Independent reproduction

After installing the full publication lock, point these commands to the historical project root containing the original raw archives and derived vintages.

```sh
.venv/bin/python audit/independent_audit.py --archive-root /path/to/historical-project --out replication
.venv/bin/python audit/historical_checks.py --archive-root /path/to/historical-project --out replication/historical_results.json
```

The [audit program](../audit/independent_audit.py) reads the archived files directly, verifies their SHA-256 values against the acquisition and CIMT receipts, and imports no project calculation or estimation modules. It compares matching keys and missing-cell masks as well as numeric values. The [machine-readable results](../audit/evidence/independent_results.json) record tolerances and differences. The [historical check](../audit/historical_checks.py) reproduced the 228 active discrepancies in 5,096 comparisons and zero out-of-rounding differences in the archived series. The same check independently parsed note 16(j), expanded it against the locked USITC edition, and verified the complete set of 744 HTS10 lines (301 HTS8, 167 HS6 and 29 HS4). It recalculated the core-steel duty ratios from the locked raw import records (0.00%, 22.83% and 22.60% in January, April and May). The locked Canadian eligibility ledger supports four common U.S.–Mexico HS6 lines and 24 HS4 groups with full U.S. support. The audit re-counted the Canadian ledger and did not independently reconstruct its line-level dictionary screening. [Historical replication evidence](../audit/evidence/historical_results.json)

| Claim | Independently reproduced value |
| --- | --- |
| Canada's annual U.S. share of domestic merchandise exports | 75.795940% in 2024 and 71.688374% in 2025, down 4.107566 percentage points. |
| 2025 export values | CAD 719.867 billion worldwide, CAD 516.061 billion to the U.S., CAD 203.806 billion elsewhere. |
| Change in the U.S. share, midpoint decomposition | −3.211520 points within sections and −0.896047 points from product composition. Energy accounts for −1.642066 points of the total change. |
| Non-U.S. HHI | 0.07234565 to 0.09382439. The all-destination index moves from 0.57874073 to 0.52144278. |
| Nominal non-U.S. export gains (CIMT) | CAD 28.796 billion. HS 710812 unwrought nonmonetary gold and HS 270900 crude petroleum contribute CAD 13.159 billion and CAD 8.236 billion, or 74.3% together. |
| United Kingdom | Share of the non-U.S. portfolio 15.72% to 22.43%. CIMT change CAD 18.196 billion, including CAD 17.743 billion of unwrought gold. |
| CIMT non-U.S. HHI with HS 710812 removed | 0.068295 to 0.070721. This calculation removes the product in both years and recomputes the denominators. |
| Monthly January–September, separate customs series | U.S. share 73.2848% in 2025 and 67.9816% in 2026. Nominal values to the U.S. and to other markets both rise in the matched comparison. |
| 2025 geography | New Brunswick leads the share ranking at 90.4%. Ontario leads in U.S. export value at CAD 189.5 billion. The denominator differs across these rankings. |
| U.S. final demand, national 2024 | 15.8998% of domestic value added and 12.0510% of jobs. For Alberta, Saskatchewan and Ontario, the corresponding 2022 values for domestic value added are 33.7095%, 24.9762% and 14.2124%. |

The reconstruction compares all **2,912** annual geography–product–year rows, **294** recent all-merchandise geography–month rows, **28** matched January–September geography–year observations, and **4,080** national identified non-U.S. destination–year rows. It rebuilds every Canadian HS6–destination annual value in the 2024–2025 CIMT bridge. The GDP and value-added ratios match the archived results within 10⁻¹⁶. Current-dollar GDP in the frozen files supports publication ratios through 2023. Supply-and-use denominators support provincial and territorial demand shares for 2013–2022 and national shares through 2024. [Annual trade](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017301) · [Monthly trade](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017501) · [Value added and jobs](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210010001) · [Current-dollar GDP](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610071101)

## Design C

The independent implementation reconstructs the full **1,540-cell** eligibility grid and the **1,454 retained cells** in **108** province–product portfolios. It uses an explicit dummy matrix and singular-value decomposition, whereas the production estimator absorbs fixed effects. The rank is 371, with 368 fixed-effect dimensions. The primary outcome is the absolute annual log change in **nominal non-U.S. domestic merchandise exports**. Lagged HHI, log lagged export scale and lagged U.S. share precede the outcome window. The sample has ten provinces, 11 NAPCS product sections and outcome-start years 2011–2024 with endpoints through 2025.

| Full 0–1 HHI scale | Independently rebuilt value |
| --- | ---: |
| HHI slope | +0.128272123531 |
| Province CR1 standard error | 0.361833591363 |
| Province CR1 t, degrees of freedom | 0.354505846314, 9 |
| Province CR1 p | 0.731124349576 |
| Province CR1 95% CI | [−0.690252326911, +0.946796573973] |
| Restricted Webb p, 9,999 draws | 0.7174 |
| Restricted Webb 95% CI | [−0.604866959, +1.052539906] |

For a +0.10 change in HHI the estimated change is +0.012827 log points, with restricted Webb 95% CI [−0.06049, +0.10525]. The audit checks 64 literal restricted bootstrap refits at two imposed nulls and uses the independently derived affine representation for the 9,999-draw inversion. It matches all **12** primary and **312** robustness coefficient–covariance rows, including coefficients, standard errors, t statistics, degrees of freedom, confidence bounds and p-values. The largest absolute p-value discrepancy is 2.0 × 10⁻¹⁴ for the primary rows and 1.8 × 10⁻¹³ for robustness rows. The value-weighted point estimate reverses sign, and all 26 secondary province-CR1 intervals cover zero. These findings support an inconclusive within-sample association. Ten clusters and effective partial-leverage support of about 7.89 warrant caution with nominal coverage. [Primary inference](../audit/evidence/model_primary.csv) · [Robustness inference](../audit/evidence/model_robustness.csv) · [Archived diagnostics](../data/phase4b/primary_diagnostics.json) · [Cluster inference reference](https://doi.org/10.1016/j.jeconom.2022.04.001) · [Webb weights reference](https://doi.org/10.1111/caje.12661)

## Interpretation, classifications and references

- Current CAD customs values combine prices, quantities, mix and transaction patterns. The UK gold line shows larger physical shipments and a higher unit value. Its unit value is a ratio of aggregate declared value to quantity for one HS8 code and destination. It supplies neither a price index nor a volume measure for the national export portfolio. The commodity exclusion is an accounting sensitivity.
- Merchandise shares use same-vintage U.S. and world Canadian domestic export totals. The gross-export-to-GDP ratio compares differently defined aggregates in current CAD. Supply-and-use value added and jobs attributed to final demand have geography-specific denominators and include a different economic coverage.
- NAPCS/SCPAN describes products. NAICS/SCIAN describes industries. HS/SH supplies common six-digit categories under the relevant nomenclature vintage. Canadian HS8 and U.S. HTSUS 8-/10-digit codes carry national detail. The research uses descriptive product categories and a narrow tariff scope. Labour Force Survey industry counts provide background only.
- The archived 2020 comparisons and active 2020 differences remain separate from the recent monthly window. Published and reconstructed concentration values remain independently labelled, and the latter retains missing cells for unreconciled partner coverage. Archived trade values are consistent with the 2022 published comparison. Exact publisher inputs and discrepancies in 2013, 2016, 2018, 2025 and at some regional geographies remain open. [2020 vintages](reconciliation_2020.md) · [HHI reconciliation](hhi_reconciliation.md)
- The February 10 announcement, March 12 entry date, 25% ordinary steel rule in note 16(j) and June 4 increase to 50% agree with the official instruments. The March rule adds to otherwise applicable preferential rates for covered core entries. Derivatives, admissibility, exclusions and stacking require entry-level review. The April guidance and subsequent updates are separate dated measures. The import mirror measures calculated duties divided by customs value, with no independent evidence on refunds, incidence or a tariff effect. [March implementation](https://www.govinfo.gov/content/pkg/FR-2025-03-05/html/2025-03598.htm) · [June proclamation](https://www.govinfo.gov/content/pkg/DCPD-202500655/html/DCPD-202500655.htm) · [CBP stacking guidance](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3e0a63e) · [Full research chronology](tariff_policy_timeline.md)
- The bilingual bibliographies use the same research and statistical sources. Primary citation records were checked for concentration and risk, value chains, inference and the Canadian official explanations for gold. The manuscript presents the economic mechanisms as mechanisms and holds inference to the province–product sample. [Portfolio reference](https://www.nber.org/papers/w16005) · [Value-chain reference](https://doi.org/10.1016/S0022-1996(00)00093-3) · [State of Trade report](https://international.canada.ca/en/global-affairs/corporate/reports/chief-economist/state-trade/2026)

The independent run does not provide a full replication of transaction-level coverage, every historical CIMT support linkage or the 2026 tariff schedule as an entry-level dataset. It supplies no new estimate for Designs A or B. The publication inventory records all remaining issues and their disposition. [Issue register](remaining_limitations.md)
