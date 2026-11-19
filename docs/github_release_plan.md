# GitHub release plan

> Historical review. The Phase 7A checklist records current approval and licensing status. [Current checklist](final_approval_checklist.md)

**State:** Private release candidate. The workspace has no Git metadata or configured remote. The checklist approves local packaging only.

## Candidate contents

| Include | Purpose |
| --- | --- |
| `README.md`, `.gitignore`, `pyproject.toml` | Quick start, measurements and scope, local hygiene and default tests. |
| `requirements.txt`, `requirements-dashboard.lock`, `requirements-phase5.lock` | Host entry dependency and pinned local dashboard and full publication environments. Earlier lock files reproduce historical phases with their inputs. |
| `dashboard/app.py`, `dashboard/style.css`, `.streamlit/config.toml` | Dashboard application and local settings. |
| `src/trade_audit/`, `tests/`, `audit/` | Production code, historical and presentation tests, independent audit programs and verification outputs. |
| `data/phase3/`, `data/phase4a/`, `data/phase4b/`, `data/phase5/`, `data/provenance/` | Frozen derived data, provenance and presentation input hashes. |
| `paper/`, `figures/`, `docs/`, `logs/phase5/` | Bilingual sources and renders, source figures, methodology and historical QA. |
| `release_manifest.json` | SHA-256 for every included file except the manifest itself. The Phase 5 manifest in `data/phase5/` is the historical baseline. |

The candidate excludes virtual environments, caches, raw ZIP files and legacy Census executables, local secrets files, staging outputs and editor or OS files. It strips the machine-specific prefix from the historical packaged build log. The pattern scan covers staged text files, PDF text and metadata, HTML and MIME-visible paths, including common credential formats. Source code uses project-relative path resolution or accepts an explicitly provided historical root. This is a static scan of the release files.

## Rights and owner decisions

Statistics Canada allows reproduction and adaptation under its Open Licence subject to the relevant source and non-endorsement notices. Keep those notices in all included public formats and preserve dataset references with exported tables. Cite the U.S. Census Bureau as the original source for derived mirror tables and USITC for the HTS edition. Keep the statistical and original-work rights distinct. [Statistics Canada Open Licence](https://www.statcan.gc.ca/en/terms-conditions/open-licence) · [Licence ouverte](https://www.statcan.gc.ca/fr/avis/licence-ouverte) · [Census citation guidance](https://www.census.gov/about/policies/citation.html) · [Attribution and permissions](data_attribution.md)

The owner should confirm author identity and affiliation and select original-work licensing before creating a public repository, applying any licence or naming a release. A prospective licence decision may revise the archive. Regenerate checksums for the approved revision.

## Sequence after authorization

1. Freeze the approved candidate, verify the manifest and prepare a Git repository from that root. The default `pytest -q` scope is the self-contained presentation suite. The archived Design C tests can be addressed explicitly from the original historical workspace.
2. Check the tracked file list, sensitive patterns, remote destination and any pre-existing history. Run the tests and record the approved digest.
3. Publish only the authorized surfaces. Associate the bilingual publications, methods, limitations and source notices with the same revision. A public repository may be released independently of the public dashboard.
4. Keep the verified private archive and its digest to support rollback or correction. For an unexpected discrepancy, withdraw the affected artifacts and publish a documented correction after review.

[Publication checklist](final_publication_checklist.md) · [Dashboard checklist](dashboard_deployment_checklist.md)
