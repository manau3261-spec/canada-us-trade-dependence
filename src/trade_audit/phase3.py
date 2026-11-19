"""Rebuild the phase 3 datasets and figures from the pinned official vintage."""
import argparse
from pathlib import Path

import pandas as pd

from .acquire import sha256, write_json
from .phase3_data import (VINTAGE, current_trade, load_manifest, read_gdp, read_lfs,
                          read_published_hhi, read_value_added)
from .phase3_indicators import (benchmark_hhi, decompose, demand_benchmark, exposure,
                                export_intensity, geography_check, matched_ytd, non_us_portfolio,
                                panel_coverage)
from .phase3_reconcile import reconcile
from .trade import domestic_checks

DATA = Path("data/phase3")
FIGURES = Path("figures/phase3")


def build_data(root: Path) -> dict:
    entries = load_manifest(root)
    print("Reading domestic exports", flush=True)
    a, meta_a = current_trade(root, entries, "12100173")
    m, meta_m = current_trade(root, entries, "12100175")
    recent = m.loc[m["period"].str.startswith(("2025", "2026"))]
    annual_checks, annual_rows = domestic_checks(a, True, len(meta_a["partner_members"]) - 1)
    monthly_checks, monthly_rows = domestic_checks(recent, False, len(meta_m["partner_members"]) - 1)
    annual, monthly = exposure(annual_rows), exposure(monthly_rows)
    print("Reconciling 2020 with older official vintages", flush=True)
    files, reconciliation = reconcile(root, a, m)
    print("Checking GDP, LFS and value-added outcomes", flush=True)
    gdp = read_gdp(root, entries)
    lfs = read_lfs(root, entries)
    io = read_value_added(root, entries)
    pub = read_published_hhi(root, entries)
    files.update({
        "annual_exposure.csv": annual,
        "monthly_exposure.csv": monthly,
        "matched_monthly_ytd.csv": matched_ytd(monthly),
        "provincial_export_intensity.csv": export_intensity(annual, gdp),
        "national_non_us_destinations.csv": non_us_portfolio(a, annual),
        "destination_hhi_benchmark.csv": benchmark_hhi(annual, pub),
        "geographic_reconciliation.csv": pd.concat([geography_check(a).assign(frequency="annual"),
                                                   geography_check(recent).assign(frequency="monthly")],
                                                  ignore_index=True),
        "national_exposure_decomposition.csv": pd.concat(
            [decompose(annual, "2010", "2025"), decompose(annual, "2024", "2025")], ignore_index=True
        ),
        "panel_coverage.csv": panel_coverage(gdp, lfs, io),
        "value_added_and_jobs_benchmarks.csv": demand_benchmark(io),
    })
    summary = {
        "pinned_vintage": VINTAGE,
        "phase2_manifest_sha256": sha256(root / f"data/provenance/acquisition-{VINTAGE}.json"),
        "supplement_manifest_sha256": sha256(root / "data/provenance/phase3-supplementary-sources.json"),
        "trade_checks": {"annual": annual_checks, "monthly_recent": monthly_checks},
        "reconciliation_2020": reconciliation,
        "files": {},
    }
    output = root / DATA
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in sorted(files.items()):
        path = output / name
        frame.to_csv(path, index=False)
        summary["files"][name] = {"rows": len(frame), "sha256": sha256(path)}
    write_json(output / "phase3_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--data-only", action="store_true")
    modes.add_argument("--charts-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if not args.charts_only:
        build_data(root)
    if not args.data_only:
        from .phase3_figures import render
        write_json(root / FIGURES / "figure_manifest.json", render(root / DATA, root / FIGURES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
