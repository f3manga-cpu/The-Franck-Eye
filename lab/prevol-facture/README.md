# Prévol Facture — contrôlez la qualité de vos fichiers tiers avant import

**Un outil gratuit, local et sans compte pour examiner un CSV clients/fournisseurs.**

La réforme française de facturation électronique impose depuis le **1er septembre 2026** la capacité de recevoir des factures électroniques aux entreprises concernées. La préparation de vos données peut faciliter le paramétrage et la migration vers une plateforme agréée.

## Utilisation gratuite — sans envoi de données

1. [**Télécharger le fichier HTML autonome**](https://raw.githubusercontent.com/f3manga-cpu/The-Franck-Eye/main/lab/prevol-facture/index.html) (enregistrez-le comme `prevol-facture.html`).
2. Double-cliquez sur le fichier pour l'ouvrir dans Chrome, Firefox ou Safari. Aucune installation ni connexion requise.
3. Choisissez un CSV de tiers (jusqu'à 5 Mo) et cliquez sur **Analyser le fichier**.
4. Consultez les alertes et téléchargez la liste des anomalies au format CSV.

**Contrôles inclus :** doublons de SIRET ou nom/code postal, vérifications syntaxiques SIREN/SIRET, valeurs vides et e-mails au format suspect, incohérences de colonnes. Les doublons de SIREN peuvent être légitimes (plusieurs établissements). Aucun fichier n'est transmis à un serveur : le code s'exécute localement dans votre navigateur.

### Option d'accompagnement : 49 €

Si un fichier de tiers requiert un nettoyage concret, nous proposons un **pilote à périmètre limité** :

- Un CSV clients ou fournisseurs, **500 lignes maximum**, après validation du format et du périmètre.
- Repérage des doublons potentiels, normalisation des champs existants, liste des éléments à corriger.
- Livraison par e-mail sous **3 jours ouvrés** après réception du fichier anonymisé et d'un dossier exploitable.
- Une révision mineure du rapport.

**Avant tout paiement, écrivez à [f3.manga@gmail.com](mailto:f3.manga@gmail.com?subject=Pr%C3%A9vol%20Facture%20%E2%80%94%20Pilote%20CSV) pour confirmer la faisabilité.**

[**Paiement sécurisé Stripe : 49 €**](https://buy.stripe.com/dRm5kEf4S57o2Agdkq43S03) (après validation du périmètre).

> L'outil ne crée pas de factures électroniques, ne garantit pas la conformité réglementaire, ne certifie pas de fichiers Factur-X/UBL/CII et n'est pas une plateforme agréée. Ce service ne remplace pas l'expert-comptable et ne requiert pas de données personnelles non nécessaires.

Sources officielles : [ministère de l'Économie](https://www.economie.gouv.fr/tout-savoir-sur-la-facturation-electronique-pour-les-entreprises) · [Service Public](https://entreprendre.service-public.gouv.fr/vosdroits/F23208).

Développé et proposé par une activité indépendante. Contact : f3.manga@gmail.com. © 2026.
