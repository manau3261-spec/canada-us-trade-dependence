# La dépendance économique du Canada envers les États-Unis

[English](README.md)

**Manau Salaun** · Étudiant aux cycles supérieurs en économie, Université de Sherbrooke · 2026

Recherche indépendante en économie appliquée. L’affiliation universitaire est indiquée à titre d’identification.

Le dépôt réunit un document de travail bilingue, une analyse reproductible et le **Canada–U.S. Trade Intelligence Monitor**. La série annuelle couvre 2010–2025. La série mensuelle distincte couvre janvier 2025 à septembre 2026. Les deux séries utilisent le millésime archivé de novembre 2026.

| Consulter | Fichiers |
| --- | --- |
| *Le Canada commerce moins avec les États-Unis. Sa dépendance diminue-t-elle vraiment ?* | [PDF](paper/rendered/canada_us_trade_fr.pdf) · [HTML](paper/rendered/canada_us_trade_fr.html) |
| *Canada Is Trading Less with the U.S. — But Is It Really Becoming Less Dependent?* | [PDF anglais](paper/rendered/canada_us_trade_en.pdf) · [HTML](paper/rendered/canada_us_trade_en.html) |
| Résumés | [Français et anglais](docs/research_abstract_bilingual.md) |
| Figures choisies | [Part américaine](figures/phase3/fr/01_national_dependence.png) · [Contribution des produits](figures/phase5/fr/03_commodity_bridge.png) · [Intervalles du modèle C](figures/phase4b/fr/01_primary_inference.png) |
| Documentation | [Méthodologie](docs/methodology.md) · [Audit scientifique](docs/final_scientific_audit.md) · [Audit de diffusion](docs/phase7a_release_audit.md) |

## Questions et résultats

1. **Comment l’exposition du Canada a-t-elle évolué ?** La part des États-Unis dans les exportations nationales de marchandises est passée de **75,8 % en 2024 à 71,7 % en 2025**. Dans la série mensuelle distincte, pour janvier à septembre, elle est passée de **73,3 % en 2025 à 68,0 % en 2026**. Les valeurs exportées augmentent vers les États-Unis et vers les autres destinations sur ces périodes comparables.
2. **Les gains hors États-Unis se répartissent-ils entre plusieurs marchés ?** La valeur des exportations hors États-Unis a augmenté de **28,796 milliards de dollars canadiens courants** entre 2024 et 2025. L’or non monétaire sous forme brute et le pétrole brut expliquent **74,3 %** de cette hausse. L’IHH hors États-Unis est passé de **0,07235 à 0,09382**. En excluant l’or brut, il est passé de **0,06830 à 0,07072**. Les quantités comparables portent sur certains produits et marchés. La diversification en volume demeure incertaine.
3. **La concentration est-elle associée aux mouvements ultérieurs des exportations ?** Dans le panel préenregistré, une hausse de **0,10** de l’IHH retardé est associée à **+0,012827 point logarithmique** de variation annuelle nominale absolue ultérieure. L’intervalle à 95 % du bootstrap restreint de Webb est **[−0,06049 ; +0,10525]**, avec **p = 0,7174**, **1 454 observations**, **108 groupes** et dix grappes provinciales. L’estimation est non concluante. Les 26 intervalles secondaires regroupés par province contiennent zéro. La pondération par la valeur inverse le signe de l’estimation ponctuelle.

Les exportations nationales de marchandises sont des valeurs douanières. La valeur ajoutée canadienne attribuable à la demande américaine est présentée séparément. Le pilote sur l’acier vérifie l’application des textes et la disponibilité des observations. Deux mois complets sous le taux initial, des mesures qui se chevauchent et le manque de comparateurs limitent l’exercice à une analyse descriptive. [Limites](docs/remaining_limitations.md) · [Rapprochement des séries de 2020](docs/reconciliation_2020.md)

## Méthodes, provenance et exécution

Le modèle C comporte des effets fixes province–produit, produit–année et province–année. L’inférence repose sur le regroupement des erreurs par province et un bootstrap restreint de Webb. Les cellules qui ne satisfont pas les règles de rapprochement des partenaires restent manquantes pour la reconstruction de l’IHH. Les fichiers de Statistique Canada, le tarif de l’USITC et les agrégats du Bureau du recensement des États-Unis sont documentés avec leurs millésimes et références. [Protocole préenregistré](docs/phase4b_preregistered_specification.md) · [Reçus de provenance](data/provenance/) · [Empreintes des données](data/phase5/source_lock.json)

Suivez les [commandes locales du README](README.md#run-the-dashboard-locally) avec une version de CPython **3.14** à jour. Le tableau de bord utilise les données dérivées incluses. Il ne demande aucun identifiant. Les tableaux s’exportent en CSV et le menu latéral permet de changer de langue. Les [commandes de reproduction](README.md#reproduce-the-research-outputs) recréent les deux articles depuis le millésime verrouillé. La [réplication indépendante](docs/final_scientific_audit.md) requiert les archives sources historiques conservées à part. [Guide Streamlit](docs/streamlit_deployment_steps.md) · [Inventaire](docs/public_repository_inventory.md)

## Licences et contact

Le code original relève de la [licence MIT](LICENSE). Les articles, figures et textes originaux relèvent de la [licence CC BY 4.0](LICENSE-CONTENT.md). Les données et contributions de tiers conservent leurs propres [conditions et mentions de source](THIRD_PARTY_NOTICES.md).

**Contact** · [Coordonnées publiques à fournir par l’auteur]

**Statut de diffusion** · Version de validation privée en attente de l’autorisation explicite de Manau Salaun. [Liste d’approbation](docs/final_approval_checklist.md)
