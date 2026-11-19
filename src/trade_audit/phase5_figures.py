"""Additional publication figures derived from the approved inputs."""

from pathlib import Path

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from .acquire import sha256, write_json
from .phase3_figures import PRODUCTS, SHORT_PRODUCTS, percent, region_label, tr
from .phase5_data import DEST_LABELS, HS_FOCUS, ROOT, bridge, exposure, load, partner_changes
from .sources import JURISDICTIONS

INK = "#173447"
TEAL = "#16786A"
BLUE = "#225C80"
RUST = "#9F4F33"
GRID = "#D8E5EB"


def style(axes):
    axes.set_axisbelow(True)
    axes.grid(axis="x", color=GRID, lw=.65)
    axes.spines[["right", "top", "left"]].set_visible(False)
    axes.spines["bottom"].set_color(GRID)
    axes.tick_params(axis="both", length=0, pad=6, labelcolor=INK)


def save(fig, path):
    results = {}
    for ext in (".png", ".svg"):
        target = path.with_suffix(ext)
        fig.savefig(target, dpi=300, facecolor="white",
                    metadata={"Date": None} if ext==".svg" else None)
        results[str(Path(target.parent.name)/target.name)] = sha256(target)
    plt.close(fig)
    return results


def render(root, data=None):
    data = data if data is not None else load(root)
    out = root/"figures/phase5"
    mpl.rcParams.update({"font.family":"DejaVu Sans", "font.size":11, "svg.fonttype":"none",
                         "svg.hashsalt":"canada-trade-phase-5", "text.color":INK, "axes.labelcolor":INK})
    manifest = {}
    for lang in ("en","fr"):
        loc = lang=="fr"
        folder=out/lang
        folder.mkdir(parents=True, exist_ok=True)
        annual=exposure(data,"Annual","2010","2025",JURISDICTIONS,["TOTAL"])
        m=annual.pivot(index="geo",columns="period",values="us_share").reindex(JURISDICTIONS)
        fig,ax=plt.subplots(figsize=(11,5.15))
        fig.subplots_adjust(left=.29,right=.92,top=.96,bottom=.12)
        palette=LinearSegmentedColormap.from_list("exposure",["#F1F7F3","#70B3A2","#10495A"]).with_extremes(bad="#ECEFEE")
        image=ax.imshow(m.to_numpy(),cmap=palette,vmin=0,vmax=1,aspect="auto")
        ax.set_yticks(range(len(m)),[region_label(g,lang) for g in m.index])
        ax.set_xticks(range(len(m.columns)),m.columns,rotation=45,ha="right")
        ax.tick_params(length=0,pad=6)
        ax.spines[:].set_visible(False)
        b=fig.colorbar(image,ax=ax,shrink=.9)
        ticks=(0,.25,.50,.75,1)
        b.set_ticks(ticks, labels=[percent(t*100,lang,0) for t in ticks])
        b.outline.set_visible(False)
        manifest.update(save(fig,folder/"01_province_year_heatmap"))

        codes=[c for c in PRODUCTS if c!="C23"]
        rows=exposure(data,"Annual","2025","2025",["Canada"],codes).sort_values("us_share")
        labels=[SHORT_PRODUCTS.get(c,PRODUCTS[c])[loc] for c in rows["product"]]
        fig,ax=plt.subplots(figsize=(11,5.05))
        fig.subplots_adjust(left=.32,right=.95,top=.94,bottom=.15)
        ax.barh(labels,rows.us_share*100,color=[BLUE if p=="C19" else TEAL for p in rows["product"]],height=.64)
        style(ax)
        ax.set_xlim(0,102)
        ticks=range(0,101,20)
        ax.set_xticks(ticks,[percent(v,lang,0) for v in ticks])
        ax.set_xlabel(tr(lang,"U.S. share of domestic merchandise exports","Part américaine des exportations nationales de marchandises"))
        manifest.update(save(fig,folder/"02_product_exposure_2025"))

        d=bridge(data)
        n=d.change_cad.to_numpy()/1e9
        bottoms=[0,n[0],n[0]+n[1],0]
        fig,ax=plt.subplots(figsize=(10.8,4.5))
        fig.subplots_adjust(left=.10,right=.95,top=.91,bottom=.20)
        ax.bar(range(4),n,bottom=bottoms,color=[TEAL,BLUE,"#7493A5",INK],width=.60)
        for i in range(3):
            ax.plot([i+.3,i+.7],[n[i]+bottoms[i]]*2,color="#7E8C97",lw=.9)
        for i,v in enumerate(n):
            text=f"{v:.2f}".replace(".",",") if loc else f"{v:.2f}"
            ax.text(i,bottoms[i]+v+.7,text,ha="center",color=INK,weight="bold")
        ax.set_ylim(0,34)
        ax.set_xticks(range(4),[tr(lang,"Unwrought gold","Or sous forme brute"),tr(lang,"Crude petroleum","Pétrole brut"),
                                tr(lang,"All other products","Autres produits"),tr(lang,"Net change","Variation nette")])
        ax.set_ylabel(tr(lang,"CAD billions, current dollars","Milliards de dollars canadiens courants"))
        ax.set_axisbelow(True)
        ax.grid(axis="y",color=GRID,lw=.65)
        ax.spines[["right","top"]].set_visible(False)
        ax.tick_params(length=0)
        manifest.update(save(fig,folder/"03_commodity_bridge"))

        d=partner_changes(data).dropna(subset="change_cad_thousands")
        import pandas as pd
        g=pd.concat([d.head(6),d.tail(3)]).sort_values("change_cad_thousands")
        labels=[DEST_LABELS.get(p,(p,p))[loc] for p in g.partner]
        x=g.change_cad_thousands/1e6
        fig,ax=plt.subplots(figsize=(10.8,4.65))
        fig.subplots_adjust(left=.23,right=.95,top=.95,bottom=.16)
        ax.barh(labels,x,color=[TEAL if v>=0 else RUST for v in x],height=.68)
        ax.axvline(0,color=INK,lw=.65)
        style(ax)
        ax.set_xlabel(tr(lang,"Change in CAD billions, current dollars","Variation en milliards de dollars canadiens courants"))
        manifest.update(save(fig,folder/"04_destination_change"))
    write_json(out/"manifest.json",manifest)
    return manifest


if __name__ == "__main__":
    render(ROOT)
