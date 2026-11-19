"""Provenance, eligibility and panel preparation for preregistered Design C."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .acquire import sha256
from .phase3_data import VINTAGE, current_trade
from .phase3_indicators import exposure
from .sources import PROVINCES
from .trade import HHI_UNALLOCATED, KEY, domestic_checks
from .validate import UNUSABLE_STATUS, USA, WORLD

PRODUCTS = tuple(f"C{code}" for code in (*range(11, 20), 21, 22))
STARTS = tuple(range(2011, 2025))
FLOOR_CAD = 1_000_000
CELLS = ["geo", "product", "t"]
SLOPES = ["hhi_ex_us", "log_lag_exports", "lag_us_share"]
FIXED_EFFECTS = [["geo", "product"], ["product", "t"], ["geo", "t"]]
FE_NAMES = ["province_product", "product_year", "province_year"]


def checked(path, expected):
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"Hash mismatch: {path}")
    return actual


def preregistration(root):
    lock = json.loads((root / "data/phase4b/preregistration_lock.json").read_text())
    checked(root / lock["file"], lock["sha256"])
    return lock


def load_years(root: Path):
    phase3_path = root / "data/phase3/phase3_summary.json"
    phase4a_path = root / "data/phase4a/manifest.json"
    phase3 = json.loads(phase3_path.read_text())
    phase4a = json.loads(phase4a_path.read_text())
    acquisition_path = root / f"data/provenance/acquisition-{VINTAGE}.json"
    checked(acquisition_path, phase3["phase2_manifest_sha256"])
    acquisition = json.loads(acquisition_path.read_text())
    source = next(row for row in acquisition["sources"] if row["pid"] == "12100173")
    if source["status"] != "downloaded" or phase4a["source_vintage"] != VINTAGE:
        raise ValueError("Phase 4B requires the approved acquisition vintage")

    published_path = root / "data/phase3/annual_exposure.csv"
    prior_coverage = root / "data/phase4a/design_C_coverage.csv"
    checked(root / source["path"], source["sha256"])
    checked(published_path, phase3["files"]["annual_exposure.csv"]["sha256"])
    checked(prior_coverage, phase4a["files"]["design_C_coverage.csv"]["sha256"])
    hashes = {str(p.relative_to(root)): sha256(p) for p in
              [phase3_path, phase4a_path, acquisition_path, root / source["path"],
               published_path, prior_coverage]}
    raw, metadata = current_trade(root, {"12100173": source}, "12100173")
    raw = raw.loc[raw.geo.isin(PROVINCES) & raw["product"].isin(PRODUCTS)].copy()
    n_partners = len(metadata["partner_members"]) - 1
    summary, controls = domestic_checks(raw, True, n_partners)
    years = exposure(controls)
    original = pd.read_csv(published_path, dtype={"period": str})
    original = original.loc[original.geo.isin(PROVINCES) & original["product"].isin(PRODUCTS)]
    pd.testing.assert_frame_equal(
        years, original.reset_index(drop=True), check_dtype=False, rtol=1e-12, atol=1e-10,
    )

    index = pd.MultiIndex.from_product([map(str, range(2010, 2026)), PROVINCES, PRODUCTS], names=KEY)
    n_year_cells = len(index)
    if len(years) != n_year_cells or len(raw) != n_year_cells * (n_partners + 1):
        raise ValueError("Incomplete expected province–product–year trade grid")
    partners = raw.loc[~raw.partner.isin({WORLD, USA, *HHI_UNALLOCATED})].copy()
    partners["rank"] = partners.groupby(KEY, sort=False).value.rank(method="first", ascending=False)
    partners["top3"] = partners.value.where(partners["rank"].le(3))
    partners["positive"] = partners.value.gt(0)
    concentrations = partners.groupby(KEY, sort=False, observed=True).agg(
        top1_value=("value", "max"), top3_value=("top3", "sum"), positive_non_us_partners=("positive", "sum"),
    ).reset_index()
    years = years.merge(concentrations, on=KEY, validate="one_to_one")
    denominator = years.non_us_cad_thousands.where(years.destination_hhi_ex_us.notna())
    for name in ("top1", "top3"):
        share = years.pop(f"{name}_value").div(denominator)
        # A reported component can exceed the rounded world-minus-US denominator.
        too_large = share.gt(1) & denominator.mul(share.sub(1)).gt(years.destination_tolerance_cad_thousands + 1e-7)
        years[f"{name}_non_us"] = share.where(~too_large).clip(upper=1)
    years["positive_non_us_partners"] = years.positive_non_us_partners.where(denominator.notna())

    world_us = raw.loc[raw.partner.isin({WORLD, USA})].pivot(index=KEY, columns="partner", values="status")
    world_us = world_us.rename(columns={WORLD: "world_status", USA: "us_status"}).reset_index()
    status_rows = raw.assign(
        is_missing=raw.value.isna(),
        is_zero=raw.value.eq(0),
        is_negative=raw.value.lt(0),
        is_suppressed=raw.status.eq("x"),
        is_unusable=raw.status.isin(UNUSABLE_STATUS),
    )
    partner_qc = status_rows.loc[~status_rows.partner.eq(WORLD)].groupby(KEY, sort=False).agg(
        partner_rows=("partner", "size"), partner_missing=("is_missing", "sum"),
        partner_zeros=("is_zero", "sum"), partner_negative=("is_negative", "sum"),
        partner_suppressed=("is_suppressed", "sum"), partner_flagged_unusable=("is_unusable", "sum"),
    ).reset_index()
    years = years.merge(world_us, on=KEY, validate="one_to_one").merge(partner_qc, on=KEY, validate="one_to_one")
    status = status_rows.assign(scope=np.select(
        [status_rows.partner.eq(WORLD), status_rows.partner.eq(USA)], ["world", "US"], default="other partners",
    )).groupby(["scope", "status"], dropna=False).agg(
        rows=("value", "size"), missing=("is_missing", "sum"), zero=("is_zero", "sum"),
        negative=("is_negative", "sum"), suppressed=("is_suppressed", "sum"), unusable=("is_unusable", "sum"),
    ).reset_index()
    summary["raw_trade_rows"] = len(raw)
    summary["source_year_cells"] = len(years)
    summary["expected_detail_partners"] = n_partners
    years["period"] = years.period.astype(int)
    return years, status, summary, hashes, pd.read_csv(prior_coverage)


def panel_grid(years, horizon=1):
    starts = STARTS if horizon == 1 else (2011, 2014, 2017, 2020, 2023)
    d = pd.MultiIndex.from_product([PROVINCES, PRODUCTS, starts], names=CELLS).to_frame(index=False)
    d = d.assign(lag_year=d.t-1, start_year=d.t, end_year=d.t+horizon)
    base = years.rename(columns={"non_us_cad_thousands": "exports"})
    trade_fields = ["exports", "world_cad_thousands", "us_cad_thousands", "world_status", "us_status"]
    lag_fields = [
        *trade_fields, "destination_hhi_ex_us", "destination_hhi", "us_share", "top1_non_us", "top3_non_us",
        "positive_non_us_partners", "destination_reconciled", "destination_gap_cad_thousands",
        "destination_tolerance_cad_thousands", "unallocated", "partner_missing", "partner_suppressed",
        "partner_negative", "partner_flagged_unusable", "partner_rows",
    ]
    for key, fields in (("lag", lag_fields), ("start", trade_fields), ("end", trade_fields)):
        rows = base[["geo", "product", "period", *fields]].rename(columns={
            "period": f"{key}_year", **{col: f"{key}_{col}" for col in fields},
        })
        d = d.merge(rows, on=["geo", "product", f"{key}_year"], how="left", validate="one_to_one")
        for col in ("exports", "us_cad_thousands", "world_cad_thousands"):
            d[f"{key}_{col}"] = d[f"{key}_{col}"].where(d[f"{key}_{col}"].ge(0))
    d["hhi_ex_us"] = d.lag_destination_hhi_ex_us
    d["lag_exports_cad"] = d.lag_exports * 1000
    d["lag_us_share"] = d.lag_us_share.where(d.lag_us_share.between(0, 1))
    d["log_lag_exports"] = np.log(d.lag_exports_cad.where(d.lag_exports_cad.gt(0)))
    d["lagged_hhi_available"] = d.hhi_ex_us.between(0, 1)
    for key in ("start", "end"):
        d[f"{key}_exports_positive"] = d[f"{key}_exports"].gt(0)
    d["prior_eligible"] = d.lagged_hhi_available & d.start_exports_positive & d.end_exports_positive
    d["controls_available"] = d.log_lag_exports.notna() & d.lag_us_share.notna()
    d["signed_growth"] = (np.log(d.end_exports.where(d.end_exports_positive)) -
                          np.log(d.start_exports.where(d.start_exports_positive))) / horizon
    d["absolute_growth"] = d.signed_growth.abs()
    d["downside"] = (-d.signed_growth).clip(lower=0)
    d["end_zero"] = d.end_exports.eq(0).where(d.end_exports.notna())
    return d.sort_values(CELLS).reset_index(drop=True)


def drop_singletons(rows):
    kept = rows.copy()
    removed = []
    iteration = 1
    while not kept.empty:
        flags = pd.DataFrame({
            name: kept.groupby(group, observed=True).t.transform("size").eq(1)
            for name, group in zip(FE_NAMES, FIXED_EFFECTS)
        })
        singleton = flags.any(axis=1)
        if not singleton.any():
            break
        trace = flags.loc[singleton].apply(lambda row: "|".join(row.index[row]), axis=1)
        removed.append(pd.DataFrame({"singleton_iteration": iteration, "singleton_fixed_effects": trace}))
        kept = kept.loc[~singleton]
        iteration += 1
    detail = pd.concat(removed) if removed else pd.DataFrame(columns=["singleton_iteration", "singleton_fixed_effects"])
    return kept.copy(), detail


def ledger_for(grid, floor=FLOOR_CAD):
    flags = pd.DataFrame({
        "lag_HHI_unavailable": ~grid.lagged_hhi_available,
        "lag_controls_unavailable": ~grid.controls_available,
        "lag_below_portfolio_floor": grid.lag_exports_cad.lt(floor),
        "start_unavailable": grid.start_exports.isna(),
        "start_zero": grid.start_exports.eq(0),
        "end_unavailable": grid.end_exports.isna(),
        "end_zero": grid.end_exports.eq(0),
    }, index=grid.index)
    base = ~flags.any(axis=1)
    kept, removed = drop_singletons(grid.loc[base])
    ledger = grid.join(flags.add_prefix("exclude_")).join(removed)
    ledger["included_main"] = ledger.index.isin(kept.index)
    reasons = flags.apply(lambda row: "|".join(row.index[row]), axis=1)
    ledger["exclusion_reason"] = reasons.mask(ledger.singleton_iteration.notna(), "absorbed_FE_singleton")
    return kept, ledger


def prepare(root):
    years, statuses, summary, hashes, earlier = load_years(root)
    grid = panel_grid(years)
    verify = grid[CELLS + ["lagged_hhi_available", "start_exports_positive", "end_exports_positive",
                          "prior_eligible"]].rename(columns={"prior_eligible": "usable"})
    pd.testing.assert_frame_equal(verify, earlier.sort_values(CELLS).reset_index(drop=True), check_dtype=False)
    primary, ledger = ledger_for(grid)
    eligible = grid.loc[grid.prior_eligible]
    summary.update({
        "full_grid": len(grid), "phase4a_eligible": len(eligible),
        "eligible_and_controls": int((grid.prior_eligible & grid.controls_available).sum()),
        "floor_eligible_before_singletons": len(primary) + int(ledger.singleton_iteration.notna().sum()),
        "primary_n": len(primary),
        "main_groups": primary.groupby(CELLS[:2]).ngroups,
        "main_complete_groups": int(primary.groupby(CELLS[:2]).size().eq(len(STARTS)).sum()),
        "pre_estimation_lagged_cad_quantiles": {
            f"q{100*p:g}": float(eligible.lag_exports_cad.quantile(p)) for p in (0, .01, .025, .05, .5, 1)
        },
        "exclusion_flags": {key: int(ledger[key].sum()) for key in ledger if key.startswith("exclude_")},
        "singleton_rows": int(ledger.singleton_iteration.notna().sum()),
        "any_non_us_zero_year_cells": int(years.non_us_cad_thousands.eq(0).sum()),
        "unavailable_non_us_year_cells": int(years.non_us_cad_thousands.isna().sum()),
    })
    return years, statuses, summary, hashes, grid, primary, ledger


def selection_check(grid):
    cohort = grid.loc[grid.lagged_hhi_available & grid.controls_available &
                      grid.lag_exports_cad.ge(FLOOR_CAD) & grid.start_exports_positive & grid.end_exports.notna()]
    exits = cohort.loc[cohort.end_exports.eq(0)]
    return cohort, {"rows_with_known_end": len(cohort), "zero_ends": len(exits), "provinces_with_zero_end": exits.geo.nunique()}
