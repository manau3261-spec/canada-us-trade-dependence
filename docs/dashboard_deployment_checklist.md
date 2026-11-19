# Dashboard deployment checklist

> Historical review. The Phase 7A checklist records current approval and licensing status. [Current checklist](final_approval_checklist.md)

**State:** Local verification complete. Public hosting is gated by owner approval and target-host verification.

| Area | Result |
| --- | --- |
| Navigation | AppTest executes national, provincial, products, concentration, decomposition, Design C, steel pilot and sources in English and French. Every section renders source context and offers a CSV path. |
| Filtering | Tested annual/monthly switching and monthly period selection, provincial rankings and group selection, product and section controls, toggling the published HHI benchmark, and model forest outputs. Also exercised live desktop language and frequency controls and mobile sidebar navigation. |
| Live HTTP | A clean dashboard-only Python 3.14.8 virtual environment installed the exact lock and passed `pip check`. The index, favicon and health endpoints returned HTTP 200. The initial Streamlit 1.58.0 and Starlette 1.10.0 combination returned HTTP 500 on the favicon. Streamlit 1.67.0 resolved that incompatibility in the same environment. A real WebSocket script session registered the annual CSV. Its HTTP response was an attachment with exact data and column order for all 16 annual rows. The filtered July–September 2026 CSV test separately validates its three rows and the corresponding chart trace at the Streamlit ASGI media route. |
| Dashboard sources | Statistics Canada snapshot November 18, 2026. Annual trade ends in 2025, monthly trade in September 2026, GDP-based ratios in 2023, and national and regional value-added benchmarks in 2024 and 2022, respectively. Pilot tables show their March 2025 legal vintage and separate import snapshots. |
| Responsive behaviour | Live Chromium at 1440 × 960 and 390 × 844. Checked plot and page widths, a collapsed and reopened mobile sidebar, and French monthly, product and econometric views. At 390 CSS pixels the inspected chart containers are 358 pixels and the page has no horizontal overflow. Long data grids can scroll inside their container. |
| Accessibility | Checked the skip link, main and sidebar landmarks, heading hierarchy, input roles and labels, text/chart distinction, accessible tabular alternatives, legend and source captions. Fixed stale section anchors and synchronized the document language with the bilingual radio via static first-party code. Plotly framework toolbar strings may remain English. Screen-reader, cross-browser and PDF/UA certification remain outside the verified scope. |
| Credentials | Health and exports run from bundled derived inputs without authentication, environment credentials, raw archives, live data calls or a dashboard model runtime. Telemetry is disabled. External links go to the cited sources when selected. |

[Streamlit release notes](https://github.com/streamlit/streamlit/releases/tag/1.62.0) · [HTTP test script](../audit/dashboard_http_smoke.py) · [HTTP transcript](../audit/evidence/dashboard_http.txt) · [Automated app tests](../tests/test_phase5.py)

## Run and verify from the candidate root

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
.venv/bin/python -m streamlit run dashboard/app.py --server.address 127.0.0.1
```

With Streamlit running, execute `.venv/bin/python audit/dashboard_http_smoke.py http://127.0.0.1:8501`. Use the full publication lock for AppTest and PDF reproduction.

The deployable app needs `dashboard/`, `src/trade_audit/`, `.streamlit/config.toml`, `requirements.txt`, `requirements-dashboard.lock` and the data paths in `src/trade_audit/phase5_data.py` and `data/phase5/source_lock.json` plus linked source and licence notices. Use the verified candidate root to retain all package-relative paths.

## After authorization

- [ ] Select a host that can build the pinned Python 3.14 dependency graph. Override the private loopback setting only for the intended deployment. Keep the existing source lock and checked data bundle.
- [ ] Run install and `pip check` on the host runtime. Confirm Plotly assets load under the host's content security, WebSockets stay connected over TLS, health returns successfully and CSV headers survive the reverse proxy.
- [ ] Exercise both languages, an annual and monthly CSV, a regional filter and mobile navigation on the public target. Record the target revision and compare mounted data hashes with the approved manifest.
- [ ] Preserve a matching local archive and a rollback mechanism. A host change requires a new operational check.

[Publication checklist](final_publication_checklist.md) · [Remaining limitations](remaining_limitations.md)
