# Methodology and data dictionary

The paper and dashboard read a common, source-locked set of verified Phase 3–4B outputs. SHA-256 is checked on every input load before display or rendering. Establishing a new lock is a separate deliberate vintage decision that requires validating upstream files. The automated test suite checks the stored lock, expected periods and model values. [Lock](../data/phase5/source_lock.json) · [Data quality record](phase5_quality_report.md)

| Measure | Construction and units | Main coverage |
| --- | --- | --- |
| U.S. domestic merchandise export share | U.S.-bound nominal domestic exports divided by the same-cell official world total. Fraction in data, percentage in figures. | Annual 2010–2025 and separate monthly 2025-01–2026-09 |
| Customs export values | Producer geography and last known destination on a customs basis. Domestic exports exclude re-exports. Phase 3 amounts are CAD thousands in current dollars. | Canada, provinces, territories and NAPCS where available |
| Gross export intensity | Same-year nominal customs export value divided by current provincial GDP at basic prices. | Comparable 2010–2023 in the pinned inputs |
| Destination HHI | Sum of squared shares, scale 0–1. Non-U.S. version removes the U.S. from the sum and denominator. Official published HHI is retained as a separate comparison. | Annual, with strict eligibility gaps |
| HS commodity bridge | Sum of changes in nominal exports across non-U.S. destinations, resolving separate 710812 and 270900 contributions and all other products net. Original detailed trade is in CAD. | 2024–2025 |
| Matched quantities | Same HS8, destination and unit in both periods, with complete positive quantity reporting for every positive-value included line. Unit values are current CAD per physical unit. | Select lines, 2024–2025 |
| Value added and jobs | Domestic value added or jobs linked to U.S. foreign demand using supply-and-use modelling and geography-specific totals. | National through 2024, subnational 2013–2022 |
| Design C outcome | Absolute log difference in non-U.S. domestic merchandise export value from t to t+1, with HHI and controls at t−1. | Ten provinces × eleven sections × starts 2011–2024 |
| U.S. import mirror | Calculated duties divided by imports-for-consumption customs value in USD in the same HTS10 group. | January, April and May 2025 snapshots |

### Periods, missingness and filters

The national dashboard’s frequency selection chooses one CSV before filtering the date range. Annual, monthly and matched-window values are served independently. Provincial heatmaps use the annual frequency. Shares are undefined if the denominator is zero or unavailable. The model’s positive endpoints follow from the log transformation. Rows prevented by a reported positive unallocated amount remain missing in the reconstructed HHI. Published benchmark values are drawn separately, and charts do not connect gaps. Phase 4A documents unresolved official vs reconstructed HHI inconsistencies. [HHI reconciliation](hhi_reconciliation.md) · [2020 annual–monthly reconciliation](reconciliation_2020.md)

The product section selector uses NAPCS/SCPAN labels. It does not infer a NAICS industry treatment. Country comparison uses national non-U.S. denominators and is labelled independently of provincial HHI filters. CSV exports use stable code and English field names, with units in the data headers. The raw reported flows are preserved. Aggregation of the HS value-change file uses the published zero-contribution convention without treating absent trade as a structural zero. [Detailed decomposition](diversification_mechanisms.md)

### Inference and policy language

The preregistered model uses equal cells, province–product, product–year and province–year fixed effects, and lagged log export size and U.S. share controls. The primary inference uses province CR1 and the null-imposed Webb bootstrap-t. Point estimates on the full HHI scale are divided by ten for a 0.10 index increase, including interval endpoints. Other outcomes and weights address separate estimands. Full robustness CSVs retain their predictor increment. [Preregistration](phase4b_preregistered_specification.md) · [Inference audit](statistical_inference_audit.md)

The March steel pilot distinguishes statutory codes and rate from economic incidence. It does not estimate a coefficient. The trade analysis distinguishes current-dollar merchandise, real quantities in specific verified units, and domestic economic value added. [Design A pilot](design_A_tariff_pilot.md)

### Français

Les deux produits lisent les mêmes fichiers vérifiés et verrouillés. Les parts se rapportent aux exportations nationales de marchandises en dollars courants. Les séries annuelle et mensuelle restent distinctes. Les valeurs manquantes sont conservées et aucun graphique ne les interpole. Le modèle C estime une association historique pour des portefeuilles provinciaux actifs. Le pilote sur l’acier vérifie les codes, les périodes et les comparateurs, sans estimer d’effet. [Document de travail](../paper/rendered/canada_us_trade_fr.html)
