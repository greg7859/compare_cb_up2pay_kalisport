import csv
import os
import glob
import logging
from typing import List
from .models import Up2PayTransaction, Up2PayPlannedTransaction, KalisportPayment


class FileReader:
    """Classe pour lire les fichiers CSV de Up2Pay et Kalisport."""

    @staticmethod
    def get_file_from_path(data_dir: str, template: str) -> str:
        logger = logging.getLogger(__name__)
        logger.debug(f"Recherche de fichiers avec le template '{template}' dans '{data_dir}'")
        
        search_pattern = os.path.join(data_dir, template)
        logger.debug(f"Pattern de recherche: {search_pattern}")
        
        files = glob.glob(search_pattern)
        logger.debug(f"Fichiers trouvés: {files}")
        
        if not files:
            error_msg = f"Aucun fichier trouvé dans {data_dir} avec le template {template}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        selected_file = files[0]  # Prend le premier fichier trouvé
        logger.info(f"Fichier sélectionné: {selected_file}")
        
        if len(files) > 1:
            logger.warning(f"Plusieurs fichiers trouvés ({len(files)}), utilisation du premier: {selected_file}")
            logger.debug(f"Fichiers ignorés: {files[1:]}")
        
        return selected_file

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
        logger = logging.getLogger(__name__)
        logger.info(f"Début de la lecture du fichier Up2Pay avec template '{template}'")
        
        up2pay_file = FileReader.get_file_from_path(data_dir, template)
        up2pay_data = []
        
        try:
            logger.debug(f"Ouverture du fichier Up2Pay: {up2pay_file}")
            with open(up2pay_file, 'r', encoding='iso-8859-1') as f:
                reader = csv.DictReader(f, delimiter=';')
                
                # Log des en-têtes de colonnes
                if reader.fieldnames:
                    logger.debug(f"Colonnes détectées dans le fichier Up2Pay: {reader.fieldnames}")
                
                row_count = 0
                for row in reader:
                    try:
                        transaction = Up2PayTransaction.from_csv_row(row)
                        up2pay_data.append(transaction)
                        row_count += 1
                        
                        # Log de debug pour les premières lignes
                        if row_count <= 3:
                            logger.debug(f"Transaction Up2Pay #{row_count}: {transaction}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement de la ligne {row_count + 1} du fichier Up2Pay: {e}")
                        logger.debug(f"Données de la ligne problématique: {row}")
                        raise
            
            logger.info(f"Lecture du fichier Up2Pay terminée: {len(up2pay_data)} transactions chargées")
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier Up2Pay '{up2pay_file}': {e}")
            raise
        
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
        logger = logging.getLogger(__name__)
        logger.info(f"Début de la lecture du fichier Up2Pay PNF avec template '{template}' (optionnel)")
        
        try:
            up2pay_file = FileReader.get_file_from_path(data_dir, template)
            up2pay_data = []
            
            logger.debug(f"Ouverture du fichier Up2Pay PNF: {up2pay_file}")
            with open(up2pay_file, 'r', encoding='iso-8859-1') as f:
                reader = csv.DictReader(f, delimiter=';')
                
                # Log des en-têtes de colonnes
                if reader.fieldnames:
                    logger.debug(f"Colonnes détectées dans le fichier Up2Pay PNF: {reader.fieldnames}")
                
                row_count = 0
                for row in reader:
                    try:
                        transaction = Up2PayPlannedTransaction.from_csv_row(row)
                        up2pay_data.append(transaction)
                        row_count += 1
                        
                        # Log de debug pour les premières lignes
                        if row_count <= 3:
                            logger.debug(f"Transaction planifiée Up2Pay #{row_count}: {transaction}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement de la ligne {row_count + 1} du fichier Up2Pay PNF: {e}")
                        logger.debug(f"Données de la ligne problématique: {row}")
                        raise
            
            logger.info(f"Lecture du fichier Up2Pay PNF terminée: {len(up2pay_data)} transactions planifiées chargées")
            return up2pay_data
            
        except FileNotFoundError:
            logger.info(f"Fichier PNF optionnel non trouvé dans {data_dir} (template: {template}). Continuation du processus...")
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier Up2Pay PNF: {e}")
            raise

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
        logger = logging.getLogger(__name__)
        logger.info(f"Début de la lecture du fichier Kalisport avec template '{template}'")
        
        kalisport_file = FileReader.get_file_from_path(data_dir, template)
        kalisport_data = []
        
        try:
            logger.debug(f"Ouverture du fichier Kalisport: {kalisport_file}")
            with open(kalisport_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                # Log des en-têtes de colonnes
                if reader.fieldnames:
                    logger.debug(f"Colonnes détectées dans le fichier Kalisport: {reader.fieldnames}")
                
                row_count = 0
                for row in reader:
                    try:
                        payment = KalisportPayment.from_csv_row(row)
                        kalisport_data.append(payment)
                        row_count += 1
                        
                        # Log de debug pour les premières lignes
                        if row_count <= 3:
                            logger.debug(f"Paiement Kalisport #{row_count}: {payment}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement de la ligne {row_count + 1} du fichier Kalisport: {e}")
                        logger.debug(f"Données de la ligne problématique: {row}")
                        raise
            
            logger.info(f"Lecture du fichier Kalisport terminée: {len(kalisport_data)} paiements chargés")
            
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier Kalisport '{kalisport_file}': {e}")
            raise
        
        return kalisport_data