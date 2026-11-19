# The diversification paradox

## Evidence from detailed customs records

Canada’s domestic merchandise exports outside the United States rose **CAD 28.796 billion** between 2024 and 2025. Non-monetary unwrought gold (HS 710812) accounted for **CAD 13.159 billion**, or **45.7%** of the increase. Crude petroleum (HS 270900) accounted for another **CAD 8.236 billion**, or **28.6%**. The increase across the two codes accounted for **74.3%** of the net non-U.S. gain. These are contributions to the change in nominal exports. [Statistics Canada detailed CIMT domestic exports](https://open.canada.ca/data/en/dataset/2909a648-5753-4924-878a-b069392d9cde) · [HS6 and destination calculations](../data/phase4a/hs6_country_value_changes.csv)

The calculation uses the national sum of the Canadian HS8 records across provinces and destination states within each partner. The 2024 and 2025 files contain **1,292,368** and **1,264,188** records, respectively, with 12 months and no duplicates on month × HS8 × partner × province × destination state. HS8 prefixes produce the common HS6 groups. The national world and U.S. totals differ from the Phase 3 annual controls by at most **CAD 169** across the four year-by-partner comparisons. This is a separate publication path for related customs statistics. Partner codes GB and US identify the United Kingdom and United States. A blank year in the output denotes no reported flow in the file. For changes in published totals, the absent record contributes no reported amount. It does not establish a structural zero for modelling.

| Product, HS6 | Change outside the U.S., CAD bn | Interpretation |
| --- | ---: | --- |
| 710812 · Non-monetary unwrought gold | +13.159 | U.K. +17.743, offset partly by Switzerland −3.271 and Hong Kong −1.180 |
| 270900 · Crude petroleum | +8.236 | China +4.635, followed by smaller gains including the Netherlands and Hong Kong |
| 760110 · Unwrought non-alloyed aluminium | +1.445 | Major positive contributor beyond gold and crude |
| 260300 · Copper ores and concentrates | +1.142 | Increase in nominal export value |
| 310420 · Potassium chloride | +1.118 | Increase in nominal export value |
| 270112 · Bituminous coal | −2.017 | Largest negative HS6 contribution outside the U.S. |

The U.K. gained **CAD 18.196 billion**, equivalent to **63.2%** of the overall non-U.S. gain. HS 710812 accounted for **97.5%** of the net U.K. gain. Unwrought silver (710691) added **CAD 416 million** in published flows, with no reported 2024 amount in the file. Crude oil added **CAD 319 million** to the U.K. Net movements in remaining products partially offset those smaller positive contributions. Statistics Canada separately attributes an increase of approximately CAD 13.5 billion in non-U.S. exports to its broader unwrought gold, silver and platinum-group grouping. That grouping and the present HS6 classification have different scopes. [Statistics Canada spring 2026 economic analysis](https://www150.statcan.gc.ca/n1/pub/36-28-0001/2026004/article/00005-eng.htm)

## Changes in product and destination composition

The U.K. share of Canada’s non-U.S. exports rose **6.707 percentage points**, from **15.719%** to **22.426%**. For each HS6 product, let `w` be its weight in the non-U.S. total and `s` the U.K. share within its non-U.S. destinations. For products with a positive denominator in both years, the exact midpoint identity is `Δ(w × s) = mean(w) × Δs + mean(s) × Δw`. Products without an observed positive denominator in both years contribute their net entry or exit in the published portfolio as a separate term. [Product and destination composition](../data/phase4a/uk_share_composition.csv)

| Component of U.K. share change | Percentage points |
| --- | ---: |
| Destinations shifted within HS6 products | +3.165 |
| HS6 product weights changed | +3.542 |
| Net contribution of entry or exit in the reported portfolio | −0.000007 |
| **Total** | **+6.707** |

Gold alone contributed **+6.910 points**, split between **+3.529** within product and **+3.380** from its increased weight. All other products together contributed roughly **−0.203 points**. This decomposition concerns where Canadian shipments were recorded and the value weights of products. It identifies neither the final location of consumption nor the underlying causal driver.

| Non-U.S. portfolio | HHI 2024 | HHI 2025 | U.K. share 2024 | U.K. share 2025 |
| --- | ---: | ---: | ---: | ---: |
| All products | 0.072346 | 0.093824 | 15.719% | 22.426% |
| Excluding HS 710812 | 0.068295 | 0.070721 | 3.626% | 3.555% |
| Excluding chapter 71 | 0.070279 | 0.072502 | 3.697% | 3.358% |

Removing unwrought gold leaves **CAD 15.637 billion** of additional non-U.S. exports and reduces the increase in the HHI from **0.021478** to **0.002426**. The U.K. share edges down under that exclusion. The scenario recalculates both numerators and denominators. It is a change-of-sample sensitivity for a nonlinear index, with no additive causal attribution implied. Chapter 71 also includes precious stones, jewellery and other articles. [Exclusion scenarios](../data/phase4a/non_us_gold_exclusion_sensitivity.csv)

## Quantities and unit values

We compare physical quantities only within a destination and the same HS8 code when every positive-value record reports positive quantity and a single nonblank unit is consistent in both years. We use the Canadian Export Classification description for each line. For a compatible pair, `V = Q × u`, with `u` the CAD unit value. The exact decomposition is `ΔV = mean(u) × ΔQ + mean(Q) × Δu`. It keeps the amount term apart from the unit-value term. Quantity is from customs declarations. Unit value can also move with quality, shipment mix, timing, and exchange rates. [CIMT files and commodity descriptions](https://open.canada.ca/data/en/dataset/2909a648-5753-4924-878a-b069392d9cde) · [HS8 quantity audit](../data/phase4a/hs8_quantity_checks.csv)

| Compatible destination × code | Quantity | Unit value in CAD | Midpoint contributions to nominal export change |
| --- | --- | --- | --- |
| U.K. × 71081210, unwrought non-monetary gold of at least 99.95% gold by weight | 207.20 to 252.13 million grams, **+21.7%** | 107.38 to 158.62 per gram, **+47.7%** | Quantity **+CAD 5.976 bn**, unit value **+CAD 11.768 bn** |
| China × 27090010, crude petroleum oils with density at least 0.9042 | 4.074 to 12.656 million m³, **+210.6%** | 600.97 to 543.53 per m³, **−9.6%** | Quantity **+CAD 4.911 bn**, unit value **−CAD 0.480 bn** |

The main gold line explains almost the entire U.K. HS 710812 value. The lower-purity line has CAD 12,897 reported in 2025 and no reported 2024 flow, so that line stays outside the quantity decomposition. Similarly, the China crude comparison covers a matched code. Another China crude code reports CAD 204.9 million in 2025 with no reported 2024 value.

Global Affairs Canada’s national gold assessment reports **+45.2% in export prices and −6.3% in export volume** in 2025 for its aggregate gold series. It also describes higher quantities and prices for shipments to the U.K. Those findings are consistent with a rising quantity in the specific U.K. customs line and a different result for all gold exports nationally. London’s trading and storage role is a plausible economic mechanism for the destination pattern. Establishing the final buyer, origin of funds or why a shipment went to London would require additional evidence. [Global Affairs Canada, State of Trade 2026, box 1.4.1](https://international.canada.ca/en/global-affairs/corporate/reports/chief-economist/state-trade/2026)

**Interpretation.** Nominal export dependence on the U.S. fell as non-U.S. flows rose, while non-U.S. destination shares became less even. Two commodity codes dominate the dollar increase. Selected physical lines show growth, and the broader portfolio result remains a nominal comparison. Broad real diversification would require consistent deflators or matched quantity coverage across products and destinations.

## Synthèse en français

L’or non monétaire sous forme brute (SH 710812) explique **13,16 G$ CA** de la hausse de **28,80 G$ CA** des exportations hors États-Unis. Le pétrole brut ajoute **8,24 G$ CA**. Au Royaume-Uni, la principale ligne d’or affiche une hausse de **21,7 %** de la quantité déclarée et de **47,7 %** de la valeur unitaire. Affaires mondiales Canada constate toutefois une baisse du volume des exportations d’or à l’échelle nationale selon sa propre série. L’IHH hors États-Unis augmente beaucoup moins lorsqu’on retire le SH 710812. Ces résultats documentent une recomposition des valeurs exportées et des quantités pour certaines lignes, avec une couverture insuffisante pour conclure à une diversification réelle de l’ensemble du portefeuille.
