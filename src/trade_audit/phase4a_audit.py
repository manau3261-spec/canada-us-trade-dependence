"""Phase 4A descriptive checks from pinned official observations."""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from .acquire import sha256, write_json
from .phase3_data import VINTAGE, read_slice
from .phase3_reconcile import GEO_BY_CIMT
from .sources import ALL_GEOS, NAPCS, PROVINCES
from .validate import USA, WORLD

YEARS = (2024, 2025)
HHI_YEARS = {"2013", "2016", "2017", "2018", "2022", "2023", "2024", "2025"}
RESIDUAL = {"Canada", "Unknown or unspecified", "Other countries"}
US_AREAS = {"Puerto Rico", "Virgin Islands, United States", "United States Minor Outlying Islands",
            "Guam", "American Samoa", "Northern Mariana Islands"}


def verified(root, record):
    path = root / record["path"]
    if record["status"] != "downloaded" or sha256(path) != record["sha256"]:
        raise ValueError(f"Source verification failed for {path}")
    return path


def load_cimt(path, year):
    with ZipFile(path) as archive:
        member = next(name for name in archive.namelist() if name.endswith(f"ODPFN016_{year}12N.csv"))
        with archive.open(member) as f:
            data = pd.read_csv(f, dtype={"YearMonth/AnnéeMois": str, "HS8": str}, keep_default_na=False)
    data.columns = ["month", "hs8", "country", "province", "state", "value_cad", "quantity", "unit"]
    keys = ["month", "hs8", "country", "province", "state"]
    if data.duplicated(keys).any() or not data.hs8.str.fullmatch(r"\d{8}").all():
        raise ValueError(f"Invalid or duplicate CIMT HS8 keys: {year}")
    if set(data.month) != {f"{year}{m:02d}" for m in range(1, 13)} or set(data.province) != set(GEO_BY_CIMT):
        raise ValueError(f"Incomplete CIMT file: {year}")
    if data.value_cad.lt(0).any():
        raise ValueError(f"Negative trade data in {year}")
    return data.assign(hs6=data.hs8.str[:6], year=year)


def values_by_product(detail):
    # Absence contributes no published flow. Presence flags preserve the
    # distinction between unpublished amounts and demonstrated structural zeroes.
    values = detail.groupby(["country", "hs6", "year"]).value_cad.sum().unstack("year")
    values.columns = ["value_cad_2024", "value_cad_2025"]
    d = values.reset_index()
    d["reported_2024"] = d.value_cad_2024.notna()
    d["reported_2025"] = d.value_cad_2025.notna()
    d["change_cad"] = d.value_cad_2025.fillna(0) - d.value_cad_2024.fillna(0)
    return d


def quantity_checks(detail, values):
    uk = values[values.country.eq("GB")].set_index("hs6")["change_cad"].abs().nlargest(12).index
    top = (values[values.country.ne("US")].groupby("hs6")["change_cad"].sum()
           .abs().nlargest(18).index)
    # Cover all non-US destinations for the largest contributors, plus the UK's largest lines.
    keep = detail.value_cad.gt(0) & detail.country.ne("US") & (
        detail.hs6.isin(top) | (detail.country.eq("GB") & detail.hs6.isin(uk))
    )
    d = detail.loc[keep].assign(positive_qty=lambda x: x.quantity.gt(0) & x.unit.ne(""))
    stat = d.groupby(["country", "hs8", "year"]).agg(
        value_cad=("value_cad", "sum"), quantity=("quantity", "sum"), units=("unit", "nunique"),
        unit=("unit", "first"), rows=("value_cad", "size"), positive_qty_rows=("positive_qty", "sum")
    )
    stat["valid"] = stat.units.eq(1) & stat.positive_qty_rows.eq(stat.rows)
    j = stat.xs(2024, level="year").add_suffix("_2024").join(
        stat.xs(2025, level="year").add_suffix("_2025"), how="outer").reset_index()
    okay = j.valid_2024.eq(True) & j.valid_2025.eq(True) & j.unit_2024.eq(j.unit_2025)
    p0, p1 = (j[f"value_cad_{y}"]/j[f"quantity_{y}"].where(okay) for y in YEARS)
    j["quantity_comparable"] = okay
    j["unit_value_2024"], j["unit_value_2025"] = p0, p1
    j["quantity_contribution_cad"] = (p0+p1)/2*(j.quantity_2025-j.quantity_2024)
    j["unit_value_contribution_cad"] = (j.quantity_2025+j.quantity_2024)/2*(p1-p0)
    j["change_cad"] = j.value_cad_2025.fillna(0)-j.value_cad_2024.fillna(0)
    error = (j.loc[okay, "quantity_contribution_cad"] + j.loc[okay, "unit_value_contribution_cad"]
             - j.loc[okay, "change_cad"]).abs()
    if error.gt(.001).any():
        raise ValueError("Unit value decomposition did not reconcile")
    return j.sort_values(["country", "hs8"]).reset_index(drop=True)


def portfolio_scenarios(values):
    rows = []
    for scope, mask in [
        ("all products", values.hs6.notna()),
        ("excluding HS 710812", values.hs6.ne("710812")),
        ("excluding chapter 71", ~values.hs6.str.startswith("71")),
    ]:
        for year in YEARS:
            p = values[mask].groupby("country")[f"value_cad_{year}"].sum()
            if any(p.get(key, 0) for key in ("CA", "", "ZZ")):
                raise ValueError("Positive unassigned country value")
            nonus = p.drop("US")
            rows.append({"scope": scope, "year": year, "world_cad": int(p.sum()),
                         "us_cad": int(p["US"]), "non_us_cad": int(nonus.sum()),
                         "uk_cad": int(p["GB"]), "uk_share_non_us": float(p["GB"]/nonus.sum()),
                         "hhi_full": float(((p/p.sum())**2).sum()),
                         "hhi_ex_us": float(((nonus/nonus.sum())**2).sum())})
    return pd.DataFrame(rows)


def destination_mix(values):
    d = values[values.country.ne("US")]
    cols = ["value_cad_2024", "value_cad_2025"]
    g = d.groupby("hs6")[cols].sum().join(d[d.country.eq("GB")].set_index("hs6")[cols],
                                          rsuffix="_uk").fillna(0)
    n0, n1 = g.value_cad_2024.sum(), g.value_cad_2025.sum()
    w0, w1 = g.value_cad_2024/n0, g.value_cad_2025/n1
    u0 = g.value_cad_2024_uk/g.value_cad_2024.where(g.value_cad_2024.gt(0))
    u1 = g.value_cad_2025_uk/g.value_cad_2025.where(g.value_cad_2025.gt(0))
    stable = u0.notna() & u1.notna()
    out = g.assign(within_product_destination_pp=100*((w0+w1)/2*(u1-u0)).where(stable),
                   between_product_mix_pp=100*((u0+u1)/2*(w1-w0)).where(stable),
                   hs_entry_exit_pp=100*(g.value_cad_2025_uk/n1-g.value_cad_2024_uk/n0).where(~stable))
    target = 100*(g.value_cad_2025_uk.sum()/n1-g.value_cad_2024_uk.sum()/n0)
    if abs(out.iloc[:, -3:].sum().sum()-target) > 1e-10:
        raise ValueError("UK share decomposition failed")
    return out.reset_index()


def hhi_methods(root, record, archived=False):
    pid = "12100133" if archived else "12100173"
    partner = "Trading Partner" if archived else "Trading partner"
    path = verified(root, record)
    f = read_slice(path, f"{pid}.csv", ["REF_DATE", "GEO", partner, NAPCS, "Trade", "VALUE", "STATUS"],
                   {"GEO": set(ALL_GEOS), NAPCS: {"All sections"}, "Trade": {"Export"}},
                   "2013", "2025", HHI_YEARS)
    rows = []
    prefix = "archived" if archived else "current"
    for (period, geo), d in f.groupby(["REF_DATE", "GEO"]):
        p = d.set_index(partner).VALUE
        if p.index.has_duplicates or p.isna().any() or p.lt(0).any():
            raise ValueError("HHI sensitivity requires complete nonnegative partner data")
        w, us = p[WORLD], p[USA]
        detail = p.drop(WORLD)
        known = detail.drop(RESIDUAL, errors="ignore")
        areas = sorted(US_AREAS & set(known.index))
        alt = known.drop(areas, errors="ignore").copy()
        moved = known.loc[areas].sum()
        alt[USA] += moved
        for measure, denom, parts, folded, norm in [
            ("destination_hhi", w, known, alt, w),
            ("destination_hhi_ex_us", w-us, known.drop(USA), alt.drop(USA), w-us-moved),
        ]:
            if min(denom, norm, parts.sum()) <= 0:
                continue
            rows.append({
                "period": period, "geo": geo, "measure": measure,
                f"{prefix}_hhi": float(((parts/denom)**2).sum()),
                f"{prefix}_normalize_partner_sum": float(((parts/parts.sum())**2).sum()),
                f"{prefix}_fold_us_territories": float(((folded/norm)**2).sum()),
                f"{prefix}_residual_cad_thousands": float(detail.loc[sorted(RESIDUAL & set(detail.index))].sum()),
                f"{prefix}_partner_sum_gap_cad_thousands": float(detail.sum()-w),
                f"{prefix}_us_share": float(us/w),
                f"{prefix}_us_cad_thousands": float(us),
                f"{prefix}_world_cad_thousands": float(w),
                f"{prefix}_positive_partners": int(parts.gt(0).sum()),
                f"{prefix}_us_territory_value_cad_thousands": float(moved),
            })
    return pd.DataFrame(rows)


def cimt_hhi_by_geo(detail, scenarios):
    rows = []
    grouped = detail.groupby(["year", "province", "country"]).value_cad.sum()
    for (year, prov), flows in grouped.groupby(level=[0, 1]):
        shares = flows.droplevel([0, 1])
        nonus = shares.drop("US")
        for measure, part in [("destination_hhi", shares), ("destination_hhi_ex_us", nonus)]:
            rows.append((str(year), GEO_BY_CIMT[prov], measure, ((part/part.sum())**2).sum()))
    for row in scenarios[scenarios.scope.eq("all products")].itertuples():
        rows.extend([(str(row.year), "Canada", "destination_hhi", row.hhi_full),
                     (str(row.year), "Canada", "destination_hhi_ex_us", row.hhi_ex_us)])
    return pd.DataFrame(rows, columns=["period", "geo", "measure", "cimt_hs8_hhi"])


def compare_hhi(root, active, existing, cimt):
    archive = json.loads((root/"data/provenance/phase3-supplementary-sources.json").read_text())
    keys = ["period", "geo", "measure"]
    old = hhi_methods(root, archive["archived_annual"], archived=True)
    now = hhi_methods(root, active)
    d = existing[existing.period.isin(HHI_YEARS)].merge(now, on=keys, how="left", validate="one_to_one").merge(
        old, on=keys, how="left", validate="one_to_one"
    )
    for field in ("current_hhi", "current_normalize_partner_sum", "current_fold_us_territories", "archived_hhi"):
        d[f"{field}_minus_official"] = d[field] - d.statcan_hhi
    return d.merge(cimt, on=keys, how="left", validate="one_to_one").sort_values(keys).reset_index(drop=True)


def design_C_coverage(root):
    a = pd.read_csv(root / "data/phase3/annual_exposure.csv", dtype={"period": int})
    a = a[a.geo.isin(PROVINCES) & ~a["product"].isin({"TOTAL", "C23"})]
    rows = []
    for (geo, product), group in a.groupby(["geo", "product"]):
        s = group.set_index("period").reindex(range(2010, 2026))
        for t in range(2011, 2025):
            lag = pd.notna(s.loc[t-1, "destination_hhi_ex_us"])
            start = s.loc[t, "non_us_cad_thousands"] > 0
            end = s.loc[t+1, "non_us_cad_thousands"] > 0
            rows.append((geo, product, t, lag, start, end, lag and start and end))
    return pd.DataFrame(rows, columns=["geo", "product", "t", "lagged_hhi_available",
                                        "start_exports_positive", "end_exports_positive", "usable"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    root = parser.parse_args().root.resolve()
    manifest = json.loads((root / "data/provenance/phase4a-cimt-sources.json").read_text())
    acquisition = json.loads((root/f"data/provenance/acquisition-{VINTAGE}.json").read_text())
    source = next(d for d in acquisition["sources"] if d["pid"] == "12100173")
    summary = json.loads((root/"data/phase3/phase3_summary.json").read_text())
    for name in ("annual_exposure.csv", "destination_hhi_benchmark.csv"):
        if sha256(root/"data/phase3"/name) != summary["files"][name]["sha256"]:
            raise ValueError(f"Phase 3 hash mismatch: {name}")
    raw = pd.concat([load_cimt(verified(root, manifest[str(y)]), y) for y in YEARS], ignore_index=True)
    values = values_by_product(raw)
    scenarios = portfolio_scenarios(values)
    hhi = pd.read_csv(root/"data/phase3/destination_hhi_benchmark.csv", dtype={"period": str})
    files = {
        "hs6_country_value_changes.csv": values,
        "hs8_quantity_checks.csv": quantity_checks(raw, values),
        "uk_share_composition.csv": destination_mix(values),
        "non_us_gold_exclusion_sensitivity.csv": scenarios,
        "hhi_method_sensitivity.csv": compare_hhi(root, source, hhi, cimt_hhi_by_geo(raw, scenarios)),
        "design_C_coverage.csv": design_C_coverage(root),
    }
    target = root/"data/phase4a"
    target.mkdir(parents=True, exist_ok=True)
    info = {"source_vintage": VINTAGE,
            "cimt_rows": {str(y): int(n) for y,n in raw.groupby("year").size().items()}, "files": {}}
    for name, frame in files.items():
        path = target/name
        frame.to_csv(path, index=False)
        info["files"][name] = {"rows": len(frame), "sha256": sha256(path)}
    write_json(target/"manifest.json", info)
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
