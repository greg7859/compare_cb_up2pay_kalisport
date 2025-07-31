import os
import argparse
import logging
import traceback
from .file_reader import FileReader
from .payment_comparator import PaymentComparator
from .excel_generator import ExcelGenerator
from .up2pay_counter import Up2PayCounter


def setup_logging(debug: bool = False):
    """Configure le système de logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('debug.log')
        ]
    )


def app():
    """Point d'entrée principal de l'application."""
    parser = argparse.ArgumentParser(description='Compare les paiements entre Up2Pay et Kalisport.')
    parser.add_argument('--data-dir', type=str, default='data',
                        help='Répertoire contenant les fichiers de données (par défaut: data)')
    parser.add_argument('--output-dir', type=str, default='output',
                        help='Répertoire de sortie pour le fichier Excel (par défaut: output)')
    parser.add_argument('--debug', action='store_true',
                        help='Active le mode debug avec logs détaillés')
    
    args = parser.parse_args()
    
    # Configuration du logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    # Obtenir les chemins absolus
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    data_dir = os.path.join(project_dir, args.data_dir)
    output_dir = os.path.join(project_dir, args.output_dir)
    
    logger.debug(f"Script directory: {script_dir}")
    logger.debug(f"Project directory: {project_dir}")
    logger.debug(f"Data directory: {data_dir}")
    logger.debug(f"Output directory: {output_dir}")
    
    try:
        # Lire les fichiers
        print(f"-> Scan des fichiers Up2Pay dans {data_dir}...")
        logger.info(f"Lecture des fichiers Up2Pay dans {data_dir}")
        
        up2pay_data = FileReader.read_up2pay_file(data_dir, "Export_transactions_*.csv")
        logger.debug(f"Données Up2Pay chargées: {len(up2pay_data)} transactions")
        if args.debug and up2pay_data:
            logger.debug(f"Premier élément Up2Pay: {up2pay_data[0]}")
        
        up2pay_pnf_data = FileReader.read_up2pay_pnf_file(data_dir, "Export_pnf_*.csv")
        logger.debug(f"Données Up2Pay PNF chargées: {len(up2pay_pnf_data)} transactions planifiées")
        if args.debug and up2pay_pnf_data:
            logger.debug(f"Premier élément Up2Pay PNF: {up2pay_pnf_data[0]}")
        
        print(f"--> Nombre de paiements Up2Pay trouvés: {len(up2pay_data)}")
        print(f"--> Nombre de paiements Up2Pay pnf trouvés: {len(up2pay_pnf_data)}")
                
        # Lire les autres fichiers Kalisport
        print(f"-> Scan des fichiers Kalisport dans {data_dir}...")
        logger.info(f"Lecture des fichiers Kalisport dans {data_dir}")
        
        kalisport_data = FileReader.read_kalisport_file(data_dir, "paiements-*.csv")
        logger.debug(f"Données Kalisport chargées: {len(kalisport_data)} paiements")
        if args.debug and kalisport_data:
            logger.debug(f"Premier élément Kalisport: {kalisport_data[0]}")
        
        print(f"--> Nombre de paiements Kalisport trouvés: {len(kalisport_data)}")
        
        # Comparer les paiements
        print("-> Comparaison des paiements...")
        logger.info("Début de la comparaison des paiements")
        
        comparison_results = PaymentComparator.compare_payments(up2pay_data, kalisport_data)
        logger.debug(f"Résultats de comparaison: {len(comparison_results)} éléments")
        
        # Analyse des paiements
        print("-> Analyse des paiements Up2Pay...")
        logger.info("Début de l'analyse des paiements Up2Pay")
        
        counter = Up2PayCounter()
        
        logger.debug("Ajout des transactions Up2Pay au compteur")
        counter.add_transactions(up2pay_data)
        
        logger.debug("Ajout des transactions planifiées Up2Pay au compteur")
        counter.add_planned_transactions(up2pay_pnf_data)
        
        reference_payment_summary = counter.get_all_summaries()
        id_payment_summary = counter.get_all_id_summaries()
        
        logger.debug(f"Résumés par référence: {len(reference_payment_summary)} éléments")
        logger.debug(f"Résumés par ID: {len(id_payment_summary)} éléments")

        # Générer le fichier Excel
        print("-> Génération du fichier Excel...")
        logger.info("Début de la génération du fichier Excel")
        
        output_file = ExcelGenerator.generate_excel(
            comparison_results, 
            reference_payment_summary, 
            id_payment_summary, 
            output_dir
        )
        
        print(f"-> Fichier Excel généré avec succès: {output_file}")
        logger.info(f"Fichier Excel généré: {output_file}")
        
    except Exception as e:
        error_msg = f"Erreur: {str(e)}"
        print(error_msg)
        logger.error(error_msg)
        
        if args.debug:
            logger.error("Traceback complet:")
            logger.error(traceback.format_exc())
            print("\n=== TRACEBACK COMPLET ===")
            traceback.print_exc()
        
        return 1
    
    return 0


if __name__ == "__main__":
    exit(app())