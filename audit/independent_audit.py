"""Rebuild Phase 6 claims directly from locked raw files, without project imports.

Run with Python 3.14 and the Phase 5 requirements:
  python audit/independent_audit.py --archive-root /path/to/historical/workspace --out results
"""
from argparse import ArgumentParser
from hashlib import file_digest
from itertools import product
import json
import math
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from scipy.linalg import svd
from scipy.stats import t as t_dist

WORLD = "All countries"
US = "United States"
OTHER = {"Canada", "Other countries", "Unknown or unspecified"}
BAD = {"x", "X", "F", "f", "..", "...", "."}
GEOS = sorted(("Alberta", "British Columbia", "Manitoba", "New Brunswick",
    "Newfoundland and Labrador", "Nova Scotia", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan"))
CODES = [f"C{i}" for i in (*range(11, 20), 21, 22)]
NAPCS = "North American Product Classification System (NAPCS)"
CELL = ["geo", "product", "t"]
FE = [("geo","product"),("product","t"),("geo","t")]
METRICS = ["coefficient","standard_error","ci_low","ci_high","p_value","t","df"]


def read_json(path):
    return json.loads(path.read_text())


def file_sha(path):
    with path.open("rb") as f:
        return file_digest(f,"sha256").hexdigest()


def checked(root, rec):
    path = root/rec["path"]
    if file_sha(path) != rec["sha256"]:
        raise ValueError(f"Raw source has changed: {rec['path']}")
    return path


def raw_rows(path, name, cols, select):
    frames = []
    with ZipFile(path) as z, z.open(name) as f:
        parser = pd.read_csv(f, usecols=cols, dtype="str",
                             keep_default_na=False, chunksize=230_000)
        for b in parser:
            keep = select(b)
            if keep.any():
                frames.append(b.loc[keep].copy())
    d = pd.concat(frames,ignore_index=True)
    d["VALUE"] = pd.to_numeric(d.VALUE,errors="coerce").where(~d.STATUS.isin(BAD))
    return d


def trade(path, pid, level, first, last, partner_name, flow, totals_only=False):
    cols = ["REF_DATE","GEO",partner_name,NAPCS,"Trade","UOM","SCALAR_FACTOR","DECIMALS","VALUE","STATUS"]
    def select(d):
        use = d.REF_DATE.between(first,last) & d.Trade.eq(flow)
        if totals_only:
            use &= d[NAPCS].eq(level) & d[partner_name].isin([WORLD,US])
        return use
    d = raw_rows(path,f"{pid}.csv",cols,select)
    assert d.UOM.eq("Dollars").all() and d.SCALAR_FACTOR.eq("thousands").all()
    d["product"] = d[NAPCS].str.extract(r"\[(C\d{2})\]\s*$",expand=False).where(~d[NAPCS].eq(level),"TOTAL")
    assert d["product"].notna().all()
    d = d.rename(columns={"REF_DATE":"period","GEO":"geo",partner_name:"partner"})
    assert not d.duplicated(["period","geo","product","partner"]).any()
    return d


def trade_rows(d, concentration):
    rows = []
    for key, part in d.groupby(["period","geo","product"],sort=True):
        part = part.set_index("partner")
        w, u = part.loc[[WORLD,US],"VALUE"]
        x = w-u
        share = u/w if w>0 and 0<=u<=w else np.nan
        all_hhi = exc = max1 = top3 = positive = np.nan
        partners = part.drop(WORLD)
        if concentration and not np.isnan(share):
            vals = partners.VALUE.to_numpy()
            tolerance = np.sum(.5 * 10.**(-part.DECIMALS.astype(float))) + 1e-7
            reserved = partners.loc[partners.index.isin(OTHER),"VALUE"]
            valid = (len(vals)==258 and np.isfinite(vals).all() and vals.min()>=0 and (reserved==0).all()
                     and abs(vals.sum()-w)<=tolerance)
            if valid:
                all_hhi = sum((vals/w)**2)
                if not 0 <= all_hhi <= 1:
                    all_hhi = np.nan
                if x>tolerance:
                    other = partners.drop(US).VALUE.to_numpy()
                    val = sum((other/x)**2)
                    if 0<=val<=1:
                        exc = val
                        ordered = np.sort(other)
                        max1, top3 = np.minimum(1,[ordered[-1]/x,ordered[-3:].sum()/x])
                        positive = np.sum(other>0)
        rows.append((*key,w,u,x,share,all_hhi,exc,max1,top3,positive))
    return pd.DataFrame(rows,columns=["period","geo","product","world_cad_thousands","us_cad_thousands",
        "non_us_cad_thousands","us_share","destination_hhi","destination_hhi_ex_us","top1","top3","dest_count"])


def check_tables(fresh, stored, keys, columns, atol=1e-7):
    a=fresh.sort_values(keys).reset_index(drop=True)
    b=stored.sort_values(keys).reset_index(drop=True)
    assert a[keys].equals(b[keys]), (len(a),len(b),keys)
    delta = {}
    for col in columns:
        np.testing.assert_allclose(a[col],b[col],rtol=2e-11,atol=atol,equal_nan=True,err_msg=col)
        diff=(a[col]-b[col]).abs().dropna()
        delta[col]=float(diff.max()) if len(diff) else None
    return delta


def fundamentals(root, records, out):
    annual_raw=trade(checked(root,records["12100173"]),"12100173","All sections","2010","2025","Trading partner","Export")
    annual=trade_rows(annual_raw,True)
    comparisons={"annual":check_tables(annual,pd.read_csv(root/"data/phase3/annual_exposure.csv",dtype={"period":str}),
        ["period","geo","product"],list(annual.columns[3:9]))}
    monthly_raw=trade(checked(root,records["12100175"]),"12100175","Total of all merchandise","2025-01","2026-09",
              "Principal trading partners","Domestic export",True)
    monthly=trade_rows(monthly_raw,False)
    prior=pd.read_csv(root/"data/phase3/monthly_exposure.csv",dtype={"period":str})
    comparisons["monthly_all_product"]=check_tables(monthly,prior.loc[prior["product"].eq("TOTAL")],
        ["period","geo","product"],list(monthly.columns[3:7]))
    matched=monthly.loc[monthly.period.str[-2:].le("09")].copy()
    matched["year"]=matched.period.str[:4].astype(int)
    sums=matched.groupby(["geo","year"],as_index=False)[list(monthly.columns[3:6])].sum()
    sums["us_share"]=sums.us_cad_thousands/sums.world_cad_thousands
    comparisons["matched"]=check_tables(sums,pd.read_csv(root/"data/phase3/matched_monthly_ytd.csv"),
             ["geo","year"],list(monthly.columns[3:7]))
    us_total=annual.loc[annual.geo.eq("Canada") & annual["product"].eq("TOTAL")].set_index("period")
    port=annual_raw.loc[annual_raw.geo.eq("Canada") & annual_raw["product"].eq("TOTAL")
                        & ~annual_raw.partner.isin({WORLD,US,*OTHER})]
    port=port[["period","partner","VALUE"]].copy()
    port["share"]=port.VALUE/port.period.map(us_total.non_us_cad_thousands)
    expected=pd.read_csv(root/"data/phase3/national_non_us_destinations.csv",dtype={"period":str})
    expected=expected.loc[expected.is_identified_destination].rename(columns={
        "exports_cad_thousands":"VALUE","share_of_non_us":"share"})
    comparisons["destination"]=check_tables(port,expected,["period","partner"],["VALUE","share"])

    # The section share identity holds before display rounding.
    national=annual.loc[annual.geo.eq("Canada")]
    current=national.loc[national.period.isin(["2024","2025"]) & national["product"].ne("TOTAL")]
    w=current.pivot(index="product",columns="period",values="world_cad_thousands").div(us_total.world_cad_thousands,
                                                                                    axis="columns")
    s=current.pivot(index="product",columns="period",values="us_share")
    by_section=pd.DataFrame({"within_pp":100*w.mean(axis=1)*(s["2025"]-s["2024"]),
                             "composition_pp":100*s.mean(axis=1)*(w["2025"]-w["2024"])})
    by_section["net_pp"]=by_section.sum(axis=1)
    by_section.to_csv(out/"annual_share_decomposition.csv")
    features={"annual_rows":len(annual),"monthly_total_rows":len(monthly),"destination_rows":len(port),
       "top5_nonUS_share":{p:float(port.loc[port.period.eq(p),"share"].nlargest(5).sum()) for p in ("2024","2025")},
       "national":{p:us_total.loc[p,["world_cad_thousands","us_cad_thousands","non_us_cad_thousands","us_share",
           "destination_hhi","destination_hhi_ex_us"]].where(pd.notna(us_total.loc[p])).to_dict() for p in ("2023","2024","2025")},
       "matched_Jan_Sep":sums.loc[sums.geo.eq("Canada")].to_dict("records"),
       "share_decomposition_2024_25_pp":by_section.sum().to_dict(),
       "energy_net_pp":float(by_section.loc["C12","net_pp"])}
    annual.to_csv(out/"annual_rebuilt.csv",index=False)
    return annual, features, comparisons


def external_benchmarks(root, records, annual):
    hp=checked(root,records["12100129"])
    cols=["REF_DATE","GEO","Partner countries","Canadian export concentration","Statistics","VALUE","STATUS"]
    h=raw_rows(hp,"12100129.csv",cols,lambda b:
        b.REF_DATE.between("2010","2025") & b["Canadian export concentration"].eq("Destination market")
        & b.Statistics.eq("Concentration ratio"))
    ref=pd.read_csv(root/"data/phase3/destination_hhi_benchmark.csv",dtype={"period":str})
    h=h.rename(columns={"REF_DATE":"period","GEO":"geo","VALUE":"statcan_hhi"})
    h["measure"]=np.where(h["Partner countries"].eq(WORLD),"destination_hhi","destination_hhi_ex_us")
    h=h[["period","geo","measure","statcan_hhi"]]
    comp=ref.merge(h,how="outer",on=["period","geo","measure"],suffixes=("_reported","_raw"),validate="one_to_one")
    np.testing.assert_allclose(comp.statcan_hhi_reported,comp.statcan_hhi_raw,equal_nan=True)
    gdp_id="36100711"
    n="North American Industry Classification System (NAICS)"
    g=raw_rows(checked(root,records[gdp_id]),gdp_id+".csv",["REF_DATE","GEO","Prices",n,"VALUE","STATUS","SCALAR_FACTOR"],
       lambda b: b.REF_DATE.between("2010","2025") & b.Prices.eq("Current dollars") & b[n].eq("All industries [T001]"))
    assert g.SCALAR_FACTOR.eq("millions").all()
    geo=annual.loc[annual["product"].eq("TOTAL") & annual.geo.ne("Canada")]
    g=g.rename(columns={"REF_DATE":"period","GEO":"geo","VALUE":"gdp"})
    g=geo.merge(g[["period","geo","gdp"]],on=["period","geo"],how="left",validate="one_to_one")
    g["us_exports_to_gdp"]=g.us_cad_thousands/(1_000*g.gdp)
    g["world_exports_to_gdp"]=g.world_cad_thousands/(1_000*g.gdp)
    original=pd.read_csv(root/"data/phase3/provincial_export_intensity.csv",dtype={"period":str})
    d=check_tables(g,original,["period","geo"],["us_exports_to_gdp","world_exports_to_gdp"])
    io="12100100"
    c="Country Code"
    v="Value added exports variable"
    pairs=[(US,"Value added due to foreign demand"),(US,"Jobs due to foreign demand"),
           ("Total of all countries","Value added"),("Total of all countries","Jobs")]
    rows=raw_rows(checked(root,records[io]),io+".csv",["REF_DATE","GEO",c,v,"Industry","Aggregation","VALUE","STATUS"],
      lambda b: b.REF_DATE.between("2010","2025") & b.Industry.eq("Total industries")
         & b.Aggregation.eq("Summary level") & b[c].isin([US,"Total of all countries"]) & b[v].isin([p[1] for p in pairs]))
    w=rows.pivot(index=["REF_DATE","GEO"],columns=[c,v],values="VALUE")
    a=w[pairs[0]]/w[pairs[2]]
    b=w[pairs[1]]/w[pairs[3]]
    va=pd.DataFrame({"us_demand_value_added_share":a,"us_demand_jobs_share":b}).reset_index().rename(
        columns={"REF_DATE":"period","GEO":"geo"})
    prior=pd.read_csv(root/"data/phase3/value_added_and_jobs_benchmarks.csv",dtype={"period":str})
    va=prior[["period","geo"]].merge(va,on=["period","geo"],how="left",validate="one_to_one")
    q=check_tables(va,prior,["period","geo"],list(va.columns[2:]))
    return {"official_HHI_rows":len(h),"GDP_ratios":d,"value_added_and_jobs_ratios":q,
             "national_2024_value_added": va.query("geo=='Canada' and period=='2024'").to_dict("records")[0],
             "provincial_2022_value_added": va.loc[va.period.eq("2022") & va.geo.isin(["Alberta","Saskatchewan","Ontario"])].to_dict("records")}


def cimt_audit(root, out):
    rec=read_json(root/"data/provenance/phase4a-cimt-sources.json")
    series=[]
    physical=[]
    counts={}
    for year in ("2024","2025"):
        with ZipFile(checked(root,rec[year])) as z:
            fname=next(n for n in z.namelist() if "ODPFN016_" in n and n.endswith(".csv"))
            with z.open(fname) as raw:
                src=pd.read_csv(raw, usecols=[1,2,5,6,7],dtype={"HS8":str},keep_default_na=False)
        src.columns=["hs8","country","value","qty","unit"]
        counts[year]=len(src)
        src["hs6"]=src.hs8.str[:6]
        series.append(src.groupby(["country","hs6"]).value.sum().rename(year))
        for market,hs in [("GB","71081210"),("CN","27090010")]:
            line=src.loc[src.country.eq(market) & src.hs8.eq(hs) & src.value.gt(0)]
            assert line.unit.nunique()==1 and line.qty.gt(0).all()
            physical.append({"year":int(year),"market":market,"hs8":hs,"unit":line.unit.iloc[0],
                "quantity":int(line.qty.sum()),"unit_value_cad":float(line.value.sum()/line.qty.sum())})
    all_hs=pd.concat(series,axis=1,join="outer")
    all_hs["change"]=all_hs["2025"].fillna(0)-all_hs["2024"].fillna(0)
    outside=all_hs.drop(index=US if US in all_hs.index.get_level_values(0) else "US",level=0)
    by=outside.groupby(level=1).change.sum()
    new=outside.change.sum()
    scenarios=[]
    goods=all_hs.index.get_level_values(1)
    for scope, keep in [("all products",goods.notna()),("excluding HS 710812",goods!="710812"),
                        ("excluding chapter 71",~goods.str.startswith("71"))]:
        by_dest=all_hs.loc[keep].groupby(level=0)[["2024","2025"]].sum()
        for year in ("2024","2025"):
            wh=by_dest[year].sum()
            us=by_dest.loc["US",year]
            no=by_dest[year].drop("US")
            scenarios.append({"scope":scope,"year":int(year),"world_cad":wh,"us_cad":us,"non_us_cad":no.sum(),
               "uk_cad":no["GB"],"uk_share_non_us":no["GB"]/no.sum(),"hhi_full":sum((by_dest[year]/wh)**2),
               "hhi_ex_us":sum((no/no.sum())**2)})
    table=pd.DataFrame(scenarios)
    deviations=check_tables(table,pd.read_csv(root/"data/phase4a/non_us_gold_exclusion_sensitivity.csv"),
        ["scope","year"],list(table.columns[2:]))
    table.to_csv(out/"cimt_scenarios.csv",index=False)
    pd.DataFrame(physical).to_csv(out/"matched_quantities.csv",index=False)
    ledger=pd.read_csv(root/"data/phase4a/hs6_country_value_changes.csv",dtype={"hs6":str},keep_default_na=False,na_values=[""])
    for k in ["2024","2025","change"]:
        ref=ledger.set_index(["country","hs6"])["change_cad" if k=="change" else f"value_cad_{k}"]
        pd.testing.assert_series_equal(all_hs[k].sort_index(),ref.sort_index(),check_names=False,check_dtype=False)
    return {"raw_observations":counts,"all_HS6_destination_rows":len(all_hs),"non_us_value_change_CAD":int(new),
        "gold_CAD":int(by["710812"]),"crude_CAD":int(by["270900"]),
        "gold_and_crude_share":float((by["710812"]+by["270900"])/new),
        "UK_change_CAD":int(outside.loc["GB","change"].sum()),"UK_unwrought_gold_change_CAD":int(outside.loc[("GB","710812"),"change"]),
        "scenarios":table.to_dict("records"),"scenario_differences":deviations,"physical":physical}


def construct(annual, starts, horizon=1):
    base=annual.assign(period=annual.period.astype(int)).set_index(["geo","product","period"])
    obs=[]
    for g,k,t in product(GEOS,CODES,starts):
        lag,start,end=[base.loc[g,k,date] for date in (t-1,t,t+horizon)]
        x=lag.non_us_cad_thousands*1000
        s=start.non_us_cad_thousands
        e=end.non_us_cad_thousands
        signed=(math.log(e)-math.log(s))/horizon if s>0 and e>0 else np.nan
        obs.append((g,k,t,x,lag.destination_hhi_ex_us,math.log(x) if x>0 else np.nan,lag.us_share,
            abs(signed),signed,max(-signed,0) if pd.notna(signed) else np.nan,lag.top1,lag.top3,lag.destination_hhi,lag.dest_count))
    return pd.DataFrame(obs,columns=[*CELL,"lag_exports_cad","hhi_ex_us","log_lag_exports","lag_us_share",
      "absolute_growth","signed_growth","downside","lag_top1_non_us","lag_top3_non_us","lag_destination_hhi","lag_positive_non_us_partners"])


def singleton_filter(d):
    while True:
        mask=np.ones(len(d),dtype=bool)
        for names in FE:
            mask &= d.groupby(list(names)).t.transform("size").to_numpy()>1
        if mask.all():
            return d
        d=d.loc[mask].copy()


def eligible(p, floor):
    d=p.loc[p.lag_exports_cad.ge(floor)].dropna(subset=["hhi_ex_us","absolute_growth","lag_us_share","log_lag_exports"])
    return singleton_filter(d)


def groups(d, cols):
    return pd.factorize(pd.MultiIndex.from_frame(d[list(cols)]),sort=True)[0]


def basis(A):
    U, spectra, V = svd(A,full_matrices=False,lapack_driver="gesdd")
    r=int((spectra > max(A.shape)*np.finfo(float).eps*spectra[0]).sum())
    return U[:,:r],spectra[:r],V[:r],r


def estimate(d, name, predictor, outcome, weight=False, bootstrap=False):
    terms=[predictor,"log_lag_exports","lag_us_share"]
    v=d[terms].to_numpy()
    raw_weights=d.lag_exports_cad.to_numpy() if weight else np.ones(len(d))
    sqrt_weight=np.sqrt(raw_weights/raw_weights.mean())
    y=d[outcome].to_numpy()*sqrt_weight
    dummies=np.column_stack([np.eye(a.max()+1)[a] for a in (groups(d,f) for f in FE)])
    X=np.column_stack([v,dummies])*sqrt_weight[:,None]
    U,s,V,rank=basis(X)
    uf,_,_,fixed_rank=basis(X[:,3:])
    assert rank-fixed_rank==3
    inverse=(V.T/s)@U.T
    theta=(inverse@y)[:3]
    residual=y-U@(U.T@y)
    n=len(d)
    variances={}
    for group, keys in {"province":("geo",),"product":("product",),"province_product":("geo","product")}.items():
        code=groups(d,keys)
        G=int(code.max()+1)
        incidence=np.eye(G)[code]
        totals=incidence.T@(inverse[:3].T*residual[:,None])
        variances[group]=(totals.T@totals * G/(G-1)*(n-1)/(n-rank),G)
    a,na=variances["province"]
    b,nb=variances["product"]
    c,_=variances["province_product"]
    variances["province_and_product"]=(a+b-c,min(na,nb))
    table=[]
    for kind,(vc,G) in variances.items():
        se=np.sqrt(np.diag(vc))
        stat=theta/se
        p=2*t_dist.sf(abs(stat),G-1)
        margin=se*t_dist.ppf(.975,G-1)
        for key, vals in zip(terms, zip(theta,se,theta-margin,theta+margin,p,stat, [G-1]*3)):
            table.append(dict(zip(METRICS, map(float,vals)),specification=name,term=key,covariance=kind))
    r=y - uf@(uf.T@y)
    yw=y-sqrt_weight*np.average(d[outcome],weights=raw_weights)
    rss=residual@residual
    fit={"n":n,"groups":int(d.groupby(["geo","product"]).ngroups),"rank":rank,"fixed_rank":fixed_rank,
         "rss":float(rss),"r_squared":float(1-rss/(yw@yw)),
         "adjusted_r_squared":float(1-rss/(yw@yw)*(n-1)/(n-rank)),
         "within_r_squared":float(1-rss/(r@r))}
    if bootstrap:
        fit["webb"]=wild_invert(X,y,U,inverse[0],theta[0],np.sqrt(a[0,0]),groups(d,("geo",)),rank)
    return table,fit


def wild_invert(X,y,U,influence,bhat,se,clusters,rank):
    """Fit via generalized inverse. Build each perturbation by a cluster basis.

    The two columns of each bootstrap score are affine functions of the tested
    null. Reuse the same draws for p-values and test inversion.
    """
    U0,_,_,_=basis(X[:,1:])
    ry=y-U0@(U0.T@y)
    ax=X[:,0]-U0@(U0.T@X[:,0])
    G=clusters.max()+1
    C=np.eye(G)[clusters]
    law=np.sqrt([.5,1,1.5])
    weights=np.random.default_rng(20261118).choice(np.r_[-law,law],size=(9999,G))
    factor=G/(G-1)*(len(y)-1)/(len(y)-rank)

    def perturb(v):
        Y=v[:,None]*C
        E=Y-U@(U.T@Y)
        B=influence@Y
        S=C.T@(influence[:,None]*E)
        return weights@B,weights@S.T

    a,A=perturb(ry)
    b,B=perturb(-ax)
    vv=(A*A).sum(axis=1)
    ww=(A*B).sum(axis=1)
    zz=(B*B).sum(axis=1)
    def tail(null):
        sd=np.sqrt(factor*(vv+2*ww*null+zz*null**2))
        count=np.count_nonzero(np.abs((a+b*null)/sd)>=abs((bhat-null)/se))
        return (1+count)/10_000

    # Literal perturb-and-refit for the first 32 draws at two null values.
    literal_max=0.
    for null in (0.,.25):
        ystar=(ry-ax*null)[:,None]*weights[:32,clusters].T
        score=C.T@(influence[:,None]*(ystar-U@(U.T@ystar)))
        literal=(influence@ystar)/np.sqrt(factor*(score**2).sum(axis=0))
        affine=((a+b*null)/np.sqrt(factor*(vv+2*ww*null+zz*null**2)))[:32]
        literal_max=max(literal_max,float(np.max(abs(literal-affine))))
    assert literal_max < 5e-9
    values=np.linspace(bhat-12*se,bhat+12*se,481)
    accepted=np.array([tail(v)>=.05 for v in values])
    where=np.flatnonzero(accepted[1:]!=accepted[:-1])
    assert len(where)==2 and not accepted[0] and not accepted[-1]
    bounds=[]
    for i in where:
        lo,hi=values[i],values[i+1]
        for _ in range(18):
            mid=(lo+hi)/2
            if (tail(mid)>=.05)==accepted[i]:
                lo=mid
            else:
                hi=mid
        bounds.append(float((lo+hi)/2))
    return {"p_at_zero":tail(0),"bounds":bounds,"independent_literal_draws":64,"max_t_score_difference":literal_max}


def regressions(root,annual,out):
    p=construct(annual,range(2011,2025))
    main=eligible(p,1_000_000)
    comparison=check_tables(main,pd.read_csv(root/"data/phase4b/design_C_model_input.csv"),
         CELL,["lag_exports_cad","hhi_ex_us","log_lag_exports","lag_us_share","absolute_growth","signed_growth","downside"])
    results, fit=estimate(main,"primary","hhi_ex_us","absolute_growth",bootstrap=True)
    d=pd.DataFrame(results)
    old=pd.read_csv(root/"data/phase4b/primary_regression.csv")
    max_primary=check_tables(d,old,["term","covariance"],METRICS,atol=1e-8)
    d.to_csv(out/"model_primary.csv",index=False)
    reported=read_json(root/"data/phase4b/primary_diagnostics.json")
    w=reported["webb_wild_restricted"]
    assert abs(fit["webb"]["p_at_zero"]-w["p_at_zero"])<1e-12
    np.testing.assert_allclose(fit["webb"]["bounds"],w["ci_95_beta_components"][0],rtol=0,atol=3e-7)
    for s in ("rss","r_squared","adjusted_r_squared","within_r_squared"):
        assert abs(fit[s]-reported["fit"][s])<5e-10
    other={
      "A_no_C14":main.loc[main["product"].ne("C14")],
      "B_positive":eligible(p,0),"B_100k":eligible(p,100_000),"B_10m":eligible(p,10_000_000),
      "C_balanced":main.loc[main.groupby(["geo","product"]).t.transform("size").eq(14)],
      "H_end_2024":main.loc[main.t.le(2023)],
      "J_even":main.loc[main.t.mod(2).eq(0)],"J_odd":main.loc[main.t.mod(2).eq(1)],
      "J_2year":eligible(construct(annual,[2011,2014,2017,2020,2023],2),1_000_000),
      **{f"I_omit_{geo}":main.loc[~main.geo.eq(geo)] for geo in GEOS},
    }
    metadata=pd.read_csv(root/"data/phase4b/robustness_summary.csv").set_index("specification")
    results=[]
    for key,row in metadata.iterrows():
        data=other.get(key,main)
        data=singleton_filter(data.dropna(subset=[row.predictor]))
        tab,f=estimate(data,key,row.predictor,row.outcome,weight=key=="D_lag_weighted")
        assert f["n"]==row.n and f["groups"]==row.groups
        results.extend(tab)
    d=pd.DataFrame(results)
    old=pd.read_csv(root/"data/phase4b/robustness_regressions.csv")
    max_secondary=check_tables(d,old,["specification","term","covariance"],METRICS,atol=1e-8)
    d.to_csv(out/"model_robustness.csv",index=False)
    return {"input_rows":len(main),"fit":fit,"input_max_differences":comparison,
       "primary_inference_rows":len(pd.read_csv(root/"data/phase4b/primary_regression.csv")),
       "robustness_inference_rows":len(d),"primary_max_differences":max_primary,"robustness_max_differences":max_secondary}


def main():
    p=ArgumentParser(description=__doc__)
    p.add_argument("--archive-root",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    root=args.archive_root
    out=args.out
    out.mkdir(parents=True,exist_ok=True)
    receipt=next((root/"data/provenance").glob("acquisition-*.json"))
    records={r["pid"]:r for r in read_json(receipt)["sources"] if r["status"]=="downloaded"}
    for raw in records.values():
        checked(root,raw)
    print("Locked original Statistics Canada files verified",flush=True)
    ann, desc, differences=fundamentals(root,records,out)
    print("Annual, monthly and destination calculations checked",flush=True)
    benchmarks=external_benchmarks(root,records,ann)
    detailed=cimt_audit(root,out)
    print("Concentration, GDP, value added and detailed HS calculations checked",flush=True)
    model=regressions(root,ann,out)
    print("Independent SVD fit, CR1 variants and restricted Webb inversion checked",flush=True)
    report={"trade":desc,"max_differences":differences,"benchmarks":benchmarks,"HS":detailed,"model":model}
    def sanitize(obj):
        if isinstance(obj,dict):
            return {k:sanitize(v) for k,v in obj.items()}
        if isinstance(obj,list):
            return [sanitize(x) for x in obj]
        if isinstance(obj,np.generic):
            return obj.item()
        return obj
    (out/"independent_results.json").write_text(json.dumps(sanitize(report),indent=2,allow_nan=False)+"\n")

if __name__=="__main__":
    main()
