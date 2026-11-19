"""Targeted readers for the phase 2 acquisition vintage."""
import json
import re
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from .acquire import sha256
from .sources import ALL_GEOS, NAICS, NAPCS, SOURCES
from .validate import ANNUAL_TRADE, MONTHLY_TRADE, embedded_metadata, is_reported, trade_data

VINTAGE = "20261119T001720Z-cacfc394"
SOURCE_INDEX = {source.pid: source for source in SOURCES}
FIRST_YEAR = "2010"
LAST_YEAR = "2025"


def load_manifest(root: Path) -> dict:
    path = root / f"data/provenance/acquisition-{VINTAGE}.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest["run_id"] != VINTAGE:
        raise ValueError("Unexpected Statistics Canada vintage")
    entries = {item["pid"]: item for item in manifest["sources"] if item["status"] == "downloaded"}
    if set(entries) != set(SOURCE_INDEX):
        raise ValueError("Complete phase 2 vintage is required")
    for pid, item in entries.items():
        if sha256(root / item["path"]) != item["sha256"]:
            raise ValueError(f"Source archive hash mismatch for {pid}")
    return entries


def read_slice(path: Path, member: str, columns: list[str], selectors: dict[str, set[str]],
               year_min: str, year_max: str, wanted_years: set[str] | None = None) -> pd.DataFrame:
    parts = []
    dtypes = {col: "category" for col in columns if col != "VALUE"}
    if "VALUE" in columns:
        dtypes["VALUE"] = str
    with ZipFile(path) as archive, archive.open(member) as raw:
        batches = pd.read_csv(raw, usecols=columns, dtype=dtypes, keep_default_na=False,
                              na_filter=False, chunksize=300_000, encoding="utf-8-sig")
        for chunk in batches:
            year = chunk["REF_DATE"].astype(str).str[:4]
            mask = year.between(year_min, year_max)
            if wanted_years is not None:
                mask &= year.isin(wanted_years)
            for column, values in selectors.items():
                mask &= chunk[column].isin(values)
            if mask.any():
                parts.append(chunk.loc[mask])
            if year.iloc[-1] > year_max:
                break
    if not parts:
        return pd.DataFrame(columns=columns)
    frame = pd.concat(parts, ignore_index=True)
    for col in dtypes:
        frame[col] = frame[col].astype(str)
    if "VALUE" in columns:
        number = pd.to_numeric(frame["VALUE"], errors="coerce")
        frame["VALUE"] = number.where(is_reported(number, frame["STATUS"]))
    return frame


def codes_for_products(values: pd.Series) -> dict[str, str]:
    labels = set(values)
    result = {}
    for label in labels:
        match = re.search(r"\[([A-Z][0-9]+)\]$", label)
        if match:
            result[label] = match.group(1)
        elif label in {"All sections", "Total of all merchandise"}:
            result[label] = "TOTAL"
        else:
            raise ValueError(f"Unrecognized merchandise product label {label}")
    return result


def current_trade(root: Path, entries: dict, pid: str) -> tuple[pd.DataFrame, dict]:
    source = SOURCE_INDEX[pid]
    annual = pid == ANNUAL_TRADE
    partner = "Trading partner" if annual else "Principal trading partners"
    flow = "Export" if annual else "Domestic export"
    columns = ["REF_DATE", "GEO", partner, NAPCS, "Trade", "VALUE", "DECIMALS", "STATUS"]
    frame = read_slice(root / entries[pid]["path"], source.data_member, columns,
                       {"GEO": set(ALL_GEOS), "Trade": {flow}},
                       FIRST_YEAR if annual else "2020", LAST_YEAR if annual else "2026",
                       None if annual else {"2020", "2025", "2026"})
    labels = codes_for_products(frame[NAPCS])
    data = trade_data(frame, source, frame["VALUE"], frame["VALUE"].notna(), labels)
    if data.duplicated(["period", "geo", "partner", "product"]).any():
        raise ValueError(f"Duplicate trade observation in {source.table}")
    data["product"] = data["product"].astype(str)
    with ZipFile(root / entries[pid]["path"]) as archive:
        metadata = embedded_metadata(archive, source)
    dim = next(d for d, name in metadata["dimensions"].items() if name == partner)
    return data, {"partner_members": list(metadata["members"][dim].values()), "products": labels}


def read_gdp(root: Path, entries: dict) -> pd.DataFrame:
    pid = "36100711"
    source = SOURCE_INDEX[pid]
    return read_slice(root / entries[pid]["path"], source.data_member,
                      ["REF_DATE", "GEO", NAICS, "Prices", "VALUE", "STATUS"],
                      {"Prices": {"Current dollars", "Chained (2017) dollars"}},
                      FIRST_YEAR, LAST_YEAR)


def read_lfs(root: Path, entries: dict) -> pd.DataFrame:
    pid = "14100022"
    source = SOURCE_INDEX[pid]
    return read_slice(root / entries[pid]["path"], source.data_member,
                      ["REF_DATE", "GEO", NAICS, "Labour force characteristics", "Gender",
                       "Age group", "VALUE", "STATUS"],
                      {"Labour force characteristics": {"Employment"}, "Gender": {"Total - Gender"},
                       "Age group": {"15 years and over"}},
                      FIRST_YEAR, "2026")


IO_VARIABLE = "Value added exports variable"
IO_TOTAL = "Total of all countries"
IO_DEMAND = {"Value added due to foreign demand", "Jobs due to foreign demand"}


def read_value_added(root: Path, entries: dict) -> pd.DataFrame:
    pid = "12100100"
    source = SOURCE_INDEX[pid]
    return read_slice(root / entries[pid]["path"], source.data_member,
                      ["REF_DATE", "GEO", "Country Code", IO_VARIABLE, "Industry", "Aggregation",
                       "VALUE", "STATUS", "UOM_ID", "SCALAR_ID"],
                      {"Aggregation": {"Summary level"}, "Country Code": {IO_TOTAL, "United States"},
                       "GEO": set(ALL_GEOS),
                       IO_VARIABLE: IO_DEMAND | {"Value added", "Jobs", "Value added exports",
                                                 "Total jobs embodied in exports"}},
                      FIRST_YEAR, LAST_YEAR)


def read_published_hhi(root: Path, entries: dict) -> pd.DataFrame:
    pid = "12100129"
    source = SOURCE_INDEX[pid]
    return read_slice(root / entries[pid]["path"], source.data_member,
                      ["REF_DATE", "GEO", "Partner countries", "Canadian export concentration",
                       "Statistics", "VALUE", "STATUS", "DECIMALS"],
                      {"Canadian export concentration": {"Destination market"},
                       "Statistics": {"Concentration ratio"}, "GEO": set(ALL_GEOS)},
                      FIRST_YEAR, LAST_YEAR)
