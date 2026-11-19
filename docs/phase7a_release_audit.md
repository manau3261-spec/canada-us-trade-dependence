# Phase 7A release audit

**Recommendation:** GO for private review. NO-GO for external publication until Manau Salaun authorizes the exact revision and destinations. Local checks support the candidate. A real Community Cloud build and access policy remain to be verified if hosting is authorized.

## Independent scientific verification

The Phase 6 source archive passed its outer SHA-256, ZIP CRC and all 213 file hashes before staging. Two independent programs were rerun against the locked historical source files. The main program reconstructs trade and concentration from source tables, builds Design C’s eligible panel and fits a separate fixed-effects implementation. The historical program checks vintage differences and steel scope against the applicable legal annex, schedule and import records. [Independent replication](../audit/independent_audit.py) · [Historical replication](../audit/historical_checks.py)

| Finding | Result |
| --- | --- |
| Canada’s annual U.S. share, 2024–2025 | 75.795940% to 71.688374%, down 4.107566 percentage points. |
| Non-U.S. export growth, 2024–2025 | CAD 28.796 billion in current dollars. Unwrought non-monetary gold and crude petroleum contribute 74.3%. |
| Non-U.S. destination HHI | 0.072346 to 0.093824, or 0.068295 to 0.070721 when unwrought gold is excluded in both years. |
| Separate monthly series | The matched January–September U.S. share falls from 73.284793% in 2025 to 67.981629% in 2026. Nominal values rise for both sets of destinations. |
| Design C | +0.012827 log points per +0.10 lagged HHI. Restricted Webb 95% CI [−0.06049, +0.10525], p = 0.7174, 1,454 observations, 108 groups and ten provincial clusters. |
| Robustness and inference | Independently reproduced all 324 reported coefficient–covariance rows. All 26 secondary province-clustered confidence intervals span zero. Value weighting reverses the point estimate’s sign. |
| Historical and tariff checks | 228 of 5,096 active comparisons in 2020 exceed the rounding allowance. The archived pair has zero such differences. The March steel list reproduces 744 covered HTS10 lines, with only two full post months under the initial rate. |

Both papers, both README editions, the dashboard and the underlying release figures use the locked values. The final numerical comparison checked 32 locked facts in each PDF, the English and French README headlines, the uncertainty disclosure in the dashboard and figure hashes with unchanged plotted dates, currencies and source captions. The revised author and attribution blocks leave the scientific text, archived values and figure assets unchanged. The estimate remains statistically inconclusive. The study describes nominal values and has no new causal estimates. [Numerical reproduction](../audit/evidence/phase7a_independent_results.json) · [Historical results](../audit/evidence/phase7a_historical_results.json)

## Packaging and deployment checks

- The English and French working papers were rebuilt in PDF and self-contained HTML. The tests reproduce all four file hashes, inspect PDF metadata and compare shared values. All 41 pages and 22 figure instances passed visual review. The public payload preserves the Phase 6 scientific evidence and includes the approved author and licence information.
- Clean macOS ARM64 environments installed the pinned dashboard and research requirements and passed `pip check`. The local framework ran with CPython 3.14.8. Use a current patched CPython 3.14 for a new deployment. Linux x86-64 wheel resolution passed for CPython 3.14. That resolution checked wheel and dependency availability. It did not run Linux binaries or a hosted app. [Environment evidence](../audit/evidence/phase7a_environments.json)
- The local server returned HTTP 200 for its index, favicon, health and exact 16-row annual CSV. Tests exercise all eight views in each language, the filtered three-month CSV, controls, confidence bounds and localized recovery when locked data are unavailable. Live desktop and 390 px mobile observations verified French language markup, month filtering, labels, attribution and responsive chart width. The app uses 23 locked files totaling 7,225,145 bytes. One cold loopback run reached health in 0.452 seconds and returned the first verified CSV in 1.648 seconds. Peak server RSS was 249.6 MiB on the test machine. [Live HTTP evidence](../audit/evidence/phase7a_dashboard_http.txt) · [Cold-start measurement](../audit/evidence/phase7a_dashboard_metrics.json)
- The payload scan covers credentials and token formats, machine paths, emails, excluded artifacts, links and release hashes. The project roots have no Git history to inspect. A temporary local Git index matched the complete candidate inventory and held no refs or remotes. The candidate contains no raw third-party archives, duplicate release archives, local contact details or secrets files. Local research evidence, data and earlier bundles were preserved. [Payload verification](../audit/release_checks.py) · [Inventory](public_repository_inventory.md)

## Automated results

| Suite | Result |
| --- | --- |
| Historical workspace | **53 passed, 5 warnings** in 29.22 seconds. [Transcript](../audit/evidence/phase7a_historical_tests.txt) |
| Release candidate | **15 passed, 5 warnings** in 7.88 seconds. [Transcript](../audit/evidence/phase7a_candidate_tests.txt) |

The five warnings in each suite concern PyMuPDF SWIG type metadata deprecations. Neither suite had failures or skips.

## Remaining risks

Scientific limitations remain those documented in Phase 6. Design C is imprecise with ten province clusters and selected active portfolios. Some official HHI comparisons remain unresolved. Current-dollar flows combine price, product mix and quantity changes, and the steel pilot supplies insufficient comparison support for tariff-effect estimation. Full vintage reproduction requires the separately retained archived raw files. [Scientific limitations](remaining_limitations.md)

The actual Linux-hosted build, host timing and resource quotas, TLS and access policy, and full assistive-technology or PDF/UA conformance remain unverified. The repository and dashboard can be approved separately. No external account or hosting console was used. [GitHub procedure](github_publication_steps.md) · [Streamlit procedure](streamlit_deployment_steps.md) · [Approval checklist](final_approval_checklist.md)
