"""Reproduce Phase 4B Design C and its registered diagnostics."""

import argparse
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import statsmodels

from .acquire import sha256, write_json
from .phase4b_data import (
    CELLS, FLOOR_CAD, STARTS, drop_singletons, ledger_for, panel_grid, prepare, preregistration, selection_check,
)
from .phase4b_inference import (
    DesignFailure, RestrictedWild, fit_model, project, validate_against_explicit, webb_weights,
)

DATA = Path("data/phase4b")
PREDICTOR = "hhi_ex_us"
OUTCOME = "absolute_growth"
BOOTSTRAP_DRAWS = 9999
BOOTSTRAP_SEED = 20261118


def robustness_specs(years, grid, main):
    balanced = main.groupby(CELLS[:2], observed=True).t.transform("size").eq(len(STARTS))
    specs = [
        ("A_no_C14", main.loc[main["product"].ne("C14")], PREDICTOR, OUTCOME, False),
        ("B_positive", ledger_for(grid, 0)[0], PREDICTOR, OUTCOME, False),
        ("B_100k", ledger_for(grid, 100_000)[0], PREDICTOR, OUTCOME, False),
        ("B_10m", ledger_for(grid, 10_000_000)[0], PREDICTOR, OUTCOME, False),
        ("C_balanced", main.loc[balanced], PREDICTOR, OUTCOME, False),
        ("D_lag_weighted", main, PREDICTOR, OUTCOME, True),
        ("E_signed", main, PREDICTOR, "signed_growth", False),
        ("F_downside", main, PREDICTOR, "downside", False),
        ("H_end_2024", main.loc[main.end_year.le(2024)], PREDICTOR, OUTCOME, False),
        ("J_even", main.loc[main.t.mod(2).eq(0)], PREDICTOR, OUTCOME, False),
        ("J_odd", main.loc[main.t.mod(2).eq(1)], PREDICTOR, OUTCOME, False),
        ("J_2year", ledger_for(panel_grid(years, horizon=2))[0], PREDICTOR, OUTCOME, False),
    ]
    specs.extend((f"G_{col}", main, f"lag_{col}", OUTCOME, False)
                 for col in ("top1_non_us", "top3_non_us", "destination_hhi", "positive_non_us_partners"))
    specs.extend((f"I_omit_{geo}", main.loc[main.geo.ne(geo)], PREDICTOR, OUTCOME, False)
                 for geo in sorted(main.geo.unique()))
    return specs


def run_robustness(years, grid, main, selection):
    summaries, results, membership = [], [], []
    specs = robustness_specs(years, grid, main)
    cohort, support = selection
    if support["zero_ends"] >= 20 and support["provinces_with_zero_end"] >= 5:
        specs.append(("selection_exit", cohort.assign(exit_outcome=cohort.end_zero.astype(int)),
                      PREDICTOR, "exit_outcome", False))
    for label, rows, predictor, outcome, weighted in specs:
        scale = 1.0 if predictor == "lag_positive_non_us_partners" else 0.10
        mask = rows[predictor].notna()
        clean, singletons = drop_singletons(rows.loc[mask])
        audit = rows[CELLS].copy().assign(specification=label)
        audit["included"] = audit.index.isin(clean.index)
        audit["reason"] = np.select(
            [~mask, audit.index.isin(singletons.index)], ["alternative predictor unavailable", "absorbed FE singleton"],
            default="",
        )
        membership.append(audit)
        try:
            if clean.empty:
                raise DesignFailure("Empty robustness sample")
            design = project(clean, predictor, clean.lag_exports_cad if weighted else None)
            _, _, stats, fit = fit_model(clean, design, outcome, predictor)
            base = next(r for r in stats if r["covariance"] == "province" and r["term"] == predictor)
            summaries.append(dict(
                base, specification=label, predictor=predictor, predictor_increment=scale, outcome=outcome,
                weights="lagged export value" if weighted else "equal", n=design.n,
                groups=design.diagnostics["province_product_groups"], fixed_effect_rank=design.diagnostics["fixed_effect_rank"],
                design_rank=design.rank, province_clusters=design.diagnostics["province_clusters"],
                start_year_min=int(clean.t.min()), start_year_max=int(clean.t.max()),
                input_before_alt_availability_and_singletons=len(rows), **fit,
            ))
            results.extend(dict(s, specification=label) for s in stats)
        except DesignFailure as error:
            summaries.append({"specification": label, "predictor": predictor, "outcome": outcome,
                              "n": len(clean), "status": str(error)})
    return pd.DataFrame(summaries), pd.DataFrame(results), pd.concat(membership, ignore_index=True)


def write_primary_table(path, estimates, summary):
    stats = estimates.query("covariance == 'province'")
    names = {"hhi_ex_us": "Lagged non-U.S. HHI", "log_lag_exports": "Lagged log non-U.S. exports",
             "lag_us_share": "Lagged U.S. export share"}
    lines = [
        "# Primary Design C regression table", "",
        "Dependent variable is the absolute annual log change in non-U.S. domestic merchandise exports. "
        "Equal cell weights and province-clustered CR1 uncertainty. HHI and U.S. share on a 0–1 scale.", "",
        "| Regressor | Coefficient | CR1 SE | t (9 df) | p | 95% lower | 95% upper |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in stats.itertuples():
        lines.append(f"| {names[r.term]} | {r.coefficient:.6f} | {r.standard_error:.6f} | {r.t:.4f} | "
                     f"{r.p_value:.5f} | {r.ci_low:.6f} | {r.ci_high:.6f} |")
    d, fit, wild = (summary[k] for k in ("design", "fit", "webb_wild_restricted"))
    lines.extend(["", "| Statistic | Value |", "| --- | ---: |",
        f"| Observations | {d['n']:,} |",
        f"| Province clustering groups | {d['province_clusters']} |",
        f"| Province × product fixed-effect levels | {d['level_counts']['province_product']} |",
        f"| Product × year fixed-effect levels | {d['level_counts']['product_year']} |",
        f"| Province × year fixed-effect levels | {d['level_counts']['province_year']} |",
        f"| Combined fixed-effect rank | {d['fixed_effect_rank']} |",
        f"| Full rank (fixed effects and slopes) | {d['design_rank']} |",
        f"| Residual degrees of freedom | {d['residual_df']} |",
        f"| Overall R² | {fit['r_squared']:.5f} |",
        f"| Adjusted R² | {fit['adjusted_r_squared']:.5f} |",
        f"| Within R² | {fit['within_r_squared']:.5f} |",
        f"| Residual RMSE (log points) | {fit['rmse_log_points']:.5f} |",
        f"| Restricted Webb p for HHI | {wild['p_at_zero']:.5f} |", ""])
    components = []
    for left, right in wild["ci_95_beta_components"]:
        lower = "open" if left is None else f"{left:.6f}"
        upper = "open" if right is None else f"{right:.6f}"
        components.append(f"[{lower}, {upper}]")
    lines.append("Restricted Webb 95% confidence set for the HHI coefficient within the scanned range "
                 + " ∪ ".join(components) + ".")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def execute(root, target, preflight=False, charts=True):
    lock = preregistration(root)
    print("Rebuilding annual trade and checking all input hashes", flush=True)
    years, statuses, sample, hashes, grid, main, ledger = prepare(root)
    target.mkdir(parents=True, exist_ok=True)
    years.to_csv(target/"source_year_audit.csv", index=False)
    statuses.to_csv(target/"source_status_counts.csv", index=False)
    ledger.to_csv(target/"sample_exclusion_ledger.csv", index=False)
    main[CELLS + ["lag_year", "start_year", "end_year", "lag_exports_cad",
                  PREDICTOR, "log_lag_exports", "lag_us_share", OUTCOME, "signed_growth", "downside"]].to_csv(
        target/"design_C_model_input.csv", index=False,
    )
    try:
        design = project(main, PREDICTOR, required_clusters=10)
    except DesignFailure as error:
        write_json(target/"primary_failure.json", {"phase": "pre-estimation design checks", "reason": str(error)})
        raise
    support = selection_check(grid)
    checks = {"preregistration": lock, "input_hashes": hashes, "sample": sample,
              "prespecified_selection_check": support[1], "design": design.diagnostics,
              "model_input_sha256": sha256(target/"design_C_model_input.csv")}
    write_json(target/"preflight.json", checks)
    print(f"Preflight passed: n={design.n}, rank={design.rank}, provinces={design.diagnostics['province_clusters']}",
          flush=True)
    if preflight:
        return checks

    print("Estimating primary model and validating restricted inference", flush=True)
    try:
        fx, y, inference, fit = fit_model(main, design, OUTCOME, PREDICTOR)
        reference = validate_against_explicit(design, fx, y, inference)
        weights = webb_weights(BOOTSTRAP_DRAWS, design.diagnostics["province_clusters"], BOOTSTRAP_SEED)
        wild = RestrictedWild(design, fx, weights)
        validation = wild.validate_direct(y)
        probability = wild.p_value(0.0)
        components, search = wild.confidence_set()
        if not components or not any((a is None or a <= wild.beta) and (b is None or b >= wild.beta)
                                     for a, b in components):
            raise DesignFailure("Invalid inverted confidence set")
    except DesignFailure as error:
        write_json(target/"primary_failure.json", {"phase": "primary fit or inference validation", "reason": str(error)})
        raise

    result = {
        "design": design.diagnostics, "fit": fit, "explicit_statsmodels_validation": reference,
        "webb_wild_restricted": {"p_at_zero": probability, "draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED,
            "standard_error_used_to_studentize": wild.se, "ci_95_beta_components": components,
            "scan_range": search, "mc_se_at_zero": float(np.sqrt(probability*(1-probability)/BOOTSTRAP_DRAWS)),
            "mc_se_near_0_05": float(np.sqrt(.05*.95/BOOTSTRAP_DRAWS)),
            "direct_refit_cross_check": validation},
        "software": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                     "scipy": scipy.__version__, "statsmodels": statsmodels.__version__},
    }
    estimates = pd.DataFrame(inference)
    estimates["per_0_10_if_share_or_hhi"] = estimates.coefficient.mul(.10).where(
        estimates.term.isin([PREDICTOR, "lag_us_share"]),
    )
    estimates.to_csv(target/"primary_regression.csv", index=False)
    write_primary_table(target/"primary_regression.md", estimates, result)
    write_json(target/"primary_diagnostics.json", result)
    print("Estimating registered secondary specifications", flush=True)
    sensitivity, full, membership = run_robustness(years, grid, main, support)
    sensitivity.to_csv(target/"robustness_summary.csv", index=False)
    full.to_csv(target/"robustness_regressions.csv", index=False)
    membership.to_csv(target/"robustness_membership.csv", index=False)
    leverage = pd.DataFrame({"geo": sorted(main.geo.unique()),
        "observations": np.bincount(design.province),
        "partial_predictor_leverage": np.bincount(design.province, weights=wild.x**2) / wild.ss,
        "predictor_score": np.bincount(design.province, weights=wild.x*wild.errors),
        "max_hat_diagonal": pd.Series((design.q**2).sum(axis=1)+(design.q_slopes**2).sum(axis=1))
            .groupby(design.province).max().to_numpy()})
    loo = sensitivity.loc[sensitivity.specification.str.startswith("I_omit_")].assign(
        geo=lambda s: s.specification.str.removeprefix("I_omit_"),
    )[["geo", "coefficient", "ci_low", "ci_high", "n"]]
    leverage.merge(loo, on="geo", validate="one_to_one").to_csv(target/"province_influence.csv", index=False)
    if charts:
        from .phase4b_figures import render
        render(target, root/"figures/phase4b")
    print(f"Completed: {len(sensitivity)} robustness fits attempted", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, help="Override the output directory. Inputs stay under --root.")
    parser.add_argument("--preflight", action="store_true", help="Validate data and rank without estimating.")
    parser.add_argument("--no-figures", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    execute(root, args.output or root/DATA, preflight=args.preflight, charts=not args.no_figures)


if __name__ == "__main__":
    main()
