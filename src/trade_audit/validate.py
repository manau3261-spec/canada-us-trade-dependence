import csv
import io
import re
from collections import Counter
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from zipfile import ZipFile
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from .acquire import sha256
from .sources import NAPCS, NAICS, Source

STANDARD = (
    "REF_DATE", "GEO", "DGUID", "UOM", "UOM_ID", "SCALAR_FACTOR", "SCALAR_ID",
    "VECTOR", "COORDINATE", "VALUE", "STATUS", "SYMBOL", "TERMINATED", "DECIMALS",
)
ANNUAL_TRADE = "12100173"
MONTHLY_TRADE = "12100175"
TRADE = (ANNUAL_TRADE, MONTHLY_TRADE)
WORLD = "All countries"
USA = "United States"
OTHER = "Other countries"
EX_US = "Countries other than the United States"
SECTION_TOTAL = "TOTAL"
UNUSABLE_STATUS = {"x", "X", "F", "f", "..", "...", "."}
CHUNK_ROWS = 350_000
UNIT_TYPES = {
    "12100173": {("Dollars", "thousands", "81", "3")},
    "12100175": {("Dollars", "thousands", "81", "3")},
    "12100129": {("Ratio", "units", "270", "0"), ("Index, 2017=100", "units", "373", "0")},
    "12100100": {("Dollars", "thousands", "81", "3"), ("Number", "units", "223", "0")},
    "36100711": {("Dollars", "millions", "81", "6"), ("Percentage point", "units", "396", "0")},
    "14100022": {("Persons in thousands", "thousands", "428", "3"), ("Percent", "units", "239", "0")},
}


def embedded_metadata(archive: ZipFile, source: Source) -> dict:
    with archive.open(source.metadata_member) as raw:
        rows = list(csv.reader(io.TextIOWrapper(raw, encoding="utf-8-sig")))
    cube = dict(zip(rows[0], rows[1]))
    if cube.get("Product Id") != source.pid or cube.get("Frequency", "").lower() != source.frequency:
        raise ValueError("Embedded metadata product or frequency does not match the requested source")
    dimensions = {}
    members = {}
    notes = []
    corrections = []
    section = None
    for row in rows[2:]:
        if not row or not row[0]:
            continue
        if row[0] == "Dimension ID":
            section = row[1]
        elif row[0] == "Correction ID":
            section = "corrections"
        elif row[0] in {"Symbol Legend", "Survey Code", "Subject Code"}:
            section = None
        elif row[0] in {"Footnote ID", "Note ID"}:
            section = "notes"
        elif len(row) >= 2 and row[0].isdigit():
            if section == "Dimension name" and len(row) >= 4:
                dimensions[int(row[0])] = row[1]
            elif section == "Member Name" and len(row) >= 8:
                dimension, label, code, member, parent = row[:5]
                members.setdefault(int(dimension), {})[member] = {"label": label, "code": code, "parent": parent}
            elif section == "corrections" and len(row) >= 3:
                corrections.append({"id": row[0], "date": row[1]})
            else:
                notes.append(row[1])
    return {"cube": cube, "dimensions": dimensions, "members": members, "notes": notes,
            "corrections": corrections}


def is_reported(numeric: pd.Series, statuses: pd.Series) -> pd.Series:
    return numeric.notna() & np.isfinite(numeric) & ~statuses.isin(UNUSABLE_STATUS)


def year_in_scope(period: str, frequency: str) -> bool:
    return "2010" <= period[:4] <= ("2026" if frequency == "monthly" else "2025")


def calendar_ok(period: str, frequency: str) -> bool:
    pattern = r"[12][0-9]{3}-(0[1-9]|1[0-2])" if frequency == "monthly" else r"[12][0-9]{3}"
    return re.fullmatch(pattern, period) is not None


def counts(values: pd.Series, numeric: pd.Series, reported: pd.Series, frame: pd.DataFrame) -> dict:
    status = frame["STATUS"]
    return {
        "rows": len(frame), "reported": int(reported.sum()), "blank": int(values.eq("").sum()),
        "suppressed": int(status.isin({"x", "X"}).sum()),
        "too_unreliable": int(status.isin({"f", "F"}).sum()),
        "unavailable_status": int(status.isin({"..", "...", "."}).sum()),
        "invalid_numbers": int((values.ne("") & ~np.isfinite(numeric)).sum()),
        "flagged_numeric": int((numeric.notna() & status.isin(UNUSABLE_STATUS)).sum()),
        "zero": int((reported & numeric.eq(0)).sum()),
        "preliminary": int(frame["SYMBOL"].isin({"p", "P"}).sum()),
        "revised": int(frame["SYMBOL"].isin({"r", "R"}).sum()),
        "terminated": int(frame["TERMINATED"].isin({"t", "T"}).sum()),
    }


def profile_specs(source: Source) -> dict:
    if source.pid in TRADE:
        flow = "Export" if source.pid == ANNUAL_TRADE else "Domestic export"
        partner = "Trading partner" if source.pid == ANNUAL_TRADE else "Principal trading partners"
        total = "All sections" if source.pid == ANNUAL_TRADE else "Total of all merchandise"
        return {"world_domestic_exports": {"Trade": flow, partner: WORLD, NAPCS: total},
                "us_domestic_exports": {"Trade": flow, partner: USA, NAPCS: total}}
    if source.pid == "12100129":
        base = {"Statistics": "Concentration ratio"}
        return {
            "product_hhi": {**base, "Canadian export concentration": "Product", "Partner countries": WORLD},
            "destination_hhi": {**base, "Canadian export concentration": "Destination market", "Partner countries": WORLD},
            "destination_hhi_ex_us": {**base, "Canadian export concentration": "Destination market", "Partner countries": EX_US},
        }
    if source.pid == "12100100":
        base = {"Industry": "Total industries", "Aggregation": "Summary level", "Country Code": USA}
        return {
            "us_value_added_exports": {**base, "Value added exports variable": "Value added exports"},
            "us_jobs_embodied": {**base, "Value added exports variable": "Total jobs embodied in exports"},
        }
    if source.pid == "36100711":
        return {
            "real_gdp": {"Prices": "Chained (2017) dollars", NAICS: "All industries [T001]"},
            "nominal_gdp": {"Prices": "Current dollars", NAICS: "All industries [T001]"},
        }
    if source.pid == "14100022":
        return {"lfs_employment": {"Labour force characteristics": "Employment", NAICS: "Total, all industries",
                                   "Gender": "Total - Gender", "Age group": "15 years and over"}}
    raise ValueError(f"Unsupported source {source.pid}")


def selection(frame: pd.DataFrame, filters: dict[str, str]) -> pd.Series:
    mask = pd.Series(True, index=frame.index)
    for column, label in filters.items():
        mask &= frame[column].eq(label)
    return mask


def duplicates(keys: pd.DataFrame, tail: pd.DataFrame | None) -> tuple[int, pd.DataFrame]:
    """Compare this chunk and the previous chunk's boundary period on the official sort order."""
    within = int(keys.duplicated().sum())
    last_period = keys["REF_DATE"].iloc[-1]
    latest = keys.loc[keys["REF_DATE"].eq(last_period)]
    if tail is None or tail["REF_DATE"].iloc[-1] != keys["REF_DATE"].iloc[0]:
        return within, latest
    first = keys.loc[keys["REF_DATE"].eq(keys["REF_DATE"].iloc[0])]
    overlap = len(first.drop_duplicates().merge(tail.drop_duplicates(), how="inner"))
    if keys["REF_DATE"].iloc[0] == last_period:
        latest = pd.concat([tail, latest], ignore_index=True).drop_duplicates()
    return within + overlap, latest


def display_label(member: dict, dimension: str) -> str:
    label = member["label"]
    code = member["code"]
    if code and dimension in {NAPCS, NAICS, "Industry"}:
        return f"{label} {code}"
    return label


def coordinates_match(series: pd.DataFrame, dimensions: list[str], members: dict) -> int:
    mismatches = 0
    names = {position: {code: display_label(member, dimensions[position - 1])
                        for code, member in options.items()}
             for position, options in members.items()}
    for labels in series[["COORDINATE", *dimensions]].itertuples(index=False, name=None):
        parts = labels[0].split(".")
        expected = tuple(names.get(position, {}).get(member)
                         for position, member in enumerate(parts, 1))
        mismatches += expected != labels[1:]
    return mismatches


def accumulate_geos(target: Counter, frame: pd.DataFrame, reported: pd.Series) -> None:
    if len(frame):
        counts_by_geo = frame[["REF_DATE", "GEO"]].assign(reported=reported).groupby(
            ["REF_DATE", "GEO"], observed=True, sort=False
        )["reported"].agg(["size", "sum"])
        for (period, geo), (rows, available) in zip(counts_by_geo.index, counts_by_geo.to_numpy()):
            target[(period, geo, "rows")] += int(rows)
            target[(period, geo, "reported")] += int(available)


def coverage_records(counter: Counter) -> list[dict]:
    return [
        {"period": period, "geo": geo, "rows": count, "reported": counter[(period, geo, "reported")]}
        for (period, geo, kind), count in sorted(counter.items()) if kind == "rows"
    ]


def trade_data(frame: pd.DataFrame, source: Source, numeric: pd.Series,
               reported: pd.Series, product_lookup: dict) -> pd.DataFrame:
    flow = "Export" if source.pid == ANNUAL_TRADE else "Domestic export"
    partner = "Trading partner" if source.pid == ANNUAL_TRADE else "Principal trading partners"
    rows = frame.loc[frame["Trade"].eq(flow) & frame["GEO"].isin(source.geos),
                     ["REF_DATE", "GEO", partner, NAPCS, "DECIMALS", "STATUS"]].copy()
    rows = rows.rename(columns={"REF_DATE": "period", "GEO": "geo", partner: "partner",
                                NAPCS: "product", "DECIMALS": "decimals", "STATUS": "status"})
    rows["product"] = rows["product"].map(product_lookup).astype("category")
    rows["value"] = numeric.loc[rows.index].where(reported.loc[rows.index])
    rows["decimals"] = pd.to_numeric(rows["decimals"], errors="coerce")
    return rows


def scan(root: Path, source: Source, item: dict, chunk_rows: int = CHUNK_ROWS) -> tuple[dict, pd.DataFrame | None]:
    path = root / item["path"]
    if sha256(path) != item["sha256"]:
        raise ValueError("Archive SHA-256 differs from acquisition manifest")
    all_counts = Counter()
    history_counts = Counter()
    recent_counts = Counter()
    statuses = Counter()
    units = Counter()
    detailed_flows = Counter()
    coverage = Counter()
    profile_counts = {}
    products = {}
    data = []
    benchmark = []
    seen_series = set()
    raw_periods = set()
    valid_geos = set()
    duplicates_vector = duplicates_coordinate = unordered = 0
    trade_unit_errors = trade_precision_errors = 0
    last_vector = last_coordinate = None
    prior_period = None
    with ZipFile(path) as archive:
        metadata = embedded_metadata(archive, source)
        dimensions = [metadata["dimensions"][pos] for pos in sorted(metadata["dimensions"])]
        if dimensions[0] == "Geography":
            dimensions[0] = "GEO"
        if not dimensions or dimensions[0] != "GEO":
            raise ValueError(f"GEO not first metadata dimension: {dimensions}")
        by_dimension = {name: metadata["members"][pos] for pos, name in enumerate(dimensions, 1)}
        labels = {name: {display_label(member, name) for member in members.values()}
                  for name, members in by_dimension.items()}
        profiles = profile_specs(source)
        for name, filters in profiles.items():
            for key, label in filters.items():
                if label not in labels[key]:
                    raise ValueError(f"Undocumented profile member in {name}: {key}={label}")
        profile_counts = {key: Counter() for key in profiles}
        if source.pid in TRADE:
            products = {
                display_label(member, NAPCS): (member["code"].strip("[]") or SECTION_TOTAL)
                for member in by_dimension[NAPCS].values()
            }
            if list(products.values()).count(SECTION_TOTAL) != 1 or len(set(products.values())) != len(products):
                raise ValueError("NAPCS section map is not one-to-one")
        usecols = [*STANDARD, *dimensions[1:]]
        with archive.open(source.data_member) as raw:
            header = pd.read_csv(raw, nrows=0, encoding="utf-8-sig")
        if set(header.columns) != set(usecols):
            raise ValueError(f"Unexpected CSV header: {list(header.columns)}")
        dtypes = {column: "category" for column in usecols if column != "VALUE"}
        dtypes["VALUE"] = str
        with archive.open(source.data_member) as raw:
            batches = pd.read_csv(raw, dtype=dtypes, keep_default_na=False, na_filter=False,
                                  chunksize=chunk_rows, encoding="utf-8-sig")
            for frame in batches:
                if frame.empty:
                    continue
                ref = frame["REF_DATE"].astype(str)
                raw_periods.update(ref.unique())
                if (not ref.is_monotonic_increasing
                        or (prior_period is not None and ref.iloc[0] < prior_period)):
                    unordered += 1
                prior_period = ref.iloc[-1]
                for column, tail in (("VECTOR", last_vector), ("COORDINATE", last_coordinate)):
                    count, trailing = duplicates(frame[["REF_DATE", column]], tail)
                    if column == "VECTOR":
                        duplicates_vector += count
                        last_vector = trailing
                    else:
                        duplicates_coordinate += count
                        last_coordinate = trailing
                series_fields = ["VECTOR", "COORDINATE", *dimensions]
                seen_series.update(frame[series_fields].drop_duplicates().itertuples(index=False, name=None))
                numeric = pd.to_numeric(frame["VALUE"], errors="coerce")
                reported = is_reported(numeric, frame["STATUS"])
                valid_geos.update(frame.loc[reported, "GEO"].unique())
                all_counts.update(counts(frame["VALUE"], numeric, reported, frame))
                history = ref.str.slice(stop=4).between("2010", "2025")
                recent = ref.str.slice(stop=4).between("2025", "2026") if source.frequency == "monthly" else pd.Series(False, index=frame.index)
                for mask, target in ((history, history_counts), (recent, recent_counts)):
                    subset = frame.loc[mask]
                    if not subset.empty:
                        target.update(counts(subset["VALUE"], numeric.loc[mask], reported.loc[mask], subset))
                scoped = history | recent
                sl = frame.loc[scoped]
                good = reported.loc[scoped]
                val = numeric.loc[scoped]
                if sl.empty:
                    continue
                statuses.update({str(k): int(v) for k, v in sl["STATUS"].value_counts().items() if v})
                unit_fields = ["UOM", "SCALAR_FACTOR", "UOM_ID", "SCALAR_ID"]
                units.update({k: int(v) for k, v in sl.loc[good, unit_fields].value_counts().items() if v})
                accumulate_geos(coverage, sl, good)
                for name, profile in profiles.items():
                    mask = selection(sl, profile)
                    accumulate_geos(profile_counts[name], sl.loc[mask], good.loc[mask])
                if source.pid in TRADE:
                    valid_units = (sl["UOM"].eq("Dollars") & sl["UOM_ID"].eq("81")
                                   & sl["SCALAR_FACTOR"].eq("thousands") & sl["SCALAR_ID"].eq("3"))
                    trade_unit_errors += int((good & ~valid_units).sum())
                    decimals = pd.to_numeric(sl["DECIMALS"], errors="coerce")
                    trade_precision_errors += int((good & ~decimals.between(0, 12)).sum())
                    flow_summary = sl.assign(reported=good, canada=sl["GEO"].eq("Canada")).groupby(
                        ["Trade", "canada"], observed=True
                    )["reported"].agg(["size", "sum"])
                    for (flow, canada), (rows, available) in zip(flow_summary.index, flow_summary.to_numpy()):
                        detailed_flows[(flow, "Canada" if canada else "Subnational", "rows")] += int(rows)
                        detailed_flows[(flow, "Canada" if canada else "Subnational", "reported")] += int(available)
                    result = trade_data(sl, source, val, good, products)
                    if not result.empty:
                        data.append(result)
                if source.pid == "12100129":
                    mask = good & sl["GEO"].isin(source.geos) & sl["Statistics"].eq("Concentration ratio") & sl["Canadian export concentration"].eq("Destination market")
                    for period, geo, partner, value, decimals in zip(
                        sl.loc[mask, "REF_DATE"], sl.loc[mask, "GEO"], sl.loc[mask, "Partner countries"],
                        val[mask], sl.loc[mask, "DECIMALS"]
                    ):
                        benchmark.append({"period": period, "geo": geo, "partner": partner, "value": float(value),
                                          "decimals": int(decimals)})
    if not raw_periods:
        raise ValueError("No observation rows")
    series_frame = pd.DataFrame(seen_series, columns=["VECTOR", "COORDINATE", *dimensions])
    classification_errors = coordinates_match(series_frame, dimensions, metadata["members"])
    vector_conflicts = int(series_frame["VECTOR"].duplicated().sum())
    coordinate_conflicts = int(series_frame["COORDINATE"].duplicated().sum())
    label_conflicts = int(series_frame[dimensions].duplicated().sum())
    raw_periods = sorted(raw_periods)
    invalid_periods = [period for period in raw_periods if not calendar_ok(period, source.frequency)]
    archive_bounds = [metadata["cube"][key] for key in ("Start Reference Period", "End Reference Period")]
    wds = item.get("publisher_metadata", {})
    wds_bounds = [wds.get(key) for key in ("cubeStartDate", "cubeEndDate")]
    release_time = wds.get("releaseTime")
    archive_modified = item.get("headers", {}).get("Last-Modified")
    release_date_match = None
    if release_time and archive_modified:
        published_date = datetime.fromisoformat(release_time).date()
        modified_date = parsedate_to_datetime(archive_modified).astimezone(ZoneInfo("America/Toronto")).date()
        release_date_match = published_date == modified_date
    display_length = 7 if source.frequency == "monthly" else 4
    metadata_matches = [bound[:display_length] for bound in archive_bounds] == [raw_periods[0], raw_periods[-1]]
    eligible_periods = [p for p in raw_periods if year_in_scope(p, source.frequency)]
    expected_start = max("2010-01" if source.frequency == "monthly" else "2010",
                         archive_bounds[0][:display_length])
    expected_end = min("2026-12" if source.frequency == "monthly" else "2025",
                       archive_bounds[-1][:display_length])
    expected_periods = set(pd.period_range(expected_start, expected_end,
                                          freq="M" if source.frequency == "monthly" else "Y").astype(str))
    historical_periods = set(pd.period_range(
        "2010-01" if source.frequency == "monthly" else "2010",
        "2025-12" if source.frequency == "monthly" else "2025",
        freq="M" if source.frequency == "monthly" else "Y",
    ).astype(str))
    issues = {
        "invalid_periods": invalid_periods, "missing_expected_periods": sorted(expected_periods - set(eligible_periods)),
        "out_of_order_chunks": unordered, "duplicate_period_vector_excess": duplicates_vector,
        "duplicate_period_coordinate_excess": duplicates_coordinate, "vector_identity_conflicts": vector_conflicts,
        "coordinate_identity_conflicts": coordinate_conflicts, "dimension_label_identity_conflicts": label_conflicts,
        "coordinate_metadata_mismatches": classification_errors, "trade_unit_mismatches": trade_unit_errors,
        "trade_precision_mismatches": trade_precision_errors,
        "unexpected_unit_combinations": [list(unit) for unit in sorted(set(units) - UNIT_TYPES[source.pid])],
        "archive_bounds_match_rows": metadata_matches,
        "wds_bounds_match_archive": wds_bounds == archive_bounds if all(wds_bounds) else None,
        "wds_release_date_matches_http_modified_local": release_date_match,
        "expected_geos_without_numeric_rows": sorted(set(source.geos) - valid_geos),
        "invalid_numbers": all_counts["invalid_numbers"], "numeric_values_with_unusable_status": all_counts["flagged_numeric"],
    }
    return {
        "pid": source.pid, "table": source.table, "status": "validated", "classification": source.classification,
        "dimensions": dimensions, "raw_first": raw_periods[0], "raw_last": raw_periods[-1],
        "scope_first": eligible_periods[0] if eligible_periods else None,
        "scope_last": eligible_periods[-1] if eligible_periods else None,
        "history_years_with_numeric_values": sorted({period[:4] for (period, _, field), count in coverage.items()
                                                       if field == "reported" and count and period[:4] <= "2025"}),
        "archive_metadata": metadata["cube"], "corrections": metadata["corrections"],
        "classification_notes": [n for n in metadata["notes"] if "2022" in n and ("NAICS" in n or "NAPCS" in n)],
        "historical_target_periods_outside_cube": sorted(historical_periods - expected_periods),
        "naics_members": [{"code": member["code"].strip("[]"), "label": member["label"]}
                          for member in by_dimension.get(NAICS, {}).values() if member["code"]],
        "series": len(series_frame), "all": dict(all_counts), "history": dict(history_counts),
        "recent": dict(recent_counts), "statuses": dict(statuses),
        "units": [dict(zip(("unit", "scalar", "unit_id", "scalar_id", "rows"), (*key, val)))
                  for key, val in sorted(units.items())],
        "geos": coverage_records(coverage),
        "profiles": {key: coverage_records(val) for key, val in profile_counts.items()},
        "profile_definitions": profiles,
        "partner_members": sorted(labels[("Trading partner" if source.pid == ANNUAL_TRADE else "Principal trading partners")])
        if source.pid in TRADE else [],
        "products": products, "issues": issues, "benchmark": benchmark,
        "flows": [
            {"flow": flow, "geo": geo, "rows": rows, "reported": detailed_flows[(flow, geo, "reported")]}
            for (flow, geo, kind), rows in sorted(detailed_flows.items()) if kind == "rows"
        ],
    }, pd.concat(data, ignore_index=True) if data else None
