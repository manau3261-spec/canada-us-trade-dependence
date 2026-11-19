# Final publication checklist

> Historical review. The Phase 7A checklist records current approval and licensing status. [Current checklist](final_approval_checklist.md)

**Recommendation: NO-GO for public release.** The audited candidate is available for private sign-off. Approval, author attribution and the licence for original work are open. Public dashboard deployment has one additional host-specific gate. [Issue register](remaining_limitations.md)

| Gate | Status | Evidence or required action |
| --- | --- | --- |
| Source integrity | Pass | The Phase 5 baseline passed CRC and all 189 manifest entries. Locked source hashes passed for the independent replication. Both clean Python 3.14.8 environments passed dependency checks. The Phase 6 manifest covers the release candidate. |
| Headline descriptive figures | Pass | Compared the two papers, published tables, data, README and dashboard output at their stated precision. Checked annual and monthly windows separately and retained missing cells. |
| Primary and secondary statistical inference | Pass | Independently reproduced all 324 coefficient–covariance rows, and the main restricted Webb p-value and interval. Inconclusive and negative results remain visible. |
| Study scope and legal language | Pass with limitations | The merchandise, value-added and employment concepts use separate denominators. The steel discussion gives legal eligibility and feasibility only. The tariff chronology has the scope in [the issue register](remaining_limitations.md). |
| Bilingual equivalence | Pass | Reconciled section conclusions, figure and table values, directional statements, and period and unit labels. French and English use their standard decimal and thousands formatting. |
| Visual PDF review | Pass | Examined every page of both rendered papers, including contents, 11 figures and their captions per language, tables and references. The final automated re-render matches both PDF and both HTML hashes using fixed Typst creation metadata. |
| Dashboard and downloads | Pass locally | Both languages and eight views, filters, visual layout, source links, CSV exports, health and no-credential startup. [Dashboard checklist](dashboard_deployment_checklist.md) |
| Automated tests | Pass | Historical full workspace **53 passed, 5 warnings in 24.51s**. Release candidate suite **13 passed, 5 warnings in 14.93s**. The five warnings in each run are PyMuPDF SWIG import deprecations. [Full suite transcript](../audit/evidence/full_tests.txt) · [Candidate transcript](../audit/evidence/candidate_tests.txt) |
| Source redistribution | Pass for the included material | Statistics Canada direct-copy and adapted-product notices retained as applicable. The papers and dashboard now display the adapted notice. The U.S. derived tables cite the original product. The raw Census archives including bundled legacy executables are outside the candidate. [Attribution](data_attribution.md) |
| Release hygiene | Pass for the candidate | Checked the staged release for sensitive path and common secret patterns and excluded caches, credentials and raw archives. The scan covers the candidate tree. A future Git history requires a separate check. [Release plan](github_release_plan.md) |
| Authorship, affiliation and original licence | **Blocking** | Obtain the owner's approved attribution and licence for code, paper, figures and original derived work. |
| Public publication | **Blocking** | Obtain explicit approval for the exact approved candidate revision from the project owner. |
| Public hosting | **Blocking for the dashboard only** | After approval, select a public host and verify the locked environment, TLS, WebSockets and CSV downloads on the actual host. |

No public release action has been taken. The candidate uses the locked November 2026 data vintage and the same scientific conclusions in both languages.
