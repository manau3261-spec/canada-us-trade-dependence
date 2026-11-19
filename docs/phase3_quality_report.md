# Phase 3 quality report / Rapport de qualité de la phase 3

## Definitions and validation

| Measure | Construction and checks |
| --- | --- |
| U.S. merchandise dependence | U.S.-bound domestic merchandise exports divided by the publisher’s world total for the same geography, period and NAPCS product section. A zero or missing denominator leaves the share blank. The two frequencies use their own official world totals. |
| Export intensity | Gross annual domestic merchandise exports, world or U.S., in CAD thousands divided by corresponding current-dollar GDP at basic prices, converted from CAD millions to thousands. Latest valid all-industry denominator is 2023. The national GDP series is outside this GDP cube’s geographic universe. |
| Destination HHI | Sum of squared destination shares in annual domestic exports. The full portfolio uses the official world denominator. The ex-U.S. portfolio drops the U.S. from the squared sum and uses world minus U.S. exports as denominator. Eligible rows require nonnegative and complete components, an observed U.S. value, reconciliation to the world row, and no positive unallocated destination amount. With the U.S. share denoted `s`, full HHI equals `s² + (1 − s)² × HHI_exUS` wherever both indices are eligible. An HHI of 1 indicates a single destination. Lower values indicate a more evenly distributed portfolio. |
| National product decomposition | For each of the 12 detailed sections, multiply the change in its U.S. share by the mean of its two export weights for the within-product contribution. Multiply the change in its weight by the mean of its U.S. shares for the mix contribution. Add contributions in percentage points. A separate rounding row reconciles the sum to the official all-product change. |
| Matched recent months | January through September in each calendar year, 2025 and 2026. Sum values first, then divide the U.S. sum by the world sum. No seasonal adjustment or extrapolation. |
| Value-added and jobs benchmarks | Use the U.S. components of “Value added due to foreign demand” and “Jobs due to foreign demand,” each divided by its own all-country, all-industry total. This supplies the perspective of domestic industries whose activity is linked to exports by any industry. The dataset also preserves the separate exporter-side amounts that can include upstream value added or jobs across regions. Jobs are counts and gross export value is outside these ratios. |

[Statistics Canada guide to merchandise statistics](https://www150.statcan.gc.ca/n1/pub/13-605-x/2025001/article/00003-eng.htm) · [Value-added measurement framework](https://www.statcan.gc.ca/en/statistical-programs/document/1401_D14_T9_V1) · [GDP table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610071101)

## Geographic totals and 2020

For the world and U.S. partner rows, all **416 annual** and all **546 recent monthly** comparisons of the sum of the 13 jurisdictions to the published Canada row passed the rounding test. The Canada row remains the national control. Both active files also reconcile within their own destination and product partitions. The cross-frequency issue is confined to 2020 in the Phase 2 overlap. Phase 3 traces it to changes in the active monthly vintage and reproduces all published headline annual totals against an independent detailed file. [Geographic checks](../data/phase3/geographic_reconciliation.csv) · [2020 evidence](reconciliation_2020.md)

## HHI benchmark and interpretation

Statistics Canada’s May 6, 2025 release explicitly publishes and discusses provincial and territorial destination HHI, including Yukon, New Brunswick and Alberta, and links table 12-10-0129-01. Its October 2018 launch notice also identifies geographic destination breakdowns. These establish that the subnational destination series are a published product despite the current footnote stating that provincial statistics are limited to product concentration. The records support comparison. Keep provenance of the footnote discrepancy and treat the two implementations separately. [May 2025 provincial results](https://www150.statcan.gc.ca/n1/daily-quotidien/250506/dq250506a-eng.htm) · [October 2018 launch notice](https://www150.statcan.gc.ca/n1/daily-quotidien/181005/dq181005g-eng.pdf) · [Concentration table](https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1210012901)

| 2010–2025 all-product HHI | Published numeric cells | Comparable to reconstruction | Within published rounding | Outside |
| --- | ---: | ---: | ---: | ---: |
| Canada, all destinations | 16 | 15 | 11 | 4 |
| Canada, ex-U.S. | 16 | 15 | 14 | 1 |
| Subnational, all destinations | 208 | 206 | 149 | 57 |
| Subnational, ex-U.S. | 208 | 206 | 161 | 45 |

National exceptions beyond the published two-decimal tolerance are 2013, 2016, 2018 and 2022 for all destinations, and 2025 for ex-U.S. The table documents the HHI concept, and the source material reviewed does not establish the detailed pipeline behind every official observation. The largest comparable subnational discrepancy is approximately **0.105** for ex-U.S. HHI. The two series remain separate in the comparison file. [Cell-level benchmark](../data/phase3/destination_hhi_benchmark.csv)

**2020 gap.** The annual national file records **CAD 1.3573 million** under the destination label “Canada.” The strict reconstruction leaves national HHI blank that year. The same issue affects the all-product British Columbia and Ontario reconciliations for HHI eligibility and the corresponding C13 cells. As a sensitivity calculation, the identifiable national destination shares alone give squared sums of **0.528657** (all destinations) and **0.075519** (ex-U.S.). Hypothetically assigning all Canada-labelled value to the largest eligible partner moves those to at most **0.528661** and **0.075523**, respectively, conditional on the reported totals and their rounding. The calculation adds `2 × s_max × r + r²`, with `r` the Canada-labelled share of the relevant denominator. Both intervals round to the contemporaneously published **0.53** and **0.08**. The sensitivity calculation assigns no destination in the production indicators. [Underlying national portfolio](../data/phase3/national_non_us_destinations.csv) · [Published ratios](../data/phase3/destination_hhi_benchmark.csv)

## Panel coverage

Coverage counts use the historically targeted geography × industry group × period grids. “Eligible” refers to the publisher’s geographic universe and the project window. Years outside a measure’s actual publication span remain gaps within that window, visible as absent rows or published blanks. GDP counts use 20 major NAICS groups plus all industries. LFS counts use 28 reported groups, including aggregates, for employed persons aged 15+ and total gender. LFS groupings can overlap. Supply-and-use coverage here is a separate summary industry classification with 30 observed groups for these tabulations.

| Outcome slice | Window | Eligible cells | Numeric | Suppressed | Other blank rows | Absent eligible cells |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Provincial and territorial real GDP | 2010–2025 | 4,368 | 4,368 | 0 | 0 | 0 |
| Provincial and territorial nominal GDP | 2010–2025 | 4,368 | 3,822 | 0 | 546 | 0 |
| LFS employed persons | 2010–2025 | 59,136 | 57,884 | 1,252 | 0 | 0 |
| LFS employed persons | Jan. 2025–Oct. 2026 | 6,776 | 6,608 | 168 | 0 | 0 |
| U.S.-demand value added | 2010–2025 | 6,720 | 4,070 | 0 | 727 | 1,923 |
| U.S.-demand jobs | 2010–2025 | 6,720 | 4,042 | 0 | 728 | 1,950 |

The GDP cube excludes Canada as a national observation, giving **336 outside-universe cells** per pricing slice. The requested LFS industry cube excludes the territories, giving **16,128** outside-universe cells for 2010–2025 and **1,848** for January 2025–October 2026. Recent joint coverage with the trade file ends in September 2026. Of the 1,252 historical LFS suppressions, **942** are in fishing, hunting and trapping and **262** in forestry and logging or its support activities. At the all-industries total, the 11 eligible geographies have all 192 historical months. These are counts for the selected employment slice and differ from suppression counts across the full LFS archive. [Geography × group counts](../data/phase3/panel_coverage.csv) · [LFS table details](https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1410002201)

For 12-10-0100-01, all-industry benchmarks in the project window cover Canada in **2010–2024** and each province and territory in **2013–2022**. The 2023–2024 Canada observations use advanced modelled supply-and-use estimates. The industry-level blanks and absent cells above combine publication windows and measure applicability. Preserve both categories. [Value added in exports release](https://www150.statcan.gc.ca/n1/daily-quotidien/260504/dq260504a-eng.htm) · [Benchmarks](../data/phase3/value_added_and_jobs_benchmarks.csv)

## Reproducibility and scope

- The final run passed **35 tests in 5.61 seconds** on Python 3.14.8, with zero failures or skips. A fresh rebuild reproduced the data and figure manifests byte for byte. The figure test also rendered all 32 PNG and SVG files in a separate directory and matched every recorded hash.
- The pinned phase 2 acquisition manifest and three supplemental comparison files have SHA-256 checks. The generated data summary records row counts and output hashes. Each figure from the two language editions has a PNG and vector SVG with a hash. The automated suite checks formulas, geographic totals, time windows, missingness and reproducible rendering. [Data manifest](../data/phase3/phase3_summary.json) · [Figure manifest](../figures/phase3/figure_manifest.json) · [Test results](../data/provenance/phase3-test-results.txt)
- The merchandise charts use NAPCS product sections. The GDP and LFS use industry groupings and the input-output benchmarks use a supply-and-use industry classification. Keep them at their original grains until stable concordances and reporting universes are documented.
- The archive preserves dated official releases. A fresh download can return revisions. The trade changes are descriptive and measured in current CAD. The scientific approval gate applies to any causal analysis.

## Synthèse en français

Les sommes provinciales et territoriales concordent avec les totaux canadiens selon l’arrondissement publié pour les **416 comparaisons annuelles** et les **546 comparaisons mensuelles récentes**. Le rapprochement de 2020 situe la rupture dans le millésime du tableau mensuel actif. Une publication de Statistique Canada confirme la diffusion de l’IHH provincial par destination malgré une note de tableau contradictoire. Les mesures publiées et reconstruites demeurent visibles séparément.

Le PIB réel couvre les 13 provinces et territoires pour les groupes retenus de 2010 à 2025. Le PIB nominal s’arrête en 2023. Les séries industrielles de l’EPA excluent les territoires et les suppressions se concentrent dans quelques industries détaillées. Les repères de valeur ajoutée et d’emplois liés à la demande américaine s’arrêtent en 2022 pour les provinces et territoires, et en 2024 pour le Canada. Les concordances entre produits et industries demeurent un préalable pour la construction des panels.
