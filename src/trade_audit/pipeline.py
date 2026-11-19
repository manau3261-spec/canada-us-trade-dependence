import json
import os
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile

import pandas as pd

from .acquire import sha256, utc_now, write_json
from .sources import SOURCES
from .trade import annual_monthly_checks, concentration_check, domestic_checks
from .validate import ANNUAL_TRADE, MONTHLY_TRADE, scan


def structural_issues(report: dict) -> list[str]:
    issues = report["issues"]
    fields = (
        "invalid_periods", "missing_expected_periods", "out_of_order_chunks",
        "duplicate_period_vector_excess", "duplicate_period_coordinate_excess",
        "vector_identity_conflicts", "coordinate_identity_conflicts", "dimension_label_identity_conflicts",
        "coordinate_metadata_mismatches", "unexpected_unit_combinations", "trade_unit_mismatches",
        "trade_precision_mismatches", "invalid_numbers", "numeric_values_with_unusable_status",
        "expected_geos_without_numeric_rows",
    )
    return [name for name in fields if issues[name]] + (
        [] if issues["archive_bounds_match_rows"] else ["archive_bounds_match_rows"]
    )


def descriptive_exports(frame: pd.DataFrame, pid: str, vintage: str) -> pd.DataFrame:
    if pid == MONTHLY_TRADE:
        frame = frame.loc[frame["period"].astype(str).ge("2025-01")].copy()
    return (
        frame.rename(columns={
            "world": "world_domestic_exports_cad_thousands", "usa": "us_domestic_exports_cad_thousands",
            "destination_gap": "destination_sum_minus_world_cad_thousands",
            "destination_tolerance": "destination_rounding_tolerance_cad_thousands",
            "product": "napcs_section", "geo": "geography",
        })
        .assign(source_pid=pid, acquisition_id=vintage, frequency="annual" if pid == ANNUAL_TRADE else "monthly")
        [["source_pid", "acquisition_id", "frequency", "period", "geography", "napcs_section",
          "world_domestic_exports_cad_thousands", "us_domestic_exports_cad_thousands",
          "us_domestic_export_share", "destination_sum_minus_world_cad_thousands",
          "destination_rounding_tolerance_cad_thousands", "destination_reconciled",
          "destination_hhi", "destination_hhi_ex_us"]]
    )


def validate_run(root: Path, manifest_path: Path) -> tuple[Path, dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_path = manifest_path.resolve()
    items = {item["pid"]: item for item in manifest["sources"]}
    vintage = manifest["run_id"]
    if not vintage or Path(vintage).name != vintage or vintage in {".", ".."}:
        raise ValueError("Invalid acquisition run ID")
    result = {
        "acquisition_id": vintage, "validated_at_utc": utc_now(),
        "manifest_path": manifest_path.relative_to(root).as_posix(),
        "manifest_sha256": sha256(manifest_path),
        "sources": {}, "trade_checks": {}, "blocking_issues": [],
    }
    evidence = manifest.get("wds_metadata", {})
    result["wds_evidence_verified"] = (
        evidence.get("status") == "downloaded" and (root / evidence["path"]).is_file()
        and sha256(root / evidence["path"]) == evidence["sha256"]
    )
    trades = {}
    derived = []
    reconciled_trades = {}
    for source in SOURCES:
        item = items.get(source.pid, {})
        if item.get("status") != "downloaded":
            err = item.get("error", "No downloaded file recorded in the manifest")
            result["sources"][source.pid] = {"status": "unavailable", "error": err}
            result["blocking_issues"].append(f"{source.table}: {err}")
            continue
        try:
            audit, frame = scan(root, source, item)
            result["sources"][source.pid] = audit
            failed = structural_issues(audit)
            if failed:
                result["blocking_issues"].append(f"{source.table}: {', '.join(failed)}")
            elif frame is not None:
                checks, reconciled = domestic_checks(
                    frame, annual=source.pid == ANNUAL_TRADE,
                    expected_partners=len(audit["partner_members"]) - 1,
                )
                trades[source.pid] = frame
                result["trade_checks"][source.pid] = checks
                reconciled_trades[source.pid] = reconciled
                derived.append(descriptive_exports(reconciled, source.pid, vintage))
            print(f"{source.table} scanned ({audit['all']['rows']:,} rows)", flush=True)
        except (OSError, BadZipFile, ValueError, KeyError, TypeError) as error:
            result["sources"][source.pid] = {"status": "validation_failed", "error": str(error)}
            result["blocking_issues"].append(f"{source.table}: {error}")
            print(f"{source.table} validation failed: {error}", flush=True)
    if ANNUAL_TRADE in trades and MONTHLY_TRADE in trades:
        annual_source = result["sources"][ANNUAL_TRADE]
        monthly_source = result["sources"][MONTHLY_TRADE]
        partners = set(annual_source["partner_members"]) & set(monthly_source["partner_members"])
        annual_products = {code: label for label, code in annual_source["products"].items()}
        monthly_products = {code: label for label, code in monthly_source["products"].items()}
        common = set(annual_products) & set(monthly_products)
        compatible = {code for code in common if code == "TOTAL" or annual_products[code] == monthly_products[code]}
        result["classification_comparison"] = {
            "common_codes_compared": sorted(compatible),
            "common_code_label_mismatches": sorted(common - compatible),
            "annual_only": sorted(set(annual_products) - common),
            "monthly_only": sorted(set(monthly_products) - common),
        }
        result["annual_monthly"] = annual_monthly_checks(
            trades[ANNUAL_TRADE], trades[MONTHLY_TRADE], partners, compatible
        )
    benchmark = result["sources"].get("12100129", {})
    if (ANNUAL_TRADE in reconciled_trades and benchmark.get("status") == "validated"
            and not structural_issues(benchmark)):
        result["concentration_benchmark"] = concentration_check(
            reconciled_trades[ANNUAL_TRADE], benchmark["benchmark"]
        )
    gdp = result["sources"]["36100711"].get("naics_members", [])
    lfs = result["sources"]["14100022"].get("naics_members", [])
    if gdp and lfs:
        gdp_by_code = {item["code"]: item["label"] for item in gdp}
        lfs_by_code = {item["code"]: item["label"] for item in lfs}
        common_naics = sorted(gdp_by_code.keys() & lfs_by_code.keys())
        result["naics_code_screen"] = {
            "gdp_codes": len(gdp_by_code), "lfs_codes": len(lfs_by_code),
            "common_codes": common_naics,
            "label_differences": [code for code in common_naics if gdp_by_code[code] != lfs_by_code[code]],
        }
    if derived:
        combined = pd.concat(derived, ignore_index=True).sort_values(
            ["frequency", "period", "geography", "napcs_section"], kind="stable"
        )
        target = root / "data" / "derived" / vintage / "domestic_export_exposure.csv"
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
        try:
            combined.to_csv(temp, index=False)
            os.replace(temp, target)
        finally:
            temp.unlink(missing_ok=True)
        flags = ["us_domestic_export_share", "destination_hhi", "destination_hhi_ex_us"]
        result["descriptive"] = {
            "path": target.relative_to(root).as_posix(), "sha256": sha256(target),
            "counts": {
                frequency: {"rows": len(group), **{name: int(group[name].notna().sum()) for name in flags}}
                for frequency, group in combined.groupby("frequency")
            },
        }
    validation = root / "data" / "provenance" / f"validation-{vintage}.json"
    write_json(validation, result)
    return validation, result
