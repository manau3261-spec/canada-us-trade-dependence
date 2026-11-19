"""Publication figures from the saved, preregistered Design C results."""

import argparse
import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, PercentFormatter
import pandas as pd

from .acquire import sha256, write_json

NAVY = "#14344C"
TEAL = "#177D80"
SLATE = "#465F74"
LIGHT = "#D9E4E9"
BG = "#FFFFFF"

ROBUST_LABELS = {
    "primary": ("Primary", "Principale"),
    "A_no_C14": ("Exclude metal/mineral products (C14)", "Sans produits métalliques et minéraux (C14)"),
    "B_positive": ("Positive portfolios, no extra floor", "Portefeuilles positifs, sans seuil"),
    "B_100k": ("CAD 100,000 minimum", "Seuil de 100 000 $ CA"),
    "B_10m": ("CAD 10 million minimum", "Seuil de 10 millions $ CA"),
    "C_balanced": ("Balanced 14-year panels", "Panels équilibrés sur 14 ans"),
    "D_lag_weighted": ("Weighted by lagged export value", "Pondération selon les exportations retardées"),
    "E_signed": ("Signed export change", "Variation signée des exportations"),
    "F_downside": ("Downside magnitude", "Ampleur des baisses"),
    "G_top1_non_us": ("Largest non-U.S. destination share", "Part du premier marché hors États-Unis"),
    "G_top3_non_us": ("Top-three non-U.S. destination share", "Part des trois premiers marchés hors États-Unis"),
    "G_destination_hhi": ("HHI including the U.S.", "IHH incluant les États-Unis"),
    "H_end_2024": ("End the outcome window in 2024", "Fin de la période de résultat en 2024"),
    "J_even": ("Non-overlapping years, even starts", "Années sans chevauchement, départ pair"),
    "J_odd": ("Non-overlapping years, odd starts", "Années sans chevauchement, départ impair"),
    "J_2year": ("Non-overlapping two-year windows", "Fenêtres de deux ans sans chevauchement"),
}

FR_PROVINCES = {
    "Alberta": "Alberta", "British Columbia": "Colombie-Britannique", "Manitoba": "Manitoba",
    "New Brunswick": "Nouveau-Brunswick", "Newfoundland and Labrador": "Terre-Neuve-et-Labrador",
    "Nova Scotia": "Nouvelle-Écosse", "Ontario": "Ontario", "Prince Edward Island": "Île-du-Prince-Édouard",
    "Quebec": "Québec", "Saskatchewan": "Saskatchewan",
}


def page(title, sub, note, size):
    fig = plt.figure(figsize=size, facecolor=BG)
    fig.text(.053, .956, title, size=17, color=NAVY, weight="bold", va="top")
    fig.text(.053, .91, sub, size=10, color=SLATE, va="top")
    fig.text(.053, .045, note, size=8.2, color=SLATE, va="bottom", linespacing=1.5)
    return fig


def forest(ax, rows, labels, x_label, ticks=.04, primary=None):
    ax.axvline(0, color="#677984", lw=1.0, ls=(0, (4, 4)), zorder=1)
    if primary is not None:
        ax.axvline(primary, color=TEAL, lw=1, alpha=.7, zorder=1)
    for i, (point, low, high) in enumerate(rows):
        color = TEAL if i == 0 and primary is None else NAVY
        ax.hlines(i, low, high, color=color, linewidth=1.5, zorder=2)
        ax.scatter(point, i, color=color, s=30, zorder=3)
    ax.set_yticks(range(len(rows)), labels=labels)
    ax.set_ylim(len(rows)-.45, -.55)
    ax.set_xlabel(x_label, labelpad=12)
    ax.xaxis.set_major_locator(MultipleLocator(ticks))
    ax.grid(axis="x", color=LIGHT, linewidth=.65)
    ax.tick_params(axis="y", length=0, pad=8)
    ax.tick_params(axis="x", length=3)
    ax.spines[["left", "top", "right"]].set_visible(False)
    ax.spines["bottom"].set_color(LIGHT)
    ax.margins(x=.09)


def scoping_note(lang):
    return ("Source: Statistics Canada, table 12-10-0173-01, pinned 2026-11-18 vintage. "
            "Domestic non-U.S. merchandise exports in current CAD."
            if lang == "en" else
            "Source : Statistique Canada, tableau 12-10-0173-01, millésime du 18 nov. 2026. "
            "Exportations nationales hors États-Unis en dollars canadiens courants.")


def render(data, figures):
    estimates = pd.read_csv(data/"primary_regression.csv")
    hhi = estimates.loc[estimates.term.eq("hhi_ex_us")].set_index("covariance")
    main = hhi.loc["province"]
    model = json.loads((data/"primary_diagnostics.json").read_text())
    ci = model["webb_wild_restricted"]["ci_95_beta_components"]
    sensitivity = pd.read_csv(data/"robustness_summary.csv").set_index("specification")
    provinces = pd.read_csv(data/"province_influence.csv").sort_values("partial_predictor_leverage", ascending=False)
    manifest = {}
    mpl.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "text.color": NAVY,
                         "axes.labelcolor": NAVY, "xtick.color": SLATE, "ytick.color": NAVY,
                         "svg.fonttype": "none", "svg.hashsalt": "canada-trade-4b"})
    for lang in ("en", "fr"):
        fr = lang == "fr"
        sub = ("Variations annuelles absolues du log des exportations hors États-Unis · 2011–2024"
               if fr else "Absolute annual log changes in non-U.S. exports · Outcome start years 2011–2024")
        unit = ("Variation en points logarithmiques par +0,10 d’IHH" if fr
                else "Change in log points per +0.10 HHI")
        labels = (["Bootstrap restreint de Webb", "Grappes provinciales", "Grappes de produits",
                   "Double regroupement province et produit", "Grappes province–produit"] if fr else
                  ["Restricted Webb bootstrap", "Province clustering", "Product clustering",
                   "Two-way province and product", "Province–product clustering"])
        fig = page("Concentration et variation des exportations" if fr else "Concentration and changes in exports",
                   sub, scoping_note(lang), (10.6, 5.0))
        ax = fig.add_axes([.35, .22, .60, .58])
        # The registered chart represents the closed interval actually obtained.
        lower, upper = ci[0] if len(ci) == 1 else (None, None)
        primary_band = (main.coefficient*.1, lower*.1, upper*.1) if lower is not None and upper is not None else None
        rows = [tuple(hhi.loc[k, ["coefficient", "ci_low", "ci_high"]]*.1)
                for k in ("province", "product", "province_and_product", "province_product")]
        if primary_band is None:
            labels = labels[1:]
        else:
            rows.insert(0, primary_band)
        forest(ax, rows, labels, unit)
        ax.text(.99, 1.055, "Intervalles à 95 %" if fr else "95% intervals",
                transform=ax.transAxes, ha="right", color=SLATE)
        manifest.update(save(fig, figures/lang, "01_primary_inference"))

        note = (("Intervalles à 95 % avec regroupement provincial. Les fenêtres de deux ans sont exprimées par an.\n"
                 if fr else "95% province-clustered intervals. Two-year changes are annualized in log points.\n")
                + scoping_note(lang))
        robustness_sub = ("Résultat principal et variantes · Exportations hors États-Unis"
                          if fr else "Primary and sensitivity outcomes · Non-U.S. exports")
        fig = page("Sensibilité aux choix de spécification" if fr else "Sensitivity to specification choices",
                   robustness_sub, note, (11.7, 8.3))
        ax = fig.add_axes([.40, .18, .55, .66])
        keys = ["primary", "A_no_C14", "B_positive", "B_100k", "B_10m", "C_balanced", "D_lag_weighted",
                "H_end_2024", "J_even", "J_odd", "J_2year", "E_signed", "F_downside"]
        rows = [tuple(main[["coefficient", "ci_low", "ci_high"]]*.1)]
        rows.extend(tuple(sensitivity.loc[k, ["coefficient", "ci_low", "ci_high"]]*.1) for k in keys[1:])
        forest(ax, rows, [ROBUST_LABELS[k][int(fr)] for k in keys], unit, ticks=.05)
        for cut in (.5, 7.5, 10.5):
            ax.axhline(cut, color=LIGHT, linewidth=.65)
        manifest.update(save(fig, figures/lang, "02_specification_sensitivity"))

        title = ("Influence et levier par province" if fr else "Provincial influence and support")
        note = (("À gauche, estimation sans la province indiquée et intervalle à 95 %. La ligne verte indique l’estimation complète.\n"
                 if fr else "Left shows the estimate after omitting the named province and its 95% clustered interval. "
                 "Teal marks the full-sample estimate.\n") + scoping_note(lang))
        fig = page(title, sub, note, (12.1, 6.6))
        ax = fig.add_axes([.29, .22, .38, .56])
        labels = [FR_PROVINCES[g] if fr else g for g in provinces.geo]
        rows = list(provinces[["coefficient", "ci_low", "ci_high"]].mul(.1).itertuples(index=False, name=None))
        forest(ax, rows, labels, unit, ticks=.04, primary=main.coefficient*.1)
        other = fig.add_axes([.73, .22, .21, .56], sharey=ax)
        other.barh(range(len(provinces)), provinces.partial_predictor_leverage, height=.52, color=TEAL, alpha=.82)
        other.set_xlim(0, .22)
        other.xaxis.set_major_locator(MultipleLocator(.05))
        other.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
        other.set_xlabel("Part du levier partiel" if fr else "Share of partial HHI leverage", labelpad=12)
        other.grid(axis="x", color=LIGHT, linewidth=.65)
        other.set_axisbelow(True)
        other.tick_params(left=False, labelleft=False)
        other.spines[["left", "top", "right"]].set_visible(False)
        other.spines["bottom"].set_color(LIGHT)
        manifest.update(save(fig, figures/lang, "03_province_influence"))
    write_json(figures/"manifest.json", manifest)
    return manifest


def save(figure, folder, stem):
    folder.mkdir(parents=True, exist_ok=True)
    png, svg = (folder/f"{stem}.{extension}" for extension in ("png", "svg"))
    figure.savefig(png, dpi=300)
    figure.savefig(svg, metadata={"Date": None})
    plt.close(figure)
    return {f"{folder.name}/{p.name}": sha256(p) for p in (png, svg)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data/phase4b"))
    parser.add_argument("--figures", type=Path, default=Path("figures/phase4b"))
    args = parser.parse_args()
    render(args.data, args.figures)
