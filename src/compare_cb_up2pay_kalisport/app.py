import os
import argparse
from .file_reader import FileReader
from .payment_comparator import PaymentComparator
from .excel_generator import ExcelGenerator
from .up2pay_counter import Up2PayCounter


def app():
    """Point d'entrée principal de l'application."""
    parser = argparse.ArgumentParser(description='Compare les paiements entre Up2Pay et Kalisport.')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Répertoire contenant les fichiers de données (par défaut: data)')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Répertoire de sortie pour le fichier Excel (par défaut: output)')
    
    args = parser.parse_args()
    
    # Obtenir les chemins absolus
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    data_dir = os.path.join(project_dir, args.data_dir)
    output_dir = os.path.join(project_dir, args.output_dir)
    
    try:
        # Lire les fichiers
        print(f"-> Scan des fichiers Up2Pay dans {data_dir}...")
        up2pay_data = FileReader.read_up2pay_file(data_dir, "Export_transactions_*.csv")
        print(f"--> Nombre de paiements Up2Pay trouvés: {len(up2pay_data)}")
                
        # Lire les autres fichiers Kalisport
        print(f"-> Scan des fichiers Kalisport dans {data_dir}...")
        kalisport_data = FileReader.read_kalisport_file(data_dir, "paiements-*.csv")
        print(f"--> Nombre de paiements Kalisport trouvés: {len(kalisport_data)}")
        
        # Comparer les paiements
        print("-> Comparaison des paiements...")
        comparison_results = PaymentComparator.compare_payments(up2pay_data, kalisport_data)
        
        # Analyse des paiements
        counter = Up2PayCounter()
        counter.add_transactions(up2pay_data)
        reference_payment_summary = counter.get_all_summaries()
        id_payment_summary = counter.get_all_id_summaries()

        # Affichage du rapport
        #counter.print_summary_report()

        # Générer le fichier Excel
        print("-> Génération du fichier Excel...")
        output_file = ExcelGenerator.generate_excel(comparison_results, reference_payment_summary, id_payment_summary, output_dir)
        
        print(f"-> Fichier Excel généré avec succès: {output_file}")
        
    except Exception as e:
        print(f"Erreur: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(app())