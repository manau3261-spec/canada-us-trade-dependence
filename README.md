# Canada's Economic Dependence on the United States

[Français](README.fr.md)

**Manau Salaun** · Graduate Student in Economics, Université de Sherbrooke · 2026

Independent Applied Economics Research. The academic affiliation is provided for identification.

This repository contains a bilingual working paper, reproducible analysis, and the **Canada–U.S. Trade Intelligence Monitor**. The annual merchandise series covers 2010–2025. The separate monthly update covers January 2025–September 2026. Both use the archived November 2026 vintage.

| Read or run | Location |
| --- | --- |
| *Canada Is Trading Less with the U.S. — But Is It Really Becoming Less Dependent?* | [English PDF](paper/rendered/canada_us_trade_en.pdf) · [HTML](paper/rendered/canada_us_trade_en.html) |
| *Le Canada commerce moins avec les États-Unis. Sa dépendance diminue-t-elle vraiment ?* | [PDF français](paper/rendered/canada_us_trade_fr.pdf) · [HTML](paper/rendered/canada_us_trade_fr.html) |
| Abstracts | [English and French](docs/research_abstract_bilingual.md) |
| Selected figures | [U.S. share](figures/phase3/en/01_national_dependence.png) · [Commodity contributions](figures/phase5/en/03_commodity_bridge.png) · [Design C with confidence intervals](figures/phase4b/en/01_primary_inference.png) |
| Methods and evidence | [Methodology](docs/methodology.md) · [Scientific audit](docs/final_scientific_audit.md) · [Release audit](docs/phase7a_release_audit.md) |

## Research questions and results

1. **How did Canadian merchandise exposure change?** The U.S. share of domestic merchandise exports fell from **75.8% in 2024 to 71.7% in 2025**. In the separate January–September comparison, it fell from **73.3% in 2025 to 68.0% in 2026**. Both U.S. and non-U.S. export values rose across those matched months.
2. **How broadly were non-U.S. gains distributed?** Non-U.S. exports rose by **CAD 28.796 billion** in current dollars from 2024 to 2025. Unwrought non-monetary gold and crude petroleum contributed **74.3%** of the gain. Non-U.S. destination HHI rose from **0.07235 to 0.09382**. Excluding unwrought gold it rose from **0.06830 to 0.07072**. Comparable quantities cover selected products and markets. Real-volume diversification remains unresolved.
3. **Is concentration associated with later export movements?** In the preregistered panel, a **0.10** higher lagged non-U.S. HHI is associated with **+0.012827 log points** in subsequent absolute annual log movement of nominal exports. The restricted Webb 95% interval is **[−0.06049, +0.10525]**, **p = 0.7174**, with **1,454 observations**, **108 groups** and ten province clusters. The estimate is statistically inconclusive, all 26 secondary province-clustered intervals include zero, and value weighting reverses the point estimate's sign.

Domestic merchandise flows are customs values. The study reports domestic value added attributable to U.S. demand separately. The March 2025 steel pilot verifies legal and reporting support. Its two full post-policy months under the initial rate, overlapping measures and sparse comparisons prevent credible tariff-effect estimation. [Limitations](docs/remaining_limitations.md) · [2020 vintage reconciliation](docs/reconciliation_2020.md)

## Methods and provenance

The analysis combines Statistics Canada annual and monthly domestic merchandise exports, destination benchmarks, GDP and value-added series, and detailed customs records. Annual HHI uses observed partner shares and reports unreconciled cells as missing. The preregistered Design C uses province–product, product–year and province–year fixed effects with province-clustered inference and a restricted Webb bootstrap. The official tariff annex, USITC tariff schedule and U.S. Census import aggregates support the descriptive pilot. [Source definitions](docs/methodology.md) · [Provenance receipts](data/provenance/) · [Data lock](data/phase5/source_lock.json) · [Preregistration](docs/phase4b_preregistered_specification.md)

## Run the dashboard locally

From the repository root, use a current security-patched CPython **3.14**. The app serves bundled, hash-verified derived data and requires no credentials.

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run dashboard/app.py --server.address 127.0.0.1
```

Use the URL printed by Streamlit and choose English or French in the sidebar. The data expanders provide table-specific CSVs. [Dashboard files](dashboard/) · [Community Cloud preparation](docs/streamlit_deployment_steps.md)

## Reproduce the research outputs

```sh
.venv/bin/python -m pip install -r requirements-phase5.lock
export PYTHONPATH=src
.venv/bin/python -m trade_audit.phase5_paper --reuse-figures --output reproduced-papers
.venv/bin/python -m pytest -q
.venv/bin/python audit/release_checks.py
```

The paper command renders manuscripts in both languages from locked derived inputs and shipped figures. Omit `--reuse-figures` to regenerate the Phase 5 figures in the working copy. The [independent audit](docs/final_scientific_audit.md) gives the raw-vintage replication commands. Its separately retained archive must match the source hashes. A fresh official download can contain revisions. [Repository inventory](docs/public_repository_inventory.md) · [Release manifest](release_manifest.json)

## Licensing and contact

Original code is under the [MIT License](LICENSE). Original research papers, figures and written material are under [CC BY 4.0](LICENSE-CONTENT.md). [Third-party data terms and attribution](THIRD_PARTY_NOTICES.md) apply to original data and their source contributions.

**Contact** · [Public contact details to be supplied by the author]

**Release status** · Private candidate awaiting Manau Salaun’s explicit authorization. [Final approval checklist](docs/final_approval_checklist.md)
