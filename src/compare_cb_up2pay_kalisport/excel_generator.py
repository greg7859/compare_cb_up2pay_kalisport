from typing import Dict, List
import os
import pandas as pd
from datetime import datetime
from .models import ReferencePaymentSummary, IdPaymentSummary, ComparisonPayment


class ExcelGenerator:
    """Classe pour générer un fichier Excel avec les résultats de comparaison."""

    @staticmethod
    def generate_excel(comparison_results: List[ComparisonPayment], 
                      reference_payment_summary: Dict[str, ReferencePaymentSummary], 
                      id_payment_summary: Dict[str, IdPaymentSummary], 
                      output_dir: str) -> str:
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
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer un nom de fichier avec la date et l'heure actuelles
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"comparaison_paiements_{timestamp}.xlsx")
        
        # Créer les DataFrames pour chaque onglet
        df_detail = ExcelGenerator._create_detailed_comparison_dataframe(comparison_results)
        df_reference_summary = ExcelGenerator._create_reference_summary_dataframe(reference_payment_summary)
        df_id_summary = ExcelGenerator._create_id_summary_dataframe(id_payment_summary)
        
        # Écrire les DataFrames dans un fichier Excel avec plusieurs onglets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            ExcelGenerator._write_detailed_comparison_sheet(df_detail, writer)
            ExcelGenerator._write_reference_summary_sheet(df_reference_summary, writer)
            ExcelGenerator._write_id_summary_sheet(df_id_summary, writer)
        
        return output_file

    @staticmethod
    def _create_detailed_comparison_dataframe(comparison_results: List[ComparisonPayment]) -> pd.DataFrame:
        """Crée le DataFrame pour l'onglet de comparaison détaillée."""
        df = pd.DataFrame(comparison_results)
        
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
        
        df = df[columns_order]
        
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
        return df

    @staticmethod
    def _create_reference_summary_dataframe(reference_payment_summary: Dict[str, ReferencePaymentSummary]) -> pd.DataFrame:
        """Crée le DataFrame pour l'onglet de résumé par référence."""
        summary_data = []
        
        for reference, summary in reference_payment_summary.items():
            row_data = ExcelGenerator._build_summary_row_data(
                summary, 
                'Référence Up2Pay', 
                summary.reference
            )
            summary_data.append(row_data)
        
        df_summary = pd.DataFrame(summary_data)
        
        if not df_summary.empty:
            df_summary = ExcelGenerator._reorder_summary_columns(df_summary, 'Référence Up2Pay')
        
        return df_summary

    @staticmethod
    def _create_id_summary_dataframe(id_payment_summary: Dict[str, IdPaymentSummary]) -> pd.DataFrame:
        """Crée le DataFrame pour l'onglet de résumé par ID."""
        id_summary_data = []
        
        for id_payment, summary in id_payment_summary.items():
            row_data = ExcelGenerator._build_summary_row_data(
                summary, 
                'ID Paiement', 
                summary.id
            )
            id_summary_data.append(row_data)
        
        df_id_summary = pd.DataFrame(id_summary_data)
        
        if not df_id_summary.empty:
            df_id_summary = ExcelGenerator._reorder_summary_columns(df_id_summary, 'ID Paiement')
        
        return df_id_summary

    @staticmethod
    def _build_summary_row_data(summary, identifier_key: str, identifier_value: str) -> Dict:
        """Construit les données d'une ligne pour les résumés."""
        row_data = {
            identifier_key: identifier_value,
            'Nombre total de transactions': summary.total_count,
            'Montant total': float(summary.total_amount)
        }
        
        # Ajouter les résumés par type
        type_columns = {}
        for type_name, type_summary in summary.by_type.items():
            type_columns[f'Type {type_name} (nombre)'] = type_summary.count
            type_columns[f'Type {type_name} (montant)'] = float(type_summary.total_amount)
        
        # Ajouter les résumés par statut
        status_columns = {}
        for status_name, status_summary in summary.by_status.items():
            status_columns[f'Statut {status_name} (nombre)'] = status_summary.count
            status_columns[f'Statut {status_name} (montant)'] = float(status_summary.total_amount)
        
        # Combiner toutes les données
        row_data.update(type_columns)
        row_data.update(status_columns)
        row_data['Numéros de transactions'] = ', '.join([t.transaction_number for t in summary.transactions])
        
        return row_data

    @staticmethod
    def _reorder_summary_columns(df: pd.DataFrame, identifier_column: str) -> pd.DataFrame:
        """Réorganise les colonnes des DataFrames de résumé pour un meilleur regroupement."""
        base_columns = [identifier_column, 'Nombre total de transactions', 'Montant total']
        type_columns = sorted([col for col in df.columns if 'Type' in col])
        status_columns = sorted([col for col in df.columns if 'Statut' in col])
        final_columns = ['Numéros de transactions']
        
        column_order = base_columns + type_columns + status_columns + final_columns
        return df[column_order]

    @staticmethod
    def _write_detailed_comparison_sheet(df: pd.DataFrame, writer: pd.ExcelWriter) -> None:
        """Écrit l'onglet de comparaison détaillée."""
        sheet_name = 'Comparaison détaillée'
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        worksheet = writer.sheets[sheet_name]
        ExcelGenerator._adjust_column_widths(worksheet, df)

    @staticmethod
    def _write_reference_summary_sheet(df: pd.DataFrame, writer: pd.ExcelWriter) -> None:
        """Écrit l'onglet de résumé par référence."""
        sheet_name = 'Résumé par référence'
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        worksheet = writer.sheets[sheet_name]
        ExcelGenerator._adjust_column_widths(worksheet, df, max_width=50)

    @staticmethod
    def _write_id_summary_sheet(df: pd.DataFrame, writer: pd.ExcelWriter) -> None:
        """Écrit l'onglet de résumé par ID."""
        sheet_name = 'Résumé par ID'
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        worksheet = writer.sheets[sheet_name]
        ExcelGenerator._adjust_column_widths(worksheet, df, max_width=50)

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