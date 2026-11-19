import numpy as np
import pandas as pd

from .validate import EX_US, OTHER, SECTION_TOTAL, USA, WORLD, UNUSABLE_STATUS

KEY = ["period", "geo", "product"]
HHI_UNALLOCATED = {"Unknown or unspecified", "Canada", OTHER}


def numeric_rounding(frame: pd.DataFrame) -> pd.Series:
    return (0.5 * np.power(10.0, -frame["decimals"].astype(float))).where(frame["value"].notna())


def domestic_checks(trade: pd.DataFrame, annual: bool, expected_partners: int) -> tuple[dict, pd.DataFrame]:
    """Reconcile destination components and product sections separately in CAD thousands."""
    frame = trade.assign(rounding=numeric_rounding(trade))
    world = (frame.loc[frame["partner"].eq(WORLD), KEY + ["value", "rounding"]]
             .set_index(KEY).rename(columns={"value": "world", "rounding": "world_rounding"}))
    usa = (frame.loc[frame["partner"].eq(USA), KEY + ["value"]]
           .set_index(KEY).rename(columns={"value": "usa"}))
    children = frame.loc[~frame["partner"].eq(WORLD)]
    children = children.assign(
        square=children["value"].pow(2),
        nonus_square=children["value"].pow(2).where(~children["partner"].eq(USA)),
        negative=children["value"].lt(0),
        unusable=children["status"].isin(UNUSABLE_STATUS - {"..", "...", "."}),
        unallocated=children["partner"].isin(HHI_UNALLOCATED) & children["value"].ne(0) & children["value"].notna(),
    )
    grouper = children.groupby(KEY, observed=True, sort=False)
    totals = grouper[["value", "square", "nonus_square", "rounding"]].sum(min_count=1)
    totals = totals.join(grouper[["negative", "unusable", "unallocated"]].sum())
    totals["numeric_partners"] = grouper["value"].count()
    totals["component_rows"] = grouper.size()
    result = world.join(usa, how="outer", validate="one_to_one").join(totals, how="outer")
    result["destination_gap"] = result["value"] - result["world"]
    result["destination_tolerance"] = result["rounding"] + result["world_rounding"]
    result["destination_reconciled"] = within_precision(result["destination_gap"], result["destination_tolerance"])
    share_ok = result["world"].gt(0) & result["usa"].ge(0) & result["usa"].le(result["world"])
    result["us_domestic_export_share"] = result["usa"].div(result["world"]).where(share_ok)

    detail = frame.loc[frame["product"].ne(SECTION_TOTAL)]
    section_key = ["period", "geo", "partner"]
    reported_sections = detail.groupby(section_key, observed=True)[["value", "rounding"]].sum(min_count=1)
    all_product = (frame.loc[frame["product"].eq(SECTION_TOTAL), section_key + ["value", "rounding"]]
                   .set_index(section_key).rename(columns={"value": "total", "rounding": "total_rounding"}))
    section = all_product.join(reported_sections, how="outer", validate="one_to_one")
    section_gap = section["value"] - section["total"]
    section_reconciled = within_precision(section_gap, section["total_rounding"] + section["rounding"])

    hhi_columns = ["destination_hhi", "destination_hhi_ex_us"]
    result[hhi_columns] = np.nan
    if annual:
        # Missing published components stay missing. Require reconciliation and complete numeric
        # disclosure for active nonzero residuals. No destination value is imputed.
        eligible = (share_ok & result["destination_reconciled"] & result["negative"].eq(0)
                    & result["numeric_partners"].eq(expected_partners)
                    & result["unusable"].eq(0) & result["unallocated"].eq(0))
        nonus = result["world"] - result["usa"]
        include = result["square"].div(result["world"].pow(2))
        exclude = result["nonus_square"].div(nonus.pow(2))
        result["destination_hhi"] = include.where(eligible & include.between(0, 1))
        result["destination_hhi_ex_us"] = exclude.where(
            eligible & nonus.gt(result["destination_tolerance"]) & exclude.between(0, 1)
        )

    diagnostics = {
        "destination": comparison_counts(result["destination_gap"], result["destination_reconciled"]),
        "world_rows_missing_numeric": int(result["world"].isna().sum()),
        "us_rows_missing_numeric": int(result["usa"].isna().sum()),
        "world_zero": int(result["world"].eq(0).sum()),
        "us_greater_than_world": int(result["usa"].gt(result["world"]).sum()),
        "groups_with_unallocated_nonzero": int(result["unallocated"].gt(0).sum()),
        "groups_with_missing_component_value": int(result["numeric_partners"].lt(result["component_rows"]).sum()),
        "groups_missing_expected_partner_rows": int((~result["component_rows"].eq(expected_partners)).sum()),
        "groups_with_suppressed_or_unreliable_components": int(result["unusable"].gt(0).sum()),
        "groups_with_negative_components": int(result["negative"].gt(0).sum()),
        "product_sections": comparison_counts(section_gap, section_reconciled),
        "product_sections_world_us": comparison_counts(
            section_gap[section.index.get_level_values("partner").isin([WORLD, USA])],
            section_reconciled[section.index.get_level_values("partner").isin([WORLD, USA])],
        ),
        "by_section": {
            product: {"groups": len(group), "world_nonzero": int((group["world"].notna() & group["world"].ne(0)).sum())}
            for product, group in result.groupby(level="product", observed=True)
        },
    }
    return diagnostics, result.reset_index()


def within_precision(gap: pd.Series, tolerance: pd.Series) -> pd.Series:
    # A small allowance for binary summation at an exact rounding boundary in CAD thousands.
    return gap.abs().le(tolerance + 1e-7)


def comparison_counts(gap: pd.Series, passed: pd.Series) -> dict:
    available = int(gap.notna().sum())
    failures = gap[gap.notna() & ~passed].abs()
    return {
        "groups": len(gap), "comparable": available, "within_rounding": int(passed.sum()),
        "outside_rounding": len(failures), "unavailable": len(gap) - available,
        "max_abs_gap_cad_thousands": float(gap.abs().max()) if available else None,
        "median_abs_gap_outside_rounding_cad_thousands": float(failures.median()) if len(failures) else None,
    }


def annual_monthly_checks(annual: pd.DataFrame, monthly: pd.DataFrame,
                          common_partners: set[str], common_products: set[str]) -> dict:
    annual = annual.loc[annual["partner"].isin(common_partners) & annual["product"].isin(common_products)]
    monthly = monthly.loc[monthly["partner"].isin(common_partners)
                          & monthly["product"].isin(common_products)
                          & monthly["period"].astype(str).lt("2026")].copy()
    year = monthly["period"].astype(str).str[:4]
    monthly = monthly.assign(period=year, rounding=numeric_rounding(monthly))
    key = [*KEY, "partner"]
    monthly_group = monthly.groupby(key, observed=True)
    months = monthly_group["value"].count()
    monthly_totals = monthly_group[["value", "rounding"]].sum(min_count=12).loc[months.eq(12)]
    annual_totals = (annual.assign(annual_rounding=numeric_rounding(annual))
                    .set_index(key)[["value", "annual_rounding"]].rename(columns={"value": "annual"}))
    paired = annual_totals.join(monthly_totals, how="outer", validate="one_to_one")
    gap = paired["value"] - paired["annual"]
    passed = within_precision(gap, paired["rounding"] + paired["annual_rounding"])
    period = paired.index.get_level_values("period")
    partner = paired.index.get_level_values("partner")
    product = paired.index.get_level_values("product")
    group_masks = {
        "all_common_partners_2010_2025": period.isin([str(y) for y in range(2010, 2026)]),
        "world_us_2010_2025": partner.isin([WORLD, USA]),
        "world_us_2025": period.isin(["2025"]) & partner.isin([WORLD, USA]),
        "world_us_all_products_2025": period.isin(["2025"]) & partner.isin([WORLD, USA]) & product.isin([SECTION_TOTAL]),
    }
    return {
        "common_partners": sorted(common_partners),
        "controls": {key: comparison_counts(gap[mask], passed[mask]) for key, mask in group_masks.items()},
        "by_year": {year: comparison_counts(gap[period == year], passed[period == year])
                    for year in sorted(set(period))},
    }


def concentration_check(annual: pd.DataFrame, benchmark: list[dict]) -> dict:
    total = annual.loc[annual["product"].eq(SECTION_TOTAL)]
    keys = ["period", "geo"]
    ratios = total.set_index(keys)[["destination_hhi", "destination_hhi_ex_us"]]
    result = {}
    for partner, column in ((WORLD, "destination_hhi"), (EX_US, "destination_hhi_ex_us")):
        official = pd.DataFrame([item for item in benchmark if item["partner"] == partner],
                                columns=[*keys, "value", "decimals"]).set_index(keys)
        joined = ratios[[column]].join(official, how="outer", validate="one_to_one")
        gap = joined[column] - joined["value"]
        valid = gap.abs().le(0.5 * np.power(10.0, -joined["decimals"].astype(float)) + 1e-12)
        geo = joined.index.get_level_values("geo")
        result[column] = {}
        for label, mask in (("Canada", geo == "Canada"), ("Subnational", geo != "Canada")):
            summary = comparison_counts(gap[mask], valid[mask])
            summary["max_abs_hhi_gap"] = summary.pop("max_abs_gap_cad_thousands")
            summary["median_abs_hhi_gap_outside_rounding"] = summary.pop(
                "median_abs_gap_outside_rounding_cad_thousands"
            )
            summary["official_numeric"] = int(joined.loc[mask, "value"].notna().sum())
            result[column][label] = summary
    return result
