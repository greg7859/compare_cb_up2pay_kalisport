# Comparateur de paiements Up2Pay et Kalisport

Ce logiciel permet de comparer les transactions de paiement entre le système Up2Pay (transactions CB) et la plateforme Kalisport pour identifier les incohérences et faciliter la réconciliation des paiements.

## Fonctionnalités

- Import des fichiers CSV de transactions Up2Pay
- Import des fichiers CSV de paiements Kalisport
- Comparaison automatique des transactions entre les deux systèmes
- Identification des transactions présentes dans un système mais absentes dans l'autre
- Génération d'un rapport Excel détaillé avec les résultats de la comparaison
- Mise en évidence des écarts de montants ou de statuts

## Prérequis

- Python 3.7 ou supérieur
- Bibliothèques Python : pandas, openpyxl

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/compare-cb-up2pay-kalisport.git
   cd compare-cb-up2pay-kalisport
   ```

2. Installez les dépendances :

```bash
poetry install
```

##  Utilisation

### Préparation des fichiers

1. **Fichier Up2Pay** : Exportez les transactions depuis l'interface Up2Pay au format CSV.
Le fichier doit contenir au minimum les colonnes : Num. transaction, Référence commande, Montant, Date & Heure, Type de transaction, Statut de la transaction
2. **Fichier Kalisport** : Exportez les paiements depuis Kalisport au format CSV.
Le fichier doit contenir au minimum les colonnes : ID_PAIEMENT, NUMERO, MONTANT, ETAT, DATE_PAIEMENT, OBJET

### Exécution du programme

#### Via la ligne de commande

```bash
python -m compare_cb_up2pay_kalisport.app --data-dir chemin/vers/fichier_a_charger --output-dir dossier/sortie
```

Options disponibles :
* --data-dir : Répertoire contenant les fichiers de données (par défaut: data)
* --output-dir : Répertoire de sortie pour le fichier Excel (par défaut: output)

## Interprétation des résultats

* **OK** : La transaction est présente dans les deux systèmes avec des statuts cohérents (Up2Pay "Acceptée" et Kalisport "Payé") ou la transaction est refusée dans Up2Pay (ce qui est normal qu'elle n'apparaisse pas dans Kalisport)
* **Erreur: Paiement accepté dans Up2Pay mais absent dans Kalisport** : La transaction est acceptée dans Up2Pay mais n'a pas été trouvée dans Kalisport
* **Erreur: Up2Pay accepté mais Kalisport [statut]** : La transaction est acceptée dans Up2Pay mais a un statut différent de "Payé" dans Kalisport
* **Erreur: Up2Pay [statut]** : La transaction a un statut problématique dans Up2Pay (ni "Acceptée" ni "Refusée")
* **Erreur: Paiement non trouvé dans Kalisport** : La transaction existe dans Up2Pay mais n'a pas été trouvée dans Kalisport (et n'est pas refusée)