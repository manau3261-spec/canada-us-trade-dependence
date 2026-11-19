"""Fixed-effect projection, cluster covariance and validated Webb WCR-t."""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import scipy.linalg as la
from scipy.stats import t as student_t
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster, cov_cluster_2groups

from .phase4b_data import FIXED_EFFECTS, FE_NAMES


class DesignFailure(ValueError):
    """A design lacks adequate rank, support or computable inference."""


@dataclass
class Projected:
    fe: np.ndarray
    q: np.ndarray
    q_slopes: np.ndarray
    xr: np.ndarray
    weighted_x: np.ndarray
    weights: np.ndarray
    province: np.ndarray
    product: np.ndarray
    group: np.ndarray
    diagnostics: dict
    fixed_levels: dict

    def partial(self, value):
        return value - self.q @ (self.q.T @ value)

    def full_residual(self, value):
        partial = self.partial(value)
        return partial - self.q_slopes @ (self.q_slopes.T @ partial)

    @property
    def n(self):
        return len(self.xr)

    @property
    def rank(self):
        return self.q.shape[1] + self.xr.shape[1]


def group_codes(rows, columns):
    return pd.factorize(pd.MultiIndex.from_frame(rows[columns]), sort=True)[0]


def project(rows, predictor, raw_weights=None, required_clusters=None):
    raw_x = rows[[predictor, "log_lag_exports", "lag_us_share"]].to_numpy(dtype=float)
    weights = np.ones(len(rows)) if raw_weights is None else np.asarray(raw_weights, dtype=float)
    if not np.isfinite(raw_x).all() or not np.isfinite(weights).all() or not np.all(weights > 0):
        raise DesignFailure("Incomplete regressors or invalid WLS weights")
    w = np.sqrt(weights / weights.mean())
    province, product, group = (group_codes(rows, cols) for cols in (["geo"], ["product"], ["geo", "product"]))
    fe = []
    levels = {}
    for name, columns in zip(FE_NAMES, FIXED_EFFECTS):
        codes = group_codes(rows, columns)
        levels[name] = int(codes.max() + 1)
        fe.append(np.eye(levels[name])[codes] * w[:, None])
    d = np.column_stack(fe)
    q, r, pivots = la.qr(d, mode="economic", pivoting=True)
    diag = np.abs(np.diag(r))
    rank_fe = int(np.sum(diag > diag[0] * max(d.shape) * np.finfo(float).eps))
    q = q[:, :rank_fe]
    weighted_x = raw_x * w[:, None]
    xr = weighted_x - q @ (q.T @ weighted_x)
    projected_sd = np.linalg.norm(xr, axis=0) / np.sqrt(len(rows))
    if projected_sd[0] <= 1e-8 or np.any(projected_sd[1:] <= 1e-12):
        raise DesignFailure("Insufficient residual variation after fixed effects")
    normalized = xr / projected_sd
    singular = la.svdvals(normalized)
    condition = float(singular[0] / singular[-1]) if singular[-1] > 0 else np.inf
    if condition >= 1e8 or np.linalg.matrix_rank(normalized) != 3:
        raise DesignFailure("Residualized slopes fail rank or conditioning check")
    q_slopes = la.qr(xr, mode="economic")[0]
    controls = la.qr(xr[:, 1:], mode="economic")[0]
    within_x = xr[:, 0] - controls @ (controls.T @ xr[:, 0])
    ss = float(within_x @ within_x)
    cluster_share = np.bincount(province, weights=within_x**2) / ss
    if len(rows) <= rank_fe + 3 or ss <= 0:
        raise DesignFailure("No residual degrees of freedom or partial predictor variation")
    if required_clusters is not None and (
        len(cluster_share) != required_clusters or np.any(cluster_share <= np.finfo(float).eps)
        or np.sqrt(ss / len(rows)) <= 1e-8
    ):
        raise DesignFailure("Primary partial predictor variation is missing in one or more clusters")
    centered_x = w * (raw_x[:, 0] - np.average(raw_x[:, 0], weights=w**2))
    diagnostic = {
        "n": len(rows), "fixed_effect_rank": rank_fe, "slope_rank": 3,
        "design_rank": rank_fe + 3, "residual_df": len(rows) - rank_fe - 3,
        "province_clusters": len(cluster_share), "product_clusters": int(product.max()+1),
        "province_product_groups": int(group.max()+1),
        "hhi_or_alternative_raw_sd": float(np.linalg.norm(centered_x) / np.sqrt(len(rows))),
        "predictor_fe_residual_sd": float(projected_sd[0]),
        "predictor_fully_partialled_sd": float(np.sqrt(ss / len(rows))),
        "predictor_fully_partialled_ss": ss,
        "slope_scaled_condition_number": condition,
        "scaled_slope_singular_values": singular.tolist(),
        "effective_provinces_partial_leverage": float(1 / np.sum(cluster_share**2)),
        "max_province_partial_leverage": float(cluster_share.max()),
        "level_counts": levels,
    }
    return Projected(d[:, pivots[:rank_fe]], q, q_slopes, xr, weighted_x, w, province, product, group, diagnostic, levels)


def cr1_multiplier(k, n, rank):
    if k < 2 or n <= rank:
        raise DesignFailure("Cluster or residual degrees of freedom are inadequate")
    return (k / (k - 1)) * ((n - 1) / (n - rank))


def cluster_sums(values, codes):
    sums = np.zeros((int(codes.max() + 1), values.shape[1]))
    np.add.at(sums, codes, values)
    return sums


def cluster_variance(influences, codes, rank):
    sums = cluster_sums(influences, codes)
    return (sums**2).sum(axis=0) * cr1_multiplier(len(sums), len(codes), rank)


def inference_rows(params, variances, groups):
    df = groups - 1
    for coef, var in zip(params, variances):
        if not np.isfinite(var) or var <= 0:
            yield {"standard_error": np.nan, "t": np.nan, "df": df, "p_value": np.nan,
                   "ci_low": np.nan, "ci_high": np.nan, "status": "nonpositive or invalid variance"}
            continue
        se = float(np.sqrt(var))
        crit = student_t.ppf(.975, df)
        yield {"standard_error": se, "t": coef/se, "df": df,
               "p_value": 2*student_t.sf(abs(coef/se), df),
               "ci_low": coef-crit*se, "ci_high": coef+crit*se, "status": "ok"}


def fit_model(rows, design, outcome, predictor):
    y = design.weights * rows[outcome].to_numpy(dtype=float)
    if not np.isfinite(y).all():
        raise DesignFailure("Invalid outcome in eligible sample")
    yr = design.partial(y)
    fx = sm.OLS(yr, design.xr, hasconst=False).fit()
    influence = fx.model.pinv_wexog.T * fx.resid[:, None]
    variances = {}
    for name, group in (("province", design.province), ("product", design.product),
                        ("province_product", design.group)):
        variances[name] = (cluster_variance(influence, group, design.rank), int(group.max()+1))
    variances["province_and_product"] = (
        variances["province"][0] + variances["product"][0] - variances["province_product"][0],
        min(variances["province"][1], variances["product"][1]),
    )
    inference = []
    terms = (predictor, "log_lag_exports", "lag_us_share")
    for covariance, (var, cluster_df) in variances.items():
        inference.extend(dict(row, term=term, coefficient=float(coef), covariance=covariance)
                         for row, term, coef in zip(inference_rows(fx.params, var, cluster_df), terms, fx.params))
    rss, within_sst = float(fx.resid@fx.resid), float(yr@yr)
    outcome_values = rows[outcome].to_numpy(dtype=float)
    centered = y - design.weights * np.average(outcome_values, weights=design.weights**2)
    sst = centered @ centered
    rdf = design.n-design.rank
    fit = {"rss": rss, "r_squared": 1-rss/sst if sst > 0 else np.nan,
           "adjusted_r_squared": 1-(rss/rdf)/(sst/(design.n-1)) if sst > 0 else np.nan,
           "within_r_squared": 1-rss/within_sst if within_sst > 0 else np.nan,
           "rmse_log_points": float(np.sqrt(rss/rdf)),
           "mean_outcome": float(np.average(outcome_values, weights=design.weights**2)),
           "median_outcome": float(np.median(outcome_values))}
    return fx, y, inference, fit


def validate_against_explicit(design, fx, y, inference):
    # The retained original dummy columns are an independently specified model.
    explicit_x = np.column_stack([design.fe, design.weighted_x])
    if np.linalg.matrix_rank(explicit_x) != design.rank:
        raise DesignFailure("Explicit full design rank differs from the QR calculation")
    ref = sm.OLS(y, explicit_x, hasconst=True).fit(method="qr")
    coeff_error = float(np.max(np.abs(ref.params[-3:] - fx.params)))
    residual_error = float(np.max(np.abs(ref.resid - fx.resid)))
    groupings = {"province": design.province, "product": design.product, "province_product": design.group}
    covariance_ref = {key: np.diag(cov_cluster(ref, value))[-3:] for key, value in groupings.items()}
    covariance_ref["province_and_product"] = np.diag(
        cov_cluster_2groups(ref, design.province, design.product)[0]
    )[-3:]
    errors = {}
    for key, reference in covariance_ref.items():
        computed = np.array([r["standard_error"]**2 for r in inference if r["covariance"] == key])
        valid = np.isfinite(computed)
        if not np.array_equal(valid, np.isfinite(reference) & (reference > 0)):
            raise DesignFailure(f"Inconsistent sign in independent {key} cluster covariance")
        error = np.max(np.abs(reference[valid]-computed[valid])) if valid.any() else 0
        errors[key] = float(error)
    if max(coeff_error, residual_error, *errors.values()) > 1e-8:
        raise DesignFailure("Fixed-effect or covariance cross-check did not reproduce")
    return {"max_coefficient_error": coeff_error, "max_residual_error": residual_error,
            "max_cluster_variance_errors": errors}


def webb_weights(draws, clusters, seed):
    a = np.sqrt([0.5, 1.0, 1.5])
    return np.random.default_rng(seed).choice(np.r_[-a, a], size=(draws, clusters))


class RestrictedWild:
    """Precompute cluster-score responses for the outcome and a null shift."""

    def __init__(self, design, fx, weights):
        self.design = design
        self.weights = weights
        self.beta = float(fx.params[0])
        self.errors = fx.resid
        qr = la.qr(design.xr[:, 1:], mode="economic")[0]
        self.x = design.xr[:, 0] - qr @ (qr.T @ design.xr[:, 0])
        self.ss = self.x @ self.x
        self.g = weights.shape[1]
        self.factor = cr1_multiplier(self.g, design.n, design.rank)
        self.se = float(np.sqrt(cluster_variance(
            (self.x * self.errors / self.ss)[:, None], design.province, design.rank,
        )[0]))
        if not np.isfinite(self.se) or self.se <= 0:
            raise DesignFailure("Cannot studentize the primary coefficient")
        self.cluster_rows = np.eye(self.g)[design.province]
        self.d0, score0 = self._multipliers(self.errors)
        self.d1, score1 = self._multipliers(self.x)
        self.a = np.sum(score0**2, axis=1)
        self.b = 2*np.sum(score0*score1, axis=1)
        self.c = np.sum(score1**2, axis=1)

    def _multipliers(self, restricted_residual):
        by_cluster = restricted_residual[:, None] * self.cluster_rows
        beta_diffs = self.weights @ (self.x @ by_cluster / self.ss)
        e_stars = self.design.full_residual(by_cluster)
        scores = cluster_sums(self.x[:, None] * e_stars, self.design.province)
        drawn_scores = self.weights @ scores.T
        return beta_diffs, drawn_scores

    def statistics(self, null):
        offset = self.beta - null
        norm2 = self.a + offset*self.b + offset**2*self.c
        if np.any(norm2 <= 0) or not np.isfinite(norm2).all():
            raise DesignFailure("Bootstrap contains nonpositive or invalid CR1 draws")
        se_star = np.sqrt(self.factor * norm2) / self.ss
        return (self.d0 + offset*self.d1) / se_star

    def p_value(self, null):
        draws = self.statistics(null)
        obs = (self.beta-null) / self.se
        return float((1 + np.count_nonzero(np.abs(draws) >= abs(obs))) / (len(draws)+1))

    def validate_direct(self, y, draws=24):
        # Literal constrained DGP and explicit WCR refits. QR is full rank
        # so full-model residuals and cluster scores can be calculated independently.
        explicit_x = np.column_stack([self.design.fe, self.design.weighted_x])
        qref, rref = la.qr(explicit_x, mode="economic")
        coefficient_influence = la.solve_triangular(rref, qref.T)[-3]
        errors = []
        for null in (0.0, self.beta + 1.25*self.se):
            x = explicit_x[:, -3]
            restricted_x = np.delete(explicit_x, -3, axis=1)
            qr0, _ = la.qr(restricted_x, mode="economic")
            y0 = y - x*null
            e0 = y0 - qr0 @ (qr0.T @ y0)
            ystar = (y - e0)[:, None] + e0[:, None]*self.weights[:draws].T[self.design.province]
            beta = coefficient_influence @ ystar
            est_resid = ystar - qref @ (qref.T @ ystar)
            variance = cluster_variance(est_resid * coefficient_influence[:, None],
                                        self.design.province, self.design.rank)
            direct = (beta-null)/np.sqrt(variance)
            errors.append(np.max(np.abs(direct-self.statistics(null)[:draws])))
        error = float(max(errors))
        if error > 1e-8:
            raise DesignFailure("Literal fixed-effect bootstrap refits failed numerical validation")
        return {"draws_per_null": draws, "nulls": 2, "max_t_error": error}

    def confidence_set(self):
        candidates = np.linspace(self.beta-12*self.se, self.beta+12*self.se, 481)
        accepted = np.array([self.p_value(b) >= .05 for b in candidates])
        edges = np.flatnonzero(accepted[1:] != accepted[:-1])
        components = []
        start = None
        for edge in edges:
            low, high = candidates[edge:edge+2]
            for _ in range(18):
                midpoint = (low+high)/2
                if (self.p_value(midpoint) >= .05) == accepted[edge]:
                    low = midpoint
                else:
                    high = midpoint
            boundary = float((low+high)/2)
            if accepted[edge]:
                components.append([start, boundary])
                start = None
            else:
                start = boundary
        if accepted[-1]:
            components.append([start, None])
        return components, candidates[[0, -1]].tolist()
