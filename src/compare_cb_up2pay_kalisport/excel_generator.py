import os
from typing import Dict, List
import pandas as pd
from datetime import datetime


class ExcelGenerator:
    """Classe pour générer un fichier Excel avec les résultats de comparaison."""

    @staticmethod
    def generate_excel(comparison_results: List[Dict], output_dir: str) -> str:
        """
        Génère un fichier Excel avec les résultats de comparaison.
        
        Args:
            comparison_results: Liste des résultats de comparaison
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
            'up2pay_type', 
            'amount',
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
            'up2pay_type': 'Type Up2Pay',
            'amount': 'Montant',
            'date_time': 'Date et heure',
            'up2pay_status': 'Statut Up2Pay',
            'kalisport_status': 'État Kalisport',
            'comparison_result': 'Résultat de la comparaison'
        }, inplace=True)
        
        # Créer le répertoire de sortie s'il n'existe pas
        os.makedirs(output_dir, exist_ok=True)
        
        # Générer un nom de fichier avec la date et l'heure actuelles
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"comparaison_paiements_{timestamp}.xlsx")
        
        # Écrire le DataFrame dans un fichier Excel avec ajustement automatique des colonnes
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Comparaison')
            
            # Ajuster automatiquement la largeur des colonnes
            worksheet = writer.sheets['Comparaison']
            for i, col in enumerate(df.columns):
                # Trouver la longueur maximale dans la colonne
                max_length = max(
                    df[col].astype(str).map(len).max(),  # Longueur maximale des données
                    len(str(col))  # Longueur de l'en-tête
                ) + 2  # Ajouter un peu d'espace supplémentaire
                
                # Définir la largeur de la colonne
                worksheet.column_dimensions[chr(65 + i)].width = max_length
        
        return output_file