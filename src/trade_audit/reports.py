import json
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime

from .sources import ALL_GEOS, SOURCES
from .validate import ANNUAL_TRADE, MONTHLY_TRADE

DASH = "—"
PROFILE_LABELS = {
    "world_domestic_exports": "World domestic exports / Exportations nationales, monde",
    "us_domestic_exports": "U.S. domestic exports / Exportations nationales, É.-U.",
    "product_hhi": "Product HHI / IHH par produit",
    "destination_hhi": "Published destination HHI† / IHH publié par destination†",
    "destination_hhi_ex_us": "Published destination HHI ex U.S.† / IHH publié par destination hors É.-U.†",
    "us_value_added_exports": "U.S. value added in exports / Valeur ajoutée des exportations vers les É.-U.",
    "us_jobs_embodied": "U.S. jobs embodied / Emplois liés aux exportations vers les É.-U.",
    "nominal_gdp": "Current-dollar GDP / PIB en dollars courants",
    "real_gdp": "Chained 2017 GDP / PIB en dollars enchaînés de 2017",
    "lfs_employment": "LFS employment / Emploi, EPA",
}
FRENCH_GEOS = {
    "Newfoundland and Labrador": "Terre-Neuve-et-Labrador", "Prince Edward Island": "Île-du-Prince-Édouard",
    "Nova Scotia": "Nouvelle-Écosse", "New Brunswick": "Nouveau-Brunswick", "Quebec": "Québec",
    "British Columbia": "Colombie-Britannique", "Northwest Territories": "Territoires du Nord-Ouest",
}
TRADE_LABELS = {
    ANNUAL_TRADE: "Annual / Annuel",
    MONTHLY_TRADE: "Monthly / Mensuel",
}


def num(value) -> str:
    return f"{value:,}" if isinstance(value, int) else DASH


def pct(part: int, total: int) -> str:
    return f"{100 * part / total:.2f}%" if total else DASH


def period_span(periods) -> str:
    if not periods:
        return DASH
    first, last = min(periods), max(periods)
    return first if first == last else f"{first}–{last}"


def paired(counts: dict) -> str:
    return f"{num(counts['reported'])} / {num(counts['rows'])}" if counts else DASH


def cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def table(headers, rows) -> str:
    return "\n".join(
        ["| " + " | ".join(map(cell, headers)) + " |",
         "| " + " | ".join("---" for _ in headers) + " |"]
        + ["| " + " | ".join(map(cell, row)) + " |" for row in rows]
    )


def statuses(result: dict) -> list[str]:
    return [f"{s.table} {result['sources'][s.pid]['status']}"
            for s in SOURCES if result["sources"][s.pid]["status"] != "validated"]


def empirical(result: dict, manifest: dict, test_log_exists: bool) -> str:
    records = []
    structural = []
    valid = [s for s in result["sources"].values() if s["status"] == "validated"]
    for src in SOURCES:
        s = result["sources"][src.pid]
        if s["status"] != "validated":
            records.append((src.table, s["status"], DASH, DASH, DASH, DASH))
            continue
        records.append((f"[{src.table}]({src.table_url})", f"{s['raw_first']}–{s['raw_last']}",
                        paired(s["all"]), pct(s["all"]["reported"], s["all"]["rows"]),
                        paired(s["history"]), paired(s["recent"])))
        issue = s["issues"]
        structural.append((src.table, num(s["series"]), num(issue["duplicate_period_vector_excess"]),
                           num(issue["duplicate_period_coordinate_excess"]),
                           num(issue["coordinate_metadata_mismatches"]),
                           "Yes / Oui" if issue["archive_bounds_match_rows"] else "No / Non",
                           {True: "Yes / Oui", False: "No / Non", None: DASH}[issue["wds_bounds_match_archive"]],
                           {True: "Yes / Oui", False: "No / Non", None: DASH}[
                               issue.get("wds_release_date_matches_http_modified_local")]))
    raw_rows = sum(s["all"]["rows"] for s in valid)
    reported = sum(s["all"]["reported"] for s in valid)
    downloaded = sum(s["status"] == "downloaded" for s in manifest["sources"])
    issue_text = "\n".join(f"- {entry}" for entry in result["blocking_issues"]) or "None in the core ingestion and structural checks. / Aucun au chapitre de l’acquisition et des contrôles structurels de base."
    partial = ", ".join(statuses(result)) or "None / Aucune"
    tests = ("The recorded [test results](../data/provenance/test-results.txt) accompany this snapshot. / "
             "Les [résultats des tests](../data/provenance/test-results.txt) accompagnent ce millésime.\n\n"
             if test_log_exists else "")
    local_date = datetime.fromisoformat(manifest["started_at_utc"]).astimezone(ZoneInfo("America/Toronto")).date()
    text = f"""# Empirical data audit / Audit empirique des données

Acquisition vintage / Millésime d’acquisition **{manifest['run_id']}**  
Local acquisition date / Date locale d’acquisition **{local_date}** (Toronto)

**English.** Downloaded **{downloaded} of {len(SOURCES)}** requested Statistics Canada archives. The validator read **{num(raw_rows)}** file rows across **{len(valid)}** archives and identified **{num(reported)}** usable numeric observations before analytical filters. The denominator includes publisher materialized blank rows. Reported zeros count as observations. Raw histories differ by source.

**Français.** **{downloaded} des {len(SOURCES)}** archives de Statistique Canada demandées ont été téléchargées. Le programme a lu **{num(raw_rows)}** lignes dans **{len(valid)}** archives et a relevé **{num(reported)}** observations numériques utilisables avant les filtres analytiques. Le dénominateur inclut les lignes vides publiées. Les zéros déclarés comptent comme observations. La profondeur historique varie selon la source.

## Observations and periods / Observations et périodes

Each pair is usable numeric observations / file rows. The monthly recent window overlaps the historical window in 2025. / Chaque paire indique les observations numériques utilisables et le nombre de lignes. Les fenêtres mensuelles historique et récente se chevauchent en 2025.

{table(["Table / Tableau", "Full span / Période intégrale", "Full numeric / rows", "Full / Intégral %", "2010–2025 numeric / rows", "2025–2026 monthly numeric / rows"], records)}

## Structural checks / Contrôles structurels

{table(["Table / Tableau", "Series / Séries", "Duplicate period × vector", "Duplicate period × coordinate", "Metadata label mismatches / Écarts", "ZIP bounds match / Concordance", "WDS bounds match / Concordance", "Release matches HTTP date / Date conforme"], structural)}

Source failures or unfinished scans / Sources en échec ou lectures incomplètes · **{partial}**

{issue_text}

See [coverage](coverage_matrix.md), [quality findings](data_quality_issues.md) and [source provenance](source_inventory.md). / Voir la [couverture](coverage_matrix.md), les [constats de qualité](data_quality_issues.md) et la [provenance](source_inventory.md).

{tests}## Preliminary descriptive file / Fichier descriptif préliminaire

"""
    if "descriptive" in result:
        data = result["descriptive"]
        data_rows = [(TRADE_LABELS[ANNUAL_TRADE if freq == "annual" else MONTHLY_TRADE],
                      num(n["rows"]), num(n["us_domestic_export_share"]), num(n["destination_hhi"]),
                      num(n["destination_hhi_ex_us"])) for freq, n in data["counts"].items()]
        text += table(["Frequency / Fréquence", "Rows / Lignes", "U.S. share / Part des É.-U.",
                       "Destination HHI / IHH", "HHI ex U.S. / IHH hors É.-U."], data_rows) + "\n\n"
        text += f"Artifact / Fichier · [domestic_export_exposure.csv](../{data['path']})  \nSHA-256 · `{data['sha256']}`\n\n"
        text += """The file measures exports in current CAD thousands and shares as fractions. Annual records span the approved historical years. Monthly records start in January 2025. The share uses the source’s own world denominator for each frequency. Blank derived fields indicate ineligibility under the data checks. Monthly market HHI is withheld because the partner partition contains an aggregate residual.

Le fichier exprime les exportations en milliers de dollars canadiens courants et les parts sous forme de fractions. Les lignes annuelles couvrent la période historique approuvée. Les lignes mensuelles commencent en janvier 2025. La part utilise le total mondial publié à la fréquence correspondante. Les champs dérivés vides ne satisfont pas aux contrôles. L’IHH mensuel par destination demeure indisponible en raison du groupe résiduel de partenaires.

Adapted from Statistics Canada tables 12-10-0173-01 and 12-10-0175-01, downloaded in the vintage above. Statistics Canada does not endorse this project. / Adapté des tableaux 12-10-0173-01 et 12-10-0175-01 de Statistique Canada, téléchargés pour le millésime ci-dessus. Statistique Canada n’appuie pas ce projet.
"""
    else:
        text += "No trade extract met the prerequisites. / Aucun extrait commercial ne satisfait aux conditions de production.\n"
    return text


def coverage(result: dict) -> str:
    sources = result["sources"]
    heading = """# Coverage matrix / Matrice de couverture

A period is covered when the selected series has a usable numeric value. The geography matrix uses all-products or all-industry slices. An em dash means no usable observation for the selected geography and series. Coverage of one slice does not establish coverage of detailed products or industries.

Une période est couverte lorsque la série ciblée contient une valeur numérique utilisable. La matrice utilise les séries pour l’ensemble des produits ou des industries. Un tiret indique l’absence d’une observation utilisable pour la région et la série. La couverture de cette série ne garantit pas celle des produits ou industries détaillés.

## Geography and series / Géographie et séries

Each entry gives the first and last usable periods and the number of usable periods. / Chaque cellule donne les première et dernière périodes utilisables et le nombre de périodes utilisables.
"""
    geography_sections = []
    for s in SOURCES:
        d = sources[s.pid]
        if d["status"] != "validated":
            continue
        relevant = list(d["profiles"])
        rows = []
        for geo in ALL_GEOS:
            marks = []
            for profile in relevant:
                periods = {p["period"] for p in d["profiles"][profile] if p["geo"] == geo and p["reported"]}
                marks.append(f"{period_span(periods)} ({len(periods)})" if periods else DASH)
            name = geo if geo not in FRENCH_GEOS else f"{geo} / {FRENCH_GEOS[geo]}"
            rows.append((name, *marks))
        geography_sections.append(f"### {s.table}\n\n" + table(
            ["Geography / Géographie"] + [PROFILE_LABELS[name] for name in relevant], rows
        ))
    years = []
    by_source = {}
    for s in SOURCES:
        d = sources[s.pid]
        rollup = Counter()
        if d["status"] == "validated":
            for g in d["geos"]:
                y = g["period"][:4]
                rollup[(y, "rows")] += g["rows"]
                rollup[(y, "reported")] += g["reported"]
        by_source[s.pid] = rollup
    for year in map(str, range(2010, 2027)):
        years.append((year, *(paired({"rows": c[(year, "rows")], "reported": c[(year, "reported")]})
                              if c[(year, "rows")] else DASH for c in by_source.values())))
    return heading + "\n" + "\n\n".join(geography_sections) + """

† The source footnote restricts subnational concentration availability to products. The matrix records numeric CSV presence for the destination series as a metadata discrepancy. Treat these series as unconfirmed for subnational use. / La note du tableau limite la concentration infranationale aux produits. La matrice relève les valeurs numériques par destination dans le CSV comme écart de métadonnées. Leur utilisation infranationale reste à confirmer.

## File rows and numeric values by year / Lignes et valeurs numériques par année

Pairs show usable values / file rows across all cube dimensions and geographies. / Les paires indiquent les valeurs utilisables et le nombre de lignes pour toutes les dimensions et régions du cube.

""" + table(["Year / Année"] + [s.table for s in SOURCES], years) + "\n"


def quality(result: dict) -> str:
    entries = []
    units = []
    for s in SOURCES:
        d = result["sources"][s.pid]
        if d["status"] != "validated":
            continue
        a = d["all"]
        entries.append((s.table, *(num(a[k]) for k in ("blank", "suppressed", "too_unreliable", "unavailable_status",
                                                       "zero", "preliminary", "revised", "terminated"))))
        for u in d["units"]:
            units.append((s.table, u["unit"], u["scalar"], f"{u['unit_id']} / {u['scalar_id']}", num(u["rows"])))
    results = []
    for pid, d in result["trade_checks"].items():
        for name, title in (("destination", "Partners to world / Destinations vers total mondial"),
                            ("product_sections", "Sections to total / Sections vers total"),
                            ("product_sections_world_us", "Sections, world and U.S. / Sections, monde et É.-U.")):
            results.append((f"{TRADE_LABELS[pid]} · {title}", d[name]))
    timeline_labels = {
        "all_common_partners_2010_2025": "2010–2025, common partners / Partenaires communs",
        "world_us_2010_2025": "2010–2025, world and U.S. / Monde et É.-U.",
        "world_us_2025": "2025, world and U.S. / Monde et É.-U.",
        "world_us_all_products_2025": "2025, world and U.S., all products / Monde et É.-U., tous produits",
    }
    comparison = result.get("annual_monthly", {})
    for key, summary in comparison.get("controls", {}).items():
        results.append((timeline_labels[key], summary))
    control_rows = [(label, *(num(row[k]) for k in ("groups", "comparable", "within_rounding",
                                                   "outside_rounding", "unavailable")),
                      f"{row['max_abs_gap_cad_thousands']:,.2f}" if row["max_abs_gap_cad_thousands"] is not None else DASH)
                    for label, row in results]
    hhi_rows = []
    for measure, geos in result.get("concentration_benchmark", {}).items():
        for geography, d in geos.items():
            hhi_rows.append((measure, geography, *(num(d[k]) for k in
                             ("official_numeric", "comparable", "within_rounding", "outside_rounding"))))
    blocks = "\n".join(f"- {entry}" for entry in result["blocking_issues"]) or "None for the validated source structure. / Aucun pour la structure des sources validées."
    cls = result.get("classification_comparison", {})
    years_with_mismatches = [f"{year} ({num(data['outside_rounding'])})"
                             for year, data in comparison.get("by_year", {}).items() if data["outside_rounding"]]
    naics = result.get("naics_code_screen", {})
    monthly_sections = result["trade_checks"].get(MONTHLY_TRADE, {}).get("by_section", {})
    metadata_only = [key for key in cls.get("monthly_only", []) if key not in monthly_sections]
    cross = f"{len(comparison.get('common_partners', []))} common partner labels and {len(cls.get('common_codes_compared', []))} common section/total keys"
    cross_fr = f"{len(comparison.get('common_partners', []))} libellés de partenaires et {len(cls.get('common_codes_compared', []))} codes de section ou de total communs"
    flow_rows = [(TRADE_LABELS[pid], a["flow"], a["geo"], num(a["rows"]), num(a["reported"]))
                 for pid in (ANNUAL_TRADE, MONTHLY_TRADE)
                 for a in result["sources"][pid].get("flows", [])]
    return f"""# Data quality issues / Problèmes de qualité des données

## Core blockers / Blocages des contrôles de base

{blocks}

## Missing values and source flags / Valeurs manquantes et indicateurs

Counts refer to full files. Blank values and status flags overlap. The published status `x` indicates suppression and `F` indicates an estimate too unreliable to publish. Revision and termination flags do not by themselves make numeric observations missing. / Les comptes portent sur les fichiers intégraux. Les valeurs vides et les indicateurs peuvent se chevaucher. Le code `x` indique une suppression et `F` une estimation trop peu fiable pour être publiée. Une révision ou un arrêt de série ne transforme pas à lui seul une valeur numérique en donnée manquante. [StatCan CSV guide / Guide CSV](https://www.statcan.gc.ca/en/developers/csv/user-guide) · [Table symbols / Symboles](https://www.statcan.gc.ca/en/concepts/definitions/guide-symbol)

{table(["Table / Tableau", "Blank / Vide", "Suppressed / Supprimées", "Unreliable / Non fiables", "Unavailable / Indisponibles", "Zero / Zéro", "Preliminary / Provisoires", "Revised / Révisées", "Terminated / Arrêt"], entries)}

## Units and currency / Unités et devise

The table lists unit and scalar combinations among reported rows in the combined project window. Trade values are CAD thousands. The LFS unit label and scalar both refer to thousands and represent a single conversion to persons. Employment in input-output accounts counts jobs. GDP volume measures and nominal measures use the same scalar but different price bases. / Le tableau indique les combinaisons d’unités et de facteurs pour les lignes publiées durant la période du projet. Les échanges sont en milliers de dollars canadiens. Dans l’EPA, le libellé et le facteur indiquent des milliers de personnes, ce qui implique une seule conversion. Les comptes d’entrées-sorties comptent des emplois. Les séries de PIB en volume et en valeur ont le même facteur et des bases de prix différentes.

{table(["Table / Tableau", "Published unit / Unité", "Scalar / Facteur", "IDs", "Numeric rows / Lignes numériques"], units)}

## Trade flow and reconciliation / Flux et rapprochement

The annual export row is domestic merchandise trade per its metadata. The monthly extract uses Domestic export. The flow counts below include archival monthly geographies within the period, where present. Re-exports never enter the descriptive calculation. / Le poste Export annuel désigne les exportations nationales selon ses métadonnées. L’extrait mensuel utilise le poste Domestic export. Les comptes ci-dessous incluent les régions mensuelles archivées si elles figurent durant la période. Les réexportations sont exclues des calculs descriptifs. [Annual trade metadata / Métadonnées annuelles](https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1210017301) · [Monthly trade metadata / Métadonnées mensuelles](https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1210017501)

{table(["Frequency / Fréquence", "Publisher flow / Flux", "Geography / Géographie", "Rows / Lignes", "Numeric / Numériques"], flow_rows)}

The annual-to-monthly check uses **{cross}** and requires all 12 component months. The currency gap is in thousands of CAD. The tolerance sums half a reporting increment for the total and each usable component, with a small floating-point allowance. The counts isolate differences larger than published rounding. Missing comparison inputs stay unavailable.

Le rapprochement annuel-mensuel utilise **{cross_fr}** et exige douze mois. Les écarts sont en milliers de dollars canadiens. La tolérance est la somme des demi-unités de précision du total et des composantes utilisables, avec une faible marge numérique. Les contrôles isolent les écarts qui dépassent l’arrondi publié. Les comparaisons sans données demeurent indisponibles.

{table(["Control / Contrôle", "Groups / Groupes", "Comparable", "Within / Dans la tolérance", "Outside / Hors tolérance", "Unavailable / Indisponibles", "Max abs. gap / Écart max. (000 CAD)"], control_rows)}

Monthly-only classification keys / Codes exclusifs au mensuel · **{", ".join(cls.get("monthly_only", [])) or DASH}**  
Monthly-only keys without domestic export rows / Codes exclusifs au mensuel sans lignes d’exportations nationales · **{", ".join(metadata_only) or DASH}**  
Annual-only classification keys / Codes exclusifs à l’annuel · **{", ".join(cls.get("annual_only", [])) or DASH}**  
Conflicting common code descriptions / Libellés divergents pour un code commun · **{", ".join(cls.get("common_code_label_mismatches", [])) or DASH}**

Years with annual-to-monthly gaps beyond rounding, with counts / Années avec des écarts annuel-mensuel au-delà de la tolérance, avec dénombrement · **{", ".join(years_with_mismatches) or DASH}**. Investigate the source of these differences before splicing series. / Déterminer l’origine de ces écarts avant de raccorder les séries.

Exact NAICS code overlap between GDP and LFS metadata / Codes SCIAN identiques entre les métadonnées du PIB et de l’EPA · **{len(naics['common_codes']) if naics else DASH}**. Matching codes are a screening result. Document industry boundaries, publisher exceptions, residence and production concepts before joining outcomes. / La concordance de codes constitue un premier contrôle. Documenter les périmètres, les exceptions et les concepts de résidence et de production avant de joindre les résultats.

## Destination concentration / Concentration par destination

The reconstruction requires a positive official world denominator, a valid U.S. component, numeric partner records, a partition within rounding, nonnegative components and zero unallocated value. A separate non-U.S. denominator must exceed the rounding tolerance. The portfolio with and excluding the U.S. uses the same annual partner universe. Grouped and unassigned value can prevent an HHI even where the U.S. share is available.

La reconstruction exige un total mondial officiel positif, une composante américaine valide, des données numériques pour les partenaires, un rapprochement dans la tolérance, des composantes non négatives et une valeur nulle pour les destinations non attribuées. Le dénominateur hors États-Unis doit dépasser la tolérance d’arrondi. Les deux portefeuilles utilisent le même univers annuel. Une valeur agrégée ou non attribuée peut empêcher le calcul de l’IHH même lorsque la part des États-Unis est disponible.

{table(["Measure / Mesure", "Universe / Univers", "CSV numeric / Numériques", "Paired / Appariés", "Within rounding / Dans la tolérance", "Outside / Hors tolérance"], hhi_rows)}

**Metadata discrepancy.** The official concentration CSV contains subnational destination entries despite the footnote restricting subnational measures to product concentration. Keep these entries as diagnostics. Obtain clarification before treating them as official regional benchmarks. The independent bilateral reconstruction is subject to its own reconciliation checks. / **Écart de métadonnées.** Le fichier CSV officiel contient des entrées infranationales par destination, bien que la note limite les mesures infranationales à la concentration par produit. Ces entrées servent au diagnostic. Une clarification est nécessaire avant de les utiliser comme références régionales officielles. La reconstruction bilatérale suit ses propres contrôles de rapprochement. [Concentration table / Tableau de concentration](https://www150.statcan.gc.ca/t1/tbl1/en/cv.action?pid=1210012901)

## Limits and design recommendations / Limites et recommandations pour la conception

- **Use a single source per frequency.** Keep annual and monthly series separate where rollups differ beyond rounding. Review the effect of differing coverage, annual revisions and totals before any pooled panel. Use matched months for 2026 year-over-year work. / **Utiliser une source par fréquence.** Conserver des séries annuelles et mensuelles distinctes lorsque les écarts dépassent l’arrondi. Examiner la couverture, les révisions et les totaux avant de regrouper les données. Comparer les mêmes mois d’une année à l’autre en 2026.
- **Use the supported geographic panels.** Territorial trade and real GDP can be retained. The monthly industry LFS excludes the territories and the GDP table excludes a national row. Keep the current-dollar GDP and value-added end years distinct from real GDP. Refer to the coverage matrix before specifying outcomes. / **Respecter les panels géographiques disponibles.** Les échanges et le PIB réel territoriaux peuvent être conservés. L’EPA mensuelle par industrie exclut les territoires et le tableau de PIB exclut la ligne nationale. Distinguer les années terminales du PIB nominal, de la valeur ajoutée et du PIB réel.
- **Handle suppression explicitly.** Use broad, prespecified LFS groups, quantify retention at the outcome and event-window level, and assess the sensitivity of balanced-panel restrictions. / **Traiter explicitement les suppressions.** Employer des groupes larges prédéfinis dans l’EPA, mesurer la couverture par résultat et fenêtre d’événement, puis évaluer les restrictions d’équilibrage du panel.
- **Verify the concordances before assigning exposure.** Preserve the NAPCS product and NAICS industry grains. Detailed work needs versioned HS mappings, pre-shock trade weights, dated tariff measures, and verified exemptions. Phase 2 uses the six specified archives. CIMT, the U.S. tariff and mirror sources, and Valet remain supplementary candidates. / **Valider les concordances avant d’attribuer l’exposition.** Conserver les niveaux de détail du SCPAN et du SCIAN. Les analyses détaillées exigent des concordances du SH, des pondérations antérieures au choc, des mesures tarifaires datées et des exemptions vérifiées. La phase 2 utilise les six archives demandées. La CICM, les sources tarifaires et miroirs américaines et Valet demeurent des sources complémentaires.
"""


def inventory(result: dict, manifest: dict) -> str:
    items = {s["pid"]: s for s in manifest["sources"]}
    evidence = manifest.get("wds_metadata", {})
    acquisition = result["manifest_path"]
    out = f"""# Source inventory / Inventaire des sources

Publisher / Éditeur · Statistics Canada / Statistique Canada.  
Acquisition manifest / Manifeste d’acquisition · [JSON](../{acquisition})  
Manifest SHA-256 / SHA-256 du manifeste · `{result['manifest_sha256']}`  
Validation / Validation · [JSON](../data/provenance/validation-{result['acquisition_id']}.json)  
WDS response hash verified / Empreinte de la réponse SDW vérifiée · **{result['wds_evidence_verified']}**  
WDS retrieval / Récupération SDW · **{evidence.get('retrieved_at_utc', DASH)}**  
WDS response SHA-256 / SHA-256 de la réponse SDW · `{evidence.get('sha256', DASH)}`

WDS release timestamps are publisher values. Archive download timestamps are UTC. SHA-256 identifiers pin exact ZIP bytes. The ZIP member inventory also records uncompressed sizes and CRC-32 checks. / Les dates de diffusion SDW proviennent de l’éditeur. Les heures de téléchargement sont exprimées en UTC. Les identifiants SHA-256 correspondent aux octets de chaque ZIP. Le manifeste contient aussi les tailles décompressées et les CRC-32.

[WDS guide / Guide SDW](https://www.statcan.gc.ca/en/developers/wds/user-guide) · [CSV file layout / Structure CSV](https://www.statcan.gc.ca/en/developers/csv/user-guide) · [Statistics Canada Open Licence / Licence ouverte de Statistique Canada](https://www.statcan.gc.ca/en/terms-conditions/open-licence)

"""
    for s in SOURCES:
        item = items.get(s.pid, {})
        checked = result["sources"][s.pid]
        out += f"## {s.table} · {s.title_en} / {s.title_fr}\n\n[Official table / Tableau officiel]({s.table_url}) · [Official ZIP / ZIP officiel]({s.url})\n\n"
        if item.get("status") != "downloaded":
            out += f"Status / État · {item.get('status', 'unavailable')} · {cell(item.get('error', DASH))}\n\n"
            continue
        m = item.get("publisher_metadata", {})
        out += table(["Field / Champ", "Recorded value / Valeur enregistrée"], [
            ("Download, UTC / Téléchargement, UTC", item["downloaded_at_utc"]),
            ("Reference bounds / Bornes", f"{m.get('cubeStartDate', DASH)} – {m.get('cubeEndDate', DASH)}"),
            ("Publisher release / Diffusion", m.get("releaseTime", DASH)),
            ("HTTP Last-Modified", item["headers"].get("Last-Modified") or DASH),
            ("ZIP bytes / Octets", num(item["bytes"])),
            ("ZIP SHA-256", f"`{item['sha256']}`"),
            ("Raw path / Chemin brut", f"`{item['path']}`"),
            ("Validation status / État de validation", checked["status"]),
            ("Classification", s.classification),
            ("Embedded correction dates / Dates de correction", ", ".join(c["date"] for c in checked.get("corrections", [])) or DASH),
        ]) + "\n\n"
    return out


def render_reports(root: Path, result: dict) -> None:
    manifest = json.loads((root / result["manifest_path"]).read_text(encoding="utf-8"))
    reports = {
        "empirical_data_audit.md": empirical(result, manifest, (root / "data/provenance/test-results.txt").is_file()),
        "coverage_matrix.md": coverage(result),
        "data_quality_issues.md": quality(result),
        "source_inventory.md": inventory(result, manifest),
    }
    docs = root / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    for name, content in reports.items():
        (docs / name).write_text(content.rstrip() + "\n", encoding="utf-8")
