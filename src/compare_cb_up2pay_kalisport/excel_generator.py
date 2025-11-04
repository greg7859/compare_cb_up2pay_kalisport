from typing import Dict, List
import os
import pandas as pd
from datetime import datetime
import logging
from .models import ReferencePaymentSummary, IdPaymentSummary, ComparisonPayment


class ExcelGenerator:
    """Classe pour générer un fichier Excel avec les résultats de comparaison."""

    @staticmethod
    def generate_excel(comparison_results: List[ComparisonPayment], 
                      reference_payment_summary: Dict[str, ReferencePaymentSummary], 
                      id_payment_summary: Dict[str, IdPaymentSummary], 
                      output_dir: str,
                      section: str) -> str:
        """
        Génère un fichier Excel avec les résultats de comparaison.
        
        Args:
            comparison_results: Liste des résultats de comparaison
            reference_payment_summary: Dictionnaire des résumés par référence
            id_payment_summary: Dictionnaire des résumés par ID
            output_dir: Répertoire de sortie pour le fichier Excel
            
        Returns:
            Chemin vers le fichier Excel généré
        """
        logger = logging.getLogger(__name__)
        logger.info("Début de la génération du fichier Excel")
        logger.debug(f"Paramètres: {len(comparison_results)} résultats de comparaison, "
                    f"{len(reference_payment_summary)} résumés par référence, "
                    f"{len(id_payment_summary)} résumés par ID")
        
        # Créer le répertoire de sortie s'il n'existe pas
        logger.debug(f"Création du répertoire de sortie: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer un nom de fichier avec la date et l'heure actuelles
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"comparaison_paiements_{section}_{timestamp}.xlsx")
        logger.info(f"Fichier Excel à générer: {output_file}")
        
        # Créer les DataFrames pour chaque onglet
        logger.info("Création des DataFrames pour les différents onglets")
        
        logger.debug("Création du DataFrame de comparaison détaillée")
        df_detail = ExcelGenerator._create_detailed_comparison_dataframe(comparison_results)
        logger.debug(f"DataFrame détaillé créé: {len(df_detail)} lignes, {len(df_detail.columns)} colonnes")
        
        logger.debug("Création du DataFrame de résumé par référence")
        df_reference_summary = ExcelGenerator._create_reference_summary_dataframe(reference_payment_summary)
        logger.debug(f"DataFrame résumé par référence créé: {len(df_reference_summary)} lignes, {len(df_reference_summary.columns)} colonnes")
        
        logger.debug("Création du DataFrame de résumé par ID")
        df_id_summary = ExcelGenerator._create_id_summary_dataframe(id_payment_summary)
        logger.debug(f"DataFrame résumé par ID créé: {len(df_id_summary)} lignes, {len(df_id_summary.columns)} colonnes")
        
        # Écrire les DataFrames dans un fichier Excel avec plusieurs onglets
        logger.info("Écriture des données dans le fichier Excel")
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                logger.debug("Écriture de l'onglet de comparaison détaillée")
                ExcelGenerator._write_detailed_comparison_sheet(df_detail, writer)
                
                logger.debug("Écriture de l'onglet de résumé par référence")
                ExcelGenerator._write_reference_summary_sheet(df_reference_summary, writer)
                
                logger.debug("Écriture de l'onglet de résumé par ID")
                ExcelGenerator._write_id_summary_sheet(df_id_summary, writer)
            
            logger.info(f"Fichier Excel généré avec succès: {output_file}")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture du fichier Excel: {str(e)}")
            raise
        
        return output_file

    @staticmethod
    def _create_detailed_comparison_dataframe(comparison_results: List[ComparisonPayment]) -> pd.DataFrame:
        """Crée le DataFrame pour l'onglet de comparaison détaillée."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Création du DataFrame détaillé à partir de {len(comparison_results)} résultats")
        
        if not comparison_results:
            logger.warning("Aucun résultat de comparaison fourni")
            return pd.DataFrame()
        
        df = pd.DataFrame(comparison_results)
        logger.debug(f"DataFrame initial créé: {len(df)} lignes, colonnes: {list(df.columns)}")
        
        # Réorganiser les colonnes dans l'ordre souhaité
        columns_order = [
            'transaction_number', 
            'reference', 
            'name', 
            'first_name', 
            'payment_method',
            'up2pay_type',
            'up2pay_amount',
            'kalisport_amount',
            'date_time',
            'up2pay_status', 
            'kalisport_status', 
            'comparison_result'
        ]
        
        # Vérifier que toutes les colonnes existent
        missing_columns = [col for col in columns_order if col not in df.columns]
        if missing_columns:
            logger.warning(f"Colonnes manquantes dans le DataFrame: {missing_columns}")
        
        available_columns = [col for col in columns_order if col in df.columns]
        df = df[available_columns]
        logger.debug(f"Colonnes réorganisées: {available_columns}")
        
        # Renommer les colonnes pour une meilleure lisibilité
        column_mapping = {
            'transaction_number': 'Numéro de transaction',
            'reference': 'Référence commande',
            'name': 'Nom', 
            'first_name': 'Prénom', 
            'payment_method': 'Méthode de paiement Kalisport',
            'up2pay_type': 'Type Up2Pay',
            'up2pay_amount': 'Montant Up2Pay',
            'kalisport_amount': 'Montant Kalisport',
            'date_time': 'Date et heure',
            'up2pay_status': 'Statut Up2Pay',
            'kalisport_status': 'État Kalisport',
            'comparison_result': 'Résultat de la comparaison'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        logger.debug(f"Colonnes renommées: {list(df.columns)}")
        
        return df

    @staticmethod
    def _create_reference_summary_dataframe(reference_payment_summary: Dict[str, ReferencePaymentSummary]) -> pd.DataFrame:
        """Crée le DataFrame pour l'onglet de résumé par référence."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Création du DataFrame de résumé par référence à partir de {len(reference_payment_summary)} références")
        
        if not reference_payment_summary:
            logger.warning("Aucun résumé par référence fourni")
            return pd.DataFrame()
        
        summary_data = []
        
        for reference, summary in reference_payment_summary.items():
            logger.debug(f"Traitement de la référence: {reference} ({summary.total_count} transactions)")
            row_data = ExcelGenerator._build_summary_row_data(
                summary, 
                'Référence Up2Pay', 
                summary.reference
            )
            summary_data.append(row_data)
        
        df_summary = pd.DataFrame(summary_data)
        logger.debug(f"DataFrame de résumé par référence créé: {len(df_summary)} lignes")
        
        if not df_summary.empty:
            logger.debug("Réorganisation des colonnes du résumé par référence")
            df_summary = ExcelGenerator._reorder_summary_columns(df_summary, 'Référence Up2Pay')
            logger.debug(f"Colonnes finales: {list(df_summary.columns)}")
        
        return df_summary

    @staticmethod
    def _create_id_summary_dataframe(id_payment_summary: Dict[str, IdPaymentSummary]) -> pd.DataFrame:
        """Crée le DataFrame pour l'onglet de résumé par ID."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Création du DataFrame de résumé par ID à partir de {len(id_payment_summary)} IDs")
        
        if not id_payment_summary:
            logger.warning("Aucun résumé par ID fourni")
            return pd.DataFrame()
        
        id_summary_data = []
        
        for id_payment, summary in id_payment_summary.items():
            logger.debug(f"Traitement de l'ID: {id_payment} ({summary.total_count} transactions)")
            row_data = ExcelGenerator._build_summary_row_data(
                summary, 
                'ID Paiement', 
                summary.id
            )
            id_summary_data.append(row_data)
        
        df_id_summary = pd.DataFrame(id_summary_data)
        logger.debug(f"DataFrame de résumé par ID créé: {len(df_id_summary)} lignes")
        
        if not df_id_summary.empty:
            logger.debug("Réorganisation des colonnes du résumé par ID")
            df_id_summary = ExcelGenerator._reorder_summary_columns(df_id_summary, 'ID Paiement')
            logger.debug(f"Colonnes finales: {list(df_id_summary.columns)}")
        
        return df_id_summary

    @staticmethod
    def _build_summary_row_data(summary, identifier_key: str, identifier_value: str) -> Dict:
        """Construit les données d'une ligne pour les résumés."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Construction des données de résumé pour {identifier_key}: {identifier_value}")
        
        row_data = {
            identifier_key: identifier_value,
            'Nombre total de transactions': summary.total_count,
            'Montant total': float(summary.total_amount)
        }
        
        # Ajouter les résumés par type
        type_columns = {}
        logger.debug(f"Ajout des résumés par type: {list(summary.by_type.keys())}")
        for type_name, type_summary in summary.by_type.items():
            type_columns[f'Type {type_name} (nombre)'] = type_summary.count
            type_columns[f'Type {type_name} (montant)'] = float(type_summary.total_amount)
        
        # Ajouter les résumés par statut
        status_columns = {}
        logger.debug(f"Ajout des résumés par statut: {list(summary.by_status.keys())}")
        for status_name, status_summary in summary.by_status.items():
            status_columns[f'Statut {status_name} (nombre)'] = status_summary.count
            status_columns[f'Statut {status_name} (montant)'] = float(status_summary.total_amount)
        
        # Combiner toutes les données
        row_data.update(type_columns)
        row_data.update(status_columns)
        row_data['Numéros de transactions'] = ', '.join([t.transaction_number for t in summary.transactions])
        
        logger.debug(f"Données de ligne construites avec {len(row_data)} colonnes")
        return row_data

    @staticmethod
    def _reorder_summary_columns(df: pd.DataFrame, identifier_column: str) -> pd.DataFrame:
        """Réorganise les colonnes des DataFrames de résumé pour un meilleur regroupement."""
        logger = logging.getLogger(__name__)
        logger.debug(f"Réorganisation des colonnes pour {identifier_column}")
        
        base_columns = [identifier_column, 'Nombre total de transactions', 'Montant total']
        type_columns = sorted([col for col in df.columns if 'Type' in col])
        status_columns = sorted([col for col in df.columns if 'Statut' in col])
        final_columns = ['Numéros de transactions']
        
        logger.debug(f"Colonnes de base: {base_columns}")
        logger.debug(f"Colonnes de type: {type_columns}")
        logger.debug(f"Colonnes de statut: {status_columns}")
        logger.debug(f"Colonnes finales: {final_columns}")
        
        column_order = base_columns + type_columns + status_columns + final_columns
        
        # Vérifier que toutes les colonnes existent
        missing_columns = [col for col in column_order if col not in df.columns]
        if missing_columns:
            logger.warning(f"Colonnes manquantes lors de la réorganisation: {missing_columns}")
            column_order = [col for col in column_order if col in df.columns]
        
        logger.debug(f"Ordre final des colonnes: {column_order}")
        return df[column_order]

    @staticmethod
    def _write_detailed_comparison_sheet(df: pd.DataFrame, writer: pd.ExcelWriter) -> None:
        """Écrit l'onglet de comparaison détaillée."""
        logger = logging.getLogger(__name__)
        sheet_name = 'Comparaison détaillée'
        logger.debug(f"Écriture de l'onglet '{sheet_name}' avec {len(df)} lignes")
        
        try:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            worksheet = writer.sheets[sheet_name]
            logger.debug(f"Ajustement des largeurs de colonnes pour l'onglet '{sheet_name}'")
            ExcelGenerator._adjust_column_widths(worksheet, df)
            
            logger.debug(f"Onglet '{sheet_name}' écrit avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture de l'onglet '{sheet_name}': {str(e)}")
            raise

    @staticmethod
    def _write_reference_summary_sheet(df: pd.DataFrame, writer: pd.ExcelWriter) -> None:
        """Écrit l'onglet de résumé par référence."""
        logger = logging.getLogger(__name__)
        sheet_name = 'Résumé par référence'
        logger.debug(f"Écriture de l'onglet '{sheet_name}' avec {len(df)} lignes")
        
        try:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            worksheet = writer.sheets[sheet_name]
            logger.debug(f"Ajustement des largeurs de colonnes pour l'onglet '{sheet_name}'")
            ExcelGenerator._adjust_column_widths(worksheet, df, max_width=50)
            
            logger.debug(f"Onglet '{sheet_name}' écrit avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture de l'onglet '{sheet_name}': {str(e)}")
            raise

    @staticmethod
    def _write_id_summary_sheet(df: pd.DataFrame, writer: pd.ExcelWriter) -> None:
        """Écrit l'onglet de résumé par ID."""
        logger = logging.getLogger(__name__)
        sheet_name = 'Résumé par ID'
        logger.debug(f"Écriture de l'onglet '{sheet_name}' avec {len(df)} lignes")
        
        try:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            worksheet = writer.sheets[sheet_name]
            logger.debug(f"Ajustement des largeurs de colonnes pour l'onglet '{sheet_name}'")
            ExcelGenerator._adjust_column_widths(worksheet, df, max_width=50)
            
            logger.debug(f"Onglet '{sheet_name}' écrit avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'écriture de l'onglet '{sheet_name}': {str(e)}")
            raise

    @staticmethod
    def _adjust_column_widths(worksheet, df: pd.DataFrame, max_width: int = None) -> None:
        """Ajuste automatiquement la largeur des colonnes."""
        for i, col in enumerate(df.columns):
            if len(df) > 0:
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
            else:
                max_length = len(str(col)) + 2
            
            if max_width:
                max_length = min(max_length, max_width)
            
            # Convertir l'index de colonne en lettre Excel
            col_letter = chr(65 + i) if i < 26 else chr(64 + i // 26) + chr(65 + i % 26)
            worksheet.column_dimensions[col_letter].width = max_length