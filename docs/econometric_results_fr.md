# Modèle C · Concentration des destinations et instabilité des exportations

**L’estimation préenregistrée est positive et imprécise.** Une hausse de 0,10 de l’indice de Herfindahl–Hirschman (IHH) des destinations hors États-Unis, mesuré avec un an de retard, est associée à une augmentation de **0,0128 point logarithmique** de la variation annuelle absolue des exportations. L’intervalle de confiance à 95 % du bootstrap restreint de Webb va de **−0,0605 à +0,1053 point logarithmique**, avec une **valeur p bilatérale de 0,7174**. L’intervalle demeure compatible avec des variations d’ampleur économique non négligeable dans les deux sens. [Protocole préenregistré](phase4b_preregistered_specification.md) · [Tableau de régression complet](../data/phase4b/primary_regression.md) · [Graphique principal](../figures/phase4b/fr/01_primary_inference.png) · [English version](econometric_results_en.md)

## Mesure et échantillon

L’unité d’observation est la combinaison d’une province, d’une section de produits du SCPAN et d’une année. Le panel couvre les dix provinces, onze sections et des années de départ de 2011 à 2024. La dernière comparaison annuelle se termine en 2025. Le résultat est la valeur absolue de la différence entre les logarithmes des exportations nationales hors États-Unis aux années `t` et `t+1`, en dollars canadiens courants. L’IHH, le logarithme des exportations hors États-Unis et la part des États-Unis utilisent l’année `t−1`. Le modèle donne un poids égal à chaque cellule et inclut des effets fixes province–produit, produit–année et province–année. [Statistique Canada, tableau 12-10-0173-01](https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=1210017301)

| Résultat de la spécification principale | Estimation |
| --- | ---: |
| Coefficient de l’IHH retardé, échelle de 0 à 1 | +0,12827 |
| Erreur-type avec regroupement provincial, échelle complète | 0,36183 |
| Valeur p avec regroupement provincial (9 degrés de liberté) | 0,73112 |
| Association pour une hausse de 0,10 de l’IHH | +0,01283 point logarithmique |
| Intervalle à 95 %, regroupement provincial, par hausse de 0,10 | [−0,06903 ; +0,09468] |
| Intervalle à 95 %, bootstrap de Webb, par hausse de 0,10 | [−0,06049 ; +0,10525] |
| Observations et groupes province–produit | 1 454 et 108 |
| Niveaux d’effets fixes, province–produit / produit–année / province–année | 108 / 154 / 140 |
| Rang des effets fixes / rang total | 368 / 371 |
| R² global / ajusté / après retrait des effets fixes | 0,51860 / 0,35414 / 0,00862 |

Parmi les 1 540 cellules possibles, 1 513 disposent d’un IHH retardé admissible et d’exportations positives aux deux dates du résultat. Le seuil préétabli de 1 million de dollars canadiens appliqué au portefeuille retardé ramène le nombre à 1 454. Aucune cellule restante n’est seule dans un niveau d’effet fixe. Le panel équilibré comprend 98 groupes et 1 372 cellules. [Registre des exclusions](../data/phase4b/sample_exclusion_ledger.csv) · [Contrôles avant estimation](../data/phase4b/preflight.json)

## Ampleur et robustesse

L’association estimée de 0,0128 point logarithmique pour une hausse de 0,10 de l’IHH est modeste par rapport à la variation annuelle absolue médiane de **0,1633 point logarithmique**. Les intervalles autorisent toutefois des associations plus grandes. L’ensemble des trois variables explicatives représente environ **0,9 %** de la variance résiduelle après retrait des effets fixes dans cet échantillon. [Diagnostics](../data/phase4b/primary_diagnostics.json)

Le retrait des produits métalliques et des produits minéraux non métalliques (C14) ou de l’année de fin 2025 modifie peu l’estimation. La pondération selon la valeur des exportations retardées inverse le signe, à **−0,0275**, avec un intervalle à 95 % de **[−0,0567 ; +0,0016]**. La variation signée et l’ampleur des baisses donnent aussi des signes opposés, avec une grande incertitude. Les fenêtres sans chevauchement et les estimations qui retirent une province à la fois donnent des signes variables. Les 26 intervalles secondaires avec regroupement provincial comprennent zéro. [Analyse de robustesse](robustness_analysis.md) · [Graphique de sensibilité](../figures/phase4b/fr/02_specification_sensitivity.png)

## Portée économique

La baisse de la part des États-Unis peut coexister avec une concentration accrue des débouchés hors États-Unis. Dans le panel historique, l’association entre concentration et variation annuelle des exportations hors États-Unis demeure trop imprécise pour établir un effet stabilisateur. Les prix des produits de base, des variations de demande propres à certains marchés, les taux de change, les changements de composition des exportateurs et l’ajustement anticipé des portefeuilles peuvent expliquer une partie de la relation mesurée. Les effets fixes absorbent les mouvements communs, et les chocs propres à un couple province–produit restent possibles. Le modèle s’applique aux portefeuilles actifs admissibles et mesure des valeurs nominales. Il ne permet pas d’identifier l’effet causal d’une politique de diversification, la variation des volumes ni la dépendance en valeur ajoutée. [Mécanismes de diversification](diversification_mechanisms.md) · [Audit de l’inférence](statistical_inference_audit.md)

Le projet pilote sur l’acier confirme que les codes et les données miroir américaines sont accessibles pour une validation descriptive. Les comparateurs et la variation indépendante exigent des vérifications supplémentaires. [Projet pilote A](design_A_tariff_pilot.md)
