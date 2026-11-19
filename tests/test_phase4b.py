"""Regression tests grounded in the pinned official observations."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from trade_audit.acquire import sha256
from trade_audit.phase4b import execute, robustness_specs
from trade_audit.phase4b_data import CELLS, ledger_for, panel_grid, prepare, preregistration, selection_check
from trade_audit.phase4b_figures import render
from trade_audit.phase4b_inference import (
    RestrictedWild, fit_model, project, validate_against_explicit, webb_weights,
)
from trade_audit.phase4b_pilot import classify, current_us_lines

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def data():
    return prepare(ROOT)


def test_preregistered_hash_and_vintage(data):
    lock = preregistration(ROOT)
    assert sha256(ROOT/lock["file"]) == lock["sha256"]
    assert data[2]["raw_trade_rows"] == 455840
    assert data[1].missing.sum() == data[1].suppressed.sum() == 0
    assert data[2]["destination"]["within_rounding"] == 1760
    for name, digest in data[3].items():
        assert sha256(ROOT/name) == digest


def test_one_and_two_year_alignment_and_values(data):
    years, _, _, _, grid, main, _ = data
    assert np.array_equal(grid.lag_year, grid.t-1)
    assert np.array_equal(grid.start_year, grid.t)
    assert np.array_equal(grid.end_year, grid.t+1)
    assert set(grid.t) == set(range(2011, 2025))
    assert not grid.duplicated(CELLS).any()
    reference = years.set_index(["geo", "product", "period"])
    lookup = reference.loc[list(zip(main.geo, main["product"], main.lag_year))]
    np.testing.assert_allclose(main.hhi_ex_us, lookup.destination_hhi_ex_us)
    np.testing.assert_allclose(main.lag_us_share, lookup.us_cad_thousands/lookup.world_cad_thousands)
    np.testing.assert_allclose(main.log_lag_exports, np.log(lookup.non_us_cad_thousands * 1000))
    growth = np.log(main.end_exports / main.start_exports)
    np.testing.assert_allclose(main.signed_growth, growth, atol=1e-13)
    np.testing.assert_allclose(main.absolute_growth, abs(growth), atol=1e-13)
    np.testing.assert_allclose(main.downside, np.maximum(0, -growth), atol=1e-13)
    two = panel_grid(years, horizon=2)
    assert set(two.t) == {2011, 2014, 2017, 2020, 2023}
    assert set(two.t).isdisjoint(two.end_year)
    assert np.array_equal(two.end_year, two.t+2)


def test_exclusions_and_balanced_eligibility(data):
    _, _, summary, _, grid, main, ledger = data
    assert (summary["full_grid"], summary["phase4a_eligible"], len(main)) == (1540, 1513, 1454)
    assert main.lag_exports_cad.ge(1_000_000).all()
    assert ledger.loc[ledger.included_main, "exclusion_reason"].eq("").all()
    assert ledger.loc[~ledger.included_main, "exclusion_reason"].str.len().gt(0).all()
    assert ledger.loc[ledger.exclude_end_zero, "end_exports"].eq(0).all()
    positive, trace = ledger_for(grid, floor=0)
    assert len(positive) == 1512
    row = trace.loc[trace.singleton_iteration.notna()].iloc[0]
    assert (row.geo, row["product"]) == ("Prince Edward Island", "C12")
    cohort, selection = selection_check(grid)
    assert len(cohort) == len(main)
    assert selection["zero_ends"] == 0
    spec = {row[0]: row for row in robustness_specs(data[0], grid, main)}
    assert len(spec["C_balanced"][1]) == 98*14
    assert set(spec["J_odd"][1].t).isdisjoint(spec["J_odd"][1].end_year)
    assert set(spec["J_even"][1].t).isdisjoint(spec["J_even"][1].end_year)


def test_fixed_effect_rank_and_covariance_agreement(data):
    main = data[5]
    design = project(main, "hhi_ex_us", required_clusters=10)
    assert design.fixed_levels == {"province_product":108, "product_year":154, "province_year":140}
    assert np.linalg.matrix_rank(np.column_stack([design.fe, design.weighted_x])) == design.rank == 371
    assert np.linalg.norm(design.q.T @ design.xr, ord=np.inf) < 1e-10
    fx, y, inference, _ = fit_model(main, design, "absolute_growth", "hhi_ex_us")
    reference = validate_against_explicit(design, fx, y, inference)
    assert reference["max_coefficient_error"] < 1e-9


def test_webb_restricted_draws_match_literal_refits(data):
    main = data[5]
    design = project(main, "hhi_ex_us", required_clusters=10)
    fx, y, _, _ = fit_model(main, design, "absolute_growth", "hhi_ex_us")
    weights = webb_weights(999, 10, seed=20261118)
    assert len(set(weights.flatten())) == 6
    np.testing.assert_array_equal(weights, webb_weights(999, 10, seed=20261118))
    wild = RestrictedWild(design, fx, weights)
    assert wild.validate_direct(y)["max_t_error"] < 1e-9
    assert wild.p_value(wild.beta) == 1
    assert wild.p_value(0) == RestrictedWild(design, fx, weights).p_value(0)


def test_pipeline_tables_robustness_and_figures_replay(tmp_path):
    result = execute(ROOT, tmp_path, charts=False)
    saved = ROOT/"data/phase4b"
    for name in ("design_C_model_input.csv", "sample_exclusion_ledger.csv", "robustness_membership.csv"):
        assert sha256(tmp_path/name) == sha256(saved/name)
    for name in ("primary_regression.csv","robustness_summary.csv","robustness_regressions.csv","province_influence.csv"):
        pd.testing.assert_frame_equal(pd.read_csv(tmp_path/name), pd.read_csv(saved/name),
                                     atol=1e-9, rtol=1e-8)
    md = (tmp_path/"primary_regression.md").read_text()
    assert "Lagged non-U.S. HHI" in md and "Combined fixed-effect rank | 368" in md
    assert "Restricted Webb 95% confidence set" in md
    assert result["webb_wild_restricted"]["p_at_zero"] == json.loads(
        (saved/"primary_diagnostics.json").read_text()
    )["webb_wild_restricted"]["p_at_zero"]
    figure_hashes = render(saved, tmp_path/"figures")
    assert figure_hashes == render(saved, tmp_path/"figures")
    assert len(figure_hashes) == 12


def test_steel_statutory_map_and_local_source_hashes():
    raw_manifest = json.loads((ROOT/"data/phase4b/design_A_source_manifest.json").read_text())
    schedule = next(r for r in raw_manifest if r["name"] == "hts_2025_rev4.csv")
    assert sha256(ROOT/schedule["path"]) == schedule["sha256"]
    lines = current_us_lines(ROOT/schedule["path"])
    assert lines.hts10.is_unique
    core = lines[lines.scope.eq("covered_core_232")]
    assert set(core.additional_statutory_rate_at_2025_03_12) == {.25}
    assert classify("7216610000")[0] == "excluded_from_core_check_derivative"
    assert classify("7204490020")[0] == "candidate_upstream_control"
    assert classify("7208101500")[0] == "covered_core_232"
    audit = ROOT/"data/phase4b/tariff_pilot"
    for name, row in json.loads((audit/"manifest.json").read_text())["files"].items():
        assert sha256(audit/name) == row["sha256"]
