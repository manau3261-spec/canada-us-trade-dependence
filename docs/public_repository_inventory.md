# Public repository inventory

The intended repository name is `canada-us-trade-dependence`. The candidate consists of the following material. The [release manifest](../release_manifest.json) records every payload file, its exact byte size and its SHA-256 digest. The manifest excludes itself. The external ZIP checksum covers the manifest and the archive envelope.

| Location | Contents |
| --- | --- |
| `README.md`, `README.fr.md` | English default and French companion with the author, findings, methods, contact placeholders and links to both papers. |
| `LICENSE`, `LICENSE-CONTENT.md`, `THIRD_PARTY_NOTICES.md` | MIT for original software, CC BY 4.0 for original research expression and separate third-party terms. |
| `paper/` | English and French Markdown manuscripts, stylesheet, final PDFs, self-contained HTML papers and render hashes. |
| `figures/` | Bilingual PNG and vector charts, figure manifests and the data exhibits used by the publications. |
| `dashboard/`, `.streamlit/config.toml` | The app entrypoint, stylesheet and environment-neutral Streamlit theme and settings. |
| `requirements.txt`, `requirements-*.lock`, `requirements.lock`, `pyproject.toml` | Pinned deployment dependencies, separate research and historical dependency specifications, and project and test configuration. |
| `src/trade_audit/`, `tests/` | Acquisition, analysis and presentation code. Default tests work with the distribution. Historical tests that need the raw vintage remain available for the archived workspace. |
| `data/phase3/`, `data/phase4a/`, `data/phase4b/`, `data/phase5/` | Derived exposure, concentration, tariff-pilot and inference tables, presentation facts and the input lock. |
| `data/provenance/` | Source URLs, retrieval timestamps, file paths relative to the historical root, and hashes for independent replication. Receipt paths can refer to archives retained separately. |
| `docs/` | Source and methods documentation, main review notes, the bilingual abstract and Phase 7A publication instructions. |
| `audit/`, `logs/phase5/` | Independent verification programs and selected outputs, including replicated estimates, test transcripts and historical review evidence. |
| `.gitignore`, `release_manifest.json` | Checkout exclusions and exact payload inventory. |

The local research archive remains separate. It retains raw Statistics Canada and U.S. inputs, old release bundles, the internal outreach draft, the superseded historical package manifest and an empty historical render log. Research evidence and source data in the local archive were preserved. The prepared distribution excludes repositories and their history, nested archives, raw government downloads and bundled legacy installers, credentials, virtual environments and scratch files.

[Audit and measurements](phase7a_release_audit.md) · [Approval gates](final_approval_checklist.md)
