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
    parser.add_argument('--data-dir', "-d", type=str, default='data',
                        help='Répertoire contenant les fichiers de données (par défaut: data)')
    parser.add_argument('--output-dir', "-o", type=str, default='output',
                        help='Répertoire de sortie pour le fichier Excel (par défaut: output)')
    parser.add_argument('--section', "-s", type=str, default="",
                        help='Section concernée par la comparaison (par défaut: ""). Elle sera utilisée pour compléter le nom du fichier de résultats.')
    parser.add_argument('--debug', action='store_true',
                        help='Active le mode debug avec logs détaillés')
    
    args = parser.parse_args()
    
    # Configuration du logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("=== Démarrage de l'application de comparaison Up2Pay/Kalisport ===")
    logger.debug(f"Arguments reçus: data-dir={args.data_dir}, output-dir={args.output_dir}, section={args.section}, debug={args.debug}")

    section = args.section.upper()  # Convertir la section en majuscule
    
    # Obtenir les chemins absolus
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(script_dir)))
    data_dir = os.path.join(project_dir, args.data_dir)
    output_dir = os.path.join(project_dir, args.output_dir)

    # Définition des sous-répertoires de données
    transaction_dir = os.path.join(data_dir, "Transaction")
    pnf_dir = os.path.join(data_dir, "Pnf")
    kalisport_dir = os.path.join(data_dir, "kalisport")

    logger.debug(f"Script directory: {script_dir}")
    logger.debug(f"Project directory: {project_dir}")
    logger.debug(f"Data directory: {data_dir}")
    logger.debug(f"Transaction directory: {transaction_dir}")
    logger.debug(f"PNF directory: {pnf_dir}")
    logger.debug(f"Kalisport directory: {kalisport_dir}")
    logger.debug(f"Output directory: {output_dir}")
    
    # Vérification de l'existence des répertoires
    if not os.path.exists(data_dir):
        logger.error(f"Le répertoire de données n'existe pas: {data_dir}")
        return 1
    
    logger.debug(f"Répertoire de données vérifié: {data_dir}")


    # Création du répertoire de sortie si nécessaire
    if not os.path.exists(output_dir):
        logger.info(f"Création du répertoire de sortie: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Lire les fichiers Up2Pay
        logger.info(f"Scan des fichiers Up2Pay dans {transaction_dir}...")
        up2pay_pattern = f"{section}_*.xlsx" if section else "Export_transactions_*.xls"
        logger.debug(f"Début de la lecture des fichiers Up2Pay avec template '{up2pay_pattern}'")

        up2pay_data = FileReader.read_up2pay_file(transaction_dir, up2pay_pattern)
        logger.info(f"Données Up2Pay chargées: {len(up2pay_data)} transactions")
        logger.debug(f"Détails du chargement Up2Pay: {len(up2pay_data)} transactions trouvées")
        if args.debug and up2pay_data:
            logger.debug(f"Premier élément Up2Pay: {up2pay_data[0]}")
        
        # Lire les fichiers Up2Pay PNF (optionnel)
        logger.info(f"Scan des fichiers Up2Pay PNF (planifiés) dans {pnf_dir}...")
        up2pay_pnf_pattern = f"{section}_*.xlsx" if section else "Export_pnf_*.xls"
        logger.debug(f"Début de la lecture des fichiers Up2Pay PNF avec template '{up2pay_pnf_pattern}'")

        up2pay_pnf_data = FileReader.read_up2pay_pnf_file(pnf_dir, up2pay_pnf_pattern)
        logger.info(f"Données Up2Pay PNF chargées: {len(up2pay_pnf_data)} transactions planifiées")
        logger.debug(f"Détails du chargement Up2Pay PNF: {len(up2pay_pnf_data)} transactions planifiées trouvées")
        if args.debug and up2pay_pnf_data:
            logger.debug(f"Premier élément Up2Pay PNF: {up2pay_pnf_data[0]}")
                
        # Lire les fichiers Kalisport
        logger.info(f"Scan des fichiers Kalisport dans {kalisport_dir}...")
        kalisport_pattern = f"{section}_*.csv" if section else "paiements-*.csv"
        logger.debug(f"Début de la lecture des fichiers Kalisport avec template '{kalisport_pattern}'")

        kalisport_data = FileReader.read_kalisport_file(kalisport_dir, kalisport_pattern)
        logger.info(f"Données Kalisport chargées: {len(kalisport_data)} paiements")
        logger.debug(f"Détails du chargement Kalisport: {len(kalisport_data)} paiements trouvés")
        if args.debug and kalisport_data:
            logger.debug(f"Premier élément Kalisport: {kalisport_data[0]}")
        
        # Vérification des données chargées
        if not up2pay_data:
            logger.warning("Aucune transaction Up2Pay trouvée")
        if not kalisport_data:
            logger.warning("Aucun paiement Kalisport trouvé")
        
        # Comparer les paiements
        logger.info("Début de la comparaison des paiements...")
        logger.debug(f"Comparaison entre {len(up2pay_data)} transactions Up2Pay et {len(kalisport_data)} paiements Kalisport")
        
        comparison_results = PaymentComparator.compare_payments(up2pay_data, kalisport_data)
        logger.info(f"Comparaison terminée: {len(comparison_results)} résultats générés")
        logger.debug(f"Détails des résultats de comparaison: {len(comparison_results)} éléments")
        
        # Analyse des paiements
        logger.info("Début de l'analyse des paiements Up2Pay...")
        logger.debug("Initialisation du compteur Up2Pay")
        
        counter = Up2PayCounter()
        
        logger.debug(f"Ajout de {len(up2pay_data)} transactions Up2Pay au compteur")
        counter.add_transactions(up2pay_data)
        
        logger.debug(f"Ajout de {len(up2pay_pnf_data)} transactions planifiées Up2Pay au compteur")
        counter.add_planned_transactions(up2pay_pnf_data)
        
        reference_payment_summary = counter.get_all_summaries()
        id_payment_summary = counter.get_all_id_summaries()
        
        logger.info(f"Analyse terminée: {len(reference_payment_summary)} résumés par référence, {len(id_payment_summary)} résumés par ID")
        logger.debug(f"Résumés par référence: {len(reference_payment_summary)} éléments")
        logger.debug(f"Résumés par ID: {len(id_payment_summary)} éléments")

        # Générer le fichier Excel
        logger.info("Début de la génération du fichier Excel...")
        logger.debug(f"Génération Excel dans le répertoire: {output_dir}")
        
        output_file = ExcelGenerator.generate_excel(
            comparison_results, 
            reference_payment_summary, 
            id_payment_summary, 
            output_dir, 
            section
        )
        
        logger.info(f"Fichier Excel généré avec succès: {output_file}")
        logger.debug(f"Chemin complet du fichier généré: {os.path.abspath(output_file)}")
        
        logger.info("=== Traitement terminé avec succès ===")
        
    except Exception as e:
        error_msg = f"Erreur lors du traitement: {str(e)}"
        logger.error(error_msg)
        
        if args.debug:
            logger.error("Traceback complet:")
            logger.error(traceback.format_exc())
        else:
            logger.error("Utilisez --debug pour plus de détails")
        
        return 1
    
    return 0


if __name__ == "__main__":
    exit(app())