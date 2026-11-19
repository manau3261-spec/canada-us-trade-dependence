"""Compare the two current sources and independent official 2020 vintages."""
import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from .acquire import sha256
from .phase3_data import codes_for_products, read_slice
from .sources import ALL_GEOS, NAPCS
from .trade import numeric_rounding, within_precision
from .validate import USA, WORLD

KEY = ["geo", "partner", "product"]
GEO_BY_CIMT = dict(zip(
    ("NL", "PE", "NS", "NB", "QC", "ON", "MB", "SK", "AB", "BC", "YT", "NT", "NU"),
    ALL_GEOS[1:],
))


def comparison(annual: pd.DataFrame, monthly: pd.DataFrame) -> pd.DataFrame:
    common = set(annual["partner"]) & set(monthly["partner"])
    products = set(annual["product"]) & set(monthly["product"])
    a = annual.loc[annual["partner"].isin(common) & annual["product"].isin(products)].copy()
    m = monthly.loc[monthly["partner"].isin(common) & monthly["product"].isin(products)].copy()
    a["annual_tolerance"] = numeric_rounding(a)
    m["rounding"] = numeric_rounding(m)
    if a.duplicated(KEY).any() or m.duplicated([*KEY, "period"]).any():
        raise ValueError("Duplicate 2020 trade keys")
    totals = m.groupby(KEY, observed=True).agg(
        monthly=("value", lambda x: x.sum(min_count=12)),
        monthly_tolerance=("rounding", lambda x: x.sum(min_count=12)),
        months=("period", "nunique"),
    )
    one = a.set_index(KEY)[["value", "annual_tolerance"]].rename(columns={"value": "annual"})
    joined = one.join(totals, how="outer", validate="one_to_one").reset_index()
    joined["monthly"] = joined["monthly"].where(joined["months"].eq(12))
    joined["monthly_minus_annual_cad_thousands"] = joined["monthly"] - joined["annual"]
    joined["rounding_tolerance_cad_thousands"] = joined["monthly_tolerance"] + joined["annual_tolerance"]
    comparable = joined["monthly_minus_annual_cad_thousands"].notna()
    joined["outside_rounding"] = comparable & ~within_precision(
        joined["monthly_minus_annual_cad_thousands"], joined["rounding_tolerance_cad_thousands"]
    )
    return joined.sort_values(KEY).reset_index(drop=True)


def supplementary_sources(root: Path) -> dict:
    path = root / "data/provenance/phase3-supplementary-sources.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    for key in ("archived_annual", "archived_monthly", "cimt_2020"):
        entry = evidence[key]
        if entry["status"] != "downloaded" or sha256(root / entry["path"]) != entry["sha256"]:
            raise ValueError(f"Missing or modified supplementary evidence: {key}")
    return evidence


def archived_trade(root: Path, entry: dict, annual: bool) -> pd.DataFrame:
    pid = "12100133" if annual else "12100119"
    flow = "Export" if annual else "Domestic export"
    partner = "Trading Partner" if annual else "Principal trading partners"
    fields = ["REF_DATE", "GEO", partner, NAPCS, "Trade", "VALUE", "DECIMALS", "STATUS"]
    data = read_slice(root / entry["path"], f"{pid}.csv", fields,
                      {"GEO": set(ALL_GEOS), "Trade": {flow}}, "2020", "2020")
    codes = codes_for_products(data[NAPCS])
    return data.rename(columns={"REF_DATE": "period", "GEO": "geo", partner: "partner",
                                NAPCS: "product", "VALUE": "value", "DECIMALS": "decimals"}).assign(
        product=data[NAPCS].map(codes), decimals=pd.to_numeric(data["DECIMALS"], errors="raise")
    )


def cimt_rollup(root: Path, entry: dict, by_month: bool = False) -> pd.DataFrame:
    """Sum the HS2 member once across chapters, provincial origins and U.S. states."""
    with ZipFile(root / entry["path"]) as archive:
        member = next(n for n in archive.namelist() if n.endswith("/ODPFN020_202012N.csv"))
        with archive.open(member) as raw:
            d = pd.read_csv(raw, usecols=["YearMonth/AnnéeMois", "Country/Pays", "Province", "Value/Valeur"],
                            dtype={"YearMonth/AnnéeMois": str}, keep_default_na=False)
    if set(d["Province"]) != set(GEO_BY_CIMT):
        raise ValueError("Unexpected CIMT provincial reporting universe")
    if set(d["YearMonth/AnnéeMois"]) != {f"2020{m:02d}" for m in range(1, 13)}:
        raise ValueError("Incomplete 2020 CIMT reference periods")
    d = d.rename(columns={"YearMonth/AnnéeMois": "period", "Country/Pays": "country",
                          "Province": "geo", "Value/Valeur": "value_cad"})
    d["geo"] = d["geo"].map(GEO_BY_CIMT)
    d["period"] = d["period"].str.slice(0, 4) + "-" + d["period"].str.slice(4)
    keys = ["period", "geo"] if by_month else ["geo"]
    frames = []
    for partner, subset in ((WORLD, d), (USA, d.loc[d["country"].eq("US")])):
        prov = subset.groupby(keys, as_index=False)["value_cad"].sum()
        if by_month:
            canada = subset.groupby("period", as_index=False)["value_cad"].sum().assign(geo="Canada")
        else:
            canada = pd.DataFrame([{"geo": "Canada", "value_cad": subset["value_cad"].sum()}])
        frames.append(pd.concat([prov, canada], ignore_index=True).assign(partner=partner))
    return pd.concat(frames, ignore_index=True).assign(cimt_cad_thousands=lambda f: f["value_cad"] / 1000)


def gap_summary(frame: pd.DataFrame) -> dict:
    mask = frame["outside_rounding"]
    return {
        "comparisons": len(frame), "matched_numeric": int(frame["monthly"].notna().sum()),
        "outside": int(mask.sum()),
        "max_abs_cad_thousands": float(frame["monthly_minus_annual_cad_thousands"].abs().max()),
    }


def reconcile(root: Path, annual: pd.DataFrame, monthly: pd.DataFrame) -> tuple[dict, dict]:
    inputs = supplementary_sources(root)
    a = annual.loc[annual["period"].eq("2020")]
    m = monthly.loc[monthly["period"].str.startswith("2020")]
    active = comparison(a, m)
    archived_a = archived_trade(root, inputs["archived_annual"], True)
    archived_m = archived_trade(root, inputs["archived_monthly"], False)
    archived = comparison(archived_a, archived_m)
    world_us = active.loc[active["partner"].isin([WORLD, USA]) & active["product"].eq("TOTAL")]
    archived_total = archived.loc[archived["partner"].isin([WORLD, USA]) & archived["product"].eq("TOTAL")]
    axes = ["geo", "partner"]
    evidence = world_us[axes + ["annual", "monthly"]].merge(
        archived_total[axes + ["annual", "monthly"]], on=axes, suffixes=("_active", "_archived"),
        validate="one_to_one",
    )
    cimt = cimt_rollup(root, inputs["cimt_2020"])
    evidence = evidence.merge(cimt[axes + ["cimt_cad_thousands"]], on=axes, validate="one_to_one")
    for label in ("annual_active", "annual_archived", "monthly_active", "monthly_archived"):
        evidence[label + "_minus_cimt"] = evidence[label] - evidence["cimt_cad_thousands"]
    cimt_months = cimt_rollup(root, inputs["cimt_2020"], by_month=True)
    selects = ["period", "geo", "partner"]
    modern = m.loc[m["partner"].isin([WORLD, USA]) & m["product"].eq("TOTAL"), selects + ["value"]]
    older = archived_m.loc[archived_m["partner"].isin([WORLD, USA]) & archived_m["product"].eq("TOTAL"), selects + ["value"]]
    month_evidence = cimt_months.merge(modern, on=selects, validate="one_to_one").merge(
        older, on=selects, suffixes=("_active", "_archived"), validate="one_to_one"
    )
    for label in ("active", "archived"):
        month_evidence[f"{label}_minus_cimt"] = month_evidence[f"value_{label}"] - month_evidence["cimt_cad_thousands"]
    stats = {
        "active": gap_summary(active), "archived": gap_summary(archived),
        "cimt_annual_active_matches": int(evidence["annual_active_minus_cimt"].abs().le(0.0500001).sum()),
        "cimt_annual_archived_matches": int(evidence["annual_archived_minus_cimt"].abs().le(0.0500001).sum()),
        "cimt_monthly_active_matches": int(month_evidence["active_minus_cimt"].abs().le(0.5000001).sum()),
        "cimt_monthly_archived_matches": int(month_evidence["archived_minus_cimt"].abs().le(0.5000001).sum()),
        "monthly_active_archived_equal": int(month_evidence["value_active"].eq(month_evidence["value_archived"]).sum()),
        "monthly_benchmark_rows": len(month_evidence),
        "annual_benchmark_rows": len(evidence),
        "active_mismatch_geographies": active.loc[active["outside_rounding"]].groupby("geo").size().to_dict(),
        "active_mismatch_sections": active.loc[active["outside_rounding"]].groupby("product").size().to_dict(),
        "active_mismatch_partners": active.loc[active["outside_rounding"]].groupby("partner").size().to_dict(),
    }
    files = {
        "reconciliation_2020.csv": active, "reconciliation_2020_archived.csv": archived,
        "reconciliation_2020_cimt_totals.csv": evidence, "reconciliation_2020_cimt_months.csv": month_evidence,
    }
    return files, stats
