# Phase 5 quality assurance and release inventory

> Historical review. The Phase 7A checklist records current approval and licensing status. [Current checklist](final_approval_checklist.md)

The English and French working papers, local Streamlit app and publication materials are ready for final scientific review. The paper and dashboard preserve the published Phase 4B results. The only new calculations are presentation tabulations of locked data, including the detailed export contribution bridge, destination changes and localized supporting tables.

## Deliverables

| Component | Delivered material |
| --- | --- |
| English working paper | [Source](../paper/working_paper_en.md) · [20-page PDF](../paper/rendered/canada_us_trade_en.pdf) · [Self-contained HTML](../paper/rendered/canada_us_trade_en.html) |
| Document de travail en français | [Source](../paper/working_paper_fr.md) · [PDF de 21 pages](../paper/rendered/canada_us_trade_fr.pdf) · [HTML autonome](../paper/rendered/canada_us_trade_fr.html) |
| Dashboard | [Streamlit entry point](../dashboard/app.py) · [Local stylesheet](../dashboard/style.css) · [Dashboard dependencies](../requirements-dashboard.lock) |
| Figures and values | Eleven figures in each paper. Four new charts per language in PNG and SVG. The [manifest](../figures/phase5/manifest.json) records their hashes. [Shared numerical values](../data/phase5/facts.json) · [Source lock](../data/phase5/source_lock.json) |
| Reproduction code | [Data preparation](../src/trade_audit/phase5_data.py) · [Report renderer](../src/trade_audit/phase5_paper.py) · [Figure renderer](../src/trade_audit/phase5_figures.py) · [Full Phase 5 lock](../requirements-phase5.lock) |
| Publication materials | [GitHub-ready README](../README.md) · [Bilingual abstract](research_abstract_bilingual.md) · [Methods](methodology.md) · [Attribution and licensing](data_attribution.md) · [Deployment instructions](dashboard_deployment.md) |

## Executed checks

| Check | Observed result |
| --- | --- |
| Full project test suite | **53 passed, 5 warnings in 22.58 seconds**. The five warnings concern PyMuPDF SWIG type metadata deprecations. There were no failed or skipped tests. |
| Bilingual statistics | English and French use the same numeric inputs for shares, net export changes, HHI, model scaling, interval endpoints, p-value and sample sizes. Assertions check the shared tokens and the rendered reports. |
| Exposure, units and periods | The tests confirm province and NAPCS coverage, the official source periods, denominator reconciliation, nominal CAD units and a separate monthly filter. The selected monthly interval never enters the annual series. |
| HHI and charts | All paper figures match their manifests. The dashboard checks the national and provincial chart values against the filtered rows, confirms the 2020 reconstructed HHI remains empty, and reconciles the HS 710812 and 270900 bridge to CAD 28,796,022,412. |
| Econometrics | The dashboard interval trace reproduces the coefficient and the two restricted Webb endpoints per 0.10. Tests confirm the frozen estimates, all 26 secondary intervals, and the sign change from lagged-value weighting. |
| Filters and exports | All eight dashboard sections execute in both languages. Tested interactions include changing frequency, time window, provincial coverage, ranking measure, product, destination, official HHI benchmarks, and robustness subsets. The Streamlit media route returned HTTP 200, a CSV attachment header and the exact filtered July–September 2026 source rows. |
| Browser and responsive layout | The actual local app was checked at 1366 × 920 and 390 × 844. At 390 px, document width was 390 px and the four KPI cards each used 358 px in a stack. Accessibility inspection found labelled controls, chart descriptions, source links and named CSV controls. |
| Paper reproduction and rendering | Both HTML rebuilds matched their SHA-256 values. Rebuilt PDFs matched the delivered page counts and extracted text. PDF binaries differ between runs. Both final PDF editions were rasterized and inspected for page structure, figures and table readability. |

[Exact test output](../logs/phase5/pytest.txt) · [Archive replay tests](../logs/phase5/bundle.txt) · [Browser check](../logs/phase5/browser.txt) · [Publication hashes](../paper/rendered/manifest.json) · [Phase 5 tests](../tests/test_phase5.py)

## Open review items

- **Scientific interpretation.** Design C is an imprecise historical association. Price and quantity composition, shared destination shocks, active-portfolio selection, and the small number of provinces remain relevant. The uncertainty spans zero. Design A lacks independently credible comparisons and remains a descriptive feasibility pilot. [Inference audit](statistical_inference_audit.md) · [Steel pilot](design_A_tariff_pilot.md)
- **Source limitations.** The 2020 annual–monthly difference and remaining official-HHI differences are documented. The latest verified monthly observation in this pinned release is September 2026. The app does not refresh automatically. [Methodology](methodology.md) · [HHI reconciliation](hhi_reconciliation.md)
- **Accessibility verification.** This was a browser and application smoke check, not a formal WCAG assessment. The browser download-event check was interrupted. The verified result is the application’s HTTP attachment response and exact payload. Browser file-save confirmation remains open. Test assisted reading and the chosen browser’s download handling during any later hosting trial.
- **Publication and deployment.** Final scientific approval, author and licence details, a compatible Python hosting environment, and a target host and access policy are pending. The local app requires no API keys. A later hosted smoke test must use the same manifest and verify both languages and a CSV. No GitHub push, remote deployment or LinkedIn publication occurred. [Deployment requirements](dashboard_deployment.md) · [Attribution and rights](data_attribution.md)
