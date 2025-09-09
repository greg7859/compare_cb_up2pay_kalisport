
from typing import List
from .models import KalisportPayment, Up2PayTransaction, ComparisonPayment

class PaymentComparator:
    """Classe pour comparer les paiements entre Up2Pay et Kalisport."""

    @staticmethod
    def compare_payments(up2pay_data: List[Up2PayTransaction], kalisport_data: List[KalisportPayment]) -> List[ComparisonPayment]:
        """
        Compare les paiements entre Up2Pay et Kalisport.
        
        Args:
            up2pay_data: Liste des paiements Up2Pay
            kalisport_data: Liste des paiements Kalisport
            
        Returns:
            Liste des résultats de comparaison
        """
        # Créer un dictionnaire pour accéder rapidement aux paiements Kalisport par numéro de transaction
        kalisport_dict = {}
        for payment in kalisport_data:
            if payment.transaction_number:
                # Supprimer les zéros en préfixe du numéro de transaction
                normalized_number = payment.transaction_number.lstrip('0')
                if normalized_number:  # S'assurer qu'il reste quelque chose après suppression des zéros
                    kalisport_dict[normalized_number] = payment

        # Créer un dictionnaire pour accéder rapidement aux paiements Up2Pay par numéro de transaction
        up2pay_dict = {}
        for payment in up2pay_data:
            if payment.transaction_number:
                normalized_number = payment.transaction_number.lstrip('0')
                if normalized_number:
                    up2pay_dict[normalized_number] = payment
        
        comparison_results = []
        processed_kalisport_numbers = set()
        
        # Traiter d'abord tous les paiements Up2Pay
        for up2pay_payment in up2pay_data:
            transaction_number = up2pay_payment.transaction_number
            # Normaliser aussi le numéro de transaction Up2Pay pour la recherche
            normalized_transaction_number = transaction_number.lstrip('0') if transaction_number else ''
            up2pay_status = up2pay_payment.status
            up2pay_amount = up2pay_payment.amount
            
            # Chercher le paiement correspondant dans Kalisport avec le numéro normalisé
            kalisport_payment = kalisport_dict.get(normalized_transaction_number)
            
            kalisport_status = "Non trouvé"
            kalisport_amount = 0
            kalisport_payment_method = ""
            kalisport_name = ""
            kalisport_first_name = ""
            comparison_result = "Erreur: Paiement non trouvé dans Kalisport"
            
            if kalisport_payment:
                # Marquer ce paiement Kalisport comme traité
                processed_kalisport_numbers.add(normalized_transaction_number)
                
                kalisport_status = kalisport_payment.status
                kalisport_amount = kalisport_payment.amount
                kalisport_name = kalisport_payment.name
                kalisport_first_name = kalisport_payment.first_name
                kalisport_payment_method = kalisport_payment.payment_method
                
                # Vérifier si le paiement est accepté dans Up2Pay et payé dans Kalisport
                if up2pay_status.lower() == "acceptée" or up2pay_status.lower() == "acceptee":
                    if kalisport_status.lower() == "payé" or kalisport_status.lower() == "paye":
                        # Comparer les montants en tenant compte du type de transaction
                        if up2pay_payment.type.lower() == "remboursement":
                            # Pour les remboursements, Up2Pay est positif et Kalisport négatif
                            # On compare en valeur absolue
                            if abs(abs(up2pay_amount) - abs(kalisport_amount)) < 0.001:
                                comparison_result = "OK"
                            else:
                                comparison_result = f"Erreur: Montants différents (Up2Pay: {up2pay_amount}, Kalisport: {kalisport_amount})"
                        else:
                            # Pour les autres types de transaction, comparaison normale
                            if abs(up2pay_amount - kalisport_amount) < 0.001:  # Tolérance de 0.1 centime
                                comparison_result = "OK"
                            else:
                                comparison_result = f"Erreur: Montants différents (Up2Pay: {up2pay_amount}, Kalisport: {kalisport_amount})"
                    else:
                        comparison_result = f"Erreur: Up2Pay accepté mais Kalisport {kalisport_status}"
                else:
                     comparison_result = f"Erreur: Up2Pay {up2pay_status}"
            elif up2pay_status.lower() == "acceptée" or up2pay_status.lower() == "acceptee":
                comparison_result = "Erreur: Paiement accepté dans Up2Pay mais absent dans Kalisport"
            elif up2pay_status.lower() == "refusée" or up2pay_status.lower() == "refusee":
                comparison_result = "OK"

            comparison_results.append(ComparisonPayment(
                transaction_number=transaction_number,
                payment_method=kalisport_payment_method,
                reference=up2pay_payment.reference,
                name=kalisport_name,
                first_name=kalisport_first_name,
                up2pay_type=up2pay_payment.type,
                up2pay_amount=up2pay_amount,
                kalisport_amount=kalisport_amount,
                up2pay_status=up2pay_status,
                kalisport_status=kalisport_status,
                comparison_result=comparison_result,
                date_time=up2pay_payment.date_time
            ))

        # Traiter les paiements Kalisport qui n'ont pas de correspondance dans Up2Pay
        for kalisport_payment in kalisport_data:
            if kalisport_payment.transaction_number:
                normalized_number = kalisport_payment.transaction_number.lstrip('0')
                if normalized_number and normalized_number not in processed_kalisport_numbers:
                    # Ce paiement Kalisport n'a pas de correspondance dans Up2Pay
                    comparison_results.append(ComparisonPayment(
                        transaction_number=kalisport_payment.transaction_number,
                        payment_method=kalisport_payment.payment_method,
                        reference="",  # Pas de référence Up2Pay
                        name=kalisport_payment.name,
                        first_name=kalisport_payment.first_name,
                        up2pay_type="",  # Pas de type Up2Pay
                        up2pay_amount=0,  # Pas de montant Up2Pay
                        kalisport_amount=kalisport_payment.amount,
                        up2pay_status="Non trouvé",
                        kalisport_status=kalisport_payment.status,
                        comparison_result="Erreur: Paiement Kalisport sans correspondance Up2Pay",
                        date_time=kalisport_payment.payment_date if hasattr(kalisport_payment, 'payment_date') else ""
                    ))
        
        return comparison_results
