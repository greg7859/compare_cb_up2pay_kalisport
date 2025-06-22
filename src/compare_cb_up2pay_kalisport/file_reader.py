import csv
import os
import glob
from typing import Dict, List, Optional


class FileReader:
    """Classe pour lire les fichiers CSV de Up2Pay et Kalisport."""

    @staticmethod
    def read_up2pay_file(data_dir: str) -> List[Dict]:
        """
        Lit le fichier Up2Pay CSV.
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            
        Returns:
            Liste de dictionnaires contenant les données Up2Pay
        """
        up2pay_files = glob.glob(os.path.join(data_dir, "Export_*.csv"))
        if not up2pay_files:
            raise FileNotFoundError(f"Aucun fichier Up2Pay trouvé dans {data_dir}")
        
        up2pay_file = up2pay_files[0]  # Prend le premier fichier trouvé
        print(f"--> Lecture du fichier Up2Pay : {up2pay_file}...")
 
        up2pay_data = []
        with open(up2pay_file, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                up2pay_data.append({
                    'transaction_number': row.get('Num. transaction', '').strip(),
                    'amount': row.get('Montant', '').strip().replace(',', '.'),
                    'reference': row.get('Référence commande', '').strip(),
                    'date_time': row.get('Date & Heure', '').strip(),
                    'type': row.get('Type de transaction', '').strip(),
                    'status': row.get('Statut de la transaction', '').strip()
                })
        
        return up2pay_data

    @staticmethod
    def read_kalisport_file(data_dir: str) -> List[Dict]:
        """
        Lit le fichier Kalisport CSV.
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            
        Returns:
            Liste de dictionnaires contenant les données Kalisport
        """
        kalisport_files = glob.glob(os.path.join(data_dir, "paiements-*.csv"))
        if not kalisport_files:
            raise FileNotFoundError(f"Aucun fichier Kalisport trouvé dans {data_dir}")
        
        kalisport_file = kalisport_files[0]  # Prend le premier fichier trouvé
        print(f"--> Lecture du fichier Up2Pay : {kalisport_file}")
 
        kalisport_data = []
        with open(kalisport_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Nettoyer les guillemets des valeurs si nécessaire
                numero = row.get('NUMERO', '').strip().strip('"')
                nom = row.get('NOM', '').strip().strip('"')
                prenom = row.get('PRENOM', '').strip().strip('"')
                mode_paiement = row.get('MODE_PAIEMENT', '').strip().strip('"')
                montant = row.get('MONTANT', '').strip().strip('"').replace(',', '.')
                paye = row.get('PAYE', '').strip().strip('"')
                etat = row.get('ETAT', '').strip().strip('"')
                date_paiement = row.get('DATE_PAIEMENT', '').strip().strip('"')
                
                kalisport_data.append({
                    'transaction_number': numero,
                    'name': nom,
                    'first_name': prenom,
                    'payment_method': mode_paiement,
                    'amount': montant,
                    'paid': paye,
                    'status': etat,
                    'payment_date': date_paiement
                })
        
        return kalisport_data