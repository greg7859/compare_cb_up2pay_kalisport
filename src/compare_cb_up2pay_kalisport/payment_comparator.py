from typing import Dict, List, Optional


class PaymentComparator:
    """Classe pour comparer les paiements entre Up2Pay et Kalisport."""

    @staticmethod
    def compare_payments(up2pay_data: List[Dict], kalisport_data: List[Dict]) -> List[Dict]:
        """
        Compare les paiements entre Up2Pay et Kalisport.
        
        Args:
            up2pay_data: Liste des paiements Up2Pay
            kalisport_data: Liste des paiements Kalisport
            
        Returns:
            Liste des résultats de comparaison
        """
        # Créer un dictionnaire pour accéder rapidement aux paiements Kalisport par numéro de transaction
        kalisport_dict = {payment['transaction_number']: payment for payment in kalisport_data if payment['transaction_number']}
        
        comparison_results = []
        
        for up2pay_payment in up2pay_data:
            transaction_number = up2pay_payment['transaction_number']
            up2pay_status = up2pay_payment['status']
            up2pay_amount = up2pay_payment['amount']
            
            # Chercher le paiement correspondant dans Kalisport
            kalisport_payment = kalisport_dict.get(transaction_number)
            
            kalisport_status = "Non trouvé"
            kalisport_amount = ""
            kalisport_payment_method = ""
            comparison_result = "Erreur: Paiement non trouvé dans Kalisport"
            
            if kalisport_payment:
                kalisport_status = kalisport_payment['status']
                kalisport_amount = kalisport_payment['amount']
                kalisport_payment_method = kalisport_payment['payment_method']
                
                # Vérifier si le paiement est accepté dans Up2Pay et payé dans Kalisport
                if up2pay_status.lower() == "acceptée" or up2pay_status.lower() == "acceptee":
                    if kalisport_status.lower() == "payé" or kalisport_status.lower() == "paye":
                         # Comparer les montants
                        try:
                            up2pay_amount_float = float(up2pay_amount) if up2pay_amount else 0.0
                            kalisport_amount_float = float(kalisport_amount) if kalisport_amount else 0.0
                            
                            if abs(up2pay_amount_float - kalisport_amount_float) < 0.001:  # Tolérance de 0.1 centime
                                comparison_result = "OK"
                            else:
                                comparison_result = f"Erreur: Montants différents (Up2Pay: {up2pay_amount_float}, Kalisport: {kalisport_amount_float})"
                        except (ValueError, TypeError):
                            comparison_result = f"Erreur: Impossible de comparer les montants (Up2Pay: {up2pay_amount}, Kalisport: {kalisport_amount})"
                    else:
                        comparison_result = f"Erreur: Up2Pay accepté mais Kalisport {kalisport_status}"
                else:
                     comparison_result = f"Erreur: Up2Pay {up2pay_status}"
            elif up2pay_status.lower() == "acceptée" or up2pay_status.lower() == "acceptee":
                comparison_result = "Erreur: Paiement accepté dans Up2Pay mais absent dans Kalisport"
            elif up2pay_status.lower() == "refusée" or up2pay_status.lower() == "refusee":
                comparison_result = "OK"
            
            comparison_results.append({
                'transaction_number': transaction_number,
                'payment_method': kalisport_payment_method,
                'reference': up2pay_payment['reference'],
                'up2pay_type': up2pay_payment['type'],
                'up2pay_amount': up2pay_amount,
                'kalisport_amount': kalisport_amount,
                'up2pay_status': up2pay_status,
                'kalisport_status': kalisport_status,
                'comparison_result': comparison_result,
                'date_time': up2pay_payment['date_time']
            })
        
        return comparison_results