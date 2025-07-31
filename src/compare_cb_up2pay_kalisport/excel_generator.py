from typing import Dict, List
import os
import pandas as pd
from datetime import datetime
from .models import ReferencePaymentSummary, IdPaymentSummary


class ExcelGenerator:
    """Classe pour générer un fichier Excel avec les résultats de comparaison."""

    @staticmethod
    def generate_excel(comparison_results: List[Dict], reference_payment_summary: Dict[str, ReferencePaymentSummary], id_payment_summary: Dict[str, IdPaymentSummary], output_dir: str) -> str:
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
        # Créer un DataFrame pandas à partir des résultats
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
        df.rename(columns={
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
        }, inplace=True)
        
        # Créer le DataFrame pour le résumé par référence
        summary_data = []
        for reference, summary in reference_payment_summary.items():
            # Préparer les données de base
            row_data = {
                'Référence Up2Pay': summary.reference,
                'Nombre total de transactions': summary.total_count
            }
            
            # Ajouter les résumés par type (regroupés)
            type_columns = {}
            for type_name, type_summary in summary.by_type.items():
                type_columns[f'Type {type_name} (nombre)'] = type_summary.count
                type_columns[f'Type {type_name} (montant)'] = float(type_summary.total_amount)
            
            # Ajouter les résumés par statut (regroupés)
            status_columns = {}
            for status_name, status_summary in summary.by_status.items():
                status_columns[f'Statut {status_name} (nombre)'] = status_summary.count
                status_columns[f'Statut {status_name} (montant)'] = float(status_summary.total_amount)
            
            # Combiner dans l'ordre souhaité : données de base, puis types, puis statuts
            row_data.update(type_columns)
            row_data.update(status_columns)
            
            # Ajouter des informations sur les transactions à la fin
            row_data['Numéros de transactions'] = ', '.join([t.transaction_number for t in summary.transactions])
            
            summary_data.append(row_data)
        
        df_summary = pd.DataFrame(summary_data)
        
        # Réorganiser les colonnes pour un meilleur regroupement
        if not df_summary.empty:
            # Colonnes de base
            base_columns = ['Référence Up2Pay', 'Nombre total de transactions']
            
            # Colonnes par type (triées)
            type_columns = sorted([col for col in df_summary.columns if 'Type' in col])
            
            # Colonnes par statut (triées)
            status_columns = sorted([col for col in df_summary.columns if 'Statut' in col])
            
            # Colonnes finales
            final_columns = ['Numéros de transactions']
            
            # Réorganiser le DataFrame
            column_order = base_columns + type_columns + status_columns + final_columns
            df_summary = df_summary[column_order]
        
        # Créer le DataFrame pour le résumé par ID
        id_summary_data = []
        for id_payment, summary in id_payment_summary.items():
            # Préparer les données de base
            row_data = {
                'ID Paiement': summary.id,
                'Nombre total de transactions': summary.total_count
            }
            
            # Ajouter les résumés par type (regroupés)
            type_columns = {}
            for type_name, type_summary in summary.by_type.items():
                type_columns[f'Type {type_name} (nombre)'] = type_summary.count
                type_columns[f'Type {type_name} (montant)'] = float(type_summary.total_amount)
            
            # Ajouter les résumés par statut (regroupés)
            status_columns = {}
            for status_name, status_summary in summary.by_status.items():
                status_columns[f'Statut {status_name} (nombre)'] = status_summary.count
                status_columns[f'Statut {status_name} (montant)'] = float(status_summary.total_amount)
            
            # Combiner dans l'ordre souhaité : données de base, puis types, puis statuts
            row_data.update(type_columns)
            row_data.update(status_columns)
            
            # Ajouter des informations sur les transactions à la fin
            row_data['Numéros de transactions'] = ', '.join([t.transaction_number for t in summary.transactions])
            
            id_summary_data.append(row_data)
        
        df_id_summary = pd.DataFrame(id_summary_data)
        
        # Réorganiser les colonnes pour un meilleur regroupement
        if not df_id_summary.empty:
            # Colonnes de base
            base_columns = ['ID Paiement', 'Nombre total de transactions']
            
            # Colonnes par type (triées)
            type_columns = sorted([col for col in df_id_summary.columns if 'Type' in col])
            
            # Colonnes par statut (triées)
            status_columns = sorted([col for col in df_id_summary.columns if 'Statut' in col])
            
            # Colonnes finales
            final_columns = ['Numéros de transactions']
            
            # Réorganiser le DataFrame
            column_order = base_columns + type_columns + status_columns + final_columns
            df_id_summary = df_id_summary[column_order]
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer un nom de fichier avec la date et l'heure actuelles
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"comparaison_paiements_{timestamp}.xlsx")
        
        # Écrire les DataFrames dans un fichier Excel avec plusieurs onglets
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Onglet principal avec tous les détails
            df.to_excel(writer, index=False, sheet_name='Comparaison détaillée')
            
            # Onglet résumé par référence
            df_summary.to_excel(writer, index=False, sheet_name='Résumé par référence')
            
            # Onglet résumé par ID
            df_id_summary.to_excel(writer, index=False, sheet_name='Résumé par ID')
            
            # Ajuster automatiquement la largeur des colonnes pour l'onglet principal
            worksheet_detail = writer.sheets['Comparaison détaillée']
            for i, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                ) + 2
                worksheet_detail.column_dimensions[chr(65 + i)].width = max_length
            
            # Ajuster automatiquement la largeur des colonnes pour l'onglet résumé par référence
            worksheet_summary = writer.sheets['Résumé par référence']
            for i, col in enumerate(df_summary.columns):
                max_length = max(
                    df_summary[col].astype(str).map(len).max() if len(df_summary) > 0 else 0,
                    len(str(col))
                ) + 2
                # Limiter la largeur maximale pour éviter des colonnes trop larges
                max_length = min(max_length, 50)
                worksheet_summary.column_dimensions[chr(65 + i)].width = max_length
            
            # Ajuster automatiquement la largeur des colonnes pour l'onglet résumé par ID
            worksheet_id_summary = writer.sheets['Résumé par ID']
            for i, col in enumerate(df_id_summary.columns):
                max_length = max(
                    df_id_summary[col].astype(str).map(len).max() if len(df_id_summary) > 0 else 0,
                    len(str(col))
                ) + 2
                # Limiter la largeur maximale pour éviter des colonnes trop larges
                max_length = min(max_length, 50)
                worksheet_id_summary.column_dimensions[chr(65 + i)].width = max_length
        
        return output_file