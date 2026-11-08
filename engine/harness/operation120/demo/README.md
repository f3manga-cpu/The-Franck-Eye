# Préventif — démonstration Excel autonome

Un classeur prêt à présenter pour suivre les équipements, les opérations préventives récurrentes, les prochaines échéances et les interventions réalisées. **Toutes les machines, zones, personnes et interventions sont fictives.** Aucun exemple ne constitue une consigne de maintenance.

Ouvrir **[Preventif_Demo.xlsx](Preventif_Demo.xlsx)** dans Excel. Pour une présentation rapide dans un navigateur, ouvrir **[APERCU.html](APERCU.html)** : cet aperçu statique reprend les valeurs calculées du classeur, sans connexion ni script. Il ne se met pas à jour après modification du XLSX.

## Contenu livré

| Onglet | Fonction |
|---|---|
| Pilotage | Indicateurs, date de référence et scénario de démonstration |
| Equipements | Table filtrable de 50 lignes, 8 équipements fictifs préremplis |
| Plan | Table filtrable de 100 lignes, 12 opérations fictives, périodicité, prochaine date, priorité |
| Historique | Table filtrable de 500 lignes, 9 interventions fictives, résultat et durée |
| Calendrier | 30 jours à partir de la référence, nombre, charge et jusqu’à 4 opérations nommées par jour |
| Guide | Mode d’emploi intégré, capacité et limites |

Cellules **bleues : saisie** ; cellules **grises : formules modifiables**. Les onglets comprennent des listes déroulantes, des contrôles de saisie, des filtres, des volets figés et une mise en forme conditionnelle. Pas de protection, de mot de passe, de macro, de lien externe ni de connexion de données.

## Démonstration en 90 secondes

1. Dans Pilotage, conserver la date démo du **08/11/2026** en B5. Les indicateurs montrent 7 équipements actifs, 10 opérations actives, 1 retard, 6 opérations dans les 7 jours et 9 dans les 30 jours ; aucune saisie à corriger.
2. Dans Plan, PM-001 arrive à échéance le 04/11/2026. Sa dernière intervention **terminée** date du 05/10/2026 ; l’intervention du 07/11 marquée `A reprendre` ne décale pas son échéance.
3. Dans Historique, saisir en **ligne 17** : A `INT-010`, B `PM-001`, D une vraie date Excel `08/11/2026`, E `Technicien test fictif`, F `Terminee`, G `20`, H `Essai fictif`. Ne pas modifier C et I.
4. Après recalcul, la prochaine date de PM-001 devient le **08/12/2026** et le nombre de retards devient zéro.
5. Annuler la saisie de démonstration ou repartir du fichier livré. Le calendrier présente les échéances des 30 jours et surligne les 7 premiers jours.

## Règles de calcul explicites

- Date de référence : B5 de Pilotage si renseignée ; sinon `TODAY()` via B6. Effacer B5 pour le suivi courant. La date système dépend de l’ordinateur qui ouvre le fichier.
- Prochaine date : dernière réalisation valide avec résultat `Terminee` + période en jours calendaires. Sans réalisation valide : première échéance saisie.
- Une réalisation future par rapport à la date de référence est signalée et exclue. Les dates doivent être de vraies dates Excel, sans heure.
- La récurrence repart de la réalisation effective : une intervention tardive ou anticipée décale donc le cycle. Il n’y a pas de planning fixé sur une date d’origine.
- Les fenêtres sont **J à J+6** et **J à J+29**, bornes incluses. Le total à 30 jours inclut celui à 7 jours. Les retards sont comptés séparément.
- Une opération ou un équipement marqué `Non` est en pause : sa date reste visible dans Plan, mais il est exclu des priorités actives et du calendrier.
- Le calendrier affiche **uniquement la prochaine échéance de chaque opération**, et non toutes ses occurrences futures. Une opération hebdomadaire n’y figure donc qu’une fois avant enregistrement d’une nouvelle réalisation.
- Au-delà de quatre opérations le même jour, `Autres` indique combien de noms supplémentaires consulter en filtrant la date dans Plan. Le nombre et la charge incluent toutes les opérations du jour.
- Les contrôles repèrent notamment les identifiants manquants ou dupliqués, les équipements/opérations inconnus, les périodes invalides et les dates de réalisation futures. Ils ne constituent pas une validation exhaustive du métier ; le collage peut contourner les listes déroulantes.

## Adaptation à un usage réel

Faire une copie et supprimer les exemples en effaçant **uniquement les cellules de saisie**. Conserver les formules. Renseigner d’abord Equipements, puis Plan, puis Historique. Utiliser les lignes préformatées : équipements 8–57, opérations 8–107, interventions 8–507. Les IDs doivent rester stables et uniques ; ne pas renommer ou réutiliser un ID déjà référencé.

Les plages de calcul et de validation sont fixes. Ajouter des lignes au-delà de ces capacités ne suffit pas : les plages, listes, formules et contrôles doivent être étendus. Les zones d’impression sont réglées pour les exemples ; les adapter pour imprimer de nouvelles lignes. La colonne Plan `Jours restants` peut rester négative pour une opération en pause ; la colonne `Priorité` fait foi pour l’inclusion dans le calendrier.

## Compatibilité et vérification

Cible : **Excel 2019, 2021 ou Microsoft 365**, avec prise en charge de `MAXIFS`, `COUNTIFS` et `SUMIFS`. Les noms de fonctions sont enregistrés en anglais dans le format XLSX et normalement localisés par Excel. Le recalcul automatique et le recalcul à l’ouverture sont demandés dans le fichier.

**Le fichier n’a pas été ouvert ni recalculé dans Excel.** LibreOffice 24.2 est installé mais n’a pas pu démarrer pour la conversion dans cet environnement. Son affichage et sa compatibilité ne sont donc pas attestés. Un essai dans l’Excel du destinataire reste nécessaire avant de promettre la livraison finale. Si les résultats ne changent pas, activer le calcul automatique puis lancer un recalcul complet (`Ctrl` + `Alt` + `F9` sous Excel Windows).

`openpyxl` n’était pas installé dans l’interpréteur disponible et n’a pas été téléchargé. Le générateur utilise uniquement la bibliothèque standard Python. Un évaluateur Python dédié a analysé et calculé les **2 228 formules stockées** ; il a aussi écrit leurs valeurs en cache pour que la démonstration soit visible avant recalcul. Cet évaluateur couvre les fonctions utilisées ici : il n’est pas une certification Excel ni un moteur général de tableur.

Le rapport exact des vérifications est dans [checks/validation.json](checks/validation.json) : intégrité ZIP, XML, valeurs attendues, changement d’échéance, limites temporelles, exclusions, doublons, débordement du calendrier, absence de macros et de liens externes. La validation ne remplace pas l’ouverture du fichier dans Excel.

Pour reconstruire et vérifier, depuis ce dossier, sans accès réseau :

```sh
python3 scripts/build_workbook.py
python3 scripts/validate_workbook.py
python3 scripts/preview.py
```

Ces commandes **réinitialisent la démonstration** et écrasent le XLSX livré et l’aperçu ; sauvegarder les modifications avant de les lancer. Le fichier dans `build/` est un intermédiaire sans valeurs calculées ; utiliser celui à la racine.

## Limites de livraison

Pas de macros, alertes automatiques, emails, application web, gestion des pièces, synchronisation, droits utilisateurs ou journal infalsifiable. Pas de périodes mensuelles, jours ouvrés, compteurs d’usage, niveaux de service ou consignes constructeur. L’historique est modifiable. Les fréquences, dates et procédures réelles doivent être validées par le responsable maintenance ; ce classeur ne fournit aucune preuve de conformité réglementaire.

La demande du prospect du 08/11/2026 est rapportée par l’orchestrateur ; son message original n’est pas présent ici. Aucun contact, envoi, devis, engagement, paiement ou revenu bancaire n’a été réalisé ou vérifié dans cette session. Voir [HANDOFF.md](HANDOFF.md).
