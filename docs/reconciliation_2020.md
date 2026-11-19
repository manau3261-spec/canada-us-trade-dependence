# 2020 trade reconciliation

## Finding

**The break is localized to the vintage of the active monthly export table.** Both archived predecessor tables reconcile for 2020. The February 2023 detailed customs file corroborates the current annual table across 28 world/U.S. headline totals and the archived monthly table across 336 monthly headline totals. The source material identifies a historical classification migration but provides no cell-level notice explaining the later changes in the active monthly file. For annual analysis, retain table 12-10-0173-01. For monthly analysis, retain table 12-10-0175-01 and keep its series separate from the annual observations.

## Matched comparison

We matched 14 geographies (Canada, ten provinces, three territories), 28 common partner labels (including the world total) and 13 common product keys (12 sections and the section total). The annual “Export” label denotes domestic exports under table 12-10-0173-01’s metadata. Monthly rows explicitly use “Domestic export.” Every comparison contained 12 distinct months and numeric inputs. The difference is monthly sum minus annual value. We retained publisher precision. Monthly values use thousands of CAD with zero decimals, and annual values report one decimal in thousands, giving **CAD 6,050** as the combined maximum rounding allowance per comparison, plus a negligible numerical allowance for floating-point sums. The overlap includes aggregates, so the 228 failures are comparisons, with totals and components sharing underlying transactions. [Annual table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017301) · [Monthly table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017501) · [Cell-level active comparison](../data/phase3/reconciliation_2020.csv)

| 2020 test | Comparable | Outside rounding | Largest absolute gap |
| --- | ---: | ---: | ---: |
| Active annual 12-10-0173-01 vs. active monthly 12-10-0175-01 | 5,096 | 228 | CAD 129.5743 million |
| Archived annual 12-10-0133-01 vs. archived monthly 12-10-0119-01 | 5,096 | 0 | CAD 3,600 |
| Detailed CIMT vs. active annual, world/U.S. all-product totals | 28 | 0 | Within CAD 50 for each |
| Detailed CIMT vs. archived monthly, world/U.S. all-product totals | 336 | 0 | Within CAD 500 for each |
| Detailed CIMT vs. active monthly, world/U.S. all-product totals | 336 | 153 | CAD 123.075 million, Canada world total in December |

The CIMT benchmark sums one HS2 member of the 2020 domestic export file, across chapters and U.S. destination states where applicable. The provincial and territorial origins are summed once to obtain the CIMT national value. The 28 annual checks are two partner universes × 14 geographies. The 336 monthly checks add 12 periods. Twenty-one of 28 archived annual totals matched CIMT within CAD 50, and its national world total differed by CAD 888. Those smaller vintage differences remain within the annual–monthly comparison’s combined published rounding allowance. [Archived annual table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210013301) · [Archived monthly table](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210011901) · [CIMT 2017–2022 files](https://open.canada.ca/data/en/dataset/b1126a07-fd85-4d56-8395-143aba1747a4) · [Supplementary source hashes](../data/provenance/phase3-supplementary-sources.json)

| Canada, all products | CIMT (CAD billions) | Active annual (CAD billions) | Active monthly sum (CAD billions) | Monthly minus annual (CAD millions) |
| --- | ---: | ---: | ---: | ---: |
| World | 478.638824 | 478.638824 | 478.768398 | +129.5743 |
| United States | 346.101438 | 346.101438 | 346.121792 | +20.3539 |

The discrepancy changes Canada’s 2020 U.S. share by **−0.0153 percentage points** if the monthly sums replace the annual amounts. December contributes **CAD 123.075 million** to the active monthly world-total difference against CIMT, around **95%** of the net annual difference. Canada’s world export gap in section C11, farm, fishing and intermediate food products, is **CAD 107.622 million**. There are **82** failures on world-total rows and **72** on U.S. rows, across product sections and geography. Canada accounts for 52 of the failures, Ontario 42, Quebec 29 and British Columbia 27. [Archived cell comparison](../data/phase3/reconciliation_2020_archived.csv) · [CIMT annual totals](../data/phase3/reconciliation_2020_cimt_totals.csv) · [CIMT month-by-month comparison](../data/phase3/reconciliation_2020_cimt_months.csv)

## What the evidence establishes

| Possible explanation | Evidence and disposition |
| --- | --- |
| File vintage or historical revision | **Supported at the source-series level.** For the 336 world/U.S. monthly headlines, 153 observations change between the archived and active monthly tables. Those same 153 differ from the detailed customs benchmark beyond monthly rounding. The annual benchmark corroborates the active annual table. |
| NAPCS version migration | **Documented, with effects on individual product categories.** The December 6, 2023 release introduced NAPCS 2022 in place of NAPCS 2017 for the merchandise program and supplied historical monthly values. A pure re-grouping of the same transactions would preserve all-product totals. The gap in those totals requires some additional change in source data, scope, or processing. The public migration note does not identify the 2020 cells. |
| Missing periods, partner labels, or geographies in the comparison | **Ruled out for the observed comparison keys.** Both vintage pairs have all 12 months, the same number of comparable keys and numeric inputs. This check cannot determine whether transaction-level coverage or processing changed within those cells. |
| Exact production cause and timing | **Unresolved.** The documents reviewed describe the revision process and the classification change. They do not document which production step revised the affected 2020 monthly cells or when each change entered the active file. The December 2023 migration establishes a public transition date, not the date of each record-level change. |

The archived monthly cube’s last reference month is September 2023, and its HTTP file modification date is December 7, 2023. The archived annual cube ends in 2022 and its file modification date is February 24, 2025. The CIMT 2020 file has a February 7, 2023 HTTP modification date. The active annual and monthly archives were released November 4, 2026. HTTP modification dates identify files, while release notices describe program changes. The contemporaneous notice cites seasonally adjusted revisions for reported September 2023 figures. The transactions in this check are on a customs basis and unadjusted, so that explanation cannot be imported directly. [October 2023 release and NAPCS migration](https://www150.statcan.gc.ca/n1/daily-quotidien/231206/dq231206a-eng.htm) · [Statistics Canada revision policy](https://www.statcan.gc.ca/en/statistical-programs/document/2201_D17_V1)

## Synthèse en français

Les **228 écarts** sur **5 096 comparaisons** se trouvent dans les séries actives. Les deux tableaux archivés concordent à la précision publiée. Dans le fichier douanier détaillé, les **28 totaux annuels** monde et États-Unis concordent avec le tableau annuel actif et les **336 observations mensuelles** avec le tableau mensuel archivé. Dans le tableau mensuel actif, **153** de ces 336 observations s’écartent du fichier douanier au-delà de l’arrondissement.

Pour le Canada, la somme mensuelle active dépasse le total annuel de **129,5743 millions de dollars** pour le monde et de **20,3539 millions** pour les États-Unis. L’écart est donc propre au millésime de la série mensuelle active. Les 12 mois et les mêmes clés de comparaison sont présents. La migration vers le SCPAN 2022 est documentée. Un simple reclassement des mêmes expéditions ne changerait pas le total tous produits. Les sources publiques consultées ne permettent pas d’identifier l’opération précise à l’origine de chacun des écarts. Conserver les séries annuelles et mensuelles séparément.
