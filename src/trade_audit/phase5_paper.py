"""Build self-contained HTML and typeset PDFs from the two reviewed Markdown texts."""

import argparse
import base64
import html
import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

from markdown_it import MarkdownIt
import pandas as pd
import typst

from .acquire import sha256, write_json
from .phase3_figures import region_label
from .phase4b_figures import ROBUST_LABELS
from .phase5_data import ROOT, exposure, fact_values, localized_number, build as prepare
from .phase5_figures import render as render_figures
from .sources import JURISDICTIONS

MD = MarkdownIt("commonmark", {"html": True}).enable("table")
F = {
    "monthly": ("phase3/07_recent_monthly", "Recent monthly export exposure",
                "Exposition récente dans la série mensuelle",
                "Monthly domestic merchandise exports, January 2025–September 2026. Exports are unadjusted for seasonality. Statistics Canada 12-10-0175-01.",
                "Exportations nationales de marchandises, janvier 2025 à septembre 2026, non désaisonnalisées. Statistique Canada 12-10-0175-01."),
    "national": ("phase3/01_national_dependence", "Canada’s U.S. share of domestic merchandise exports",
                 "Part américaine des exportations nationales de marchandises du Canada",
                 "Share of world exports in percent, annual 2010–2025. Statistics Canada 12-10-0173-01.",
                 "Part des exportations mondiales en pourcentage, série annuelle 2010–2025. Statistique Canada 12-10-0173-01."),
    "ranking": ("phase3/02_regional_ranking_2025", "U.S. export exposure by jurisdiction",
                "Exposition aux États-Unis par province et territoire",
                "Share of each jurisdiction’s world exports destined for the U.S., 2025. Statistics Canada 12-10-0173-01.",
                "Part des exportations de chaque province ou territoire destinée aux États-Unis, 2025. Statistique Canada 12-10-0173-01."),
    "province_heat": ("phase5/01_province_year_heatmap", "Provincial and territorial exposure over time",
                      "Évolution de l’exposition provinciale et territoriale",
                      "Annual U.S. share of domestic merchandise exports, 2010–2025. The darkest cells have the highest shares. Statistics Canada 12-10-0173-01.",
                      "Part américaine des exportations nationales de marchandises, 2010–2025. Les cellules foncées ont les parts les plus élevées. Statistique Canada 12-10-0173-01."),
    "product": ("phase5/02_product_exposure_2025", "U.S. exposure by merchandise product section",
                "Exposition américaine par section de marchandises",
                "Canadian U.S. share within each NAPCS section, 2025. Special transactions excluded. Statistics Canada 12-10-0173-01.",
                "Part américaine du Canada dans chaque section du SCPAN, 2025. Transactions spéciales exclues. Statistique Canada 12-10-0173-01."),
    "commodity": ("phase5/03_commodity_bridge", "Contributions to the non-U.S. export increase",
                  "Contributions à la hausse des exportations hors États-Unis",
                  "Change from 2024 to 2025, CAD billions in current dollars. Gold is HS 710812 and crude petroleum HS 270900. Statistics Canada CIMT domestic exports.",
                  "Variation de 2024 à 2025, en milliards de dollars canadiens courants. Or (SH 710812) et pétrole brut (SH 270900). Exportations nationales, CICM."),
    "dest_change": ("phase5/04_destination_change", "Largest destination gains and losses outside the U.S.",
                    "Principales hausses et baisses par destination hors États-Unis",
                    "Six largest gains and three largest declines in recorded Canadian domestic exports, 2024–2025. CAD billions. Statistics Canada 12-10-0173-01.",
                    "Six principales hausses et trois principaux reculs, 2024–2025. Milliards de dollars canadiens. Statistique Canada 12-10-0173-01."),
    "hhi": ("phase3/05_destination_concentration", "Destination concentration, including and excluding the U.S.",
            "Concentration des destinations, avec et sans les États-Unis",
            "HHI on the 0–1 scale, annual 2010–2025. Reconstructed gaps remain blank. Statistics Canada 12-10-0173-01 and 12-10-0129-01.",
            "IHH de 0 à 1, 2010–2025. Les lacunes de la reconstruction sont laissées vides. Statistique Canada 12-10-0173-01 et 12-10-0129-01."),
    "intervals": ("phase4b/01_primary_inference", "Design C point estimate and 95% intervals",
                  "Estimation ponctuelle du modèle C et intervalles à 95 %",
                  "Log points per +0.10 HHI. The restricted Webb interval and four CR1 alternatives apply to the same estimate. Design C, Statistics Canada 12-10-0173-01.",
                  "Points logarithmiques par hausse de 0,10. Intervalle de Webb et quatre variantes CR1 pour la même estimation. Modèle C, Statistique Canada 12-10-0173-01."),
    "robust": ("phase4b/02_specification_sensitivity", "Registered secondary specifications",
               "Spécifications secondaires préenregistrées",
               "Selected point estimates and provincial CR1 95% intervals, log points per +0.10 of the relevant index. Appendix A gives all rows. Design C, Statistics Canada 12-10-0173-01.",
               "Estimations retenues et intervalles provinciaux CR1 à 95 %, en points logarithmiques par +0,10 de l’indice. L’annexe A donne toutes les lignes. Statistique Canada 12-10-0173-01."),
    "loo": ("phase4b/03_province_influence", "Provincial influence and leave-one-out estimates",
            "Levier provincial et estimations après retrait d’une province",
            "Each row omits the named province. Left, 95% CR1 interval and estimate per +0.10 HHI. Right, share of primary partial HHI leverage. Statistics Canada 12-10-0173-01.",
            "Chaque ligne retire la province indiquée. À gauche, intervalle CR1 à 95 % et estimation par +0,10 d’IHH. À droite, part du levier partiel. Statistique Canada 12-10-0173-01."),
}


def markdown_table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |",
                      "| " + " | ".join("---" for _ in headers) + " |",
                      *["| " + " | ".join(map(str, row)) + " |" for row in rows]])


def tables(data, lang):
    def l(en, fr):
        return (en, fr)[lang=="fr"]

    def n(value, d):
        return localized_number(value, d, lang)

    source = [
        (l("Annual customs exports","Exportations douanières annuelles"),"12-10-0173-01","2010–2025",l("CAD thousands; domestic exports by producer, NAPCS and destination","Milliers de $ CA; production, SCPAN et destination")),
        (l("Recent customs exports","Exportations douanières récentes"),"12-10-0175-01","2025-01–2026-09",l("CAD thousands; monthly, unadjusted","Milliers de $ CA; mensuel, non désaisonnalisé")),
        (l("Published concentration","Concentration publiée"),"12-10-0129-01","2010–2025",l("Dimensionless destination HHI","IHH des destinations, sans dimension")),
        ("CIMT / CICM","HS6 / HS8","2024–2025",l("Trade in CAD; quantities by common HS8 unit","Commerce en $ CA; quantité par unité SH8 commune")),
        (l("Provincial GDP","PIB provincial"),"36-10-0711-01","2010–2023",l("Current CAD millions for matching denominators","Millions de $ CA courants pour les dénominateurs")),
        (l("Domestic value added and jobs","Valeur ajoutée et emplois"),"12-10-0100-01",l("National to 2024","Canada jusqu’en 2024"),l("CAD thousands and jobs; subnational 2013–2022","Milliers de $ CA et emplois; infranational 2013–2022")),
    ]
    scopes = {"all products":l("All products","Tous les produits"),
              "excluding HS 710812":l("Excluding unwrought gold","Sans l’or sous forme brute"),
              "excluding chapter 71":l("Excluding chapter 71","Sans le chapitre 71")}
    hhi = [(scopes[r.scope], str(r.year), n(r.hhi_ex_us,6), n(r.uk_share_non_us*100,3))
           for r in data["gold_hhi"].itertuples()]
    term = {"hhi_ex_us":l("Lagged non-U.S. HHI","IHH hors États-Unis retardé"),
            "log_lag_exports":l("Lagged log non-U.S. exports","Log des exportations hors États-Unis retardé"),
            "lag_us_share":l("Lagged U.S. share","Part américaine retardée")}
    r = data["regression"].query("covariance == 'province'")
    reg = [(term[s.term],n(s.coefficient,6),n(s.standard_error,6),n(s.p_value,5),
            f"[{n(s.ci_low,5)} ; {n(s.ci_high,5)}]") for s in r.itertuples()]
    labels = dict(ROBUST_LABELS)
    labels["G_positive_non_us_partners"] = ("One more positive non-U.S. partner","Un partenaire hors États-Unis de plus")
    rows = []
    for s in data["robustness"].itertuples():
        if s.specification.startswith("I_omit_"):
            label = l("Omit ", "Sans ") + region_label(s.specification.removeprefix("I_omit_"),lang)
        else:
            label = labels[s.specification][lang=="fr"]
        scale = s.predictor_increment
        rows.append((label, n(s.n,0), n(s.groups,0), n(s.coefficient*scale,4),
                     f"[{n(s.ci_low*scale,4)} ; {n(s.ci_high*scale,4)}]"))
    ranked = exposure(data,"Annual","2025","2025",JURISDICTIONS,["TOTAL"]).sort_values("us_share",ascending=False)
    regions = [(region_label(row.geo,lang), n(row.us_share*100,1), n(row.us_cad_thousands/1e6,1),
                n(row.world_cad_thousands/1e6,1)) for row in ranked.itertuples()]
    windows = data["matched"].loc[lambda d:d.geo.eq("Canada")].sort_values("year")
    monthly = [(int(r.year), n(r.world_cad_thousands/1e6,3), n(r.us_cad_thousands/1e6,3),
                n(r.non_us_cad_thousands/1e6,3), n(r.us_share*100,2)) for r in windows.itertuples()]
    grid = data["coverage"]
    rules = [(l("Expected grid","Grille attendue"),len(grid)),
             (l("Phase 4A eligibility","Admissibilité de la phase 4A"), int(grid.prior_eligible.sum())),
             (l("Primary included","Cellules retenues"),int(grid.included_main.sum())),
             (l("Lag HHI unavailable","IHH retardé indisponible"),int(grid.exclude_lag_HHI_unavailable.sum())),
             (l("Lag controls unavailable","Contrôles retardés indisponibles"),int(grid.exclude_lag_controls_unavailable.sum())),
             (l("Lag export floor failed","Seuil des exportations retardées non atteint"),int(grid.exclude_lag_below_portfolio_floor.sum())),
             (l("Zero exports at start","Exportations nulles au départ"),int(grid.exclude_start_zero.sum())),
             (l("Zero exports at end","Exportations nulles à la fin"),int(grid.exclude_end_zero.sum()))]
    coverage = markdown_table([l("Status or flag","Statut ou indicateur"),l("Cells","Cellules"),
                               l("Scope","Champ"),l("Overlap","Chevauchement")],
         [(label,n(count,0), "2011–2024", l("Flag counts can overlap.","Les motifs peuvent se chevaucher.") if j>=3 else "—")
          for j,(label,count) in enumerate(rules)])
    return {
        "monthly":markdown_table([l("Year","Année"),l("World","Monde"),l("U.S.","États-Unis"),
            l("Non-U.S.","Hors États-Unis"),l("U.S. share, %","Part américaine, %")],monthly),
        "sample":coverage,
        "regions":markdown_table([l("Producing jurisdiction","Province ou territoire de production"),
            l("U.S. share, %","Part américaine, %"),l("U.S., CAD B","États-Unis, G$ CA"),
            l("World, CAD B","Monde, G$ CA")],regions),
        "sources": markdown_table([l("Source use","Utilisation"), l("Table","Tableau"), l("Period","Période"), l("Units and scope","Unité et champ")],source),
        "gold_hhi":markdown_table([l("Product scope","Champ de produits"),l("Year","Année"),
            l("Non-U.S. HHI","IHH hors États-Unis"),l("U.K. share, % of non-U.S.","Part britannique hors États-Unis, %")],hhi),
        "regression":markdown_table([l("Predictor, full scale","Prédicteur, échelle complète"),l("Coefficient","Coefficient"),
            l("Province SE","Erreur-type provinciale"),l("p-value","Valeur p"),l("95% CR1 interval","Intervalle CR1 à 95 %")],reg),
        "robustness":markdown_table([l("Specification","Spécification"),"N",l("Groups","Groupes"),l("Estimate","Estimation"),l("95% CR1 interval","Intervalle CR1 à 95 %")],rows),
    }


def interpolate(text, facts, table, lang):
    values = {key: localized_number(v,d,lang) for key,(v,d) in facts.items()}
    text = re.sub(r"\{\{([A-Z0-9_]+)\}\}",lambda m:values[m[1]],text)
    return re.sub(r"\{\{table:([a-z0-9_]+)\}\}",lambda m:table[m[1]],text)


def figure(root, name, lang):
    stem,en,fr,capen,capfr = F[name]
    phase,file = stem.split("/")
    file = f"{lang}/{file}.png"
    manifest_name = "figure_manifest.json" if phase=="phase3" else "manifest.json"
    manifest = json.loads((root/"figures"/phase/manifest_name).read_text())
    path = root/"figures"/phase/file
    if sha256(path)!=manifest[file]:
        raise ValueError(f"Figure does not match its source manifest: {path}")
    return path, (en,fr)[lang=="fr"], (capen,capfr)[lang=="fr"]


def html_document(source, root, lang):
    figures = iter(range(1,len(F)+1))
    def img(m):
        p,title,caption=figure(root,m[1],lang)
        svg=base64.b64encode(p.read_bytes()).decode("ascii")
        return (f'<figure><img src="data:image/png;base64,{svg}" alt="{html.escape(title)}">'
                f'<figcaption><strong>Figure {next(figures)}. {html.escape(title)}.</strong> '
                f'{html.escape(caption)}</figcaption></figure>\n')
    result=MD.render(re.sub(r"^\{\{fig:([a-z0-9_]+)\}\}\s*$",img,source,flags=re.M))
    result=result.replace("<table>",'<div class="table-wrap" role="region" aria-label="'
                          + ("Tableau de données" if lang=="fr" else "Data table") +'" tabindex="0"><table>')
    result=result.replace("</table>","</table></div>").replace("<th>","<th scope=\"col\">")
    items=[]
    def nav_head(m):
        slug=f"section-{len(items)+1}"
        items.append((slug,m[1]))
        return f'<h2 id="{slug}">{m[1]}</h2>'
    result=re.sub(r"<h2>(.*?)</h2>",nav_head,result)
    title=re.search(r"<h1>(.*?)</h1>",result)[1]
    nav=('<nav aria-label="'+("Sommaire" if lang=="fr" else "Contents")+'"><strong>'
         +("Sommaire" if lang=="fr" else "Contents")+"</strong><ol>"
         +"".join(f'<li><a href="#{slug}">{name}</a></li>' for slug,name in items)+"</ol></nav>")
    result=result.replace('<h2 id="section-3">',nav+'\n<h2 id="section-3">',1)
    css=(root/"paper/paper.css").read_text()
    return ("<!doctype html>\n"
            + f'<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            + '<meta name="author" content="Manau Salaun">'
            + '<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">'
            + f"<title>{title}</title><style>{css}</style></head><body><main>{result}</main></body></html>\n")


def q(s):
    return json.dumps(s,ensure_ascii=False)


def inline(token):
    out=[]
    for t in token.children or ():
        if t.type=="text":
            out.append(f"#text({q(t.content)})")
        elif t.type=="code_inline":
            out.append(f"#text(fill: rgb(\"#175863\"), weight: \"semibold\", {q(t.content)})")
        elif t.type=="strong_open":
            out.append("#strong[")
        elif t.type=="em_open":
            out.append("#emph[")
        elif t.type=="link_open":
            out.append(f"#link({q(t.attrGet('href'))})[")
        elif t.type in ("strong_close","em_close","link_close"):
            out.append("]")
        elif t.type in ("softbreak","hardbreak"):
            out.append(" " if t.type=="softbreak" else "#linebreak()")
        else:
            raise ValueError(f"Unsupported inline token {t.type}")
    return "".join(out)


def typst_table(tokens):
    parts=[]; columns=0; in_header=True; headers=[]
    for t in tokens:
        if t.type=="thead_close":
            in_header=False
        elif t.type=="inline":
            cell=f"[{inline(t)}]"
            if in_header:
                headers.append(cell)
                columns+=1
            else:
                parts.append(cell)
    widths={4:"(1.35fr,.95fr,.92fr,1.65fr)", 5:"(2.1fr,.7fr,.7fr,.74fr,1.4fr)"}[columns]
    if columns==5 and len(parts)==15:
        widths="(1.9fr,.82fr,.88fr,.76fr,1.32fr)"
    return ("#table(columns: "+widths+", inset: (x: 6pt, y: 5pt), stroke: (bottom: .35pt + rgb(\"#d2e1e6\")),"
            +' fill: (_, y) => if y==0 {rgb("#e8f1f4")} else if calc.even(y) {rgb("#f6fafb")},'
            +" table.header("+",".join(headers)+"),"+",".join(parts)+")")


def typst_document(source, root, lang):
    tokens=MD.parse(source)
    title=tokens[1].content
    config=f'''
#set document(title: {q(title)}, author: "Manau Salaun", date: datetime(year: 2026, month: 11, day: 18))
#set page(paper: "us-letter", margin: (left: 0.90in, right: 0.90in, top: 0.83in, bottom: 0.79in),
  header: context {{
    if counter(page).get().first() > 1 {{
      set text(size: 8.5pt, fill: rgb("#526b79"))
      grid(columns: (1fr,auto), [{("Canada and the U.S. · Working paper" if lang=="en" else "Le Canada et les États-Unis · Document de travail")}], [2026])
      line(length: 100%, stroke: .5pt + rgb("#d2e2e7"))
    }}
  }},
  footer: context {{
    align(right, text(size: 9pt, fill: rgb("#426477"), counter(page).display()))
  }})
#set text(font: "Libertinus Serif", size: 10pt, lang: {q(lang)}, fill: rgb("#203747"))
#set par(leading: 0.51em, spacing: .76em, justify: true)
#show heading: set text(font: "Libertinus Sans", weight: "bold", fill: rgb("#173447"))
#show heading: set par(justify: false)
#show heading.where(level: 1): set text(size: 25pt, hyphenate: false)
#show heading.where(level: 2): set text(size: 16.2pt)
#show link: set text(fill: rgb("#13695f"))
#show table: set text(size: 8.9pt, font: "Libertinus Sans")
'''
    body=[config]
    page_openers=("9. ","References","Références","Appendix A.","Annexe A.","Appendix B.","Annexe B.","Appendix C.","Annexe C.")
    i=0
    in_bullet=False
    idx=1
    while i<len(tokens):
        token=tokens[i]
        if token.type=="heading_open":
            text=tokens[i+1]
            level=int(token.tag[1:])
            if level==2 and text.content.startswith("1. "):
                body.append('#pagebreak(weak: true)\n#set text(size: 11pt)\n#set par(leading: .66em, spacing: .97em, justify: true)\n#outline(title: '
                            + q("Contents" if lang=="en" else "Sommaire") + ', depth: 2)\n#pagebreak(weak: true)')
            elif level==2 and text.content.startswith(page_openers):
                body.append("#pagebreak(weak: true)")
            body.append(f"#heading(level: {level})[{inline(text)}]")
            i+=3
        elif token.type=="paragraph_open":
            text=tokens[i+1]
            f=re.fullmatch(r"\{\{fig:([a-z0-9_]+)\}\}",text.content)
            if f:
                p,label,caption=figure(root,f[1],lang)
                file="/"+p.relative_to(root).as_posix()
                width="87%" if f[1] in {"robust","loo"} else "100%"
                body.append(f'#block(breakable: false)[#align(center, image({q(file)}, width: {width}, alt: {q(label)}))'
                      + f'\n#text(size: 9.5pt)[#strong[#text({q(f"Figure {idx}. {label}.")})] #text({q(caption)})]]')
                idx+=1
            elif in_bullet:
                body.append(f"- {inline(text)}")
            else:
                body.append(inline(text))
            i+=3
        elif token.type=="table_open":
            end=i+1
            while tokens[end].type!="table_close":
                end+=1
            body.append(typst_table(tokens[i:end]))
            i=end+1
        else:
            if token.type=="bullet_list_open":
                in_bullet=True
            elif token.type=="bullet_list_close":
                in_bullet=False
            elif token.type not in ("list_item_open","list_item_close"):
                raise ValueError(f"Unsupported block {token.type}")
            i+=1
    return "\n\n".join(body)+"\n"


def render(root, target, pdf=True, make_figures=True):
    data=prepare(root)
    if make_figures:
        render_figures(root,data)
    target.mkdir(parents=True,exist_ok=True)
    facts=fact_values(data)
    manifest={}
    for lang in ("en","fr"):
        markdown=(root/"paper"/f"working_paper_{lang}.md").read_text()
        source=interpolate(markdown,facts,tables(data,lang),lang)
        h=target/f"canada_us_trade_{lang}.html"
        h.write_text(html_document(source,root,lang),encoding="utf-8")
        manifest[h.name]=sha256(h)
        if pdf:
            t=typst_document(source,root,lang)
            tmp=None
            try:
                with NamedTemporaryFile(mode="w",encoding="utf-8",suffix=".typ",dir=root/"paper",delete=False) as file:
                    tmp=Path(file.name)
                    file.write(t)
                p=target/f"canada_us_trade_{lang}.pdf"
                p.write_bytes(typst.compile(tmp,root=root))
                manifest[p.name]=sha256(p)
            finally:
                if tmp:
                    tmp.unlink(missing_ok=True)
    write_json(target/"manifest.json",manifest)
    return manifest


if __name__=="__main__":
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--root",type=Path,default=ROOT)
    arg.add_argument("--output",type=Path)
    arg.add_argument("--html-only",action="store_true")
    arg.add_argument("--reuse-figures",action="store_true")
    opts=arg.parse_args()
    root=opts.root.resolve()
    render(root,opts.output or root/"paper/rendered",not opts.html_only,not opts.reuse_figures)
