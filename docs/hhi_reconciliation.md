# Destination concentration reconciliation

## Measurement contract

The Phase 3 reconstruction sums squared partners’ shares of domestic merchandise exports in table 12-10-0173-01. The full measure uses the publisher’s world total. For ex-U.S. HHI the denominator is world less the U.S., and the U.S. is dropped from the squared sum. Each eligible geography-year must have a reconciled, nonnegative partner partition and zero value assigned to residual destinations. Zero reported values can be retained. A positive unallocated amount blocks the strict reconstruction. HHI runs from 0 to 1 and measures the evenness of shares. The published comparator is the **concentration ratio**, never the rebased “Index” field in table 12-10-0129-01. [Annual bilateral trade](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017301) · [Official concentration](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210012901) · [Phase 3 complete comparison](../data/phase3/destination_hhi_benchmark.csv)

The annual cube includes a world row and individual partner and special labels. Use only the detail partition to form squared shares and reconcile the partition to the separate world control. The Canadian merchandise program records the export country as the last known destination. A country label can identify a territory or a commercial destination. Phase 4A tests the impact of treating the U.S. and separately labelled U.S. areas as one destination, but retains the exact “United States” label for published project results. The official concentration metadata explicitly excludes chapters 98 and 99 in its **product** concentration measure. The documentation reviewed does not extend that exclusion to **destination** HHI, so the main denominator keeps those products. [Merchandise concepts and partner definitions](https://www150.statcan.gc.ca/n1/pub/13-605-x/2025001/article/00003-eng.htm) · [Statistics Canada diversification method](https://www150.statcan.gc.ca/n1/pub/13-605-x/2017001/article/54890-eng.htm)

## Targeted national differences

The comparison uses half a unit of the official decimal precision, **0.005**, as the tolerance. The raw bilateral values have a separate much smaller CAD rounding allowance. A mismatch just beyond the HHI cutoff is distinguished from a material discrepancy. The archived comparator uses former annual table 12-10-0133-01. The 2024 and 2025 CIMT cross-check constructs the partner portfolio by summing the official HS8 observations and uses its own sum as denominator. [Archived annual series](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210013301) · [Sensitivity and precision results](../data/phase4a/hhi_method_sensitivity.csv)

| Year and measure | Published | Reconstructed | Archived annual reconstruction | Assessment |
| --- | ---: | ---: | ---: | --- |
| 2013 all destinations | 0.58 | 0.574920 | 0.574920 | About 0.000080 below the published rounding interval. Summing partners or folding in U.S. areas leaves it outside. |
| 2016 all destinations | 0.57 | 0.575054 | 0.575054 | About 0.000054 above the interval. The tested archived vintage yields the same result. |
| 2018 all destinations | 0.55 | 0.555250 | 0.555250 | About 0.000250 above the interval. The U.S. area sensitivity moves it further from the interval. |
| 2022 all destinations | 0.59 | 0.581086 | **0.587571** | The archived value rounds to 0.59. Strong vintage evidence. |
| 2025 ex-U.S. | 0.10 | 0.093824 | Outside archived coverage | The detailed CIMT reconstruction also gives 0.093824. The U.S. area sensitivity gives 0.093893. Both remain below the 0.095 lower boundary. |

For 2022, the archived Canada world total was CAD **727.180 billion** and the active world total was CAD **731.201 billion**. The U.S. amounts were CAD **555.763 billion** and **555.603 billion**, respectively. The implied U.S. share moved from **76.427%** to **75.985%**. Canada’s published 2022 HHI is consistent with the archived vintage. The different trade amounts identify an observable vintage mechanism for the gap. The publisher’s exact concentration input files remain unverified. The three boundary cases and the 2025 ex-U.S. case remain unresolved.

## Significant subnational differences

| Geography and year | Measure | Published | Reconstructed | Cross-check |
| --- | --- | ---: | ---: | --- |
| Yukon 2025 | Ex-U.S. | 0.11 | **0.214931** | HS8 CIMT 0.214932. U.S. area folding yields 0.218333. |
| Yukon 2025 | All destinations | 0.82 | **0.766661** | HS8 CIMT 0.766661. U.S. area folding yields 0.768420. |
| Prince Edward Island 2024 | All destinations | 0.65 | **0.573525** | HS8 CIMT 0.573525. |
| Prince Edward Island 2023 | All destinations | 0.64 | **0.575586** | Normalizing by the partner sum leaves the discrepancy. The archived annual series ends in 2022. |
| Prince Edward Island 2018 | All destinations | 0.66 | **0.606158** | Archived table returns 0.606158. |
| Ontario 2022 | All destinations | 0.62 | **0.597256** | Archived reconstruction **0.616588** rounds to 0.62. |

The Phase 4A detailed CIMT reaggregation agrees with the active bilateral reconstruction across all 56 comparable 2024–2025 geography-year-measure cells within **0.000004**. Small non-U.S. portfolios amplify the influence of individual Yukon flows. For 2025 Yukon and 2024 Prince Edward Island the exact active U.S. share also fails to reconcile the two *published* HHI measures under `HHI_all = s_US² + (1 − s_US)² × HHI_exUS`, even after allowing the official rounding intervals. A different historical market share or a different reporting universe is plausible. The archived data support that interpretation for 2022 Ontario and Canada. The larger Yukon and P.E.I. differences remain unresolved.

## Alternatives checked and use rule

- **Residual and denominator.** The targeted active cells have zero reported residual value. Replacing the world denominator with the sum of destination amounts changes the targeted indices by less than 0.0001. For the separate 2020 exception, a positive Canada-labelled destination amount guards the strict reconstruction. The Phase 3 sensitivity and published ratios remain visible in the [quality report](phase3_quality_report.md).
- **Partner territories.** The U.S. regrouping is a sensitivity, with matching denominator changes for ex-U.S. It moves the two large Yukon values by roughly 0.002 and 0.0034. It fails to explain the big regional gaps and does not reproduce the national exceptions.
- **Classification and vintages.** The aggregate HHI uses the all-product row, so pure reassignment across NAPCS sections would leave the country weights unchanged. Geography of production, country attribution, archived snapshots and exclusions can affect totals. Active detailed HS8 recreates the current HHI in 2024–2025. The predecessor recreates 2022 Canada and Ontario at published precision. No dated documentation found establishes a general official adjustment that reconciles every comparison.
- **Official geographic publication.** The May 6, 2025 Statistics Canada release explicitly presents provincial and territorial destination HHI despite the cube’s footnote describing only product concentration at the provincial level. This corroborates the existence of the provincial series and warrants retaining it. [The Daily, provincial results](https://www150.statcan.gc.ca/n1/daily-quotidien/250506/dq250506a-eng.htm)

Keep the reconstructed and published measures in parallel. The proposed research panel uses the consistently reconstructed ex-U.S. HHI, conditional on eligibility. Published total-export HHI is a benchmark and sensitivity at its own aggregate grain. For small portfolios, report positive partner counts, export denominators, and geography/product exclusions. Producer geography and last known destination should remain fixed when constructing future panels. The eight targeted years provide 224 geography-year-measure sensitivity rows.

## Synthèse en français

Le millésime archivé reproduit à l’arrondi l’IHH publié du Canada et de l’Ontario en 2022. Les écarts nationaux près du seuil d’arrondissement en 2013, 2016 et 2018, celui de 2025 hors États-Unis et plusieurs écarts régionaux demeurent inexpliqués. Les données détaillées de la CICM reproduisent les IHH reconstruits pour 2024 et 2025. Les deux versions seront conservées séparément.
