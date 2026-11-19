# Design A · March 2025 core steel feasibility pilot

**Decision: use the mapping for descriptive validation. Defer tariff-effect estimation.** The legal map and official U.S. import data are available. A comparison with enough common product support, verified exposure and independent shock variation was not established. This pilot estimates no Design A coefficients. [Approved Design A](econometric_design_A.md) · [Tariff chronology](tariff_policy_timeline.md)

## Legal dates and scope

| Date | Pilot treatment and consequence |
| --- | --- |
| February 10, 2025 | Proclamation 10896 announced the reinstatement of Section 232 steel duties for previously exempt Canada-origin entries and expanded derivative coverage. February is an anticipation month. [Signed proclamation](https://www.govinfo.gov/content/pkg/FR-2025-02-18/html/2025-02833.htm) |
| March 4 and March 7 | The separate northern-border IEEPA charge began, followed by an exemption for qualifying duty-free CUSMA entries. These changes precede the steel effective date and can affect treated and comparison codes differently. [CUSMA amendment](https://www.whitehouse.gov/presidential-actions/2025/03/amendment-to-duties-to-address-the-flow-of-illicit-drugs-across-our-northern-border-0c3c/) |
| March 12, 00:01 EDT | Core products in Chapter 99 note 16(j) became subject to the 25% additional rate under **9903.81.87** for ordinary entries for consumption or withdrawal for consumption. The notice gives exact ordinary HTS headings and subheadings. Separate codes and conditions apply to foreign trade zones, derivatives and derivative U.S. melt/pour treatment. Existing qualifying exclusions could continue through expiration or volume exhaustion. March has multiple policy transitions. [90 FR 11249, implementation and annex](https://www.govinfo.gov/content/pkg/FR-2025-03-05/html/2025-03598.htm) · [CBP CSMS 64384423](https://content.govdelivery.com/bulletins/gd/USDHSCBP-3d66da7) |
| April 29 | EO 14289 imposed stacking priorities, applied retroactively to March 4 for covered combinations. CBP's worked example assigns nonqualifying Canadian steel to the 25% border IEEPA charge and CUSMA-qualified core steel to the 25% Section 232 charge under this regime. The statutory steel listing does not establish an incremental 25-point wedge for every Canada-origin entry. [EO 14289](https://www.whitehouse.gov/presidential-actions/2025/04/addressing-certain-tariffs-on-imported-articles/) · [CBP CSMS 65054270](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3e0a63e) |
| June 4, 00:01 EDT | The applicable steel rate increased to 50% for Canada, and priority with IEEPA was amended. June is outside the proposed 25% comparison. [June proclamation and annexes](https://www.whitehouse.gov/presidential-actions/2025/06/adjusting-imports-of-aluminum-and-steel-into-the-united-states/) |

The pilot implements note 16(j) for ordinary core products. It enumerates **744 HTS10 reporting lines across 301 HTS8 subheadings, 167 HS6 products, and 29 HS4 headings** in the archived March 11 U.S. schedule. The legal rule covers specified flat-rolled products; bars, rods, wire, sections and rail products; tubes and pipes; primary and semifinished forms; and stainless products. The exceptions 7216.61.00, 7216.69.00 and 7216.91.00 stay out of the core group, and may require separate derivative scope work. For example, 7208.10.15.00 is a core line. HS6 730210, rails, has 11 covered U.S. reporting lines across two HTS8 subheadings. [USITC 2025 HTS Revision 4](https://www.usitc.gov/2025_hts_revision_4) · [Exact pilot map](../data/phase4b/tariff_pilot/us_legal_hts10.csv)

## Canadian concordance and monthly support

Canadian HS8 and U.S. HTS10 national suffixes distinguish different products within the same international HS6. The concordance retains all U.S. HTS10 descendants of each screened HS6, requires homogeneous core treatment for the core designation, and checks the Canadian HS6 description in the four annual CIMT dictionaries for 2022–2025. Of the 167 legal core HS6 parents, **166** have stable Canadian descriptions and positive reported trade to the screened destinations. The map establishes stable classification and eligibility under the published core schedule, with residual scope at entry for exclusions, Chapter 98 and other regimes. [Canadian Export Classification](https://www150.statcan.gc.ca/n1/en/catalogue/65-209-X2025001) · [Canadian HS6 links](../data/phase4b/tariff_pilot/hs6_linkage.csv)

The four CIMT files contain 1,283,380 HS8 records in 2022, 1,294,235 in 2023, 1,292,368 in 2024 and 1,264,188 in 2025. Each file has twelve months. For the pilot, January 2022–January 2025 gives **37** pre-event months. February–March 2025 are transition months. April–May gives only **two** full post months before the June increase. The audit counts a positive month only when the archive actually reports a positive flow. Missing reported flows remain blank.

| Candidate destination | Core HS6 with ≥1 positive pre month | Core HS6 positive in both post months | Stable core HS6 positive in all 37 pre and both post months |
| --- | ---: | ---: | ---: |
| United States | 166 | 107 | 86 |
| Mexico | 96 | 16 | 4 |
| United Kingdom | 54 | 1 | 0 |
| Germany | 48 | 2 | 0 |
| Japan | 40 | 3 | 0 |
| South Korea | 24 | 1 | 0 |

Mexico is the clearest *candidate* destination from this positive-month screen. It shares full support with the U.S. on only **four core HS6 lines** (721049, 722530, 722830, 730630). One overlaps a separate corrosion-resistant steel proceeding. Commerce’s Canadian preliminary dumping determination applied from **April 10, 2025**. The legal scope includes some 7210.49.00 child lines and depends on the written product definition. Pig iron, ferroalloys, direct-reduced iron, scrap, and iron or steel powders (7201–7205) are potential upstream controls. Fourteen of their HS6 lines have full U.S. support across four headings. Only one upstream HS6, 720521, has full common U.S.–Mexico support. These input products differ from finished steel and can be affected by substitution, demand shifts, and border policy. Other destinations can absorb trade diverted from the U.S. and face their own market and policy changes. [Coverage rows](../data/phase4b/tariff_pilot/canadian_coverage.csv) · [Canadian preliminary AD determination](https://www.govinfo.gov/content/pkg/FR-2025-04-10/html/2025-06135.htm) · [Corrosion-resistant scope and illustrative codes](https://www.govinfo.gov/content/pkg/FR-2025-12-19/html/2025-23430.htm)

The pilot finds **29 nominal treated HS4 families**, of which **24** contain a stably aligned HS6 with continuous U.S. support. The primary law puts all 29 under **one common effective-date cohort**. Four families retain the strict common U.S.–Mexico match before confounder checks. No count of independent identifying shocks is verified. The screen does not rule out all future designs with discontinuous positive-flow histories. Such a design would still need an audited no-flow treatment and a credible counterfactual.

## U.S. import mirror

The official Census Merchandise Trade Imports detailed files for **January, April and May 2025** were retrieved and read at HTS10 and Canada-origin code 1220. The pilot aggregates compatible imports-for-consumption customs value, dutiable value and calculated duty across districts and separately preserves rate-provision groupings. Code layouts are included in the original archives. No observed positive scoped U.S. HTS10 in the three snapshots failed the March-edition concordance. DataWeb offers the same Census-origin concepts as an alternative, subject to query coverage and the account required for its API.

| Snapshot for covered core steel | Imports for consumption, USD m | Calculated duties, USD m | Calculated duties / consumption value |
| --- | ---: | ---: | ---: |
| January 2025 | 637.54 | 0.00 | 0.00% |
| April 2025 | 446.92 | 102.04 | 22.83% |
| May 2025 | 411.80 | 93.07 | 22.60% |

These ratios confirm usable import and duty fields for the feasibility check. The numerator is an administrative estimate under applicable rates and claims. It does not establish a Section 232-only rate, net duties after refunds, or effective incidence on firms or consumers. Anti-dumping and countervailing duties are outside the calculated-duty field as described by DataWeb. Statutory eligibility, claimed CUSMA treatment and approved exclusions need separate evidence, and import entry and Canadian export reporting dates can differ. [Census source files](https://www.census.gov/foreign-trade/data/IMDB.html) · [USITC calculated-duty definitions](https://dataweb.usitc.gov/trade/search/Import/HTS.) · [Mirror details](../data/phase4b/tariff_pilot/us_import_mirror.csv) · [Source hashes and URLs](../data/phase4b/design_A_source_manifest.json)

## Conditions before an estimation decision

A later protocol would need a clean comparison with more common product support, a line- and date-level map of preference and overrides, and separate screens for concurrent trade remedies and Canadian retaliation. It would also need enough independent policy variation to support its inference. Longer post coverage would require explicit design for the June 4 rate increase and other later policy changes. With the policy-comparison work unresolved and two full months in the original post window, the pilot remains a **no-go for estimation**.

**Synthèse.** Le rapprochement des codes et des données miroir permet une validation descriptive. Seuls quatre produits à six chiffres visés disposent d’une couverture mensuelle complète aux États-Unis et au Mexique, dont un touché par une procédure parallèle. Les comparateurs et les variations indépendantes restent insuffisamment établis pour estimer un effet tarifaire.
