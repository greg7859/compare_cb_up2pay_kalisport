import csv
import os
import glob
from typing import List
from .models import Up2PayTransaction, Up2PayPlannedTransaction, KalisportPayment


class FileReader:
    """Classe pour lire les fichiers CSV de Up2Pay et Kalisport."""

    @staticmethod
    def get_file_from_path(data_dir: str, template: str) -> str:
        up2pay_files = glob.glob(os.path.join(data_dir, template))
        if not up2pay_files:
            raise FileNotFoundError(f"Aucun fichier Up2Pay trouvé dans {data_dir}")
        
        up2pay_file = up2pay_files[0]  # Prend le premier fichier trouvé
        print(f"--> Lecture du fichier Up2Pay : {up2pay_file}...")
        return up2pay_file

    @staticmethod
    def read_up2pay_file(data_dir: str, template: str) -> List[Up2PayTransaction]:
        """
        Lit le fichier Up2Pay CSV.
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            template: Template du nom de fichier à rechercher
            
        Returns:
            Liste d'objets Up2PayTransaction
        """
        up2pay_file = FileReader.get_file_from_path(data_dir, template)
        up2pay_data = []
        with open(up2pay_file, 'r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                transaction = Up2PayTransaction.from_csv_row(row)
                up2pay_data.append(transaction)
        
        return up2pay_data

    @staticmethod
    def read_up2pay_pnf_file(data_dir: str, template: str) -> List[Up2PayPlannedTransaction]:
        """
        Lit le fichier Up2Pay PNF CSV (optionnel).
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            template: Template du nom de fichier à rechercher
            
        Returns:
            Liste d'objets Up2PayPlannedTransaction (vide si fichier non trouvé)
        """
        try:
            up2pay_file = FileReader.get_file_from_path(data_dir, template)
            up2pay_data = []
            with open(up2pay_file, 'r', encoding='iso-8859-1') as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    transaction = Up2PayPlannedTransaction.from_csv_row(row)
                    up2pay_data.append(transaction)
            
            return up2pay_data
        except FileNotFoundError:
            print(f"--> Fichier PNF optionnel non trouvé dans {data_dir} (template: {template}). Continuation du processus...")
            return []

    @staticmethod
    def read_kalisport_file(data_dir: str, template: str) -> List[KalisportPayment]:
        """
        Lit le fichier Kalisport CSV.
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            template: Template du nom de fichier à rechercher
            
        Returns:
            Liste d'objets KalisportPayment
        """
        kalisport_file = FileReader.get_file_from_path(data_dir, template)
        kalisport_data = []
        with open(kalisport_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                payment = KalisportPayment.from_csv_row(row)
                kalisport_data.append(payment)
        
        return kalisport_data