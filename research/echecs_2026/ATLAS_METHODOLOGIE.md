# Atlas des échecs français — protocole d'enquête

## Objet
Mesurer la structure des activités échiquéennes publiques françaises par triangulation : tournoi (référence FFE), personne adulte (présence sportive / arbitrage / organisation), club (effectifs engagés), ville, année et financements publiés.

## Trois graphes distincts
1. **Sportif** : personne adulte — participe à — tournoi ; club — représente N inscrits — tournoi.
2. **Organisation** : arbitre — arbitre — tournoi ; organisateur — organise — tournoi.
3. **Économique** : financeur — verse — bénéficiaire ; le montant n'est affecté à un tournoi que lorsqu'une convention ou une comptabilité analytique l'établit.

Une arête de **co-présence** est dérivée de deux présences indépendamment publiées à un même événement ; elle ne signifie pas connaissance, relation personnelle, contrat, collusion ou favoritisme.

## Métriques
- Récurrence : nombre de références FFE distinctes partagées par une paire d'acteurs.
- Stabilité temporelle : nombre d'années distinctes où apparaissent les références communes.
- Portée territoriale : lieux distincts observés, non lieux de résidence.
- Concentration de club : parts des inscriptions agrégées parmi les tableaux de participants effectivement récupérés.
- Communautés : Louvain sur le **sous-graphe des co-présences répétées** ; ne pas inférer de communauté sociale réelle.
- Flux économiques : identifiant SIREN/SIRET préféré aux noms ; vérifier les intitulés et périmètres des versements.

## Règles de précaution
- Nommage longitudinal : uniquement catégories adultes (Senior/Vétéran) et deux grands maîtres nommément étudiés dont la majorité en 2026 est documentée.
- Données de mineurs : aucun profil longitudinal ; uniquement total de participants et nombre par club.
- Homonymies : la normalisation du nom permet de proposer une jointure, pas d'attester une identité.
- Un événement peut être subdivisé en plusieurs tournois, et une même personne apparaître dans plusieurs tableaux : ne pas interpréter ces références comme des rencontres indépendantes.
- Tous les événements affichés sont historiques à la date du 1er novembre 2026.

## Couverture et audit
Le premier export départemental concerne **la première page de chaque liste** ; ce n'est pas le recensement complet. La FFE utilise une pagination ASP.NET ; les extractions nationales exhaustives exigeraient la collecte des pages secondaires, un contrôle des doublons et une vérification croisée du calendrier.
Les nombres affichés dans le site sont ceux des pages effectivement extraites, conservés dans `summary.json`. Le corpus brut des subventions est celui du PLF 2025 pour l'année de versement 2023.
La collecte des fiches individuelles et listes de participants est bornée : les résultats sont des **statistiques de corpus**, jamais des taux nationaux.
Les liens de preuve doivent toujours être de la forme `https://www.echecs.asso.fr/FicheTournoi.aspx?Ref=...` ou `Resultats.aspx?...Action=Ls`.

## Fichiers
- `atlas_v3/results/national_index_first_pages.csv` : catalogue initial.
- `atlas_v3/results/events.csv` : dates, lieux et personnes en fonction.
- `atlas_v3/results/adult_public_participations.csv` : participation adulte par événement.
- `atlas_v3/results/club_delegations.csv` : total des participants par club et événement.
- `atlas_v3/results/coappearances_repeated.csv` : liens répétés et références.
- `atlas_v3/results/communities.json` : communautés statistiques.
- `docs/echecs-atlas/index.html` : interface autonome et consultable hors ligne.

## Sources de référence
- https://www.echecs.asso.fr/Tournois.aspx
- https://www.echecs.asso.fr/ListeTournois.aspx?Action=TOURNOICOMITE&ComiteRef=03
- https://www.echecs.asso.fr/Resultats.aspx?Action=Ls&URL=Tournois%2FId%2F72269%2F72269
- https://data.economie.gouv.fr/
- https://www.echecs.asso.fr/Actus/16020/PV_CD_2026mars.pdf

## Objectifs pour toute analyse élargie
Les agrégats d'autres sources (compte associatif, convention, contrat, société partenaire) doivent comporter date, identifiant source, forme juridique, qualité du lien et niveau de preuve, sans compléter automatiquement les informations manquantes par des hypothèses de parenté ou des similarités de noms.
