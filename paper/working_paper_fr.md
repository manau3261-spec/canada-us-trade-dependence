# Le Canada commerce moins avec les États-Unis. Sa dépendance diminue-t-elle vraiment ?

**Manau Salaun** · Étudiant aux cycles supérieurs en économie, Université de Sherbrooke  
Recherche indépendante en économie appliquée · Affiliation indiquée à titre d’identification  
Document de travail · Novembre 2026

Exportations nationales de marchandises, 2010–2025 · Mise à jour mensuelle vérifiée jusqu’en septembre 2026

## Résumé

La part des États-Unis dans les exportations nationales de marchandises du Canada est passée de **{{US24}} % en 2024 à {{US25}} % en 2025**. Les exportations qui ont pris du poids hors États-Unis se sont réparties moins uniformément entre les destinations. Leur valeur a augmenté de {{NON_US_CHANGE}} milliards de dollars canadiens courants. L’or non monétaire sous forme brute et le pétrole brut expliquent **{{GOLD_CRUDE_PCT}} %** de cette hausse nette. L’indice de Herfindahl–Hirschman (IHH) des destinations hors États-Unis est passé de {{HHI24}} à {{HHI25}}. En excluant l’or sous forme brute, il passe de {{EX_GOLD24}} à {{EX_GOLD25}}. L’importance du Royaume-Uni est particulièrement sensible à cette exclusion.

Un modèle préenregistré à trois ensembles d’effets fixes relie la concentration retardée des destinations hors États-Unis à la variation annuelle absolue ultérieure du logarithme des exportations nominales. Il couvre {{N}} observations province–produit–année, réparties en {{G}} groupes. Une hausse de 0,10 de l’IHH est associée à **+{{SCALED}} point logarithmique**, avec un intervalle de confiance à 95 % du bootstrap restreint de Webb de **[{{LOW}} ; +{{HIGH}}]** et une **valeur p de {{P}}**. La pondération par la valeur et les autres définitions du résultat changent le signe de l’estimation ponctuelle. Un projet pilote distinct sur les droits de mars 2025 visant l’acier vérifie le champ juridique et les données américaines d’importation, avec des comparateurs insuffisants pour une estimation. Les résultats documentent une recomposition de la valeur nominale des exportations. L’effet de la diversification sur la vulnérabilité économique reste indéterminé.

*Mots-clés* : Canada, États-Unis, dépendance commerciale, concentration des exportations, volatilité nominale, composition des produits.  
*JEL* : F14, F15, F40, C23.

## Sommaire exécutif

- **Variation de la part américaine de {{US_DPP}} points de pourcentage.** En 2025, le Canada a exporté {{WORLD25}} milliards de dollars de marchandises nationales, dont {{US25_CAD}} milliards vers les États-Unis et {{NON_US25}} milliards vers les autres destinations. Dans la série mensuelle distincte, la part américaine est passée de {{MONTH25}} % à {{MONTH26}} % entre les fenêtres de janvier à septembre 2025 et 2026. La valeur exportée vers les États-Unis a augmenté dans cette comparaison à mois identiques.
- **Le poids du principal marché diminue tandis que les autres destinations se concentrent.** La part du Royaume-Uni dans les exportations hors États-Unis passe de {{UK24}} % à {{UK25}} %. Sur une hausse de {{UK_CHANGE}} milliards de dollars, {{UK_GOLD}} milliards proviennent de l’or sous forme brute. Le retrait de ce produit atténue fortement la hausse de l’IHH hors États-Unis et fait légèrement baisser la part britannique.
- **L’exposition dépend du dénominateur.** En 2025, le Nouveau-Brunswick arrive en tête pour la part des exportations brutes vers les États-Unis. L’Ontario arrive en tête pour la valeur des marchandises exposées. Les exportations brutes, leur rapport au PIB et la valeur ajoutée nationale attribuable à la demande américaine éclairent des questions différentes.
- **L’incertitude domine l’estimation.** Le coefficient de l’IHH est de +{{BETA}} sur l’échelle de 0 à 1. L’intervalle couvre les deux signes. Le modèle est associatif et porte sur des portefeuilles actifs et suffisamment bien mesurés. Les effets de politique publique, les quantités réelles, la production et le bien-être restent à étudier.
- **La portée juridique ne suffit pas à mesurer l’exposition constatée.** Le projet pilote sur l’acier répertorie {{PILOT_LINES}} lignes tarifaires américaines, avec deux mois complets après l’entrée en vigueur pour le régime initial. Les préférences, le cumul des droits, les recours commerciaux parallèles et la rareté des comparateurs empêchent une estimation défendable.

## 1. Introduction et motivation

La baisse de la part des exportations vendues au principal partenaire est souvent interprétée comme un progrès de la diversification. Le dénominateur oblige à nuancer ce constat. Si l’essor d’un produit de grande valeur augmente les livraisons vers un seul autre marché, la part américaine diminue et le reste du portefeuille devient plus concentré. Les prix et le rôle de certaines places de négoce peuvent infléchir les valeurs douanières sans déplacement équivalent de la demande finale ou de la production. Il faut donc déterminer quelles expositions ont diminué, dans quelles provinces et pour quels produits, et si la nouvelle répartition des marchés est associée à des exportations plus stables.

L’étude examine trois questions. Premièrement, quelle est l’ampleur de la baisse de la part américaine dans une série comparable d’exportations nationales de marchandises ? Deuxièmement, comment les produits, les destinations et certaines quantités observables éclairent-ils le changement de 2024 à 2025? Troisièmement, la concentration passée des marchés hors États-Unis est-elle associée à l’instabilité ultérieure des exportations pour des portefeuilles comparables? Un projet pilote distinct examine si une mesure tarifaire importante de 2025 sur l’acier pourrait se prêter à un protocole ultérieur. Il ne comporte aucune estimation de son effet.

La contribution est d’observer dans un même millésime douanier la part du partenaire dominant et l’IHH conditionnel aux destinations hors États-Unis. Le document reconstitue le poids des pays et la contribution de produits détaillés, puis compare les indices aux statistiques publiées en documentant les écarts. Le protocole économétrique fixe à l’avance l’échantillon, les variables de contrôle et l’inférence et rend compte des résultats faibles ou contradictoires. L’ensemble délimite ce que la valeur des échanges observés permet d’affirmer au sujet de la résilience.

## 2. Contexte économique et commercial canadien

La production et les expéditions canadiennes dépendent de la proximité des clients, de la logistique frontalière, de la spécialisation et des chaînes de production intégrées avec les États-Unis. Une part nationale élevée englobe des relations différentes. Dans l’énergie et le matériel de transport, l’infrastructure, les normes et les liens de production peuvent être propres à un débouché. D’autres produits transitent par de grandes places de négoce. Ces différences influent sur le coût et le délai d’une réorientation, ainsi que sur le sens du pays déclaré en douane.

La part des États-Unis s’établissait à environ 74,7 % en 2010 et a atteint {{US23}} % en 2023, son maximum durant la période étudiée. L’observation de 2025 en est le minimum. En dollars canadiens courants, les exportations vers les États-Unis ont diminué de 5,8 % entre 2024 et 2025. Celles vers les autres marchés ont progressé de 16,5 % et les exportations mondiales ont baissé de 0,4 %. La répartition des destinations s’est modifiée au cours d’une année de légère baisse de la valeur mondiale.

La série mensuelle apporte un éclairage différent. De janvier à septembre 2026, les expéditions vers les États-Unis ont augmenté d’environ 3,4 % par rapport aux mêmes mois de 2025, et celles vers les autres destinations d’environ 33,6 %. La valeur a donc progressé des deux côtés. Les données mensuelles proviennent d’un tableau distinct et restent non désaisonnalisées. La comparaison utilise les mêmes mois des deux années. Leur somme ne remplace ni le total annuel 2025 ni une observation annuelle 2026. Le calendrier des mesures, la facturation, les prix et l’évolution de la demande restent des explications plausibles.

{{fig:monthly}}

## 3. Littérature et mécanisme économique

La logique de portefeuille précise pourquoi la répartition des destinations importe. Lorsque les recettes par marché sont soumises à des chocs partiellement indépendants, des ventes mieux réparties peuvent réduire l’exposition à un choc propre à un marché. Sous l’hypothèse illustrative de variances communes et de chocs indépendants, la variance normalisée du portefeuille est proportionnelle à la somme des parts au carré. Avec des risques hétérogènes ou corrélés, elle correspond plutôt à une forme quadratique utilisant les parts et la matrice de covariance. Deux portefeuilles peuvent donc partager le même IHH avec des risques très différents. L’indice décrit les valeurs réalisées. Il ne renseigne pas directement sur la covariance de la demande future.

Koren et Tenreyro (2007) distinguent plusieurs sources de volatilité agrégée, dont la composition sectorielle et les chocs propres à un pays. Di Giovanni et Levchenko (2010) élaborent une mesure du risque des exportations qui combine la spécialisation et le risque sectoriel. Haddad et ses coauteurs (2013) montrent, à partir de données internationales, que la diversification module la relation entre l’ouverture et la volatilité de la croissance. Ces travaux motivent l’hypothèse d’un effet stabilisateur dans certaines circonstances. Leurs variables de résultat, unités et stratégies d’identification diffèrent du panel canadien de valeurs douanières annuelles. Ils ne déterminent ni la taille ni le signe du coefficient attendu dans ce panel.

Cadot, Carrère et Strauss-Kahn (2011) distinguent la redistribution des exportations entre lignes déjà actives de l’ajout de nouvelles lignes. La distinction s’applique aux destinations. Une hausse de la valeur vers un partenaire connu, l’apparition d’un flux déclaré et une répartition plus uniforme correspondent à des marges différentes. Le nombre de destinations peut progresser en même temps que l’IHH si le premier marché prend du poids. L’étude complète donc l’IHH par les parts du premier marché et des trois premiers marchés, le nombre de partenaires actifs et un calcul hors or.

Une deuxième distinction concerne la production. Hummels, Ishii et Yi (2001) documentent l’utilisation d’intrants importés dans les biens exportés. Dans une chaîne de production intégrée, la valeur brute d’une expédition dépasse parfois la valeur créée à l’étape réalisée au Canada. Pour mesurer l’exposition de la production, il faut un indicateur de valeur ajoutée nationale et un dénominateur distinct. Une mesure douanière ne suffit donc pas à établir la contribution au PIB ou le nombre d’emplois exposés à une mesure américaine.

Les effets fixes réduisent certaines sources de confusion et le regroupement des erreurs permet de tenir compte de certaines dépendances résiduelles. Ils ne rendent pas la concentration passée exogène. MacKinnon, Nielsen et Webb (2023) soulignent l’importance du choix des grappes et du levier des observations. Webb (2023) étudie des poids à six valeurs pour le bootstrap avec peu de grappes. Ces travaux guident les intervalles d’incertitude. Leurs hypothèses restent importantes avec dix provinces exposées à des marchés communs.

## 4. Sources et construction des données

La base annuelle utilise le tableau 12-10-0173-01 de Statistique Canada, par province ou territoire de production, section du SCPAN et partenaire. Elle retient les exportations nationales de marchandises et les totaux monde et États-Unis d’une même cellule et d’une même période. Les réexportations sont exclues. Les valeurs sont en dollars canadiens courants, sur une base douanière. La province de production diffère du port de sortie et le dernier pays de destination connu peut différer du lieu d’utilisation ou du dernier acheteur.

L’extrait annuel couvre 2010 à 2025. Le tableau mensuel 12-10-0175-01 couvre la période récente de janvier 2025 à septembre 2026. Les deux fréquences restent séparées. L’examen de 2020 montre que les observations mensuelles archivées s’additionnent aux observations annuelles correspondantes, alors que le millésime mensuel actif présente des écarts. La comparaison associe l’écart au nouveau millésime mensuel sans établir l’opération exacte du diffuseur. La série annuelle sert à l’analyse historique et les données mensuelles à la comparaison descriptive de mois correspondants.

Le tableau 12-10-0129-01 fournit les rapports officiels de concentration des destinations. La reconstruction reprend les échanges bilatéraux annuels de la même période. La comparaison exclut les indices rebasés du tableau officiel. Les fichiers détaillés de la CICM pour 2024 et 2025 contiennent 2 556 556 observations mensuelles à huit chiffres du SH, agrégées une seule fois à six chiffres et par destination. Les quatre totaux monde et États-Unis s’écartent d’au plus 169 $ CA des contrôles annuels. La comparaison des quantités à huit chiffres exige une unité commune non vide et une quantité positive pour chaque ligne de valeur positive.

Le PIB provincial en dollars courants (36-10-0711-01) permet de calculer l’intensité des exportations brutes jusqu’en 2023 dans le millésime retenu. Les valeurs sont manquantes pour les années suivantes. Le tableau 12-10-0100-01 mesure séparément la valeur ajoutée nationale et les emplois attribuables à la demande étrangère. La série nationale est disponible jusqu’en 2024 et la série infranationale comparable couvre 2013–2022. Les repères nationaux de 2023 et de 2024 reposent sur des estimations avancées issues d’un modèle. Le tableau de l’emploi 14-10-0022-01 sert aux vérifications de couverture. La concordance entre les industries du SCIAN et les sections de produits du SCPAN serait nécessaire avant une analyse intégrée de l’emploi.

Toutes les données proviennent de fichiers dont le millésime et les empreintes sont fixés. Les observations manquantes, invalides ou supprimées demeurent indisponibles. Un zéro déclaré conserve son sens. Pour réconcilier les variations détaillées de valeur, une ligne absente du fichier CICM ne contribue aucun montant publié. Cette convention ne prouve pas que le flux réel était nul et ne permet aucune imputation dans les régressions.

{{table:sources}}

## 5. Définitions de la dépendance et de la diversification

Soit X(g,k,d,t) la valeur en dollars canadiens courants des exportations nationales de marchandises de la géographie g vers la destination d, pour le produit k et la période t. La part américaine divise la valeur destinée aux États-Unis par le total mondial de la même cellule. Son complément mesure le poids des autres destinations. Le niveau des expéditions brutes mesure l’ampleur en dollars. Le rapport des exportations au PIB décrit l’exposition brute par rapport à la taille de l’économie. Il inclut les intrants contenus dans les biens et le dénominateur diffère de celui d’une part de valeur ajoutée nationale.

L’IHH des destinations est la somme des parts par destination élevées au carré. L’indice toutes destinations utilise le total mondial. L’indice hors États-Unis retire les États-Unis de la somme et du dénominateur. Si l’univers des destinations forme une partition complète, l’identité suivante s’applique.

`IHH(toutes) = s(É.-U.)² + (1 − s(É.-U.))² × IHH(hors É.-U.).`

La baisse de la part américaine peut ainsi réduire la concentration toutes destinations même si le portefeuille des autres destinations se concentre. La reconstruction conserve le libellé exact États-Unis. La réconciliation examine séparément le regroupement d’autres territoires américains. Une valeur positive non attribuée bloque le calcul strict. L’indice est compris entre 0 et 1, et une hausse indique une concentration accrue. Sa sensibilité aux valeurs élevées justifie le suivi parallèle du nombre de partenaires actifs et des parts des premiers marchés.

La variable de résultat du modèle C correspond à l’ampleur absolue d’une variation annuelle du logarithme. Elle augmente avec une hausse importante comme avec une forte baisse. Cette mesure d’instabilité réalisée ne permet pas de déduire une variance conditionnelle, une variation en volume ou la probabilité d’un choc. Les variantes sur la variation signée et sur l’ampleur des baisses précisent ce que masque la valeur absolue.

## 6. Exposition des provinces et des produits

Le recul national masque des profils différents. En 2025, le Nouveau-Brunswick a la part américaine la plus élevée (90,4 %), devant le Yukon (87,4 %) et l’Alberta (85,4 %). L’Ontario arrive en tête en dollars courants avec 189,5 milliards de dollars, suivi de l’Alberta avec 152,0 milliards. Au total, ces deux provinces représentent environ 66,2 % des exportations nationales destinées aux États-Unis. La taille du flux vers un marché et sa part dans les débouchés locaux donnent deux classements distincts.

À Terre-Neuve-et-Labrador, la part américaine passe de 50,4 % en 2024 à 34,2 % en 2025. Dans les petits portefeuilles territoriaux, quelques expéditions importantes peuvent modifier la part annuelle. Les faibles parts observées dans les Territoires du Nord-Ouest et au Nunavut en 2025 ne suffisent pas à établir une faible exposition durable à la demande américaine. Les graphiques descriptifs incluent les territoires lorsque les données le permettent. Le panel économétrique approuvé se limite aux dix provinces.

En 2025, la part américaine atteint 93,4 % dans les véhicules automobiles et pièces, 84,9 % dans les produits chimiques, plastiques et caoutchouc, et 84,4 % dans l’énergie. Elle est plus faible pour les minerais métalliques et minéraux non métalliques (22,0 %) et les produits agricoles, de la pêche et aliments intermédiaires (46,4 %). L’énergie représente la plus grande section en valeur mondiale (188,6 milliards de dollars). Une part élevée dans une section importante peut amplifier un choc frontalier. Les possibilités de substitution et la provenance des intrants en déterminent aussi les conséquences.

En 2023, les exportations brutes vers les États-Unis équivalaient à 37,2 % du PIB courant du Nouveau-Brunswick, à 35,5 % de celui de l’Alberta et à 26,2 % de celui de la Saskatchewan. Dans les tableaux des ressources et des emplois pour 2022, la part de valeur ajoutée nationale attribuable à la demande américaine était de 33,7 % en Alberta, de 25,0 % en Saskatchewan et de 14,2 % en Ontario. Au niveau national, en 2024, les parts modélisées étaient de 15,9 % pour la valeur ajoutée et de 12,1 % pour les emplois. Les périodes, les périmètres et les dénominateurs diffèrent. Ils doivent rester explicites dans une évaluation du risque commercial ou dans le ciblage d’une mesure régionale.

{{fig:national}}

{{fig:ranking}}

{{fig:province_heat}}

{{fig:product}}

## 7. Décomposition du changement entre 2024 et 2025

Une identité au point milieu décompose la part américaine selon le poids des sections et selon les parts américaines à l’intérieur de chaque section. Sur une variation totale de {{US_DPP}} points, le déplacement des parts à l’intérieur des sections contribue −3,21 points et la composition des produits −0,90 point. L’énergie a la plus grande contribution nette, soit −1,64 point. Les moyennes des deux années répartissent l’interaction de manière symétrique. Il s’agit d’une décomposition comptable de part, distincte de l’attribution de la hausse hors États-Unis aux produits du SH.

Ce deuxième calcul additionne les variations par code à six chiffres du SH sur l’ensemble des destinations hors États-Unis. L’or non monétaire sous forme brute (SH 710812) contribue {{GOLD}} milliards de dollars, le pétrole brut (SH 270900) {{CRUDE}} milliards, et les autres produits {{REMAINDER}} milliards, en valeur nette. L’aluminium non allié sous forme brute, les minerais et concentrés de cuivre et le chlorure de potassium contribuent aussi à la hausse. La houille bitumineuse a une contribution négative importante. L’or et le pétrole représentent {{GOLD_CRUDE_PCT}} % de l’augmentation nette. Les reculs des autres produits rehaussent mécaniquement cette fraction.

Le Royaume-Uni illustre la concentration des gains par destination. Sur une hausse de {{UK_CHANGE}} milliards de dollars, {{UK_GOLD}} milliards proviennent de l’or brut. Les expéditions d’or vers la Suisse et Hong Kong reculent. Dans la décomposition au point milieu de la part britannique hors États-Unis, 3,165 des quelque 6,707 points viennent d’une hausse de la part du Royaume-Uni à l’intérieur des produits à six chiffres, et 3,542 points de l’évolution du panier de produits. Les entrées et sorties de produits déclarés ont une contribution négligeable. L’or à lui seul contribue environ 6,910 points. Le rôle de Londres comme place de négoce et d’entreposage aide à interpréter la destination. Les données douanières ne permettent pas de suivre l’acheteur final au-delà du marché déclaré.

Les quantités comparables apportent un autre éclairage. Pour la principale ligne d’or brut destinée au Royaume-Uni (SH8 71081210), la quantité déclarée passe de 207,20 à 252,13 millions de grammes (+21,7 %) et la valeur unitaire nominale de 107,38 à 158,62 $ CA par gramme (+47,7 %). La décomposition au point milieu attribue environ 5,976 milliards de dollars à la quantité et 11,768 milliards à la valeur unitaire. Pour la ligne chinoise de pétrole brut lourd (SH8 27090010), la quantité passe de 4,074 à 12,656 millions de mètres cubes, tandis que la valeur unitaire baisse de 600,97 à 543,53 $ CA par mètre cube. La qualité, le calendrier des opérations, les contrats et la devise influencent aussi la valeur unitaire. L’analyse distincte d’Affaires mondiales Canada indique une hausse du prix et une baisse du volume de l’or toutes destinations en 2025. Cette observation est compatible avec la hausse de quantité d’une ligne vers le Royaume-Uni.

{{fig:commodity}}

{{fig:dest_change}}

## 8. Concentration géographique et réconciliation des mesures

L’IHH national toutes destinations diminue d’environ 0,579 en 2024 à 0,521 en 2025. L’IHH hors États-Unis augmente de {{HHI24}} à {{HHI25}}. Les cinq premières destinations non américaines, classées séparément chaque année, représentent 50,0 % du portefeuille en 2024 et 54,9 % en 2025. Le Royaume-Uni devance la Chine en 2025. La part chinoise reste près de 16,9 % après arrondissement.

L’exclusion d’un produit entraîne le recalcul des parts et du dénominateur. Sans le SH 710812, l’IHH hors États-Unis passe de {{EX_GOLD24}} à {{EX_GOLD25}}. Dans ce panier, la part du Royaume-Uni baisse de 3,626 % à 3,555 %. L’exclusion du chapitre 71 entier atténue aussi fortement la hausse. L’exercice décrit un portefeuille observé selon un périmètre différent. Il ne simule pas le commerce ni les achats dans un monde sans or. La non-linéarité de l’IHH empêche d’interpréter ces écarts comme des contributions causales additives.

Les indices publiés et reconstruits sont conservés en parallèle. Le millésime annuel archivé reproduit, à la précision affichée, le chiffre national publié de 0,59 pour 2022. L’archive donne 0,587571 et la série active 0,581086. La vérification reproduit aussi le 0,62 ontarien. En 2013, 2016 et 2018, les écarts nationaux dépassent légèrement la tolérance d’arrondissement. En 2025, l’IHH hors États-Unis reconstruit de {{HHI25}} reste inférieur au seuil de 0,095 qui permettrait l’affichage de 0,10. La normalisation du dénominateur par la somme des partenaires et le regroupement des zones américaines ne résolvent pas ces écarts.

La reconstitution à partir des lignes détaillées concorde avec l’IHH du tableau annuel actif en 2024–2025, notamment pour le Yukon et l’Île-du-Prince-Édouard, où les indices officiels demeurent différents. La concentration ou la petite taille de ces portefeuilles peut amplifier un changement de comptabilisation, et l’explication des écarts reste à vérifier. Pour le Canada en 2020, une valeur positive libellée Canada empêche la reconstruction stricte. Le graphique conserve cette interruption et présente séparément la mesure publiée. Le modèle économétrique applique ses propres contrôles à la date du prédicteur.

{{fig:hhi}}

{{table:gold_hhi}}

## 9. Méthodologie économétrique

Le modèle C est une projection conditionnelle historique. Soit X(g,k,t) la valeur positive des exportations nationales hors États-Unis d’un groupe province–produit. Pour une année de départ t, Y(g,k,t) est la valeur absolue de la différence entre log X(g,k,t+1) et log X(g,k,t). La régression utilise l’IHH hors États-Unis à t−1, le logarithme de X à t−1 et la part américaine des exportations mondiales à t−1. Elle couvre dix provinces et onze sections du SCPAN. Les totaux nationaux, les territoires et les transactions spéciales sont hors champ. Les années de départ de 2011 à 2024 utilisent des observations sources de 2010 à 2025.

`Y(g,k,t) = a(g,k) + b(k,t) + c(g,t) + β IHH(g,k,t−1) + γ₁ log X(g,k,t−1) + γ₂ PartÉU(g,k,t−1) + u(g,k,t).`

Les effets fixes province–produit absorbent les différences de spécialisation persistantes. Les effets produit–année absorbent les chocs communs dans chaque section. Les effets province–année absorbent les mouvements partagés par les produits d’une province. Le délai d’un an entre la mesure de l’IHH et le début du résultat évite le partage d’un même point de mesure. L’anticipation de la demande, la persistance des chocs, la sélection des portefeuilles actifs et les variations locales de prix restent possibles. Toutes les cellules ont le même poids et l’association est exprimée pour une hausse de 0,10 de l’IHH.

Sur 1 540 cellules attendues, 1 513 satisfont aux critères de retard et de positivité des deux années du résultat. Le seuil préétabli de 1 million de dollars canadiens pour le portefeuille retardé retire 59 cellules admissibles. Il réduit le poids des très petits montants de référence. Avant estimation, les premier et cinquième centiles des valeurs retardées admissibles s’établissaient à environ 0,211 et 1,283 million de dollars. Des variantes de seuil et de panel équilibré ont été définies avant le calcul du coefficient. Parmi les 1 454 cellules principales, aucune n’est seule dans un niveau d’effet fixe après le seuil. La spécification admet un panel non équilibré. Les deux valeurs positives nécessaires au logarithme limitent l’analyse des cessations d’exportation.

Les nombres de niveaux des effets fixes sont de 108, 154 et 140. Le rang combiné est de 368 et passe à 371 en incluant les trois coefficients. L’écart-type de l’IHH passe de 0,16126 à 0,08359 après projection sur les effets fixes et les contrôles. Les dix provinces contribuent à la variation utilisée. La concentration des leviers correspond à environ 7,89 provinces de poids égal. Les moindres carrés après retrait des effets fixes concordent avec une régression explicite de plein rang. Cette corroboration vérifie le calcul sous la structure retenue.

L’inférence utilise la covariance CR1 regroupée par province et le bootstrap restreint de Webb. Le bootstrap impose l’hypothèse nulle, applique un poids par province tiré parmi six valeurs, réestime le modèle complet et standardise la statistique avec la covariance provinciale CR1. Il comprend 9 999 tirages. L’intervalle à 95 % résulte de l’inversion des tests. Les inférences par produit ou à deux dimensions et les exclusions d’une province éclairent la sensibilité. Des fenêtres annuelles adjacentes partagent des dates, ce qui peut induire une dépendance. Le regroupement provincial traite la dépendance sérielle et interproduit à l’intérieur d’une province. Après retrait des moyennes produit–année, des chocs résiduels communs aux provinces peuvent subsister.

## 10. Estimation principale et incertitude

Le coefficient de l’IHH vaut **+{{BETA}}** sur l’échelle de 0 à 1. Une hausse de 0,10 correspond à **+{{SCALED}} point logarithmique**, contre une variation annuelle absolue médiane de 0,1633 point logarithmique. L’intervalle à 95 % par hausse de 0,10 avec covariance provinciale CR1 est [−0,06903 ; +0,09468]. Celui du bootstrap restreint de Webb est [{{LOW}} ; +{{HIGH}}] avec une valeur p de {{P}}. Une association d’ampleur économique non négligeable demeure compatible avec les résultats dans les deux sens. Le signe de l’estimation ponctuelle ne suffit pas à déterminer celui de l’association sous-jacente.

Le R² global vaut 0,51860, le R² ajusté 0,35414 et le R² après retrait des effets fixes 0,00862. Les trois variables explicatives expliquent ensemble moins de 1 % de la variation restante. Le calcul décrit la qualité de l’ajustement dans l’échantillon. Une prévision hors échantillon exigerait une référence disponible lorsque les futurs effets fixes sont inconnus. Cet exercice est hors du protocole.

Toutes les variantes de covariance donnent des intervalles couvrant zéro. Avec dix grappes provinciales et des marchés de destination partagés, le nombre d’informations indépendantes reste limité. Le Nouveau-Brunswick a le levier partiel provincial le plus élevé (17,85 %). Certaines observations ont aussi un levier individuel important dans des portefeuilles petits ou irréguliers. Retirer la Nouvelle-Écosse ou l’Île-du-Prince-Édouard change le signe de l’estimation. Le document conserve ces résultats dans l’évaluation empirique.

{{table:regression}}

{{fig:intervals}}

## 11. Robustesse et sensibilité

L’exclusion des produits métalliques et des minéraux non métalliques (C14) donne +0,0145 point logarithmique par hausse de 0,10 de l’IHH. La fin du résultat en 2024 donne +0,0126. Ces estimations restent proches de la principale. Sans seuil supplémentaire, l’estimation est de −0,0015. Les seuils de 100 000 $ et de 10 millions de dollars donnent respectivement +0,0124 et +0,0113. Le panel équilibré de 1 372 observations et 98 groupes donne +0,0259.

La pondération par la valeur retardée donne plus de poids aux portefeuilles initialement grands et produit **−0,0275**, avec un intervalle provincial à 95 % de [−0,0567 ; +0,0016]. La variation signée donne +0,0564 tandis que l’ampleur des baisses donne −0,0218. Les deux variables répondent à des questions différentes et leurs signes peuvent diverger. Les variantes utilisant la part de la première destination et celle des trois premières donnent des estimations positives faibles. L’IHH toutes destinations donne une estimation négative faible. Le décompte des partenaires actifs donne une estimation près de zéro par destination supplémentaire.

Les exercices sans chevauchement séparent les années de départ paires et impaires et utilisent aussi des variations annualisées sur deux ans. Les signes varient selon la fenêtre. En retirant une province à la fois, la plage va de −0,0077 à +0,0329 par hausse de 0,10. Les 26 intervalles secondaires avec regroupement provincial incluent zéro. Ces comparaisons sont diagnostiques et portent parfois sur des variables de résultat ou des populations différentes. Aucun portefeuille répondant aux critères avec départ positif et valeur finale observée n’atteint un total nul. La régression de sortie prévue ne satisfait donc pas au seuil minimal de soutien. L’absence de sorties à ce niveau ne renseigne pas sur les entreprises ou destinations qui disparaissent au sein d’un portefeuille qui continue d’exporter.

{{fig:robust}}

{{fig:loo}}

## 12. Projet pilote sur les droits visant l’acier

L’annonce du 10 février 2025 et l’entrée en vigueur du 12 mars définissent une fenêtre possible pour analyser l’article 232 sur l’acier. Le régime de mars prévoit un taux additionnel de 25 % pour les entrées ordinaires visées à la note 16(j) du chapitre 99, sous réserve des autres règles et des exceptions applicables. La hausse du 4 juin à 50 % change le régime. Février peut refléter l’anticipation et mars combine plusieurs régimes. La fenêtre initiale offre 37 mois complets avant l’événement et deux après, avril et mai.

Le barème américain archivé et l’annexe juridique établissent {{PILOT_LINES}} lignes HTS10 sur 301 sous-positions HTS8, {{PILOT_HS6}} produits SH6 et {{PILOT_HS4}} positions SH4 nominales. Les suffixes nationaux du SH8 canadien et du HTS10 américain diffèrent. L’analyse conserve toutes les lignes américaines descendantes des positions à six chiffres retenues, puis vérifie l’homogénéité du traitement et les libellés canadiens. Vingt-quatre positions de base à quatre chiffres ont au moins un produit à six chiffres stable avec des flux américains positifs dans tous les mois requis. Les familles relèvent d’une seule date d’effet. Ce décompte ne constitue pas un nombre vérifié de chocs indépendants.

Le recensement américain fournit les valeurs en douane des importations pour consommation et les droits calculés en janvier, avril et mai. Les ratios de droits du panier visé s’établissent à 0,00 %, 22,83 % et 22,60 %. Ils décrivent les importations observées et peuvent inclure plusieurs autorités et demandes de préférence. Ils ne révèlent ni les paiements nets après remboursement, ni l’incidence de l’article 232 seul, ni la répartition du coût entre exportateurs, importateurs et consommateurs. Les mesures à la frontière nord de mars, l’ACEUM, le cumul précisé en avril et les contre-mesures canadiennes se chevauchent. Un code tarifaire seul ne permet pas de mesurer ces expositions.

Le Mexique présente les flux les plus continus parmi les autres destinations examinées. Seuls quatre produits de base à six chiffres ont un soutien positif continu commun aux États-Unis et au Mexique. L’un chevauche une procédure antidumping sur certains aciers résistants à la corrosion, dont la décision préliminaire américaine sur les produits canadiens s’applique à partir du 10 avril. Les comparateurs en amont ont des caractéristiques économiques différentes, et un seul possède une couverture complète commune aux deux destinations. Le détournement des échanges peut toucher les comparateurs. Avec deux mois après l’entrée en vigueur, des conditions à l’entrée encore imparfaitement observées et peu de variation de comparaison, le projet pilote reste descriptif. Aucun coefficient tarifaire n’est estimé.

## 13. Interprétation économique et implications pour le suivi

Trois mesures répondent à des questions distinctes. La part américaine des exportations brutes indique où la valeur déclarée des marchandises est expédiée. L’IHH conditionnel décrit la répartition de la valeur entre les autres destinations. L’exposition de la production et de l’emploi canadiens requiert des données de valeur ajoutée et d’emploi tenant compte des intrants importés, des fournisseurs et de la demande finale. Les mesures peuvent évoluer à des rythmes différents.

Pour suivre la dépendance, la baisse de la part américaine et la hausse simultanée de l’IHH hors États-Unis justifient d’observer les deux indicateurs. Les exclusions de produits montrent si le mouvement est dominé par quelques lignes. Un panel en volume ou à prix constants serait plus informatif qu’un changement de composition en valeur si la question concerne l’activité réelle. La valeur brute est utile pour suivre les flux douaniers. Le PIB régional donne une échelle et la valeur ajoutée estime l’activité nationale attribuable à une demande. Les données d’entreprises et de travailleurs sont nécessaires pour étudier l’ajustement et sa répartition. Ces implications portent sur la mesure, sans effet de traitement estimé.

La régression ne fournit pas de règle fiable pour convertir une baisse de l’IHH en amélioration attendue de la stabilité des exportations. Une politique d’accès aux marchés peut agir sur les volumes déjà exportés, l’entrée sur de nouveaux marchés, l’investissement, la tarification et les chocs de demande. L’exclusion de l’or décrit un panier observé différent et ne mesure pas les substitutions après une intervention. Le projet pilote sur l’acier apporte une leçon analogue. Le taux légal est un point de départ. L’exposition dépend aussi du calendrier, de l’origine déclarée, du contenu, de la préférence et des exemptions.

## 14. Limites et travaux futurs

La base douanière ne retrace pas la demande finale lorsque les marchandises transitent par des places commerciales. Les valeurs courantes combinent prix, quantités et composition. Une extension empirique devrait réunir des unités physiques concordantes ou des déflateurs à l’échelle produit–destination, avec des seuils de couverture explicites. Si ces données sont rares, une étude limitée à des lignes bien mesurées sera préférable à une extrapolation des exemples à huit chiffres.

Les portefeuilles historiques peuvent incorporer des anticipations de volatilité, des coûts logistiques, du financement commercial et des changements dans les entreprises exportatrices. Les effets fixes retirent les mouvements communs. Des chocs locaux différenciés subsistent. Une mesure de résilience réelle pourrait intégrer les corrélations de demande entre destinations et les possibilités de substitution des trajets. Une analyse prédictive exigerait de réserver une période future et de définir une référence exploitable avant de connaître les futurs effets fixes.

Les indices de concentration peuvent aussi suivre avec retard les révisions des valeurs bilatérales. Des fichiers archivés supplémentaires et des métadonnées du diffuseur pourraient résoudre certains écarts régionaux, récents ou d’arrondissement. Les indicateurs demeurent versionnés séparément. Une future étude tarifaire devrait assurer la concordance des codes, la vérification de l’origine et des exonérations à l’entrée, ainsi qu’une variation de comparaison non contaminée. Le présent travail vérifie la faisabilité documentaire sans mesurer l’incidence. Enfin, le commerce de marchandises exclut les services et une large part des mécanismes d’ajustement des ménages et des entreprises. La dépendance économique globale dépasse ce que les ratios douaniers permettent d’observer.

## 15. Conclusion

La part américaine des exportations nationales de marchandises passe de {{US24}} % à {{US25}} % entre 2024 et 2025. Les autres destinations se concentrent davantage et l’or et le pétrole brut expliquent {{GOLD_CRUDE_PCT}} % de la hausse nominale hors États-Unis. Le retrait de l’or brut change sensiblement l’interprétation par destination. Certaines lignes présentent une hausse des quantités, et l’analyse met aussi en évidence une forte composante de valeur unitaire et des mouvements différents en volume agrégé.

Le coefficient préenregistré est faible au regard de son incertitude statistique. Les résultats n’établissent pas qu’une baisse de la concentration stabiliserait les exportations nominales ou réelles. Le projet pilote sur l’acier vérifie la portée juridique et les données miroir, tout en révélant les lacunes du groupe de comparaison. L’étude décrit l’évolution de l’exposition. Son effet sur la résilience économique demeure ouvert.

## Références

- Affaires mondiales Canada (2026). *Le point sur le commerce en 2026*, encadré 1.4.1 sur les exportations d’or. [Rapport](https://international.canada.ca/en/global-affairs/corporate/reports/chief-economist/state-trade/2026).
- Cadot, O., Carrère, C. et Strauss-Kahn, V. (2011). Export Diversification: What’s behind the Hump? *Review of Economics and Statistics*, 93(2), 590–605. [Article](https://doi.org/10.1162/REST_a_00078).
- Di Giovanni, J. et Levchenko, A. A. (2010). The Risk Content of Exports: A Portfolio View of International Trade. *Document de travail NBER 16005*. [NBER](https://www.nber.org/papers/w16005).
- Haddad, M., Lim, J. J., Pancaro, C. et Saborowski, C. (2013). Trade openness reduces growth volatility when countries are well diversified. *Canadian Journal of Economics*, 46(2), 765–790. [Article](https://doi.org/10.1111/caje.12031).
- Hummels, D., Ishii, J. et Yi, K.-M. (2001). The nature and growth of vertical specialization in world trade. *Journal of International Economics*, 54(1), 75–96. [Article](https://doi.org/10.1016/S0022-1996(00)00093-3).
- Koren, M. et Tenreyro, S. (2007). Volatility and Development. *Quarterly Journal of Economics*, 122(1), 243–287. [Article](https://doi.org/10.1162/qjec.122.1.243).
- MacKinnon, J. G., Nielsen, M. Ø. et Webb, M. D. (2023). Cluster-robust inference: A guide to empirical practice. *Journal of Econometrics*, 232(2), 272–299. [Article](https://doi.org/10.1016/j.jeconom.2022.04.001).
- Statistique Canada. Commerce annuel et mensuel de marchandises (12-10-0173-01 et 12-10-0175-01), millésime du 18 novembre 2026 à Toronto. [Annuel](https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=1210017301) · [Mensuel](https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=1210017501).
- Statistique Canada. Concentration des marchés d’exportation (12-10-0129-01). [IHH publié](https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=1210012901) · [Résultats provinciaux](https://www150.statcan.gc.ca/n1/daily-quotidien/250506/dq250506a-fra.htm).
- Statistique Canada. Commerce international canadien de marchandises (CICM), archives du SH pour les exportations nationales. [Données ouvertes](https://open.canada.ca/data/en/dataset/2909a648-5753-4924-878a-b069392d9cde) · [Guide de référence](https://www150.statcan.gc.ca/n1/pub/13-605-x/2025001/article/00003-fra.htm).
- Statistique Canada. PIB des provinces et territoires (36-10-0711-01), valeur ajoutée et emplois attribuables aux exportations et à la demande étrangère (12-10-0100-01), emploi de l’Enquête sur la population active (14-10-0022-01). [PIB](https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=3610071101) · [Valeur ajoutée et emplois](https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=1210010001) · [Emploi](https://www150.statcan.gc.ca/t1/tbl1/fr/tv.action?pid=1410002201).
- États-Unis. Proclamation 10896 et mise en œuvre à 90 FR 11249. [Champ juridique](https://www.govinfo.gov/content/pkg/FR-2025-03-05/html/2025-03598.htm) · [Directives de cumul de la CBP](https://content.govdelivery.com/accounts/USDHSCBP/bulletins/3e0a63e) · [Hausse de taux en juin](https://www.govinfo.gov/content/pkg/DCPD-202500655/html/DCPD-202500655.htm) · [Décision antidumping préliminaire](https://www.govinfo.gov/content/pkg/FR-2025-04-10/html/2025-06135.htm).
- Bureau du recensement des États-Unis et USITC. Fichiers détaillés d’importations de marchandises et révision 4 du HTS pour 2025. [Importations](https://www.census.gov/foreign-trade/data/IMDB.html) · [Barème HTS](https://www.usitc.gov/2025_hts_revision_4).
- Webb, M. D. (2023). Reworking wild bootstrap-based inference for clustered errors. *Canadian Journal of Economics*, 56(3), 839–858. [Article](https://doi.org/10.1111/caje.12661).

## Annexe A. Échantillon principal et variantes

Le registre des 1 540 cellules enregistre les motifs qui se chevauchent et les niveaux d’effets fixes isolés. Les 24 IHH retardés indisponibles incluent des destinations invalides ou non attribuées. Huit cellules ont des contrôles retardés indisponibles. Le panel théorique comporte neuf départs et neuf fins avec un zéro vérifié. Le seuil de taille peut se superposer à un autre motif. Les zéros et les valeurs indisponibles gardent des statuts distincts, sans données fabriquées. L’application du seuil après les autres contrôles laisse 1 454 cellules d’estimation.

{{table:robustness}}

La ligne sur le nombre de partenaires s’interprète par destination active supplémentaire. Les parts et indices sont exprimés par hausse de 0,10. Les variations sur deux ans sont annualisées en divisant la variation logarithmique par deux. Tous les intervalles secondaires utilisent CR1 regroupé par province. Le projet conserve les estimations détaillées, la composition de chaque échantillon et le champ du projet pilote sur l’acier.

## Annexe B. Données et reproductibilité

Les valeurs du classement géographique de 2025 sont détaillées ci-dessous à la précision affichée. Les montants sont en dollars canadiens courants. La part divise les exportations vers les États-Unis par les exportations mondiales de la même géographie. Source : Statistique Canada, 12-10-0173-01.

{{table:regions}}

Ce travail et l’observatoire Streamlit lisent les mêmes fichiers verrouillés des phases 3 à 4B. Le rendu part de sources Markdown distinctes par langue et d’une insertion commune des valeurs principales et des tableaux. Les graphiques reprennent les fichiers annuels et mensuels vérifiés, la décomposition par produit issue de la CICM et les fichiers d’estimation et d’incertitude contrôlés. Les empreintes des sources, les commandes de rendu et les journaux de tests sont disponibles dans le dossier du projet.

© 2026 Manau Salaun. Les textes et figures originaux sont sous licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr). Les données sources conservent les conditions citées ci-dessous.

Adapté de Statistique Canada, tableaux 12-10-0173-01 et 12-10-0129-01 (2010–2025), 12-10-0175-01 (janvier 2025 à septembre 2026), 12-10-0100-01 (Canada jusqu’en 2024 et provinces et territoires de 2013 à 2022), 36-10-0711-01 (2010–2023) et archives des exportations nationales de la CICM (2022–2025). Cela ne constitue pas une approbation de ce produit par Statistique Canada. Les sources américaines sont attribuées au Bureau du recensement des États-Unis, à l’USITC et aux textes juridiques pertinents. [Licence ouverte de Statistique Canada](https://www.statcan.gc.ca/fr/avis/licence-ouverte)

## Annexe C. Comparaison mensuelle et admissibilité du panel

Le tableau couvre janvier à septembre de chaque année dans la série mensuelle distincte non désaisonnalisée. Les montants sont en milliards de dollars canadiens courants. La part repose sur les sommes de neuf mois. Statistique Canada, tableau 12-10-0175-01.

{{table:monthly}}

Le modèle principal utilise la série annuelle. Les contrôles du tableau suivant précèdent l’estimation. Un montant retardé nul peut à la fois rendre l’IHH indisponible, empêcher le calcul du logarithme et faire échouer le seuil de taille. La somme des motifs compterait donc plusieurs fois certaines observations. Le registre archivé relève les 86 exclusions distinctes.

{{table:sample}}

Les contrôles préservent la distinction entre un zéro déclaré et une donnée manquante ou non utilisable. Le résultat logarithmique exclut les valeurs nulles aux deux dates. Étudier la disparition des débouchés demanderait une autre variable de résultat, des données d’une autre granularité et un protocole adapté.
