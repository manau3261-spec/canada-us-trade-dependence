"""Load the locked research outputs and build bilingual presentation inputs."""

import argparse
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

from .acquire import sha256, write_json

ROOT = Path(__file__).resolve().parents[2]
D = Path("data")
P5 = D / "phase5"
VINTAGE = "2026-11-18"
URLS = {
    "annual": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017301",
    "monthly": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210017501",
    "hhi": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210012901",
    "gdp": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3610071101",
    "value_added": "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1210010001",
    "hs": "https://open.canada.ca/data/en/dataset/2909a648-5753-4924-878a-b069392d9cde",
    "pilot": "https://www.govinfo.gov/content/pkg/FR-2025-03-05/html/2025-03598.htm",
    "mirror": "https://www.census.gov/foreign-trade/data/IMDB.html",
}
INPUTS = {
    **{n: D / "phase3" / f"{f}.csv" for n, f in {
        "annual": "annual_exposure", "monthly": "monthly_exposure", "matched": "matched_monthly_ytd",
        "hhi": "destination_hhi_benchmark", "destinations": "national_non_us_destinations",
        "share_decomposition": "national_exposure_decomposition", "intensity": "provincial_export_intensity",
        "value_added": "value_added_and_jobs_benchmarks",
    }.items()},
    **{n: D / "phase4a" / f"{f}.csv" for n, f in {
        "hs": "hs6_country_value_changes", "hs8": "hs8_quantity_checks",
        "gold_hhi": "non_us_gold_exclusion_sensitivity", "uk_mix": "uk_share_composition",
        "hhi_audit": "hhi_method_sensitivity",
    }.items()},
    **{n: D / "phase4b" / f"{f}.csv" for n, f in {
        "regression": "primary_regression", "robustness": "robustness_summary", "influence": "province_influence",
        "coverage": "sample_exclusion_ledger", "pilot_codes": "tariff_pilot/us_legal_hts10",
        "pilot_coverage": "tariff_pilot/canadian_coverage", "pilot_mirror": "tariff_pilot/us_import_scope_totals",
    }.items()},
    "model_metadata": D/"phase4b/primary_diagnostics.json",
    "preflight": D/"phase4b/preflight.json",
    "pilot_metadata": D/"phase4b/tariff_pilot/manifest.json",
}
MERCH = ["world_cad_thousands", "us_cad_thousands", "non_us_cad_thousands", "us_share"]
PERIODS = {"Annual": ("2010", "2025"), "Monthly": ("2025-01", "2026-09")}
FOREST_IDS = [
    "A_no_C14", "B_positive", "B_100k", "B_10m", "C_balanced", "D_lag_weighted", "E_signed", "F_downside",
    "G_top1_non_us", "G_top3_non_us", "G_destination_hhi", "H_end_2024", "J_even", "J_odd", "J_2year",
]
HS_FOCUS = {
    "710812": ("Unwrought non-monetary gold", "Or non monétaire sous forme brute"),
    "270900": ("Crude petroleum", "Pétrole brut"),
    "760110": ("Unwrought non-alloyed aluminium", "Aluminium non allié sous forme brute"),
    "260300": ("Copper ores and concentrates", "Minerais et concentrés de cuivre"),
    "310420": ("Potassium chloride", "Chlorure de potassium"),
    "270112": ("Bituminous coal", "Houille bitumineuse"),
}
DEST_LABELS = {
    "United Kingdom": ("United Kingdom", "Royaume-Uni"), "China": ("China", "Chine"),
    "United States": ("United States", "États-Unis"), "Hong Kong": ("Hong Kong", "Hong Kong"),
    "Japan": ("Japan", "Japon"), "Mexico": ("Mexico", "Mexique"), "Germany": ("Germany", "Allemagne"),
    "Netherlands": ("Netherlands", "Pays-Bas"), "Switzerland": ("Switzerland", "Suisse"),
    "South Korea": ("South Korea", "Corée du Sud"), "Belgium": ("Belgium", "Belgique"),
    "India": ("India", "Inde"), "France": ("France", "France"),
}
COUNTRY_HS = {"GB": "United Kingdom", "CN": "China", "JP": "Japan", "MX": "Mexico", "DE": "Germany",
              "CH": "Switzerland", "HK": "Hong Kong", "NL": "Netherlands", "KR": "South Korea",
              "IN": "India", "BE": "Belgium", "FR": "France", "US": "United States"}


def _json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def establish_lock(root):
    """Verify upstream records and create the baseline once against the Phase 4B release."""
    path = root/P5/"source_lock.json"
    if path.exists():
        raise ValueError("Phase 5 source lock already exists")
    phase3 = _json(root/D/"phase3/phase3_summary.json")["files"]
    phase4a = _json(root/D/"phase4a/manifest.json")["files"]
    pilot = _json(root/INPUTS["pilot_metadata"])["files"]
    provenance = {}
    with ZipFile(root/"canada-trade-phase-4b.zip") as release:
        from hashlib import sha256 as hash_bytes

        for name, rel in INPUTS.items():
            if rel.parts[1] == "phase3":
                certified = phase3[rel.name]["sha256"]
            elif rel.parts[1] == "phase4a":
                certified = phase4a[rel.name]["sha256"]
            elif rel.parent.name == "tariff_pilot" and rel.suffix == ".csv":
                certified = pilot[rel.name]["sha256"]
            else:
                certified = hash_bytes(release.read(f"canada-trade-phase-4b/{rel.as_posix()}")).hexdigest()
            if sha256(root/rel) != certified:
                raise ValueError(f"Upstream input mismatch for {rel}")
            provenance[name] = {"path": rel.as_posix(), "sha256": certified}
    write_json(path, {"vintage_toronto": VINTAGE, "inputs": provenance})


def load(root=ROOT):
    lock = _json(root/P5/"source_lock.json")
    data = {}
    for name, rel in INPUTS.items():
        record = lock["inputs"][name]
        if record["path"] != rel.as_posix() or sha256(root/rel) != record["sha256"]:
            raise ValueError(f"Locked Phase 5 source mismatch for {rel}")
        if rel.suffix == ".json":
            data[name] = _json(root/rel)
        else:
            data[name] = pd.read_csv(root/rel, dtype={"period": str, "hs6": str, "hs8": str,
                                                     "hts10": str, "month": str})
    for freq, label in (("annual", "Annual"), ("monthly", "Monthly")):
        table = data[freq]
        pattern = r"\d{4}" if freq == "annual" else r"\d{4}-(0[1-9]|1[0-2])"
        if (not table.period.str.fullmatch(pattern).all() or table.duplicated(["period", "geo", "product"]).any()
                or (table.period.min(), table.period.max()) != PERIODS[label]):
            raise ValueError(f"Invalid {freq} trade period or key")
    return data


def exposure(data, frequency, start, end, geos, products):
    lower, upper = PERIODS[frequency]
    if not lower <= start <= end <= upper or len(start) != len(lower) or len(end) != len(upper):
        raise ValueError(f"Dates {start} to {end} do not fit {frequency.lower()} data")
    d = data[frequency.lower()]
    return d.loc[d.period.between(start, end) & d.geo.isin(geos) & d["product"].isin(products),
                 ["period", "geo", "product", *MERCH]].copy()


def hhi_trend(data, geo, start, end):
    annual = data["annual"]
    d = annual.loc[annual.geo.eq(geo) & annual["product"].eq("TOTAL") & annual.period.between(start, end)]
    out = d[["period", "geo", "destination_hhi", "destination_hhi_ex_us"]].copy()
    published = data["hhi"].loc[data["hhi"].geo.eq(geo)].pivot(
        index=["period", "geo"], columns="measure", values="statcan_hhi",
    ).add_prefix("published_").reset_index()
    return out.merge(published, on=["period", "geo"], how="left", validate="one_to_one")


def destination_slice(data, start, end, partners):
    d = data["destinations"]
    return d.loc[d.period.between(start, end) & d.partner.isin(partners) & d.is_identified_destination,
                 ["period", "partner", "exports_cad_thousands", "share_of_non_us"]].copy()


def partner_changes(data):
    d = data["destinations"]
    d = d.loc[d.period.isin(["2024", "2025"]) & d.is_identified_destination]
    values = d.pivot(index="partner", columns="period", values="exports_cad_thousands")
    shares = d.pivot(index="partner", columns="period", values="share_of_non_us")
    out = values.add_prefix("value_cad_thousands_").join(shares.add_prefix("share_non_us_")).reset_index()
    out["change_cad_thousands"] = out.value_cad_thousands_2025 - out.value_cad_thousands_2024
    out["change_share_pp"] = 100*(out.share_non_us_2025 - out.share_non_us_2024)
    return out.sort_values("change_cad_thousands", ascending=False, na_position="last")


def product_changes(data, country=None):
    d = data["hs"]
    d = d.loc[d.country.ne("US") if country is None else d.country.eq(country)]
    out = d.groupby("hs6", sort=True).agg(change_cad=("change_cad", "sum"),
        reported_flows_2024=("reported_2024", "sum"), reported_flows_2025=("reported_2025", "sum")).reset_index()
    return out.sort_values("change_cad", ascending=False)


def bridge(data):
    amounts = product_changes(data).set_index("hs6").change_cad
    named = amounts.loc[["710812", "270900"]]
    return pd.DataFrame({"component": ["710812", "270900", "remainder", "total"],
                         "change_cad": [*named, amounts.sum()-named.sum(), amounts.sum()]})


def primary(data):
    row = data["regression"].loc[lambda d: d.term.eq("hhi_ex_us") & d.covariance.eq("province")].iloc[0]
    meta = data["model_metadata"]
    boot = meta["webb_wild_restricted"]
    lower, upper = boot["ci_95_beta_components"][0]
    return {"beta": row.coefficient, "scaled": row.coefficient*.10,
            "ci_low": lower*.10, "ci_high": upper*.10, "webb_p": boot["p_at_zero"],
            "n": meta["design"]["n"], "groups": meta["design"]["province_product_groups"]}


def fact_values(data):
    def national(key, period, column):
        d = data[key]
        return d.loc[d.geo.eq("Canada") & d.period.eq(period) & d["product"].eq("TOTAL"), column].item()

    hhi = data["gold_hhi"].set_index(["scope", "year"])
    model = primary(data)
    product = bridge(data).set_index("component").change_cad
    change = partner_changes(data).set_index("partner")
    monthly = data["matched"].loc[lambda d: d.geo.eq("Canada")].set_index("year")
    pilot = data["pilot_metadata"]
    return {
        "US24": [national("annual", "2024", "us_share")*100, 1],
        "US25": [national("annual", "2025", "us_share")*100, 1],
        "US_DPP": [(national("annual", "2025", "us_share")-national("annual", "2024", "us_share"))*100, 2],
        "US23": [national("annual", "2023", "us_share")*100, 1],
        "US25_CAD": [national("annual", "2025", "us_cad_thousands")/1e6, 1],
        "WORLD25": [national("annual", "2025", "world_cad_thousands")/1e6, 1],
        "NON_US25": [national("annual", "2025", "non_us_cad_thousands")/1e6, 1],
        "NON_US_CHANGE": [product["total"]/1e9, 3],
        "GOLD": [product["710812"]/1e9, 3],
        "CRUDE": [product["270900"]/1e9, 3],
        "REMAINDER": [product["remainder"]/1e9, 3],
        "GOLD_CRUDE_PCT": [(product["710812"]+product["270900"])/product["total"]*100, 1],
        "HHI24": [hhi.loc[("all products", 2024), "hhi_ex_us"], 6],
        "HHI25": [hhi.loc[("all products", 2025), "hhi_ex_us"], 6],
        "EX_GOLD24": [hhi.loc[("excluding HS 710812", 2024), "hhi_ex_us"], 6],
        "EX_GOLD25": [hhi.loc[("excluding HS 710812", 2025), "hhi_ex_us"], 6],
        "UK24": [hhi.loc[("all products", 2024), "uk_share_non_us"]*100, 2],
        "UK25": [hhi.loc[("all products", 2025), "uk_share_non_us"]*100, 2],
        "UK_CHANGE": [change.loc["United Kingdom", "change_cad_thousands"]/1e6, 3],
        "UK_GOLD": [product_changes(data, "GB").set_index("hs6").loc["710812", "change_cad"]/1e9, 3],
        "MONTH25": [monthly.loc[2025, "us_share"]*100, 1],
        "MONTH26": [monthly.loc[2026, "us_share"]*100, 1],
        "BETA": [model["beta"], 6], "SCALED": [model["scaled"], 6], "LOW": [model["ci_low"], 5],
        "HIGH": [model["ci_high"], 5], "P": [model["webb_p"], 4], "N": [model["n"], 0], "G": [model["groups"], 0],
        "PILOT_LINES": [pilot["potential_core_hts10_lines"], 0],
        "PILOT_HS6": [pilot["potential_core_hs6"], 0],
        "PILOT_HS4": [pilot["potential_core_hs4"], 0],
    }


def localized_number(value, decimals, lang):
    s = f"{float(value):,.{decimals}f}"
    if lang == "fr":
        s = s.replace(",", "\u202f").replace(".", ",")
    return s.replace("-", "−")


def build(root):
    data = load(root)
    target = root/P5
    bridge(data).to_csv(target/"commodity_bridge.csv", index=False)
    partner_changes(data).to_csv(target/"partner_changes.csv", index=False)
    facts = {k: [float(v), d] for k, (v, d) in fact_values(data).items()}
    write_json(target/"facts.json", facts)
    return data


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--establish-lock", action="store_true")
    args = p.parse_args()
    if args.establish_lock:
        establish_lock(args.root)
    build(args.root)
