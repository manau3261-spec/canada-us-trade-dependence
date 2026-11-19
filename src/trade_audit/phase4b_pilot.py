"""March 2025 core steel legal and coverage pilot. Descriptive validation only."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import pandas as pd
import requests

from .acquire import sha256, write_json
from .phase4a_audit import load_cimt
from .phase4b_data import checked

# Annex 1, 90 FR 11249, note 16(j), expanded against March 11 HTS Revision 4.
CORE_BLOCKS = {
    "flat_rolled": {"7208", "7209", "7210", "7211", "7212", "7225", "7226"},
    "bars_wire_sections": {"7213", "7214", "7215", "7216", "7217", "7227", "7228", "7229",
                            "73011000", "730210", "73024000", "73029000"},
    "tubes_and_pipes": {"7304", "7305", "7306"},
    "primary_semifinished": {"7206", "7207", "7224"},
    "stainless": {"7218", "7219", "7220", "7221", "7222", "7223"},
}
CORE_EXCEPTIONS = {"72166100", "72166900", "72169100"}
CANDIDATE_CONTROLS = {"7201", "7202", "7203", "7204", "7205"}
DESTINATIONS = ("US", "MX", "GB", "DE", "JP", "KR")
PRE = tuple(pd.period_range("2022-01", "2025-01", freq="M").strftime("%Y%m"))
TRANSITION = ("202502", "202503")
POST = ("202504", "202505")


def classify(code):
    if code[:4] in CANDIDATE_CONTROLS:
        return "candidate_upstream_control", "upstream"
    if code.startswith(tuple(CORE_EXCEPTIONS)):
        return "excluded_from_core_check_derivative", ""
    for family, prefixes in CORE_BLOCKS.items():
        if code.startswith(tuple(prefixes)):
            return "covered_core_232", family
    return "outside_pilot", ""


def current_us_lines(path):
    data = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    data["hts10"] = data["HTS Number"].str.replace(".", "", regex=False)
    numbered = data.loc[data.hts10.str.fullmatch(r"\d{10}")].copy()
    pairs = numbered.hts10.map(classify)
    numbered[["scope", "steel_legal_block"]] = pd.DataFrame(pairs.tolist(), index=numbered.index)
    numbered["hs6"] = numbered.hts10.str[:6]
    scoped_hs6 = numbered.loc[numbered.scope.ne("outside_pilot"), "hs6"]
    # Retain every U.S. HTS10 child of a scoped HS6. An uncovered sibling
    # makes that HS6 mixed and therefore ineligible for a binary mapping.
    numbered = numbered.loc[numbered.hs6.isin(scoped_hs6)].copy()
    numbered.loc[numbered.scope.eq("outside_pilot"), "scope"] = "other_child_review"
    if numbered.hts10.duplicated().any():
        raise ValueError("Multiple schedule rows for one scoped HTS10")
    numbered["hts4_family"] = numbered.hts10.str[:4]
    numbered["ordinary_hts8"] = numbered.hts10.str[:8]
    numbered["chapter99_ordinary_entry"] = numbered.scope.map({"covered_core_232": "9903.81.87"})
    numbered["additional_statutory_rate_at_2025_03_12"] = numbered.scope.map({"covered_core_232": .25})
    numbered["source"] = "USITC HTS 2025 Revision 4 and 90 FR 11249, note 16(j)"
    return numbered[["hts10", "ordinary_hts8", "hs6", "hts4_family", "scope", "steel_legal_block",
                     "chapter99_ordinary_entry", "additional_statutory_rate_at_2025_03_12", "Description",
                     "Unit of Quantity", "General Rate of Duty", "Special Rate of Duty", "source"]].sort_values("hts10")


def canadian_dict(path, year):
    with ZipFile(path) as z:
        name = next(name for name in z.namelist() if name.endswith("HS6XDesc.TXT"))
        with z.open(name) as file:
            rows = []
            for line in file:
                fields = line.decode("latin-1")
                start, end, unit = fields[11:29].strip().split(maxsplit=2)
                if int(start) <= year*100+12 and int(end) >= year*100+1:
                    rows.append((fields[:6], unit, fields[29:111].strip()))
    return pd.DataFrame(rows, columns=["hs6", "unit", "description"]).drop_duplicates()


def canadian_coverage(input_paths, hts):
    years, dictionaries, n_rows = [], [], {}
    candidates = set(hts.hs6)
    for year in range(2022, 2026):
        raw = load_cimt(input_paths[f"cimt{year}.zip"], year)
        n_rows[str(year)] = len(raw)
        dictionaries.append(canadian_dict(input_paths[f"cimt{year}.zip"], year).assign(year=year))
        detail = raw.loc[raw.hs6.isin(candidates) & raw.country.isin(DESTINATIONS)
                         & raw.month.isin((*PRE, *TRANSITION, *POST))]
        years.append(detail.groupby(["hs6", "country", "month"], sort=False).value_cad.sum().reset_index())
    trade = pd.concat(years)
    dicts = pd.concat(dictionaries)
    dicts = dicts.loc[dicts.hs6.isin(candidates)]
    dict_check = dicts.groupby("hs6").agg(
        ca_dictionary_years=("year", "nunique"), ca_description_versions=("description", "nunique"),
        ca_uom_versions=("unit", "nunique"), canada_hs6_description=("description", "last"),
    )
    scope = hts.groupby("hs6").agg(
        us_hts10_lines=("hts10", "size"), us_hts8_lines=("ordinary_hts8", "nunique"),
        scopes=("scope", "nunique"), scope=("scope", "first"),
        hts4_family=("hts4_family", "first"), steel_legal_block=("steel_legal_block", "first"),
    )
    scope.loc[scope.scopes.ne(1), "scope"] = "mixed_treatment_ineligible"
    link = scope.join(dict_check, how="left")
    link["stable_ca_hs6_dictionary"] = link.ca_dictionary_years.eq(4) & link.ca_description_versions.eq(1)
    canadian_active = trade.groupby("hs6").value_cad.sum().gt(0)
    link["active_in_selected_canadian_destinations"] = canadian_active.reindex(link.index, fill_value=False)
    coverage = pd.MultiIndex.from_product([link.index, DESTINATIONS], names=["hs6","country"]).to_frame(index=False)
    trade = trade.loc[trade.value_cad.gt(0)].assign(
        period=lambda d: d.month.map({**dict.fromkeys(PRE,"pre"), **dict.fromkeys(TRANSITION,"transition"),
                                      **dict.fromkeys(POST,"post")}),
    )
    for stage in ("pre", "transition", "post"):
        stage_rows = trade.loc[trade.period.eq(stage)].groupby(["hs6","country"]).agg(
            value_cad=("value_cad","sum"), positive_months=("month","nunique"),
        ).add_prefix(stage+"_")
        coverage = coverage.merge(stage_rows.reset_index(), on=["hs6","country"], how="left", validate="one_to_one")
        # Zero counts refer to the number of positive months. Missing values
        # in the reported flow column are preserved rather than imputed.
        months = f"{stage}_positive_months"
        coverage[months] = coverage[months].fillna(0).astype(int)
    coverage = coverage.merge(link.reset_index()[["hs6", "scope", "hts4_family", "stable_ca_hs6_dictionary"]],
                              on="hs6", validate="many_to_one")
    return trade.sort_values(["hs6", "country", "month"]), coverage, link.reset_index(), n_rows


def census_mirror(path, month):
    sums = defaultdict(lambda: [0, 0, 0, 0])
    with ZipFile(path) as archive:
        country = [line for line in archive.read("COUNTRY.txt").splitlines() if line.startswith(b"1220")]
        if len(country) != 1 or b"CANADA" not in country[0]:
            raise ValueError("Census Canada country code did not verify")
        specification = archive.read("Documentation/IMP_DETL.lay").decode("latin1")
        expected_fields = {("74-88", "con_val_mo"), ("89-103", "dut_val_mo"), ("104-118", "cal_dut_mo")}
        if not all(re.search(fr"{positions}\s+{field}\b", specification) for positions, field in expected_fields):
            raise ValueError("Unexpected US Census layout for import and calculated duty")
        code_month = month.encode()
        with archive.open("IMP_DETL.txt") as data:
            for line in data:
                if line[10:14] != b"1220" or not line.startswith((b"72", b"73")):
                    continue
                if line[22:28] != code_month:
                    raise ValueError("Unexpected US Census reference month")
                hts10 = line[:10].decode("ascii")
                scope, _ = classify(hts10)
                if scope == "outside_pilot":
                    continue
                code = line[20:22].decode("ascii").strip()
                amounts = [int(line[73:88]), int(line[88:103]), int(line[103:118])]
                if not any(amounts):
                    continue
                d = sums[hts10, code]
                for i, amount in enumerate(amounts):
                    d[i] += amount
                d[3] += 1
    return pd.DataFrame([(month, hts, code, *values) for (hts, code), values in sorted(sums.items())],
                        columns=["month", "hts10", "rate_provision_code", "consumption_customs_value_usd",
                                 "dutiable_value_usd", "calculated_duty_usd", "raw_rows_nonzero"])


def ensure_input(root, record, fetch_missing):
    path = root / record["path"]
    if fetch_missing and not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with requests.get(record["url"], stream=True, timeout=(15, 90)) as response:
                response.raise_for_status()
                with NamedTemporaryFile(dir=path.parent, suffix=".part", delete=False) as file:
                    temporary = Path(file.name)
                    for chunk in response.iter_content(2**20):
                        file.write(chunk)
            checked(temporary, record["sha256"])
            temporary.replace(path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    checked(path, record["sha256"])
    return path


def execute(root, output, fetch_missing=False):
    manifest = json.loads((root / "data/phase4b/design_A_source_manifest.json").read_text())
    inputs = {}
    for rec in manifest:
        if rec["status"] == "downloaded":
            inputs[rec["name"]] = ensure_input(root, rec, fetch_missing)
    legal = inputs["steel_implementation_2025-03598.html"].read_bytes().replace(b"\x00", b"").decode()
    block = legal[legal.index("(j) The rates of duty set forth"):legal.index("(k) Headings")]
    normalized_note = re.sub(r"(\d)\.(?=\d)", r"\1", block)
    if not all(prefix in normalized_note for prefix in set.union(CORE_EXCEPTIONS, *CORE_BLOCKS.values())):
        raise ValueError("Pilot prefixes missing in legal note 16(j)")
    hts = current_us_lines(inputs["hts_2025_rev4.csv"])
    trade, coverage, links, counts = canadian_coverage(inputs, hts)
    mirror = pd.concat([census_mirror(inputs[f"imdb{month[2:]}.zip"], month)
                        for month in ("202501", *POST)], ignore_index=True)
    mirror = mirror.merge(hts[["hts10", "scope"]], on="hts10", how="left", validate="many_to_one")
    mirror["matched_march_edition"] = mirror.scope.notna()
    mirror["scope"] = mirror.scope.fillna(mirror.hts10.map(lambda c: classify(c)[0]))
    mirror["hs6"] = mirror.hts10.str[:6]
    measures = ["consumption_customs_value_usd", "dutiable_value_usd", "calculated_duty_usd", "raw_rows_nonzero"]
    us = mirror.groupby(["month","scope"], sort=True)[measures].sum().reset_index()
    us["calculated_duties_over_consumption_value"] = us.calculated_duty_usd / us.consumption_customs_value_usd
    core = hts.loc[hts.scope.eq("covered_core_232")]
    linked = links.loc[links.scope.eq("covered_core_232") & links.stable_ca_hs6_dictionary
                        & links.active_in_selected_canadian_destinations]
    complete = coverage.loc[coverage.stable_ca_hs6_dictionary & coverage.pre_positive_months.eq(len(PRE))
                            & coverage.post_positive_months.eq(len(POST))]
    coverage_counts = complete.groupby(["scope", "country"]).agg(
        complete_hs6=("hs6", "nunique"), complete_hs4=("hts4_family", "nunique"),
    ).reset_index()
    summary = {"cimt_rows_by_year": counts, "pre_months": len(PRE), "transition_months": len(TRANSITION),
        "post_months": len(POST), "potential_core_hts10_lines": len(core),
        "potential_core_hts8_lines": core.ordinary_hts8.nunique(),
        "potential_core_hs6": core.hs6.nunique(), "potential_core_hs4": core.hts4_family.nunique(),
        "core_legal_blocks": core.steel_legal_block.nunique(),
        "core_stable_active_hs6": linked.hs6.nunique(), "core_stable_active_hs4": linked.hts4_family.nunique(),
        "core_hs4_with_complete_US_coverage": int(complete.loc[complete.scope.eq("covered_core_232")
                                                                   & complete.country.eq("US")].hts4_family.nunique()),
        "core_distinct_legal_effective_date_cohorts": 1,
        "independent_shock_families_verified": False,
        "unmatched_march_hts10_with_positive_us_consumption_value": int(
            mirror.loc[~mirror.matched_march_edition & mirror.consumption_customs_value_usd.gt(0)].hts10.nunique()),
        "mirror_rows_aggregated_by_rate_code": len(mirror), "mapping_is_statutory_not_entry_eligibility": True,
        "estimation_decision": "no-go pending policy-clean comparisons and validated preference/exemption coverage"}
    output.mkdir(parents=True, exist_ok=True)
    files = {"us_legal_hts10": hts, "hs6_linkage": links, "canadian_reported_trade": trade,
             "canadian_coverage": coverage, "complete_link_counts": coverage_counts,
             "us_import_mirror": mirror, "us_import_scope_totals": us}
    summary["files"] = {}
    for name, frame in files.items():
        path = output / f"{name}.csv"
        frame.to_csv(path, index=False)
        summary["files"][path.name] = {"rows": len(frame), "sha256": sha256(path)}
    write_json(output/"manifest.json", summary)
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fetch-missing", action="store_true", help="Fetch absent inputs only if their hashes match.")
    args = parser.parse_args()
    root = args.root.resolve()
    execute(root, args.output or root / "data/phase4b/tariff_pilot", fetch_missing=args.fetch_missing)


if __name__ == "__main__":
    main()
