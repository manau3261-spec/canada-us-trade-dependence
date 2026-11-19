"""Independently check locked 2020 reconciliation and March steel pilot support."""
from argparse import ArgumentParser
import json
from pathlib import Path
import re
from zipfile import ZipFile

import numpy as np
import pandas as pd

from independent_audit import checked, read_json, trade


def vintage(a, m, baseline):
    keys = ["geo", "product", "partner"]
    result = a.set_index(keys).join(m.groupby(keys).VALUE.agg(["sum", "size"]), how="inner")
    assert result["size"].eq(12).all() and result.VALUE.notna().all()
    result["gap"] = result["sum"] - result.VALUE
    ref = pd.read_csv(baseline).set_index(keys).sort_index()
    expected = ref["monthly_minus_annual_cad_thousands"]
    pd.testing.assert_index_equal(result.sort_index().index, expected.index)
    np.testing.assert_allclose(result.gap.sort_index(), expected, atol=1e-7)
    return {"comparisons":len(result), "outside_rounding":int(result.gap.abs().gt(6.0500001).sum()),
            "largest_absolute_difference_CAD":float(result.gap.abs().max()*1_000)}


def validate_pilot(root):
    manifest = read_json(root/"data/phase4b/design_A_source_manifest.json")
    files = {r["name"]:checked(root,r) for r in manifest if r["status"]=="downloaded"}
    html = files["steel_implementation_2025-03598.html"].read_text().replace("\0","")
    legal = html.split("(j) The rates of duty set forth",1)[1].split("(k) Headings",1)[0]
    # Select the U.S. Chapter 72/73 tariff codes listed in 16(j).
    schedule = pd.read_csv(files["hts_2025_rev4.csv"], dtype=str, keep_default_na=False)
    lines = schedule["HTS Number"].str.replace(".","",regex=False)
    numeric = lines.loc[lines.str.fullmatch(r"\d{10}")]
    # The text identifies headings and selected 6-/8-digit subheadings.
    exceptions = re.search(r"\(except\s+subheadings (.*?)\)", legal, flags=re.S)
    excluded = set(re.findall(r"\b7216\.\d\d\.\d\d\b", exceptions[1]))
    listing = legal[:exceptions.start()] + legal[exceptions.end():]
    included = set(re.findall(r"\b7[23]\d\d(?:\.\d\d){0,2}\b", listing))
    assert excluded == {"7216.61.00","7216.69.00","7216.91.00"}
    inc = tuple(q.replace(".","") for q in included)
    exc = tuple(q.replace(".","") for q in excluded)
    core = set(numeric.loc[numeric.str.startswith(inc) & ~numeric.str.startswith(exc)])
    prior = root/"data/phase4b/tariff_pilot"
    ref = pd.read_csv(prior/"us_legal_hts10.csv",dtype=str)
    assert core == set(ref.loc[ref.scope.eq("covered_core_232"),"hts10"])
    duties = []
    for month in ("202501","202504","202505"):
        values=np.zeros(3,dtype="int64")
        with ZipFile(files[f"imdb{month[-4:]}.zip"]) as z, z.open("IMP_DETL.txt") as rows:
            assert re.search(rb"^1220[^\n]*CANADA",z.read("COUNTRY.txt"),flags=re.M)
            assert "104-118" in z.read("Documentation/IMP_DETL.lay").decode("latin1")
            for row in rows:
                if row[10:14]==b"1220" and row[:10].decode("ascii") in core:
                    assert row[22:28].decode("ascii")==month
                    values += [int(row[start:end]) for start,end in ((73,88),(88,103),(103,118))]
        duties.append({"month":month,"consumption_customs_value_usd":int(values[0]),
                       "dutiable_value_usd":int(values[1]),"calculated_duty_usd":int(values[2]),
                       "ratio":float(values[2]/values[0])})
    cols=list(duties[0])[1:]
    d=pd.DataFrame(duties).set_index("month")
    x=pd.read_csv(prior/"us_import_scope_totals.csv",dtype={"month":str}).query("scope=='covered_core_232'")
    x=x.set_index("month").rename(columns={"calculated_duties_over_consumption_value":"ratio"})
    pd.testing.assert_frame_equal(d[cols],x[cols],check_exact=False)
    support=pd.read_csv(prior/"canadian_coverage.csv",dtype={"hs6":str})
    support=support.loc[support.scope.eq("covered_core_232") & support.stable_ca_hs6_dictionary
                        & support.pre_positive_months.eq(37) & support.post_positive_months.eq(2)]
    us=set(support.loc[support.country.eq("US"),"hs6"])
    mx=set(support.loc[support.country.eq("MX"),"hs6"])
    assert len(us & mx)==4 and len({p[:4] for p in us})==24
    return {"core_hts10":len(core),"hts8":len({p[:8] for p in core}),"hs6":len({p[:6] for p in core}),
            "hs4":len({p[:4] for p in core}),"complete_us_hs4_from_locked_coverage":len({p[:4] for p in us}),
            "common_us_mexico_from_locked_coverage":sorted(us & mx),"duties":duties}


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument("--archive-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    root=args.archive_root
    receipt=next((root/"data/provenance").glob("acquisition-*.json"))
    records={r["pid"]:r for r in read_json(receipt)["sources"] if r["status"]=="downloaded"}
    previous=read_json(root/"data/provenance/phase3-supplementary-sources.json")
    active_a=trade(checked(root,records["12100173"]),"12100173","All sections","2020","2020","Trading partner","Export")
    active_m=trade(checked(root,records["12100175"]),"12100175","Total of all merchandise","2020-01","2020-12",
                   "Principal trading partners","Domestic export")
    old_a=trade(checked(root,previous["archived_annual"]),"12100133","All sections","2020","2020","Trading Partner","Export")
    old_m=trade(checked(root,previous["archived_monthly"]),"12100119","Total of all merchandise","2020-01","2020-12",
                "Principal trading partners","Domestic export")
    ans={"active_2020":vintage(active_a,active_m,root/"data/phase3/reconciliation_2020.csv"),
         "archived_2020":vintage(old_a,old_m,root/"data/phase3/reconciliation_2020_archived.csv"),
         "pilot":validate_pilot(root)}
    assert ans["active_2020"]["outside_rounding"]==228 and ans["archived_2020"]["outside_rounding"]==0
    args.out.write_text(json.dumps(ans,indent=2)+"\n")


if __name__=="__main__":
    main()
