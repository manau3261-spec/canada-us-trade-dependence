# Phase 4A scientific review

**Recommendation for approval.** Adopt **Design C** as the primary analysis of the association between non-U.S. destination concentration and later instability in nominal exports. Advance **Design A** to a legal and data mapping pilot for March 2025 core steel. Defer **Design B** until a defensible link from the affected products to producing industries and geographic exposure is available. [Model selection](model_selection.md)

## Evidence and implications

- **Verified · The redistribution of export value was concentrated.** The U.S. share fell from 75.8% to 71.7%, while non-U.S. destination HHI rose from 0.072346 to 0.093824. Non-U.S. domestic exports rose by CAD 28.80 billion. Unwrought gold and crude petroleum accounted for 74.3% of that increase. Gold accounted for CAD 17.74 billion of the CAD 18.20 billion increase in exports to the U.K. Excluding unwrought gold, the U.K. share of non-U.S. exports edged down and the non-U.S. HHI rose by 0.00243. [Diversification mechanisms](diversification_mechanisms.md)
- **Verified · Quantity and unit value both matter.** For the main U.K. gold line, reported grams rose 21.7% and CAD per gram rose 47.7%. The same-line nominal decomposition assigns CAD 5.98 billion to the quantity component and CAD 11.77 billion to the unit-value component. For a major Chinese crude line, physical volume rose while the average unit value fell. These lines have specific product definitions, and their quantity patterns cannot establish an economy-wide real diversification effect. [Quantity checks](../data/phase4a/hs8_quantity_checks.csv)
- **Verified · The 2022 archived trade comparison explains part of the HHI discrepancy.** The archived annual bilateral table reproduces published national and Ontario HHI to the displayed precision. The selected national boundary discrepancies in 2013, 2016 and 2018 and the national ex-U.S. difference in 2025 remain open. Detailed customs reaggregation corroborates the current 2024–2025 reconstruction, including large differences from published values for Yukon and P.E.I. Both versions remain in the research record. [HHI reconciliation](hhi_reconciliation.md)
- **Verified · Tariff regimes require entry-level eligibility.** The chronology distinguishes IEEPA, Section 122, Section 301, Section 232 and Section 338, including bans and relevant CUSMA treatment. Public Canadian export data do not observe preference claims, metal content, company terms or duties. Product mapping for a broad all-tariff design remains unvalidated. A duty ratio from compatible U.S. import fields could aid validation, with a separate check of Chapter 99 duties and limitations. [Tariff chronology](tariff_policy_timeline.md)

### Interpretation and unresolved risks

The 2025 change in destination shares is consistent with partly different market allocations and a large shift in product weights. It also reflects price movements and the U.K.’s role as a bullion trading hub. Customs’ last known destination and unit values cannot identify final buyers or isolate an independent price index. In Design C, persistent price movements, common shocks across destinations, portfolio adjustment in anticipation of volatility and selection into active non-U.S. exporting remain identification risks. Only ten provinces support the main clustered inference. In Design A, overlapping tariffs, third-market diversion and a short period before the next rate change threaten the comparison. In Design B, exposure may be concentrated in a few provinces or industries and employment responds to other local and national shocks. [Design A](econometric_design_A.md) · [Design B](econometric_design_B.md) · [Design C](econometric_design_C.md)

## Reproduce the descriptive checks

Run from the project or archive root. The supplemental module verifies the pinned source ZIPs and the two Phase 3 CSV hashes and rebuilds the six CSVs. It reads official CIMT HS8 data with monthly observations, the active and archived annual trade cubes, and the Phase 3 HHI benchmark. The program covers 1,292,368 official HS8 observations in 2024 and 1,264,188 in 2025. It does not download a replacement vintage or fit a model. [Input provenance](../data/provenance/phase4a-cimt-sources.json) · [Output manifest](../data/phase4a/manifest.json) · [Descriptive code](../src/trade_audit/phase4a_audit.py)

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
PYTHONPATH=src .venv/bin/python -m trade_audit.phase4a_audit
```

The CSV manifest matched byte for byte after replay, including the six output hashes. The full project’s existing test suite passed **35 tests**. The standalone Phase 4A archive contains the pinned inputs and requirements for the descriptive replay. Earlier-phase figures and unrelated raw datasets stay in the project’s previous releases. Additional spot checks reproduced the national and U.K. headline changes, reconciled the two selected quantity decompositions, and confirmed the 56 current-cube versus CIMT HHI comparisons and Design C eligibility counts.

| Output | Rows | Use |
| --- | ---: | --- |
| `hs6_country_value_changes.csv` | 109,482 | Product and partner contributions in current CAD |
| `hs8_quantity_checks.csv` | 1,549 | Quantity and unit-value notes for selected product families |
| `uk_share_composition.csv` | 4,801 | Within-product and between-product contributions to the U.K. non-U.S. share |
| `non_us_gold_exclusion_sensitivity.csv` | 6 | Two years and three product-scope sensitivities |
| `hhi_method_sensitivity.csv` | 224 | Official, reconstructed, archived and detail comparisons, where defined |
| `design_C_coverage.csv` | 1,540 | Eligibility audit for 10 provinces, 11 products and 14 outcome-start years |

**Data attribution.** Source: Statistics Canada, Canadian International Merchandise Trade domestic exports (2024–2025) and annual trade tables 12-10-0173-01 and 12-10-0133-01 (pinned November 18, 2026 Toronto time). Reproduced and distributed on an “as is” basis with the permission of Statistics Canada. The project’s calculations also use the concentration ratios in table 12-10-0129-01 and the employment coverage from 14-10-0022-01. [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/terms-conditions/open-licence) · [CIMT data and terms](https://open.canada.ca/data/en/dataset/2909a648-5753-4924-878a-b069392d9cde)

## Approval to advance

1. Confirm the C estimand, time index, fixed effects, minimum portfolio size, missingness rules, weighting, inference and interpretation. Decide which signed and downside outcomes are secondary.
2. Confirm use of reconstructed HHI for eligible province–product cells with official HHI reserved for the coarser published benchmark. Retain unresolved discrepancies and record results with and without the broad gold-containing category.
3. Authorize the A mapping pilot, including dated HTS annexes, pre-period CIMT and U.S. DataWeb checks. Agree on minimum independent product-family support, overlap criteria and the evidence needed for a credible comparison. Defer B until the exposure concordance and effective sample are reviewed.

**Phase boundary.** The documentation and descriptive validation complete Phase 4A. No econometric coefficients were estimated, no causal models were implemented, and no dashboard or repository publication was produced.

## Résumé scientifique

Le **modèle C** est recommandé pour mesurer une association historique entre l’IHH des destinations hors États-Unis et l’instabilité ultérieure des exportations nominales par province et groupe de produits. L’or sous forme brute explique 97,5 % de la hausse de la valeur exportée vers le Royaume-Uni. La quantité déclarée et la valeur unitaire ont toutes deux augmenté pour le principal code canadien de lingots. Ces observations ne permettent pas de conclure à une diversification générale en volume. Les archives reproduisent l’IHH publié pour le Canada et l’Ontario en 2022 à la précision affichée. Les autres écarts ciblés restent documentés. Le volet acier est subordonné à la validation des codes et du comparateur. L’étude de l’emploi exige une concordance produits–industries suffisamment précise. Avant toute estimation, approuver la spécification, les seuils d’admissibilité et la méthode d’inférence.
