# Dashboard reproduction and deployment preparation

> Historical review. The Phase 7A checklist records current approval and licensing status. [Current checklist](final_approval_checklist.md)

The review app uses Streamlit, Plotly and the pinned, read-only derived CSV/JSON inputs. It does not need API keys, network requests at runtime, a database, or write access to the research files. The first load verifies all input hashes. The two publications are static files and can be served independently. [Methodology](methodology.md)

## Local access

Install `requirements-dashboard.lock` with Python 3.14, and run from the project root.

```sh
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-dashboard.lock
.venv/bin/python -m streamlit run dashboard/app.py --server.address 127.0.0.1
```

The shipped configuration uses the loopback address and turns off telemetry. Download buttons export original and derived research data only, at the granularity of the table and current filters.

## After publication approval

- Confirm authorship and public licensing. Retain the data attributions and Phase 5 source lock. Decide whether to distribute prior raw archival companions separately. [Attribution](data_attribution.md)
- For GitHub with Streamlit Community Cloud, keep the app entry point at `dashboard/app.py`. Include `src/`, `data/phase5/source_lock.json` and all file paths it names, along with the dashboard stylesheet. Copy the verified dashboard lock to `requirements.txt` in the release checkout so the host installs it. Select a Python version supported by both the host and the pinned wheels. The inspected development environment is Python 3.14.8. Availability on a chosen hosted plan must be checked independently. [Streamlit dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) · [Deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- For a self-hosted environment, install the same lock into a clean compatible runtime. Run `python -m streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501` inside the platform boundary and use the platform’s normal TLS and access controls. Keep the development default on loopback. Limit deployment artifacts to the files in the QA release and a reviewed hosting configuration.
- Verify both languages and a filtered CSV after a test deployment. Confirm that the host exposes the intended access scope and that the selected historical vintage is still displayed. Treat changing the data vintage as a new release with fresh reconciliation, hashes, figures and validation.

The local environment was exercised during Phase 5. No remote provider has been selected or tested. Public hosting remains subject to the scientific and release review.
