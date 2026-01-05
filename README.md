# Comparateur de paiements Up2Pay et Kalisport

Ce logiciel permet de comparer les transactions de paiement entre le système Up2Pay (transactions CB) et la plateforme Kalisport pour identifier les incohérences et faciliter la réconciliation des paiements.

## Fonctionnalités

- **Scan automatique** de répertoires pour les données Up2Pay (Transactions classiques et PNF).
- **Scan automatique** pour les données Kalisport.
- **Support des sections** (ex: "BASKET", "FOOT") pour filtrer les fichiers et nommer les rapports.
- Comparaison automatique des transactions entre les deux systèmes.
- Analyse détaillée des paiements (références, remboursements, restes à payer).
- Génération d'un rapport Excel multi-onglets.

## Prérequis

- Python 3.10 ou supérieur
- [Poetry](https://python-poetry.org/) pour la gestion des dépendances.
- Bibliothèques Python : pandas, openpyxl

## Installation

1. Clonez ce dépôt.
2. Installez les dépendances avec Poetry :
   ```bash
   poetry install
   ```

##  Utilisation

### Préparation des fichiers

1. **Fichier Up2Pay** : Exportez les transactions depuis l'interface Up2Pay au format xls.
Le fichier doit contenir au minimum les colonnes : Num. transaction, Référence commande, Montant, Date & Heure, Type de transaction, Statut de la transaction
2. **Fichier Kalisport** : Exportez les paiements depuis Kalisport au format CSV.
Le fichier doit contenir au minimum les colonnes : ID_PAIEMENT, NUMERO, MONTANT, ETAT, DATE_PAIEMENT, OBJET

### Structure des données

Le programme n'attend plus des fichiers isolés mais une structure de dossiers dans le répertoire de données (par défaut `./data`) :

```text 
data/ 
├── Transaction/ # Contient les fichiers Excel Up2Pay (Export_transactions__.xls) 
├── Pnf/ # Contient les fichiers Excel Up2Pay PNF (Export_pnf__.xls) 
└── kalisport/ # Contient les exports CSV Kalisport (paiements-*.csv)
```
*Note : Si vous utilisez l'option `--section`, le programme cherchera des fichiers commençant par le nom de la section (ex: `AQS_*.xlsx`).*

### Exécution du programme

#### Via la ligne de commande

```bash
python -m compare_cb_up2pay_kalisport.app --data-dir chemin/vers/fichier_a_charger --output-dir dossier/sortie --section SECTION
```

**Options disponibles :**
* `--data-dir`, `-d` : Répertoire racine des données (par défaut: `data`).
* `--output-dir`, `-o` : Répertoire où sera généré le rapport Excel (par défaut: `output`).
* `--section`, `-s` : Nom de la section (ex: `ATH`). Filtre les fichiers d'entrée et préfixe le fichier de sortie.
* `--debug` : Active les logs détaillés dans la console et dans `debug.log`.

## Interprétation des résultats

Le fichier Excel généré contient plusieurs onglets :
1. **Comparaison** : Analyse ligne par ligne entre Up2Pay et Kalisport.
2. **Résumé par Référence** : Synthèse par référence Up2Pay (nombre de paiements, montants, remboursements).
3. **Résumé par ID** : Analyse technique basée sur les IDs de transaction.

### Statuts de comparaison

* **OK** : La transaction est présente dans les deux systèmes avec des statuts cohérents (Up2Pay "Acceptée" et Kalisport "Payé") ou la transaction est refusée dans Up2Pay (ce qui est normal qu'elle n'apparaisse pas dans Kalisport)
* **Erreur: Paiement accepté dans Up2Pay mais absent dans Kalisport** : La transaction est acceptée dans Up2Pay mais n'a pas été trouvée dans Kalisport
* **Erreur: Up2Pay accepté mais Kalisport [statut]** : La transaction est acceptée dans Up2Pay mais a un statut différent de "Payé" dans Kalisport
* **Erreur: Up2Pay [statut]** : La transaction a un statut problématique dans Up2Pay (ni "Acceptée" ni "Refusée")
* **Erreur: Paiement non trouvé dans Kalisport** : La transaction existe dans Up2Pay mais n'a pas été trouvée dans Kalisport (et n'est pas refusée)

## Dépannage

Si aucun fichier n'est trouvé :
1. Vérifiez que vos fichiers sont bien dans les bons sous-répertoires (`Transaction/`, `Pnf/`, `kalisport/`).
2. Si vous utilisez l'option `--section KRT`, assurez-vous que vos fichiers commencent par `BASKET_`.
3. Utilisez le mode `--debug` pour voir exactement quels motifs de recherche (patterns) le programme utilise pour scanner les dossiers.
