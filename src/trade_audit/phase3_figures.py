"""Deterministic bilingual publication figures."""
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter, MaxNLocator

from .acquire import sha256
from .reports import FRENCH_GEOS
from .sources import JURISDICTIONS, TERRITORIES

INK, MUTED, GRID = "#172b3b", "#52646f", "#dce5eb"
BLUE, TEAL, RUST, GRAY = "#1c5275", "#087c75", "#a34a2c", "#8999a6"
MARKET_COLORS = [BLUE, RUST, TEAL, "#664592", "#77600d"]
PAPER = "#ffffff"
PRODUCTS = {
    "C11": ("Farm, fishing and intermediate food", "Produits agricoles, de la pêche et aliments intermédiaires"),
    "C12": ("Energy", "Énergie"),
    "C13": ("Metal ores and non-metallic minerals", "Minerais métalliques et minéraux non métalliques"),
    "C14": ("Metal and mineral products", "Produits métalliques et minéraux"),
    "C15": ("Chemicals, plastics and rubber", "Produits chimiques, plastiques et caoutchouc"),
    "C16": ("Forestry, building and packaging", "Produits forestiers, de construction et d’emballage"),
    "C17": ("Industrial machinery and parts", "Machines et pièces industrielles"),
    "C18": ("Electrical and electronic equipment", "Matériel électrique et électronique"),
    "C19": ("Motor vehicles and parts", "Véhicules automobiles et pièces"),
    "C21": ("Aircraft and other transport", "Aéronefs et autre matériel de transport"),
    "C22": ("Consumer goods", "Biens de consommation"),
    "C23": ("Special transactions", "Transactions spéciales"),
}
SHORT_PRODUCTS = {
    "C11": ("Farm, fish and food", "Agriculture, pêche et aliments"),
    "C13": ("Ores and minerals", "Minerais et minéraux"),
    "C14": ("Metals and minerals", "Métaux et minéraux"),
    "C15": ("Chemicals and plastics", "Chimie et plastiques"),
    "C16": ("Forestry and materials", "Forêt et matériaux"),
    "C17": ("Industrial machinery", "Machines industrielles"),
    "C18": ("Electrical equipment", "Matériel électrique"),
    "C19": ("Vehicles and parts", "Véhicules et pièces"),
    "C21": ("Aircraft and transport", "Aéronefs et transport"),
}
FR_MARKETS = {
    "China": "Chine", "United Kingdom": "Royaume-Uni", "Japan": "Japon",
    "Germany": "Allemagne", "Netherlands": "Pays-Bas", "South Korea": "Corée du Sud",
    "France": "France", "Mexico": "Mexique", "India": "Inde",
}
MONTHS = {
    "en": "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(),
    "fr": "janv. févr. mars avr. mai juin juill. août sept. oct. nov. déc.".split(),
}


def tr(lang: str, en: str, fr: str) -> str:
    return fr if lang == "fr" else en


def format_value(x: float, lang: str, decimals: int = 1) -> str:
    s = f"{x:.{decimals}f}"
    return s.replace(".", ",") if lang == "fr" else s


def percent(x: float, lang: str, decimals: int = 1) -> str:
    return format_value(x, lang, decimals) + (" %" if lang == "fr" else "%")


def percent_axis(lang: str) -> FuncFormatter:
    return FuncFormatter(lambda value, _: percent(value, lang, 0))


def region_label(geo: str, lang: str) -> str:
    return FRENCH_GEOS.get(geo, geo) if lang == "fr" else geo


def product_label(code: str, lang: str, short: bool = False) -> str:
    en, fr = SHORT_PRODUCTS.get(code, PRODUCTS[code]) if short else PRODUCTS[code]
    return tr(lang, en, fr)


def page(lang, title, subtitle, source, size, layout=(1, 1), **kwargs):
    fig, axes = plt.subplots(*layout, figsize=size, **kwargs)
    fig.text(.065, .956, title, ha="left", va="top", color=INK,
             fontsize=23, fontfamily="DejaVu Serif", fontweight="bold")
    fig.text(.066, .895, subtitle, ha="left", va="top", color=MUTED, fontsize=10.5)
    publisher = tr(lang, "Source — Statistics Canada", "Source — Statistique Canada")
    release = tr(lang, "4 Nov. 2026 release. Calculations from domestic merchandise exports.",
                 "Diffusion du 4 nov. 2026. Calculs à partir des exportations nationales de marchandises.")
    fig.text(.066, .050, f"{publisher} · {source}\n{release}", fontsize=8, color=MUTED,
             ha="left", va="bottom", linespacing=1.5)
    return fig, axes


def style(ax, axis="y"):
    ax.set_axisbelow(True)
    ax.grid(axis=axis, color=GRID, linewidth=.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="both", length=0, pad=6, colors=MUTED, labelsize=9)


def total(data, geo="Canada"):
    return data.loc[data["product"].eq("TOTAL") & data["geo"].eq(geo)].sort_values("period")


def national(data, lang):
    series = total(data["annual"])
    years = series["period"].astype(int)
    values = 100 * series["us_share"]
    fig, ax = page(lang, tr(lang, "Canada’s dependence on the U.S. market", "La dépendance du Canada au marché américain"),
                   tr(lang, "U.S. share of Canada’s domestic merchandise exports, 2010–2025 (%)",
                      "Part des États-Unis dans les exportations nationales de marchandises du Canada, 2010–2025 (%)"),
                   "12-10-0173-01", (11, 5.5))
    fig.subplots_adjust(left=.095, right=.925, top=.82, bottom=.19)
    style(ax)
    ax.plot(years, values, color=BLUE, lw=2.6, marker="o", ms=3.8)
    for i, offset, align in ((0, (0, 12), "center"), (len(series)-1, (7, -14), "left")):
        ax.scatter(years.iloc[i], values.iloc[i], color=BLUE, s=28, zorder=4)
        ax.annotate(percent(values.iloc[i], lang), (years.iloc[i], values.iloc[i]),
                    xytext=offset, textcoords="offset points", ha=align, color=BLUE,
                    fontsize=11, fontweight="bold")
    ax.set(xlim=(2009.55, 2025.95), ylim=(np.floor(values.min())-1.5, np.ceil(values.max())+1.5))
    ax.set_xticks([2010, 2013, 2016, 2019, 2022, 2025])
    ax.yaxis.set_major_formatter(percent_axis(lang))
    return fig


def ranking(data, lang):
    d = data["annual"]
    last = d.loc[d["period"].eq("2025") & d["product"].eq("TOTAL") & d["geo"].isin(JURISDICTIONS)]
    last = last.sort_values("us_share", ascending=True)
    reference = total(d).loc[lambda s: s["period"].eq("2025"), "us_share"].item() * 100
    subtitle = tr(lang, f"U.S. share of each jurisdiction’s exports (%) · Canada {percent(reference, lang)} · Territories in teal",
                  f"Part des États-Unis dans les exportations (%) · Canada {percent(reference, lang)} · Territoires en vert")
    fig, ax = page(lang, tr(lang, "Provincial and territorial exposure in 2025",
                           "Exposition des provinces et territoires en 2025"), subtitle, "12-10-0173-01", (11, 7.4))
    fig.subplots_adjust(left=.245 if lang == "fr" else .22, right=.94, top=.84, bottom=.15)
    style(ax, "x")
    y = np.arange(len(last))
    x = last["us_share"].to_numpy() * 100
    ax.barh(y, x, color=[TEAL if g in TERRITORIES else BLUE for g in last["geo"]], height=.65)
    ax.axvline(reference, color=MUTED, ls=(0, (4, 3)), lw=1.3, zorder=1)
    ax.set_yticks(y, [region_label(g, lang) for g in last["geo"]])
    ax.set(xlim=(0, 108), ylim=(-.65, len(last)-.35))
    ax.set_xticks(range(0, 101, 20))
    ax.xaxis.set_major_formatter(percent_axis(lang))
    for pos, value in zip(y, x, strict=True):
        ax.text(value + 1.0, pos, percent(value, lang, 2 if 0 < value < 1 else 1),
                va="center", color=INK, fontsize=9)
    return fig


def regions(data, lang):
    d = data["annual"]
    canada = total(d)
    fig, axes = page(lang, tr(lang, "How regional exposure evolved", "Évolution de l’exposition régionale"),
                     tr(lang, "U.S. share of domestic merchandise exports (%) · Dashed line shows Canada",
                        "Part des États-Unis dans les exportations nationales (%) · Tirets : ensemble du Canada"),
                     "12-10-0173-01", (13.3, 10), (4, 4), sharex=True, sharey=True)
    fig.subplots_adjust(left=.084, right=.966, top=.82, bottom=.13, hspace=.61, wspace=.25)
    for i, (ax, geo) in enumerate(zip(axes.flat, JURISDICTIONS)):
        group = total(d, geo)
        style(ax)
        ax.set_title(region_label(geo, lang), loc="left", fontsize=9.4, weight="bold", pad=7)
        ax.plot(canada["period"].astype(int), 100 * canada["us_share"], color=GRAY, lw=1.05, ls="--")
        ax.plot(group["period"].astype(int), 100 * group["us_share"],
                color=TEAL if geo in TERRITORIES else BLUE, lw=1.85)
        ax.set(xlim=(2010, 2025), ylim=(0, 105))
        ax.set_yticks([0, 50, 100])
        ax.set_xticks([2010, 2017, 2025])
        ax.yaxis.set_major_formatter(percent_axis(lang))
        ax.tick_params(labelbottom=i >= 8, labelsize=8)
    for ax in list(axes.flat)[len(JURISDICTIONS):]:
        ax.set_visible(False)
    return fig


def heatmap(data, lang):
    sel = data["annual"].loc[lambda d: d["geo"].eq("Canada") & d["product"].isin(PRODUCTS)]
    m = sel.pivot(index="product", columns="period", values="us_share").reindex(PRODUCTS) * 100
    fig, ax = page(lang, tr(lang, "U.S. exposure by product section", "Exposition aux États-Unis par section de produits"),
                   tr(lang, "U.S. share of exports within each Canadian NAPCS section, 2010–2025 (%)",
                      "Part des États-Unis dans les exportations canadiennes de chaque section du SCPAN, 2010–2025 (%)"),
                   "12-10-0173-01", (13, 7))
    fig.subplots_adjust(left=.38 if lang == "fr" else .325, right=.905, top=.83, bottom=.22)
    cmap = LinearSegmentedColormap.from_list("exposure", ["#f2f5ed", "#a0caca", "#367e99", "#154569"])
    cmap.set_bad("#dddddd")
    im = ax.imshow(np.ma.masked_invalid(m.to_numpy()), aspect="auto", cmap=cmap, vmin=0, vmax=100)
    ax.set_xticks([0, 3, 6, 9, 12, 15], m.columns[[0, 3, 6, 9, 12, 15]])
    ax.set_yticks(range(len(m)), [product_label(k, lang) for k in m.index], fontsize=9)
    ax.tick_params(length=0, pad=7, colors=INK)
    ax.spines[:].set_visible(False)
    for y, value in enumerate(m.iloc[:, -1]):
        if pd.notna(value):
            ax.text(15.72, y, percent(value, lang), ha="left", va="center", color=INK,
                    fontsize=9, clip_on=False)
    bar_ax = fig.add_axes([.51, .115, .39, .019])
    cb = fig.colorbar(im, cax=bar_ax, orientation="horizontal", ticks=[0, 25, 50, 75, 100],
                      format=percent_axis(lang))
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, colors=MUTED, labelsize=8)
    return fig


def hhi(data, lang):
    d = data["hhi"].loc[lambda d: d["geo"].eq("Canada")].copy()
    fig, axes = page(lang, tr(lang, "Concentration of Canada’s export destinations",
                            "Concentration des destinations d’exportation du Canada"),
                     tr(lang, "Herfindahl–Hirschman index (0–1) · Panels use different vertical scales",
                        "Indice de Herfindahl–Hirschman (0 à 1) · Les échelles verticales diffèrent"),
                     "12-10-0173-01 · 12-10-0129-01", (12, 6.1), (1, 2))
    fig.subplots_adjust(left=.092, right=.95, top=.79, bottom=.22, wspace=.31)
    for ax, measure, title in zip(
        axes, ("destination_hhi", "destination_hhi_ex_us"),
        (tr(lang, "All destinations", "Toutes les destinations"),
         tr(lang, "Excluding the United States", "Hors États-Unis")), strict=True
    ):
        style(ax)
        ax.set_title(title, loc="left", fontsize=12, weight="bold", pad=11)
        s = d.loc[d["measure"].eq(measure)].sort_values("period")
        years = s["period"].astype(int)
        ax.plot(years, s["reconstructed_hhi"], color=BLUE, lw=2.1,
                label=tr(lang, "Reconstructed", "Reconstitution"))
        ax.scatter(years, s["statcan_hhi"], s=22, facecolors="white", edgecolors=RUST, linewidths=1.15,
                   label=tr(lang, "Published", "Valeur publiée"), zorder=3)
        ax.set_xlim(2009.7, 2025.3)
        ax.set_xticks([2010, 2015, 2020, 2025])
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_value(x, lang, 2)))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.5, .114), ncol=2,
               frameon=False, fontsize=9)
    return fig


def markets(data, lang):
    d = data["portfolio"].loc[lambda d: d["is_identified_destination"]]
    chosen = d.loc[d["period"].eq("2025")].nlargest(5, "exports_cad_thousands")["partner"].tolist()
    totals = d.groupby("period")["non_us_cad_thousands"].first() / 1e6
    fig, (ax, total_ax) = page(lang, tr(lang, "How non-U.S. exports changed",
                                        "Évolution des exportations hors États-Unis"),
                              tr(lang, "Fixed set of the five largest non-U.S. destinations in 2025",
                                 "Ensemble fixe des cinq principaux marchés hors États-Unis en 2025"),
                              "12-10-0173-01", (12.4, 6.3), (1, 2),
                              gridspec_kw={"width_ratios": [1.55, 1]})
    fig.subplots_adjust(left=.083, right=.95, top=.785, bottom=.23, wspace=.27)
    style(ax)
    style(total_ax)
    ax.set_title(tr(lang, "Share of non-U.S. exports (%)", "Part des exportations hors États-Unis (%)"),
                 loc="left", fontsize=11, weight="bold", pad=10)
    for partner, color in zip(chosen, MARKET_COLORS, strict=True):
        s = d.loc[d["partner"].eq(partner)].sort_values("period")
        label = FR_MARKETS.get(partner, partner) if lang == "fr" else partner
        ax.plot(s["period"].astype(int), 100 * s["share_of_non_us"], color=color,
                lw=2, label=label, marker="o", ms=2.6)
    ax.set_xticks([2010, 2015, 2020, 2025])
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(percent_axis(lang))
    ax.legend(loc="upper left", bbox_to_anchor=(0, -.09), ncol=3, frameon=False, fontsize=8)
    total_ax.set_title(tr(lang, "Non-U.S. export value (CAD billions)", "Exportations hors États-Unis (G$ CA)"),
                       loc="left", fontsize=11, weight="bold", pad=10)
    total_ax.bar(totals.index.astype(int), totals, color=[TEAL if y == "2025" else BLUE for y in totals.index], width=.72)
    total_ax.set_xticks([2010, 2015, 2020, 2025])
    total_ax.set_ylim(0, totals.max() * 1.15)
    total_ax.annotate(format_value(totals.iloc[-1], lang), (2025, totals.iloc[-1]), xytext=(0, 5),
                      textcoords="offset points", ha="center", fontsize=9, color=TEAL, fontweight="bold")
    return fig


def recent(data, lang):
    s = total(data["monthly"])
    d = pd.to_datetime(s["period"], format="%Y-%m")
    fig, (ax, volume) = page(lang, tr(lang, "Canada’s recent monthly export exposure",
                                      "Exposition mensuelle des exportations canadiennes"),
                            tr(lang, "Customs basis, current dollars, unadjusted · January 2025 to September 2026",
                               "Base douanière, dollars courants, données brutes · Janvier 2025 à septembre 2026"),
                            "12-10-0175-01", (11.5, 7.4), (2, 1), sharex=True)
    fig.subplots_adjust(left=.10, right=.95, top=.81, bottom=.17, hspace=.43)
    for pan in (ax, volume):
        style(pan)
        pan.axvline(pd.Timestamp("2026-01-01"), color=GRAY, ls="--", lw=1)
    ax.set_title(tr(lang, "U.S. share of domestic exports (%)", "Part des États-Unis dans les exportations (%)"),
                 loc="left", weight="bold", fontsize=11, pad=9)
    ax.plot(d, 100 * s["us_share"], color=BLUE, marker="o", lw=2.2, ms=3.2)
    ax.yaxis.set_major_formatter(percent_axis(lang))
    ax.yaxis.set_major_locator(MaxNLocator(5))
    volume.set_title(tr(lang, "Exports by broad destination (CAD billions)", "Exportations par grande destination (G$ CA)"),
                     loc="left", weight="bold", fontsize=11, pad=9)
    volume.plot(d, s["us_cad_thousands"] / 1e6, color=BLUE, lw=2, label=tr(lang, "United States", "États-Unis"))
    volume.plot(d, s["non_us_cad_thousands"] / 1e6, color=TEAL, lw=2, label=tr(lang, "Other markets", "Autres marchés"))
    volume.set_ylim(bottom=0)
    volume.legend(loc="center right", frameon=False, fontsize=8)
    ticks = pd.date_range("2025-01-01", d.max(), freq="2MS")
    volume.set_xticks(ticks, [f"{MONTHS[lang][x.month-1]} {str(x.year)[-2:]}" for x in ticks])
    ax.set_xlim(d.min() - pd.Timedelta(days=10), d.max() + pd.Timedelta(days=10))
    return fig


def decomposition(data, lang):
    raw = data["decomposition"]
    d = raw.loc[raw["start_year"].eq("2024") & raw["product"].ne("ROUNDING")]
    d = d.sort_values("total_contribution_pp")
    fig, (products, overall) = page(lang, tr(lang, "Decomposing Canada’s U.S. export share",
                                                "Décomposition de la part des États-Unis"),
                                    tr(lang, "Midpoint decomposition of the U.S. share · Percentage-point contributions",
                                       "Décomposition au point milieu de la part américaine · Contributions en points de pourcentage"),
                                    "12-10-0173-01", (13, 7), (1, 2),
                                    gridspec_kw={"width_ratios": [1.35, 1]})
    fig.subplots_adjust(left=.235 if lang=="fr" else .195, right=.947, top=.80, bottom=.18, wspace=.40)
    style(products, "x")
    style(overall, "x")
    y = np.arange(len(d))
    products.barh(y+.16, d["within_product_pp"], height=.27, color=BLUE,
                  label=tr(lang, "Within product", "Au sein des produits"))
    products.barh(y-.16, d["composition_pp"], height=.27, color=TEAL,
                  label=tr(lang, "Product mix", "Composition des produits"))
    products.axvline(0, color=MUTED, lw=.95)
    products.set_yticks(y, [product_label(code, lang, True) for code in d["product"]], fontsize=8)
    products.set_title(tr(lang, "Product contributions, 2024–2025", "Contributions des produits, 2024–2025"),
                       fontsize=11, weight="bold", loc="left", pad=9)
    products.legend(loc="upper center", bbox_to_anchor=(.49, -.08), ncol=2, fontsize=8, frameon=False)
    overall.set_title(tr(lang, "Net change and components", "Variation nette et composantes"),
                      fontsize=11, weight="bold", loc="left", pad=9)
    overall.axvline(0, color=MUTED, lw=.95)
    for i, (start, color) in enumerate((("2010", GRAY), ("2024", BLUE))):
        s = raw.loc[raw["start_year"].eq(start)]
        vals = [s["within_product_pp"].sum(), s["composition_pp"].sum(), s["total_contribution_pp"].sum()]
        overall.barh(np.arange(3) + .18 * (2*i-1), vals, height=.30, color=color, label=f"{start}–2025")
    overall.set_yticks(range(3),
                       [tr(lang, "Within", "Au sein"), tr(lang, "Mix", "Composition"), tr(lang, "Net", "Variation")],
                       fontsize=8)
    overall.legend(loc="upper center", bbox_to_anchor=(.5, -.08), ncol=2, fontsize=8, frameon=False)
    for ax in (products, overall):
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: format_value(x, lang)))
    return fig


FIGURES = {
    "01_national_dependence": national,
    "02_regional_ranking_2025": ranking,
    "03_regional_evolution": regions,
    "04_product_heatmap": heatmap,
    "05_destination_concentration": hhi,
    "06_non_us_diversification": markets,
    "07_recent_monthly": recent,
    "08_exposure_decomposition": decomposition,
}
INPUTS = {
    "annual": "annual_exposure.csv", "monthly": "monthly_exposure.csv",
    "portfolio": "national_non_us_destinations.csv", "hhi": "destination_hhi_benchmark.csv",
    "decomposition": "national_exposure_decomposition.csv",
}


def render(data_dir: Path, chart_dir: Path) -> dict:
    data = {
        name: pd.read_csv(data_dir / file, dtype={"period": str, "start_year": str, "end_year": str})
        for name, file in INPUTS.items()
    }
    config = {
        "font.family": "DejaVu Sans", "text.color": INK, "axes.labelcolor": INK,
        "axes.titlecolor": INK, "figure.facecolor": PAPER, "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER, "svg.hashsalt": "canada-trade-phase3", "axes.unicode_minus": True,
    }
    result = {}
    with mpl.rc_context(config):
        for lang in ("en", "fr"):
            directory = chart_dir / lang
            directory.mkdir(parents=True, exist_ok=True)
            for name, draw in FIGURES.items():
                figure = draw(data, lang)
                try:
                    for ext, meta in (("svg", {"Date": None}), ("png", {"Software": "Matplotlib"})):
                        path = directory / f"{name}.{ext}"
                        figure.savefig(path, dpi=220, metadata=meta)
                        result[path.relative_to(chart_dir).as_posix()] = sha256(path)
                finally:
                    plt.close(figure)
    return result
