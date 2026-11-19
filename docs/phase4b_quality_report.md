# Phase 4B quality report and reproduction guide

The preregistered Design C passed the rank, support and numerical inference checks. The primary estimate is an imprecise association. All 26 registered secondary specifications ran. Design A passed basic legal-code and data availability checks and remains at the mapping stage. [English results](econometric_results_en.md) · [Résultats en français](econometric_results_fr.md) · [Steel pilot](design_A_tariff_pilot.md)

## Provenance and the sample

The specification was hashed and locked before estimation at **2026-11-19 02:25:24 UTC** (November 18 Toronto time). File SHA-256 is `7e3ca592b66be5aaa960da5cd55e0fa6f6ea798f2abb35bc47cbcd1efb46c374`. The pipeline checks it each time. It validates the acquisition manifest, checks the original annual Statistics Canada ZIP and archived Phase 3 and Phase 4A extracts against their hashes, and rebuilds the annual cells and eligibility flags from the official data. The rebuilt results agree with the pinned upstream extracts. The Design A module separately verifies all 11 official inputs against its source manifest. No source file was overwritten. [Preregistration lock](../data/phase4b/preregistration_lock.json) · [Primary source checks](../data/phase4b/preflight.json) · [Steel source manifest](../data/phase4b/design_A_source_manifest.json)

| Control | Verified result |
| --- | ---: |
| Scoped raw annual trade observations, 2010–2025 | 455,840 |
| Province–product–source-year cells | 1,760 |
| World and partner groups reconciled within rounding | 1,760 of 1,760 |
| Missing numeric or flagged suppressed raw records in scope | 0 |
| Reported raw zero values | 308,496, including 4 world and 6 U.S. |
| Valid source-year non-U.S. export values equal to zero | 10 |
| HHI-blocking nonzero unallocated groups | 2, both C13 in 2020 (British Columbia and Ontario) |
| Complete anticipated outcome-start grid | 1,540 |
| Phase 4A eligibility and complete controls | 1,513 |
| Additional exclusions from the preregistered CAD 1m floor among eligible cells | 59 |
| Primary fixed-effect singletons excluded after the floor | 0 |
| Primary observations / province–product groups | 1,454 / 108 |
| Complete balanced primary sensitivity | 1,372 cells / 98 groups |

Across the entire expected grid, **24** rows lack admissible lagged HHI, **8** lack lagged controls, **83** fail the lagged floor and **9** each have zero start or end values. Flags overlap, so the unique exclusions are **86**. All expected outcome endpoints have numeric world and U.S. controls. The no-extra-floor sensitivity drops one Prince Edward Island C12 singleton and retains 1,512 rows. Blank or unavailable destination flows are never replaced with zeros. [Status counts](../data/phase4b/source_status_counts.csv) · [Source-year audit](../data/phase4b/source_year_audit.csv) · [Exclusion ledger](../data/phase4b/sample_exclusion_ledger.csv)

## Estimation and verification

- **Rank and inference.** QR and SVD show fixed-effect rank 368 and full rank 371. The explicit-dummy statsmodels fit agrees with absorbed OLS and the reported slope variances from all four covariance estimators to numerical precision. The restricted Webb implementation was compared with literal full-model bootstrap refits on the actual panel at two nulls. [Inference audit](statistical_inference_audit.md)
- **Complete results.** The main table contains all three slope coefficients, clustered uncertainty, fit statistics and absorbed levels. Detailed CSVs preserve the estimates, sample membership, constructed input and influence diagnostics, including the alternative covariance estimators. The selection fit was ineligible because there were no verified zero ends among otherwise eligible portfolios. [Primary table](../data/phase4b/primary_regression.md) · [Robustness output](../data/phase4b/robustness_summary.csv) · [Model input](../data/phase4b/design_C_model_input.csv)
- **Replays.** All **12** primary and robustness output files and the **12** figure files plus their manifest matched byte for byte on a fresh run in the same environment. The **seven** steel pilot CSVs and their manifest also matched byte for byte. The charts are in English and French, each as 300 dpi PNG and editable SVG. [Estimation replay](../logs/phase4b/replay.txt) · [Steel replay](../logs/phase4b/pilot_replay.txt) · [Figure manifest](../figures/phase4b/manifest.json)
- **Automated tests.** The full project suite completed with **42 passed in 18.02 seconds**. It includes seven Phase 4B tests for hash and vintage checks, date and variable construction, eligibility and balance, rank, independently checked inference, regression and robustness tables, figure reproducibility and the steel scope. Tests use official project data. [Exact pytest output](../logs/phase4b/pytest.txt) · [Phase 4B tests](../tests/test_phase4b.py)

## Reproduce

Run from the project directory or the extracted main archive. The verified environment used Python 3.14.8, numpy 2.4.4, pandas 3.0.2, SciPy 1.17.1, statsmodels 0.14.6 and Matplotlib 3.10.9. The lock pins these and ancillary dependencies. The Phase 4B archive contains the annual trade snapshot needed for C and the pilot’s exact derived tables and legal snapshots. Extract the separate raw-data companion into the same project folder to replay the complete pilot offline. The pilot can retrieve missing inputs from their original listed URLs with `--fetch-missing`, accepting downloads only at the recorded hashes. Revision or access failures remain visible.

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-phase4b.lock
export PYTHONPATH=src
export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
.venv/bin/python -m trade_audit.phase4b --preflight
.venv/bin/python -m trade_audit.phase4b
.venv/bin/python -m trade_audit.phase4b_pilot
.venv/bin/python -m pytest -q tests/test_phase4b.py
```

The existing workspace also holds the Phase 2 and 3 data used by the previous tests. It can rerun the full suite with `.venv/bin/python -m pytest -q`. The execution logs record the commands’ outcomes. [Preflight log](../logs/phase4b/preflight.txt) · [Estimation log](../logs/phase4b/estimation.txt) · [Tariff pilot log](../logs/phase4b/tariff_pilot.txt)

**Data attribution.** Source: Statistics Canada, annual domestic merchandise trade table 12-10-0173-01 (2010–2025, pinned November 18, 2026 Toronto time) and Canadian International Merchandise Trade detailed domestic exports (2022–2025). Reproduced and distributed on an “as is” basis with the permission of Statistics Canada. For the steel pilot, U.S. schedule data are from the USITC and the import mirror is from the U.S. Census Bureau. [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/terms-conditions/open-licence) · [U.S. imports files](https://www.census.gov/foreign-trade/data/IMDB.html)

## Scientific validation requested

Confirm the reporting of Design C as a positive but inconclusive nominal-export association, with the sign changes and the two-way and small-cluster inference reported alongside the main estimate. Confirm the decision to hold Design A at descriptive mapping and to keep Design B deferred. Completion of Phase 4B stops the research workflow pending that review.
