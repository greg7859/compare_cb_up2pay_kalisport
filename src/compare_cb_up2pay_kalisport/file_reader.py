import csv
import os
import glob
import logging
import pandas as pd
from typing import List
from .models import Up2PayTransaction, Up2PayPlannedTransaction, KalisportPayment


class FileReader:
    """Classe pour lire les fichiers CSV de Up2Pay et Kalisport."""

    @staticmethod
    def get_files_from_path(data_dir: str, template: str) -> List[str]:
        """
        Récupère tous les fichiers correspondant au template dans le répertoire.
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            template: Template du nom de fichier à rechercher
            
        Returns:
            Liste des chemins des fichiers trouvés
            
        Raises:
            FileNotFoundError: Si aucun fichier n'est trouvé
        """
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
        
        # Tri des fichiers pour un ordre déterministe
        files.sort()
        logger.info(f"{len(files)} fichier(s) trouvé(s) avec le template '{template}'")
        for i, file in enumerate(files, 1):
            logger.info(f"  Fichier {i}: {file}")
        
        return files

    @staticmethod
    def get_file_from_path(data_dir: str, template: str) -> str:
        """
        Récupère le premier fichier correspondant au template (pour compatibilité).
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            template: Template du nom de fichier à rechercher
            
        Returns:
            Chemin du premier fichier trouvé
            
        Raises:
            FileNotFoundError: Si aucun fichier n'est trouvé
        """
        logger = logging.getLogger(__name__)
        files = FileReader.get_files_from_path(data_dir, template)
        
        selected_file = files[0]  # Prend le premier fichier trouvé
        logger.info(f"Fichier sélectionné: {selected_file}")
        
        if len(files) > 1:
            logger.warning(f"Plusieurs fichiers trouvés ({len(files)}), utilisation du premier: {selected_file}")
            logger.debug(f"Fichiers ignorés: {files[1:]}")
        
        return selected_file

    @staticmethod
    def read_up2pay_file(data_dir: str, template: str) -> List[Up2PayTransaction]:
        """
        Lit tous les fichiers Up2Pay Excel correspondant au template.
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            template: Template du nom de fichier à rechercher
            
        Returns:
            Liste d'objets Up2PayTransaction de tous les fichiers
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Début de la lecture des fichiers Up2Pay Excel avec template '{template}'")
        
        up2pay_files = FileReader.get_files_from_path(data_dir, template)
        all_up2pay_data = []
        
        for file_index, up2pay_file in enumerate(up2pay_files, 1):
            logger.info(f"Traitement du fichier {file_index}/{len(up2pay_files)}: {up2pay_file}")
            
            try:
                logger.debug(f"Ouverture du fichier Up2Pay Excel: {up2pay_file}")
                
                # Détection automatique du moteur selon l'extension
                file_extension = os.path.splitext(up2pay_file)[1].lower()
                if file_extension == '.xls':
                    df = pd.read_excel(up2pay_file, engine='xlrd')
                elif file_extension == '.xlsx':
                    df = pd.read_excel(up2pay_file, engine='openpyxl')
                else:
                    # Laisser pandas choisir automatiquement
                    df = pd.read_excel(up2pay_file)
                
                # Log des en-têtes de colonnes
                logger.debug(f"Colonnes détectées dans le fichier Up2Pay Excel: {list(df.columns)}")
                
                file_transactions = []
                row_count = 0
                for index, row in df.iterrows():
                    try:
                        # Conversion de la ligne pandas en dictionnaire
                        row_dict = row.to_dict()
                        
                        # Conversion des valeurs NaN en chaînes vides
                        row_dict = {k: str(v) if pd.notna(v) else '' for k, v in row_dict.items()}
                        
                        transaction = Up2PayTransaction.from_csv_row(row_dict)
                        file_transactions.append(transaction)
                        row_count += 1
                        
                        # Log de debug pour les premières lignes du premier fichier
                        if file_index == 1 and row_count <= 3:
                            logger.debug(f"Transaction Up2Pay #{row_count}: {transaction}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement de la ligne {row_count + 1} du fichier {up2pay_file}: {e}")
                        logger.debug(f"Données de la ligne problématique: {row_dict}")
                        raise
                
                logger.info(f"Fichier {file_index} traité: {len(file_transactions)} transactions chargées")
                all_up2pay_data.extend(file_transactions)
                
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier Up2Pay Excel '{up2pay_file}': {e}")
                raise
        
        logger.info(f"Lecture de tous les fichiers Up2Pay Excel terminée: {len(all_up2pay_data)} transactions chargées au total")
        return all_up2pay_data

    @staticmethod
    def read_up2pay_pnf_file(data_dir: str, template: str) -> List[Up2PayPlannedTransaction]:
        """
        Lit tous les fichiers Up2Pay PNF Excel correspondant au template (optionnel).
        
        Args:
            data_dir: Chemin vers le répertoire contenant les fichiers de données
            template: Template du nom de fichier à rechercher
            
        Returns:
            Liste d'objets Up2PayPlannedTransaction de tous les fichiers (vide si aucun fichier trouvé)
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Début de la lecture des fichiers Up2Pay PNF Excel avec template '{template}' (optionnel)")
        
        try:
            up2pay_files = FileReader.get_files_from_path(data_dir, template)
            all_up2pay_data = []
            
            for file_index, up2pay_file in enumerate(up2pay_files, 1):
                logger.info(f"Traitement du fichier PNF {file_index}/{len(up2pay_files)}: {up2pay_file}")
                
                logger.debug(f"Ouverture du fichier Up2Pay PNF Excel: {up2pay_file}")
                
                # Détection automatique du moteur selon l'extension
                file_extension = os.path.splitext(up2pay_file)[1].lower()
                if file_extension == '.xls':
                    df = pd.read_excel(up2pay_file, engine='xlrd')
                elif file_extension == '.xlsx':
                    df = pd.read_excel(up2pay_file, engine='openpyxl')
                else:
                    # Laisser pandas choisir automatiquement
                    df = pd.read_excel(up2pay_file)
                
                # Log des en-têtes de colonnes
                logger.debug(f"Colonnes détectées dans le fichier Up2Pay PNF Excel: {list(df.columns)}")
                
                file_transactions = []
                row_count = 0
                for index, row in df.iterrows():
                    try:
                        # Conversion de la ligne pandas en dictionnaire
                        row_dict = row.to_dict()
                        
                        # Conversion des valeurs NaN en chaînes vides
                        row_dict = {k: str(v) if pd.notna(v) else '' for k, v in row_dict.items()}
                        
                        transaction = Up2PayPlannedTransaction.from_csv_row(row_dict)
                        file_transactions.append(transaction)
                        row_count += 1
                        
                        # Log de debug pour les premières lignes du premier fichier
                        if file_index == 1 and row_count <= 3:
                            logger.debug(f"Transaction planifiée Up2Pay #{row_count}: {transaction}")
                        
                    except Exception as e:
                        logger.error(f"Erreur lors du traitement de la ligne {row_count + 1} du fichier {up2pay_file}: {e}")
                        logger.debug(f"Données de la ligne problématique: {row_dict}")
                        raise
                
                logger.info(f"Fichier PNF {file_index} traité: {len(file_transactions)} transactions planifiées chargées")
                all_up2pay_data.extend(file_transactions)
            
            logger.info(f"Lecture de tous les fichiers Up2Pay PNF Excel terminée: {len(all_up2pay_data)} transactions planifiées chargées au total")
            return all_up2pay_data
            
        except FileNotFoundError:
            logger.info(f"Aucun fichier PNF Excel trouvé dans {data_dir} (template: {template}). Continuation du processus...")
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la lecture des fichiers Up2Pay PNF Excel: {e}")
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