"""Local Canada–U.S. Trade Intelligence Monitor."""

import html
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(os.environ.get("CANADA_TRADE_ROOT", Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT/"src"))

from trade_audit.phase3_figures import PRODUCTS, product_label, region_label
from trade_audit.phase4b_figures import ROBUST_LABELS
from trade_audit.phase5_data import (
    COUNTRY_HS, DEST_LABELS, FOREST_IDS, HS_FOCUS, PERIODS, URLS, VINTAGE, bridge,
    destination_slice, exposure, hhi_trend, load, localized_number, partner_changes,
    primary, product_changes,
)
from trade_audit.sources import JURISDICTIONS, PROVINCES

st.set_page_config(page_title="Canada–U.S. Trade Intelligence Monitor", page_icon="📈", layout="wide")
st.html(ROOT/"dashboard/style.css")
INK = "#152D3C"
TEAL = "#12786A"
BLUE = "#215D87"
RUST = "#9B522F"
GRID = "#DFE8ED"
COLORS = [TEAL, BLUE, RUST, "#755582", "#6F660F", "#435866", "#A13A62"]
TITLES = {
    "national": ("National overview", "Vue d’ensemble nationale"),
    "province": ("Provincial exposure", "Exposition provinciale"),
    "products": ("Products and sectors", "Produits et secteurs"),
    "concentration": ("Destination concentration", "Concentration des destinations"),
    "decomposition": ("2024–2025 decomposition", "Décomposition de 2024 à 2025"),
    "model": ("Econometric results", "Résultats économétriques"),
    "pilot": ("Steel tariff pilot", "Projet pilote sur l’acier"),
    "sources": ("Sources and methodology", "Sources et méthodologie"),
}
lang = st.sidebar.radio("Language / Langue", ["en", "fr"], format_func=lambda v: {"en": "English", "fr": "Français"}[v],
                        horizontal=True, key="language")


def tr(en, fr):
    return fr if lang == "fr" else en


# Static, allowlisted script for assistive-technology pronunciation.
st.html(tr("<script>document.documentElement.lang = 'en';</script>",
           "<script>document.documentElement.lang = 'fr';</script>"),
        unsafe_allow_javascript=True)

st.sidebar.markdown(tr("### Canada–U.S. trade", "### Commerce Canada–États-Unis"))
st.sidebar.caption(tr("Domestic merchandise exports", "Exportations nationales de marchandises"))
section = st.sidebar.radio(tr("Sections", "Sections"), list(TITLES), format_func=lambda v: tr(*TITLES[v]), key="section")
st.sidebar.divider()
st.sidebar.caption(tr("Pinned vintage · 18 Nov 2026", "Millésime du 18 nov. 2026"))
st.sidebar.caption(tr("Manau Salaun · Independent research", "Manau Salaun · Recherche indépendante"))


@st.cache_resource(show_spinner="Validating archived inputs / Validation des données")
def inputs(root):
    return load(root)


try:
    D = inputs(ROOT)
except (OSError, ValueError, KeyError):
    st.error(tr(
        "The verified data are unavailable. Restore the locked files from the same release and reload.",
        "Les données vérifiées sont indisponibles. Restaurez les fichiers verrouillés de la même version, puis rechargez la page.",
    ))
    st.stop()


def num(value, decimals=1):
    return localized_number(value, decimals, lang) if pd.notna(value) else "—"


def pct(value):
    return num(value*100)+tr("%", " %") if pd.notna(value) else "—"


def region(value):
    return region_label(value, lang)


def product(value):
    return tr("All merchandise", "Toutes les marchandises") if value == "TOTAL" else product_label(value, lang)


def partner(value):
    return tr(*DEST_LABELS.get(value, (value, value)))


def unit_bn():
    return tr("CAD billions, current dollars", "Milliards de dollars canadiens courants")


def header(title, description, pills):
    values = ''.join(f"<span>{html.escape(v)}</span>" for v in pills)
    h = f'<div class="page-title"><div class="market-wordmark">{html.escape(tr("CANADA–U.S. TRADE INTELLIGENCE MONITOR", "OBSERVATOIRE DU COMMERCE CANADA–ÉTATS-UNIS"))}</div>'
    h += f'<h1>{html.escape(title)}</h1><p>{html.escape(description)}</p></div>'
    st.html(h + f'<div class="period-strip">{values}</div>')


def note(text):
    st.html(f'<div class="note-callout">{html.escape(text)}</div>')


def controls(freq, key):
    a, b = PERIODS[freq]
    years = list(range(int(a), int(b)+1)) if freq == "Annual" else list(pd.period_range(a, b, freq="M").astype(str))
    label = tr("Annual reference period", "Période annuelle") if freq=="Annual" else tr("Monthly reference period", "Période mensuelle")
    s, e = st.select_slider(label, years, value=(years[0], years[-1]), key=key)
    return str(s), str(e)


def base(figure, ylabel="", xlabel="", height=390, horizontal=False):
    figure.update_layout(template=None, height=height, font={"family": "Arial, sans-serif", "size": 14, "color": INK},
        margin={"l": 12, "r": 20, "t": 20, "b": 12}, paper_bgcolor="white", plot_bgcolor="white",
        hoverlabel={"bgcolor": "#FFFFFF", "font_color": INK}, separators=tr(".,", ", "),
        legend={"orientation": "h", "x":0, "y":1.05}, bargap=.26)
    figure.update_xaxes(title_text=xlabel, automargin=True, gridcolor=GRID, showgrid=horizontal, zerolinecolor="#657987")
    figure.update_yaxes(title_text=ylabel, automargin=True, gridcolor=GRID, showgrid=not horizontal, zerolinecolor="#657987")
    return figure


def source(label, url_keys, period, units):
    links = " · ".join(f"[{title}]({URLS[key]})" for title, key in url_keys)
    st.caption(f"{label} · {period} · {units} · {links}")


def chart(title, fig, desc, key):
    st.subheader(title, anchor=False)
    st.plotly_chart(fig, theme=None, key=key, width="stretch",
                    config={"displaylogo": False, "scrollZoom": False, "responsive": True})
    st.caption(desc)


def table(rows, slug, cols=None):
    frame = rows[cols].copy() if cols else rows.copy()
    with st.expander(tr("Data table and CSV", "Tableau de données et CSV")):
        st.dataframe(frame, width="stretch", hide_index=True, key=f"table_{slug}")
        st.download_button(tr("Download CSV", "Télécharger le CSV"), frame.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"{slug}.csv", mime="text/csv", on_click="ignore", key=f"download_{slug}")


def timeline(rows, specs, column="period", axis="", percent=False):
    fig = go.Figure()
    for label, col, color, dash in specs:
        fig.add_scatter(x=rows[column].tolist(), y=rows[col].tolist(), name=label, mode="lines+markers",
                        connectgaps=False, line={"width": 2.5, "color": color, "dash": dash},
                        marker={"size": 6}, hovertemplate=("%{x}<br>%{y:.1%}<extra>%{fullData.name}</extra>" if percent
                                                           else "%{x}<br>%{y:,.3f}<extra>%{fullData.name}</extra>"))
    f = base(fig, ylabel=axis)
    f.update_xaxes(type="category", nticks=9)
    if percent:
        f.update_yaxes(tickformat=".0%")
    return f


def bars(rows, value, labels, xaxis, percent=False):
    y = rows[labels].tolist()
    fig = go.Figure(go.Bar(x=rows[value].tolist(), y=y, orientation="h",
                         marker_color=[RUST if v < 0 else TEAL for v in rows[value]], name="",
                         hovertemplate="%{y}<br>%{x:.1%}<extra></extra>" if percent else "%{y}<br>%{x:,.3f}<extra></extra>"))
    base(fig, xlabel=xaxis, height=max(285, min(580, len(y)*33+105)), horizontal=True)
    fig.update_yaxes(autorange="reversed")
    if percent:
        fig.update_xaxes(tickformat=".0%")
    return fig


def forest(rows, point, lower, upper, label, x_label):
    fig = go.Figure(go.Scatter(x=rows[point].tolist(), y=rows[label].tolist(), mode="markers",
        name="", marker={"size":8,"color":BLUE}, error_x={"type":"data","symmetric":False,"color":TEAL,
          "array":(rows[upper]-rows[point]).tolist(),"arrayminus":(rows[point]-rows[lower]).tolist(),"thickness":1.6,"width":4},
        hovertemplate="%{y}<br>%{x:+.5f}<extra></extra>"))
    base(fig, xlabel=x_label, height=max(300, len(rows)*33+100), horizontal=True)
    fig.update_yaxes(autorange="reversed")
    fig.add_vline(x=0, line_dash="dash", line_color="#576D7A", line_width=1)
    return fig


PUBLISHER = tr("Statistics Canada", "Statistique Canada")
SHARE = tr("U.S. share of exports", "Part des exportations vers les États-Unis")
NONUS_SHARE = tr("Share of non-U.S. exports", "Part des exportations hors États-Unis")
FIXED = tr("Annual · 2010–2025", "Annuel · 2010–2025")
RECENT = tr("Monthly · to September 2026", "Mensuel · jusqu’en septembre 2026")
CURRENT = tr("Current Canadian dollars", "Dollars canadiens courants")
LOGUNIT = tr("Log points per +0.10 index", "Points logarithmiques pour +0,10 d’indice")


def show_national():
    header(TITLES["national"][lang=="fr"], tr("Follow Canada’s export exposure to the United States and the value shipped to other markets.",
        "Suivez l’exposition des exportations canadiennes aux États-Unis et les valeurs livrées aux autres marchés."), [FIXED, RECENT, CURRENT])
    freq = st.radio(tr("Trade frequency", "Fréquence des échanges"), ["Annual", "Monthly"], horizontal=True,
                    format_func=lambda f: tr("Annual","Annuel") if f=="Annual" else tr("Monthly","Mensuel"), key="national_frequency")
    start, end = controls(freq, f"national_period_{freq}")
    rows = exposure(D, freq, start, end, ["Canada"], ["TOTAL"]).sort_values("period")
    key = freq.lower()
    tail = rows.iloc[-1]
    st.caption(f"{tr('Selected endpoint','Fin de la période sélectionnée')} · {tail.period}")
    c = st.columns(4)
    c[0].metric(SHARE, pct(tail.us_share))
    for column, label, name in zip(c[1:],
        (tr("All destinations","Toutes destinations"), tr("United States","États-Unis"), tr("Outside the U.S.","Hors États-Unis")),
        ("world","us","non_us")):
        column.metric(label, num(tail[f"{name}_cad_thousands"]/1e6)+tr(" B CAD"," G$ CA"))
    fig = timeline(rows, [(SHARE,"us_share",TEAL,"solid")], axis=tr("Share of world exports","Part des exportations mondiales"), percent=True)
    chart(tr("National U.S. exposure", "Exposition nationale aux États-Unis"), fig,
          tr("Share of Canadian domestic merchandise exports destined for the United States.",
             "Part des exportations nationales de marchandises destinée aux États-Unis."), "national_share")
    source(PUBLISHER, [(f"12-10-01{73 if key=='annual' else 75}-01",key)], f"{start}–{end}", "%")
    st.divider()
    if key == "monthly":
        z = D["matched"].query("geo == 'Canada'")[["year","first_month","last_month","months","us_share",
                                                      "us_cad_thousands","non_us_cad_thousands","world_cad_thousands"]]
        st.subheader(tr("Matched January–September comparison", "Comparaison de janvier à septembre"), anchor=False)
        note(tr("This separate benchmark sums nine months per year. Observations are unadjusted for seasonality.",
                "Ce repère distinct additionne neuf mois par année. Les observations sont non désaisonnalisées."))
        source(PUBLISHER,[("12-10-0175-01","monthly")],"2025-01–09 · 2026-01–09",tr("CAD thousands and shares","Milliers de dollars canadiens et parts"))
        table(z, "national_matched_months")
    else:
        note(tr("Annual and monthly estimates come from separate source tables. Monthly windows never replace annual totals.",
                "Les estimations annuelles et mensuelles forment des séries distinctes. Les mois ne remplacent jamais les totaux annuels."))
    table(rows, f"national_{key}_{start}_{end}")


def show_province():
    header(tr(*TITLES["province"]), tr("Compare the share and dollar value of exports to the U.S. across provinces and territories.",
        "Comparez la part et la valeur des exportations vers les États-Unis selon la province ou le territoire."), [FIXED, CURRENT])
    c = st.columns(3)
    year = c[0].selectbox(tr("Reference year","Année de référence"), list(range(2025,2009,-1)), key="province_year")
    group = c[1].radio(tr("Coverage","Couverture"), ["all","provinces"], horizontal=True,
                       format_func=lambda s: tr("Include territories","Inclure les territoires") if s=="all" else tr("Provinces","Provinces"), key="province_group")
    choice = c[2].selectbox(tr("Rank by","Classer selon"), ["share","value"],
                           format_func=lambda v: SHARE if v=="share" else tr("U.S. export value","Valeur des exportations vers les États-Unis"), key="province_measure")
    geos = JURISDICTIONS if group=="all" else PROVINCES
    rows = exposure(D,"Annual",str(year),str(year),geos,["TOTAL"])
    rows["us_cad_billions"] = rows.us_cad_thousands/1e6
    rows["label"] = rows.geo.map(region)
    value = "us_share" if choice=="share" else "us_cad_billions"
    rows = rows.sort_values(value, ascending=False)
    chart(tr("Exposure ranking","Classement de l’exposition"), bars(rows, value, "label", SHARE if choice=="share" else unit_bn(),choice=="share"),
          tr("Ranking of jurisdictions by selected measure.","Classement des territoires selon la mesure choisie."), "province_rank")
    source(PUBLISHER,[("12-10-0173-01","annual")],str(year),"%" if choice=="share" else unit_bn())
    table(rows.drop(columns="label"),f"province_ranking_{year}_{choice}")
    keep = st.multiselect(tr("Jurisdictions in heatmap","Administrations dans la carte thermique"), list(geos),
                          default=list(geos), format_func=region, key="province_heat_geos")
    historical = exposure(D,"Annual","2010",str(year),keep,["TOTAL"])
    if historical.empty:
        st.info(tr("Select at least one jurisdiction.","Sélectionnez au moins une administration."))
        return
    pivot = historical.pivot(index="geo",columns="period",values="us_share").reindex(keep)
    fig = go.Figure(go.Heatmap(x=pivot.columns.tolist(),y=[region(g) for g in keep],z=pivot.to_numpy(),
          zmin=0,zmax=1,colorscale=[[0,"#E6F2EA"],[.55,"#6DAA98"],[1,"#104A59"]],
          colorbar={"tickformat":".0%","thickness":12},hoverongaps=False,hovertemplate="%{y} · %{x}<br>%{z:.1%}<extra></extra>"))
    base(fig,height=max(290,len(keep)*32+125))
    fig.update_xaxes(type="category",nticks=9)
    fig.update_yaxes(autorange="reversed")
    chart(tr("Province–year exposure heatmap","Carte thermique par province et année"),fig,
          tr("Darker cells indicate higher U.S. export shares. Blank cells indicate unavailable values.",
             "Les cellules foncées indiquent une part américaine élevée. Les cellules vides indiquent des données indisponibles."),"province_heat")
    source(PUBLISHER,[("12-10-0173-01","annual")],f"2010–{year}","%")
    table(historical,f"province_history_2010_{year}")


def show_products():
    header(tr(*TITLES["products"]),tr("Compare U.S. shares within merchandise product sections and trace them over time.",
        "Comparez les parts américaines dans les sections de produits de marchandises et leur évolution."),[FIXED,"NAPCS / SCPAN",CURRENT])
    c = st.columns(2)
    geo = c[0].selectbox(tr("Producing geography","Géographie de production"),["Canada",*JURISDICTIONS],format_func=region,key="product_geo")
    year = c[1].selectbox(tr("Reference year","Année de référence"),list(range(2025,2009,-1)),key="product_year")
    codes = st.multiselect(tr("Product sections","Sections de produits"),list(PRODUCTS),default=[p for p in PRODUCTS if p!="C23"],format_func=product,key="product_codes")
    if not codes:
        st.info(tr("Select a product section.","Sélectionnez une section de produits."))
        return
    rows = exposure(D,"Annual",str(year),str(year),[geo],codes).sort_values("us_share",ascending=False)
    plot = rows.dropna(subset="us_share").assign(label=lambda d:d["product"].map(product))
    chart(tr("Export exposure by section","Exposition des exportations par section"),
          bars(plot,"us_share","label",SHARE,True),tr("U.S. export share within each selected product section.",
          "Part américaine dans chaque section sélectionnée."),"products_rank")
    source(PUBLISHER,[("12-10-0173-01","annual")],f"{region(geo)} · {year}","%")
    table(rows,f"product_exposure_{year}")
    c = st.selectbox(tr("Product section history","Historique d’une section"),codes,format_func=product,key="product_history_section")
    start,end = controls("Annual","product_history_period")
    hist = exposure(D,"Annual",start,end,[geo],[c]).sort_values("period")
    chart(tr("Selected section over time","Évolution de la section choisie"),
          timeline(hist,[(product(c),"us_share",BLUE,"solid")],axis=SHARE,percent=True),
          tr("Annual U.S. share for the selected province and product.","Part américaine annuelle pour la géographie et le produit sélectionnés."),"products_trend")
    source(PUBLISHER,[("12-10-0173-01","annual")],f"{start}–{end}","%")
    table(hist,f"product_history_{c}_{start}_{end}")
    note(tr("NAPCS describes shipped merchandise. These sections do not measure NAICS industry output or employment.",
            "Le SCPAN décrit les marchandises expédiées. Ces sections ne mesurent ni la production ni l’emploi selon le SCIAN."))


def show_concentration():
    header(tr(*TITLES["concentration"]),tr("Follow how evenly exports are distributed across markets, with and without the U.S.",
           "Suivez la répartition des exportations entre les marchés, avec et sans les États-Unis."),[FIXED,tr("HHI · 0–1","IHH · 0–1")])
    c = st.columns(2)
    geo=c[0].selectbox(tr("Producing geography","Géographie de production"),["Canada",*JURISDICTIONS],format_func=region,key="hhi_geo")
    official=c[1].checkbox(tr("Show published benchmark","Afficher le repère officiel"),value=True,key="hhi_benchmark")
    start,end=controls("Annual","hhi_period")
    rows=hhi_trend(D,geo,start,end).sort_values("period")
    names=[tr("All destinations","Toutes les destinations"),tr("Excluding the U.S.","Hors États-Unis")]
    specs=[(names[0],"destination_hhi",BLUE,"solid"),(names[1],"destination_hhi_ex_us",TEAL,"solid")]
    if official:
        tag=tr("Published","Publié")
        specs += [(f"{tag} · {names[0]}","published_destination_hhi",BLUE,"dot"),
                  (f"{tag} · {names[1]}","published_destination_hhi_ex_us",TEAL,"dot")]
    chart(tr("Destination concentration","Concentration par destination"),timeline(rows,specs,axis=tr("HHI from 0 to 1","IHH de 0 à 1")),
          tr("Reconstructed and published concentration. A break marks a missing index.","Indices reconstruits et publiés. Les interruptions indiquent des données manquantes."),"hhi_trend")
    source(PUBLISHER,[("12-10-0173-01","annual"),("12-10-0129-01","hhi")],f"{region(geo)} · {start}–{end}",tr("Index, 0–1","Indice de 0 à 1"))
    table(rows[["period","geo",*[x[1] for x in specs]]],f"hhi_{start}_{end}")
    note(tr("Reconstructed gaps remain blank. Canada's 2020 aggregate has an unallocated Canada-labelled amount. Published estimates can use a different vintage.",
            "Les valeurs reconstruites manquantes restent vides. L’agrégat canadien de 2020 contient un montant non attribué libellé Canada. Le millésime des valeurs publiées peut différer."))
    partners = st.multiselect(tr("National destinations to compare","Destinations nationales à comparer"),
          [k for k in DEST_LABELS if k!="United States"],
          default=["United Kingdom","China","Japan","Mexico"],format_func=partner,key="dest_compare")
    selected=destination_slice(D,start,end,partners)
    if not selected.empty:
        p=selected.pivot(index="period",columns="partner",values="share_of_non_us").reset_index()
        lines=[(partner(k),k,COLORS[i%len(COLORS)],"solid") for i,k in enumerate(partners) if k in p.columns]
        chart(tr("Canada’s non-U.S. destination shares","Parts des destinations canadiennes hors États-Unis"),
             timeline(p,lines,axis=NONUS_SHARE,percent=True),tr("National destination comparison. Denominator excludes the U.S.",
             "Comparaison nationale. Les États-Unis sont exclus du dénominateur."),"destination_trend")
        source(PUBLISHER,[("12-10-0173-01","annual")],f"Canada · {start}–{end}","%")
        table(selected,f"national_destinations_{start}_{end}")


def show_decomposition():
    header(tr(*TITLES["decomposition"]),tr("Separate the commodity contribution to non-U.S. export growth from changes in destination concentration.",
          "Distinguez la contribution des produits à la croissance hors États-Unis de la concentration des destinations."),["2024–2025",CURRENT,"HS / SH"])
    d=bridge(D)
    d["change_cad_billions"]=d.change_cad/1e9
    labels = {"710812":tr(*HS_FOCUS["710812"]),"270900":tr(*HS_FOCUS["270900"]),
              "remainder":tr("All other products, net","Autres produits, contribution nette"),
              "total":tr("Total change","Variation totale")}
    d["label"]=d.component.map(labels)
    chart(tr("Gold and crude oil accounted for most of the gain","L’or et le pétrole brut expliquent l’essentiel du gain"),
          bars(d,"change_cad_billions","label",unit_bn()),tr("Change in non-U.S. domestic exports by component and in total.",
          "Variation des exportations nationales hors États-Unis, par composante et au total."),"commodity_bridge")
    source(PUBLISHER,[("CIMT HS6","hs")],"2024–2025",unit_bn())
    table(d.drop(columns="label"),"gold_crude_contribution")
    h=D["gold_hhi"]
    hplot=h.copy()
    hplot["year"]=hplot.year.astype(str)
    wide=hplot.pivot(index="year",columns="scope",values="hhi_ex_us").reset_index()
    chart(tr("Non-U.S. HHI with and without unwrought gold","IHH hors États-Unis, avec et sans l’or brut"),
          timeline(wide,[(tr("All products","Tous les produits"),"all products",BLUE,"solid"),
                         (tr("Excluding HS 710812","Sans le SH 710812"),"excluding HS 710812",TEAL,"solid"),
                         (tr("Excluding chapter 71","Sans le chapitre 71"),"excluding chapter 71",RUST,"dot")],
                   column="year",axis=tr("Non-U.S. HHI","IHH hors États-Unis")),
          tr("The denominators and shares are recalculated for each product exclusion.",
             "Les dénominateurs et les parts sont recalculés après chaque exclusion."),"gold_hhi")
    source(PUBLISHER,[("CIMT HS8","hs")],"2024–2025",tr("Index, 0–1","Indice de 0 à 1"))
    table(h,"gold_exclusion_scenarios")
    z=partner_changes(D).dropna(subset="change_cad_thousands")
    v=pd.concat([z.head(6),z.tail(3)]).drop_duplicates("partner").sort_values("change_cad_thousands",ascending=False)
    v=v.assign(label=v.partner.map(partner),change_cad_billions=v.change_cad_thousands/1e6)
    chart(tr("Largest destination gains and losses","Principaux gains et reculs par destination"),bars(v,"change_cad_billions","label",unit_bn()),
          tr("Largest six gains and three declines outside the United States.","Six plus fortes hausses et trois plus forts reculs hors États-Unis."),"dest_changes")
    source(PUBLISHER,[("12-10-0173-01","annual")],"Canada · 2024–2025",unit_bn())
    table(z,"non_us_destination_changes")
    country = st.selectbox(tr("HS6 detail destination","Destination pour le détail SH6"),["non_us",*[k for k in COUNTRY_HS if k!="US"]],
                            format_func=lambda k: tr("All non-U.S. markets","Tous les marchés hors États-Unis") if k=="non_us" else partner(COUNTRY_HS[k]),key="decomp_destination")
    detail=product_changes(D,None if country=="non_us" else country)
    top=pd.concat([detail.head(8),detail.tail(3)]).drop_duplicates("hs6").sort_values("change_cad",ascending=False)
    top=top.assign(label=top.hs6.map(lambda c:f"{c} · {tr(*HS_FOCUS[c])}" if c in HS_FOCUS else c),
                   change_cad_billions=top.change_cad/1e9)
    chart(tr("Detailed product contributions","Contributions détaillées des produits"),bars(top,"change_cad_billions","label",unit_bn()),
          tr("Largest eight gains and three declines by HS6 for the selected portfolio.","Huit principaux gains et trois principaux reculs par SH6 pour le portefeuille choisi."),"hs6_changes")
    source(PUBLISHER,[("CIMT HS6","hs")],"2024–2025",unit_bn())
    table(detail,f"hs6_change_{country.lower()}")
    qty=D["hs8"].loc[(D["hs8"].country.eq("GB")&D["hs8"].hs8.eq("71081210"))|
                      (D["hs8"].country.eq("CN")&D["hs8"].hs8.eq("27090010"))]
    table(qty,"selected_matched_physical_quantities")
    note(tr("Unwrought gold and crude petroleum dominate the nominal increase. Valid matched quantities exist for selected HS8 lines. Unit values vary with prices and the mix of shipments.",
         "L’or brut et le pétrole brut dominent la hausse nominale. Certaines lignes SH8 offrent des quantités comparables. La valeur unitaire varie avec les prix et la composition des envois."))


def show_model():
    header(tr(*TITLES["model"]),tr("Design C estimates how lagged destination concentration is associated with later annual export movements.",
          "Le modèle C estime l’association entre la concentration retardée et les variations annuelles ultérieures des exportations."),
           [tr("2011–2024 outcome-start years","Années de départ 2011–2024"),tr("Ten provinces","Dix provinces"),tr("Associational model","Modèle associatif")])
    p=primary(D)
    c=st.columns(4)
    c[0].metric(tr("Change per +0.10 HHI","+0,10 d’IHH"),num(p["scaled"],6))
    c[1].metric(tr("Restricted Webb p-value","Valeur p, bootstrap de Webb"),num(p["webb_p"],4))
    c[2].metric(tr("Eligible observations","Observations admissibles"),num(p["n"],0))
    c[3].metric(tr("Province–product groups","Groupes province–produit"),num(p["groups"],0))
    note(tr("The estimate is statistically inconclusive. The 95% Webb interval spans zero, and value weighting reverses the point estimate's sign.",
           "L’estimation est statistiquement non concluante. L’intervalle de Webb à 95 % inclut zéro et la pondération par la valeur inverse le signe de l’estimation."))
    r=D["regression"].query("term == 'hhi_ex_us'").copy()
    r=r.assign(label=r.covariance.map({
        "province":tr("Province CR1","Province CR1"),"product":tr("Product CR1","Produit CR1"),
        "province_product":tr("Province–product CR1","Province–produit CR1"),
        "province_and_product":tr("Two-way CR1","CR1 à deux dimensions"),
    }))
    r[["point","lower","upper"]]=r[["coefficient","ci_low","ci_high"]]*.1
    s=pd.concat([pd.DataFrame([{"label":tr("Restricted Webb","Bootstrap restreint de Webb"),"point":p["scaled"],"lower":p["ci_low"],"upper":p["ci_high"]}]),r],ignore_index=True)
    chart(tr("Primary estimate and 95% intervals","Estimation principale et intervalles à 95 %"),
          forest(s,"point","lower","upper","label",LOGUNIT),tr("Point estimate and confidence intervals from five inference methods.",
          "Estimation ponctuelle et intervalles selon cinq méthodes d’inférence."),"model_primary")
    source(PUBLISHER,[("12-10-0173-01","annual")],tr("Design C · 2011–2024","Modèle C · 2011–2024"),LOGUNIT)
    table(s[["label","point","lower","upper"]],"primary_intervals_per_point1")
    table(D["regression"],"complete_regression_full_scale")
    mode=st.selectbox(tr("Robustness subset","Sous-ensemble de robustesse"),["all","absolute","direction"],
                      format_func=lambda x:{"all":tr("All comparable index specifications","Toutes les spécifications d’indice comparables"),
                                            "absolute":tr("Absolute growth only","Variation absolue seulement"),
                                            "direction":tr("Signed and downside outcomes","Variations signées et baisses")}[x],key="model_robust_mode")
    r=D["robustness"].set_index("specification").loc[FOREST_IDS].reset_index()
    if mode!="all":
        r=r.loc[r.outcome.eq("absolute_growth") if mode=="absolute" else r.outcome.ne("absolute_growth")].copy()
    r["label"]=r.specification.map(lambda x:ROBUST_LABELS[x][lang=="fr"])
    r[["point","lower","upper"]]=r[["coefficient","ci_low","ci_high"]].mul(r.predictor_increment,axis=0)
    chart(tr("Robustness forest plot","Diagramme de robustesse"),forest(r,"point","lower","upper","label",LOGUNIT),
          tr("Secondary point estimates with province-clustered 95% intervals. Outcomes vary by specification.",
             "Estimations secondaires et intervalles à 95 % regroupés par province. Le résultat varie selon la spécification."),"robust_forest")
    source(PUBLISHER,[("12-10-0173-01","annual")],tr("Design C · secondary specifications","Modèle C · spécifications secondaires"),LOGUNIT)
    table(r.drop(columns="label"),f"robustness_{mode}")
    table(D["robustness"],"all_registered_robustness")
    z=D["influence"].sort_values("partial_predictor_leverage",ascending=False).assign(label=lambda d:d.geo.map(region))
    z[["point","lower","upper"]]=z[["coefficient","ci_low","ci_high"]]*.1
    chart(tr("Leave-one-province-out sensitivity","Sensibilité au retrait d’une province"),forest(z,"point","lower","upper","label",LOGUNIT),
          tr("Each line reestimates the model without the named province.","Chaque ligne réestime le modèle sans la province indiquée."),"model_loo")
    source(PUBLISHER,[("12-10-0173-01","annual")],tr("Design C · 2011–2024","Modèle C · 2011–2024"),LOGUNIT)
    table(z.drop(columns="label"),"leave_one_province_out")


def show_pilot():
    header(tr(*TITLES["pilot"]),tr("Check statutory code coverage, reporting support and import mirrors for the March 2025 steel measure.",
          "Vérifiez la couverture des codes, le soutien statistique et les importations miroir de la mesure sur l’acier de mars 2025."),
          ["Section 232","2022–2025",tr("Feasibility only","Faisabilité seulement")])
    p=D["pilot_metadata"]
    c=st.columns(4)
    c[0].metric(tr("Covered HTS10 lines","Lignes HTS10 visées"),num(p["potential_core_hts10_lines"],0))
    c[1].metric(tr("HS6 products","Produits SH6"),num(p["potential_core_hs6"],0))
    c[2].metric(tr("Full pre months","Mois complets avant"),num(p["pre_months"],0))
    c[3].metric(tr("Full post months","Mois complets après"),num(p["post_months"],0))
    note(tr("Estimation decision: no-go. Four core HS6 products have full U.S.–Mexico positive-flow support. One overlaps a separate antidumping proceeding.",
            "L’estimation reste bloquée. Quatre produits SH6 ont des flux positifs continus aux États-Unis et au Mexique. L’un chevauche une procédure antidumping."))
    st.markdown(tr("The 25% core measure took effect on March 12, 2025. The June 4 increase and preference-dependent stacking define separate regimes.",
        "La mesure de 25 % est entrée en vigueur le 12 mars 2025. La hausse du 4 juin et le cumul dépendant des préférences définissent des régimes distincts."))
    z=D["pilot_mirror"].query("scope == 'covered_core_232'").copy()
    z["duty_ratio"]=z.calculated_duties_over_consumption_value
    z["period"] = z.month.str[:4] + "-" + z.month.str[4:]
    chart(tr("U.S. import mirror snapshots","Instantanés des importations miroir américaines"),
          bars(z,"duty_ratio","period",tr("Calculated duty / customs value","Droits calculés / valeur en douane"),True),
          tr("Calculated aggregate duty ratios for three separately observed months.",
             "Rapports agrégés des droits calculés pour trois mois observés séparément."),"steel_mirror")
    source(tr("U.S. Census Bureau","Bureau du recensement des États-Unis"),[("Census IMDB","mirror"),("90 FR 11249","pilot")],
           "2025-01 · 2025-04 · 2025-05",tr("USD ratio","Ratio en dollars américains"))
    table(z,"steel_mirror_snapshots")
    geo=st.selectbox(tr("Screened destination","Destination examinée"),["US","MX","GB","DE","JP","KR"],
                     format_func=lambda k:partner(COUNTRY_HS[k]),key="pilot_destination")
    code=st.radio(tr("Product support","Soutien par produit"),["all","core","comparison"],horizontal=True,
                  format_func=lambda c:{"all":tr("All scoped lines","Toutes les lignes"),"core":tr("Covered core","Produits de base visés"),
                                        "comparison":tr("Upstream candidates","Comparateurs en amont")}[c],key="pilot_scope")
    d=D["pilot_coverage"].loc[lambda r:r.country.eq(geo)]
    if code!="all":
        d=d.loc[d.scope.eq("covered_core_232" if code=="core" else "candidate_upstream_control")]
    source(PUBLISHER,[("CIMT","hs")],"2022-01–2025-05",tr("Months and CAD","Mois et dollars canadiens"))
    table(d,f"steel_support_{geo.lower()}_{code}")
    table(D["pilot_codes"],"steel_legal_hts10")
    note(tr("The import ratio uses calculated duties. It does not isolate Section 232, net refunds or who bore the cost.",
            "Le rapport utilise les droits calculés. Il n’isole ni l’article 232, ni les remboursements nets, ni la répartition du coût."))


def show_sources():
    header(tr(*TITLES["sources"]),tr("Read the units, coverage and rules behind each dashboard measure.",
          "Consultez les unités, périodes et règles qui sous-tendent les indicateurs."),[tr("Vintage 18 November 2026","Millésime du 18 novembre 2026"),tr("Official sources","Sources officielles")])
    for title, key, period, explanation in [
      (tr("Annual trade","Commerce annuel"),"annual","2010–2025",tr("Customs basis, current CAD, domestic exports. Province or territory of production and NAPCS product section.",
          "Base douanière, dollars canadiens courants, exportations nationales. Province ou territoire de production et section SCPAN.")),
      (tr("Recent monthly trade","Commerce mensuel récent"),"monthly","2025-01–2026-09",tr("Monthly series, kept apart from annual estimates. Matched windows use January–September in both years.",
          "Série mensuelle indépendante des estimations annuelles. Fenêtres comparables de janvier à septembre.")),
      (tr("Concentration benchmark","Repère de concentration"),"hhi","2010–2025",tr("Separate published index compared with the reconstructed partner HHI.",
          "Indice officiel distinct comparé à l’IHH reconstruit par partenaire.")),
      (tr("Detailed product trade","Commerce détaillé par produit"),"hs","2024–2025",tr("CIMT HS8 and HS6. Valid matched quantities are shown only when same-unit coverage is verified.",
          "CICM SH8 et SH6. Les quantités comparées exigent une unité commune vérifiée.")),
      (tr("Gross export intensity","Intensité des exportations brutes"),"gdp","2010–2023",tr("Gross exports divided by provincial current-price GDP. Comparisons hold the reference year fixed.",
          "Exportations brutes divisées par le PIB provincial aux prix courants, pour une même année.")),
      (tr("U.S. final demand","Demande finale américaine"),"value_added",tr("Canada to 2024 · subnational 2013–2022","Canada jusqu’en 2024 · provinces et territoires 2013–2022"),
          tr("Domestic value added and jobs from supply-and-use models, with geography-specific denominators.",
             "Valeur ajoutée nationale et emplois estimés à partir des tableaux des ressources et des emplois, avec un dénominateur propre à chaque géographie.")),
    ]:
        st.markdown(f"**{title}** · {period}  \n{explanation}  \n[{tr('Official source','Source officielle')}]({URLS[key]})")
    st.divider()
    st.subheader(tr("Missing observations and definitions","Observations manquantes et définitions"), anchor=False)
    st.markdown(tr(
      "Shares use observed same-period controls. Empty table cells and gaps indicate unavailable values. A reported zero remains zero. "
      "The reconstructed HHI requires a complete and reconciled destination universe. For details on the 2020 monthly vintage, see the methods and working paper in the project folder. "
      "CSV headers carry measurement units where relevant; share columns are fractions from 0 to 1.",
      "Les parts utilisent les totaux observés de la même période. Les cellules vides signalent des valeurs indisponibles et les zéros déclarés restent des zéros. "
      "L’IHH reconstruit exige un univers de destinations complet et réconcilié. La méthodologie et le document de travail décrivent le millésime mensuel de 2020. "
      "Les en-têtes CSV indiquent les unités et les parts sont des fractions comprises entre 0 et 1."))
    table(D["intensity"],"provincial_gross_export_intensity")
    table(D["value_added"],"us_demand_value_added_and_jobs")


{
    "national":show_national, "province":show_province, "products":show_products, "concentration":show_concentration,
    "decomposition":show_decomposition, "model":show_model, "pilot":show_pilot, "sources":show_sources,
}[section]()

st.divider()
st.caption(tr(
    'Adapted from Statistics Canada, tables 12-10-0173-01 and 12-10-0129-01 (2010–2025), 12-10-0175-01 (January 2025–September 2026), 12-10-0100-01 (national to 2024 and subnational 2013–2022), 36-10-0711-01 (2010–2023) and CIMT domestic export archives (2022–2025). This does not constitute an endorsement by Statistics Canada of this product.',
    'Adapté de Statistique Canada, tableaux 12-10-0173-01 et 12-10-0129-01 (2010–2025), 12-10-0175-01 (janvier 2025 à septembre 2026), 12-10-0100-01 (Canada jusqu’en 2024 et provinces et territoires de 2013 à 2022), 36-10-0711-01 (2010–2023) et archives des exportations nationales de la CICM (2022–2025). Cela ne constitue pas une approbation de ce produit par Statistique Canada.',
))
st.caption(tr("[Statistics Canada Open Licence](https://www.statcan.gc.ca/en/terms-conditions/open-licence)",
              "[Licence ouverte de Statistique Canada](https://www.statcan.gc.ca/fr/avis/licence-ouverte)"))
