# Phase 4A model selection

**Recommend Design C as the primary analysis.** Estimate the historical association between the concentration of a province–product group’s non-U.S. export destinations and the size of its subsequent annual nominal export change. The trade cube supports this at consistent grain. The Phase 4A coverage audit finds 1,513 eligible cells out of 1,540 before fixed-effect singleton and full-design checks. Approve the specification and reporting rules before estimation. [Design C](econometric_design_C.md) · [Coverage audit](../data/phase4a/design_C_coverage.csv)

## Evaluation against the research criteria

Weights and scores are scientific planning judgments on a 1–5 scale. The weighted scores divide each weighted rating by five and sum to a 0–100 score. Identification refers to credibility for the stated estimand; a high rank does not grant causal interpretation.

| Criterion | Weight | A · Steel export response | B · Employment response | C · Concentration and instability |
| --- | ---: | ---: | ---: | ---: |
| Economic relevance | 20% | 5 | 5 | 4 |
| Identification credibility | 20% | 3 | 2 | 3 |
| Data quality and comparability | 15% | 3 | 3 | 5 |
| Reproducibility | 15% | 3 | 3 | 5 |
| Originality | 10% | 5 | 4 | 4 |
| Practical feasibility | 10% | 3 | 2 | 5 |
| Professional relevance | 10% | 5 | 5 | 4 |
| **Weighted score** | **100%** | **76** | **68** | **84** |
| **Readiness rank** | | **2** | **3** | **1** |

1. **C · Primary.** The same official customs cube supplies the outcome, predictor and initial controls. Strict concentration rules and the product/composition sensitivity directly address the finding that non-U.S. concentration rose even as the U.S. share fell. The historical depth makes exclusions and diagnostics visible. Reverse causality, common destination shocks, product-price exposure, exporter selection and ten provincial clusters remain material.
2. **A · Secondary, conditional.** A legally dated steel shock offers the best opportunity to address trade-policy response directly. Coverage audit and U.S. mirror evidence could sharpen the estimand. CUSMA treatment, simultaneous policy changes, post-shock sample length and the need for independent treated families lower current readiness. Proceed first with code-level mapping and coverage/validation only. If identification fails after mapping, retain a descriptive event analysis. [Design A](econometric_design_A.md) · [Tariff chronology](tariff_policy_timeline.md)
3. **B · Deferred.** Provincial employment is policy-relevant and official broad outcomes are available. The necessary production-industry allocation, broad-sector within-province contrasts, supplier spillovers and small number of independent exposure units make this the weakest candidate for a defensible policy-effect estimate now. A coverage-labeled employment comparison can inform later work. [Design B](econometric_design_B.md)

## Secondary descriptive work

Report the Canada and province-wide HHI series from both sources at their actual grain. Keep the 2024–2025 product and destination decompositions and the gold-exclusion check alongside the main protocol. Compare signed export growth and downside changes in Design C after approval, with no claims about real trade unless separate compatible physical quantities support them. Treat a future tariff pilot and employment design as separate studies with their own eligibility checks. [Diversification mechanisms](diversification_mechanisms.md) · [HHI reconciliation](hhi_reconciliation.md)

## Decisions requiring scientific approval

- Approve C as the primary **associational** design. Confirm the absolute log-change outcome, lagged ex-U.S. HHI, fixed effects, baseline controls and interpretation per 0.10 HHI.
- Approve the main equal-weight cell estimand and decision rule for minimum portfolio size, an unbalanced main panel, an extensive-margin sensitivity, the C14 exclusion, and reporting of the ten-cluster inference.
- Approve the reconciliation rule that reconstructed HHI is primary and the official values are preserved at their published grain. Approve retaining strictly invalid HHI as missing and retaining the ambiguous official differences as unresolved.
- Authorize A’s legal/code pilot separately. Set a threshold for verified coverage of treatment and comparison lines, minimum number of independent families and post months, and acceptable USITC validation evidence. A and B require a further decision before coefficient estimation.

## Synthèse en français

Le modèle **C** est recommandé. Il mesure, à l’échelle province–produit, l’association entre la concentration des destinations hors États-Unis et l’ampleur de la variation annuelle ultérieure des exportations nominales. Le modèle **A** vient ensuite, sous réserve de vérifier les codes tarifaires, les exemptions et les comparateurs de l’acier. Le modèle **B**, sur l’emploi, exige d’abord une concordance documentée entre produits et industries ainsi qu’une variation provinciale suffisante de l’exposition.
