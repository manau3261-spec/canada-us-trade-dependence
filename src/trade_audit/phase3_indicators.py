"""Descriptive calculations from official customs, GDP and supply-use observations."""
import numpy as np
import pandas as pd

from .phase3_data import IO_TOTAL, IO_VARIABLE
from .sources import ALL_GEOS, JURISDICTIONS, NAICS, PROVINCES
from .trade import HHI_UNALLOCATED, numeric_rounding, within_precision
from .validate import EX_US, SECTION_TOTAL, USA, WORLD

GDP_SECTORS = {"11", "21", "22", "23", "31-33", "41", "44-45", "48-49", "51",
               "52", "53", "54", "55", "56", "61", "62", "71", "72", "81", "91"}


def safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator.where(denominator.gt(0))).where(numerator.ge(0))


def exposure(controls: pd.DataFrame) -> pd.DataFrame:
    d = controls.rename(columns={"world": "world_cad_thousands", "usa": "us_cad_thousands",
                                 "us_domestic_export_share": "us_share",
                                 "value": "partner_sum_cad_thousands",
                                 "destination_gap": "destination_gap_cad_thousands",
                                 "destination_tolerance": "destination_tolerance_cad_thousands"}).copy()
    d["non_us_cad_thousands"] = (d["world_cad_thousands"] - d["us_cad_thousands"]).where(
        d["world_cad_thousands"].ge(d["us_cad_thousands"])
    )
    return d[[
        "period", "geo", "product", "world_cad_thousands", "us_cad_thousands", "non_us_cad_thousands",
        "us_share", "destination_hhi", "destination_hhi_ex_us", "destination_reconciled",
        "partner_sum_cad_thousands", "destination_gap_cad_thousands", "destination_tolerance_cad_thousands",
        "numeric_partners", "unallocated",
    ]].sort_values(["period", "geo", "product"]).reset_index(drop=True)


def export_intensity(annual: pd.DataFrame, gdp: pd.DataFrame) -> pd.DataFrame:
    trades = annual.loc[annual["product"].eq(SECTION_TOTAL) & annual["geo"].isin(JURISDICTIONS),
                        ["period", "geo", "world_cad_thousands", "us_cad_thousands"]]
    rows = gdp.loc[gdp["Prices"].eq("Current dollars") & gdp[NAICS].eq("All industries [T001]"),
                   ["REF_DATE", "GEO", "VALUE", "STATUS"]]
    rows = rows.rename(columns={"REF_DATE": "period", "GEO": "geo", "VALUE": "gdp_current_cad_millions",
                                 "STATUS": "gdp_source_status"})
    d = trades.merge(rows, how="left", on=["period", "geo"], validate="one_to_one")
    denominator = d["gdp_current_cad_millions"] * 1000
    d["world_exports_to_gdp"] = safe_ratio(d["world_cad_thousands"], denominator)
    d["us_exports_to_gdp"] = safe_ratio(d["us_cad_thousands"], denominator)
    return d.sort_values(["period", "geo"]).reset_index(drop=True)


def non_us_portfolio(trade: pd.DataFrame, annual: pd.DataFrame) -> pd.DataFrame:
    base = annual.loc[annual["geo"].eq("Canada") & annual["product"].eq(SECTION_TOTAL),
                      ["period", "non_us_cad_thousands"]]
    rows = (trade.loc[trade["geo"].eq("Canada") & trade["product"].eq(SECTION_TOTAL)
                      & ~trade["partner"].isin({USA, WORLD}), ["period", "partner", "value"]]
            .rename(columns={"value": "exports_cad_thousands"}).merge(base, on="period", validate="many_to_one"))
    rows["is_identified_destination"] = ~rows["partner"].isin(HHI_UNALLOCATED)
    rows["share_of_non_us"] = safe_ratio(rows["exports_cad_thousands"], rows["non_us_cad_thousands"])
    return rows.sort_values(["period", "partner"]).reset_index(drop=True)


def geography_check(trade: pd.DataFrame) -> pd.DataFrame:
    keys = ["period", "partner", "product"]
    base = trade.loc[trade["partner"].isin({WORLD, USA})].copy()
    base["rounding"] = numeric_rounding(base)
    direct = base.loc[base["geo"].eq("Canada")].set_index(keys)[["value", "rounding"]]
    region = base.loc[base["geo"].isin(JURISDICTIONS)]
    by_geo = region.groupby(keys)
    summed = by_geo[["value", "rounding"]].sum(min_count=len(JURISDICTIONS)).join(
        by_geo["geo"].nunique().rename("jurisdictions")
    )
    joined = direct.join(summed, how="outer", rsuffix="_regional", validate="one_to_one").reset_index()
    joined["subnational_minus_canada_cad_thousands"] = joined["value_regional"] - joined["value"]
    joined["rounding_tolerance"] = joined["rounding"] + joined["rounding_regional"]
    joined["within_rounding"] = joined["jurisdictions"].eq(13) & within_precision(
        joined["subnational_minus_canada_cad_thousands"], joined["rounding_tolerance"]
    )
    return joined.rename(columns={"value": "canada_cad_thousands", "value_regional": "sum_regions_cad_thousands"}).drop(
        columns=["rounding", "rounding_regional"]
    ).sort_values(keys).reset_index(drop=True)


def benchmark_hhi(annual: pd.DataFrame, published: pd.DataFrame) -> pd.DataFrame:
    keys = ["period", "geo"]
    regions = annual.loc[annual["product"].eq(SECTION_TOTAL)]
    frames = []
    for partner, measure in ((WORLD, "destination_hhi"), (EX_US, "destination_hhi_ex_us")):
        p = published.loc[published["Partner countries"].eq(partner),
                          ["REF_DATE", "GEO", "VALUE", "DECIMALS"]].rename(
            columns={"REF_DATE": "period", "GEO": "geo", "VALUE": "statcan_hhi", "DECIMALS": "decimals"}
        )
        d = regions[keys + [measure]].rename(columns={measure: "reconstructed_hhi"}).merge(
            p, on=keys, how="outer", validate="one_to_one"
        )
        d["decimals"] = pd.to_numeric(d["decimals"], errors="coerce")
        d["reconstruction_minus_published"] = d["reconstructed_hhi"] - d["statcan_hhi"]
        tol = (0.5 * (10.0 ** -d["decimals"])).where(d["statcan_hhi"].notna())
        d["within_published_rounding"] = d["reconstruction_minus_published"].abs().le(tol + 1e-12).where(
            d["reconstruction_minus_published"].notna()
        )
        frames.append(d.assign(measure=measure))
    return pd.concat(frames, ignore_index=True).sort_values(["measure", *keys]).reset_index(drop=True)


def demand_benchmark(io: pd.DataFrame) -> pd.DataFrame:
    concepts = {
        (USA, "Value added due to foreign demand"): ("us_demand_value_added_cad_thousands", "81", "3"),
        (IO_TOTAL, "Value added"): ("all_value_added_cad_thousands", "81", "3"),
        (USA, "Jobs due to foreign demand"): ("us_demand_jobs", "223", "0"),
        (IO_TOTAL, "Jobs"): ("all_jobs", "223", "0"),
        (USA, "Value added exports"): ("us_exports_value_added_all_regions_cad_thousands", "81", "3"),
        (USA, "Total jobs embodied in exports"): ("us_exports_embodied_jobs_all_regions", "223", "0"),
    }
    out = pd.MultiIndex.from_product(
        [list(map(str, range(2010, 2026))), ALL_GEOS], names=["period", "geo"]
    ).to_frame(index=False)
    for (country, variable), (name, uom, scale) in concepts.items():
        d = io.loc[io["Country Code"].eq(country) & io[IO_VARIABLE].eq(variable)
                   & io["Industry"].eq("Total industries")].copy()
        numeric = d["VALUE"].notna()
        if not (d.loc[numeric, "UOM_ID"].eq(uom) & d.loc[numeric, "SCALAR_ID"].eq(scale)).all():
            raise ValueError(f"Unexpected units for {variable}")
        d = d[["REF_DATE", "GEO", "VALUE"]].rename(columns={"REF_DATE": "period", "GEO": "geo", "VALUE": name})
        out = out.merge(d, on=["period", "geo"], how="left", validate="one_to_one")
    for stem, parts in {
        "us_demand_value_added_share": ("us_demand_value_added_cad_thousands", "all_value_added_cad_thousands"),
        "us_demand_jobs_share": ("us_demand_jobs", "all_jobs"),
    }.items():
        num, den = [out[k] for k in parts]
        out[stem] = safe_ratio(num, den).where(num.le(den))
    return out


def coverage_slice(frame: pd.DataFrame, groups: list[str], periods: list[str],
                   geos: tuple[str, ...], eligible: tuple[str, ...]) -> pd.DataFrame:
    keys = ["REF_DATE", "GEO", "industry"]
    observed = frame.loc[frame["REF_DATE"].isin(periods), keys + ["VALUE", "STATUS"]].copy()
    if observed.duplicated(keys).any():
        raise ValueError("Duplicate observation in coverage slice")
    grid = pd.MultiIndex.from_product([periods, geos, groups], names=keys).to_frame(index=False)
    grid = grid.merge(observed.assign(present=True), on=keys, how="left", validate="one_to_one")
    grid["reported"] = grid["VALUE"].notna()
    grid["suppressed"] = grid["STATUS"].isin({"x", "X"})
    grid["unreliable"] = grid["STATUS"].isin({"f", "F"})
    grid["expected"] = grid["GEO"].isin(eligible)
    grid["present"] = grid["present"].eq(True)
    grid["other_missing_row"] = grid["present"] & ~grid["reported"] & ~grid["suppressed"] & ~grid["unreliable"]
    grid["absent_eligible"] = grid["expected"] & ~grid["present"]
    grid["outside_geographic_universe"] = ~grid["expected"]
    fields = ["expected", "present", "reported", "suppressed", "unreliable", "other_missing_row",
              "absent_eligible", "outside_geographic_universe"]
    return grid.groupby(["GEO", "industry"], as_index=False, observed=True)[fields].sum().rename(
        columns={"GEO": "geo", "expected": "eligible_periods", "present": "rows_present"}
    )


def panel_coverage(gdp: pd.DataFrame, lfs: pd.DataFrame, io: pd.DataFrame) -> pd.DataFrame:
    annual_periods = list(map(str, range(2010, 2026)))
    historical_months = pd.period_range("2010-01", "2025-12", freq="M").astype(str).tolist()
    recent_months = pd.period_range("2025-01", lfs["REF_DATE"].max(), freq="M").astype(str).tolist()
    gdp_code = gdp[NAICS].str.extract(r"\[([^]]+)\]$", expand=False)
    gdp = gdp.loc[gdp_code.isin(GDP_SECTORS | {"T001"})].rename(columns={NAICS: "industry"})
    lfs = lfs.rename(columns={NAICS: "industry"})
    io = io.rename(columns={"Industry": "industry"})
    specifications = [
        ("GDP real", "2010–2025", gdp.loc[gdp["Prices"].eq("Chained (2017) dollars")], annual_periods, JURISDICTIONS),
        ("GDP nominal", "2010–2025", gdp.loc[gdp["Prices"].eq("Current dollars")], annual_periods, JURISDICTIONS),
        ("LFS employed persons", "2010–2025", lfs, historical_months, ("Canada",) + PROVINCES),
        ("LFS employed persons", "2025–2026 observed", lfs, recent_months, ("Canada",) + PROVINCES),
        ("US value added due to demand", "2010–2025",
         io.loc[io[IO_VARIABLE].eq("Value added due to foreign demand") & io["Country Code"].eq(USA)],
         annual_periods, ALL_GEOS),
        ("US jobs due to demand", "2010–2025",
         io.loc[io[IO_VARIABLE].eq("Jobs due to foreign demand") & io["Country Code"].eq(USA)],
         annual_periods, ALL_GEOS),
    ]
    frames = []
    for measure, window, frame, periods, geos in specifications:
        groups = sorted(frame["industry"].unique())
        results = coverage_slice(frame, groups, periods, ALL_GEOS, geos)
        frames.append(results.assign(measure=measure, window=window))
    return pd.concat(frames, ignore_index=True)


def matched_ytd(monthly: pd.DataFrame) -> pd.DataFrame:
    data = monthly.loc[monthly["product"].eq(SECTION_TOTAL)].copy()
    data[["year", "month"]] = data["period"].str.split("-", expand=True)
    ordered = sorted(set(data.loc[data["year"].eq("2025"), "month"]) &
                     set(data.loc[data["year"].eq("2026"), "month"]))
    ytd = data.loc[data["year"].isin(["2025", "2026"]) & data["month"].isin(ordered)]
    amounts = ["world_cad_thousands", "us_cad_thousands", "non_us_cad_thousands"]
    sums = ytd.groupby(["geo", "year"])[amounts].sum(min_count=len(ordered)).reset_index()
    sums["us_share"] = safe_ratio(sums["us_cad_thousands"], sums["world_cad_thousands"])
    return sums.assign(first_month=ordered[0], last_month=ordered[-1], months=len(ordered)).sort_values(
        ["geo", "year"]
    ).reset_index(drop=True)


def decompose(annual: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    national = annual.loc[annual["geo"].eq("Canada") & annual["period"].isin({start, end})]
    detail = national.loc[national["product"].ne(SECTION_TOTAL)]
    after = detail.loc[detail["period"].eq(end)].set_index("product")
    before = detail.loc[detail["period"].eq(start)].set_index("product")
    if (set(before.index) != set(after.index) or before["us_share"].isna().any()
            or after["us_share"].isna().any()):
        raise ValueError("Decomposition requires a common complete national product partition")
    v0, v1 = before["world_cad_thousands"], after["world_cad_thousands"]
    w0, w1 = v0 / v0.sum(), v1 / v1.sum()
    s0, s1 = before["us_share"], after["us_share"]
    result = pd.DataFrame({
        "within_product_pp": 100 * (w0 + w1) / 2 * (s1 - s0),
        "composition_pp": 100 * (s0 + s1) / 2 * (w1 - w0),
    })
    result["total_contribution_pp"] = result["within_product_pp"] + result["composition_pp"]
    official = national.loc[national["product"].eq(SECTION_TOTAL)].set_index("period")["us_share"]
    headline = 100 * (official[end] - official[start])
    result.loc["ROUNDING", "total_contribution_pp"] = headline - result["total_contribution_pp"].sum()
    return result.rename_axis("product").reset_index().assign(
        start_year=start, end_year=end, national_change_pp=headline
    ).sort_values("product").reset_index(drop=True)
