from typing import Dict, List
from decimal import Decimal
import re
from .models import Up2PayTransaction, Up2PayPlannedTransaction, PaymentSummary, ReferencePaymentSummary, IdPaymentSummary


class Up2PayCounter:
    """Classe pour compter et analyser les paiements Up2Pay par référence."""
    
    def __init__(self):
        self.transactions: List[Up2PayTransaction] = []
        self.planned_transactions: List[Up2PayPlannedTransaction] = []
        self.summaries_by_reference: Dict[str, ReferencePaymentSummary] = {}
        self.summaries_by_id: Dict[str, IdPaymentSummary] = {}
   
    def add_transaction(self, transaction: Up2PayTransaction) -> None:
        """Ajoute une transaction à l'analyse."""
        self.transactions.append(transaction)
        self._update_summary(transaction)
        self._update_id_summary(transaction)
    
    def add_planned_transaction(self, planned_transaction: Up2PayPlannedTransaction) -> None:
        """Ajoute une transaction planifiée à l'analyse."""
        self.planned_transactions.append(planned_transaction)
        self._update_summary_with_planned(planned_transaction)
        self._update_id_summary_with_planned(planned_transaction)
    
    def add_transactions(self, transactions: List[Up2PayTransaction]) -> None:
        """Ajoute plusieurs transactions à l'analyse."""
        for transaction in transactions:
            self.add_transaction(transaction)
    
    def add_planned_transactions(self, planned_transactions: List[Up2PayPlannedTransaction]) -> None:
        """Ajoute plusieurs transactions planifiées à l'analyse."""
        for planned_transaction in planned_transactions:
            self.add_planned_transaction(planned_transaction)
    
    def _extract_id_from_reference(self, reference: str) -> str:
        """Extrait l'ID de la référence (format: ID1716)."""
        match = re.search(r'ID(\d+)', reference)
        return match.group(0) if match else "ID_INCONNU"
    
    def _update_id_summary(self, transaction: Up2PayTransaction) -> None:
        """Met à jour le résumé par ID."""
        transaction_id = self._extract_id_from_reference(transaction.reference)
        
        if transaction_id not in self.summaries_by_id:
            self.summaries_by_id[transaction_id] = IdPaymentSummary(
                id=transaction_id,
                total_count=0,
                total_amount=Decimal('0'),
                by_type={},
                by_status={},
                transactions=[]
            )
        
        summary = self.summaries_by_id[transaction_id]
        transaction_status = transaction.status
        transaction_type = transaction.type

        # Mise à jour des totaux
        summary.total_count += 1
        transaction_amount_to_add = transaction.amount
        if transaction_type.lower() == 'remboursement':
            transaction_amount_to_add = -transaction.amount

        # On ajoute le montant uniquement si le statut n'est pas "Refusée"
        if transaction_status != "Refusée":
            summary.total_amount += transaction_amount_to_add
        summary.transactions.append(transaction)
        
        # Mise à jour par type   
        if transaction_type not in summary.by_type:
            summary.by_type[transaction_type] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_type[transaction_type].count += 1
        summary.by_type[transaction_type].total_amount += transaction_amount_to_add
        
        # Mise à jour par statut
        if transaction_status not in summary.by_status:
            summary.by_status[transaction_status] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_status[transaction_status].count += 1
        summary.by_status[transaction_status].total_amount += transaction_amount_to_add
    
    def _update_summary(self, transaction: Up2PayTransaction) -> None:
        """Met à jour le résumé pour la référence de la transaction."""
        reference = transaction.reference
        
        if reference not in self.summaries_by_reference:
            self.summaries_by_reference[reference] = ReferencePaymentSummary(
                reference=reference,
                total_count=0,
                total_amount=Decimal('0'),
                by_type={},
                by_status={},
                transactions=[]
            )
        
        summary = self.summaries_by_reference[reference]

        transaction_status = transaction.status
        transaction_type = transaction.type
        transaction_amount_to_add = transaction.amount
        if transaction_type.lower() == 'remboursement':
            transaction_amount_to_add = -transaction.amount

        summary.total_count += 1
        # On ajoute le montant uniquement si le statut n'est pas "Refusée"
        if transaction_status != "Refusée":
            summary.total_amount += transaction_amount_to_add
        summary.transactions.append(transaction)
        
        # Mise à jour par type

        if transaction_type not in summary.by_type:
            summary.by_type[transaction_type] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_type[transaction_type].count += 1
        summary.by_type[transaction_type].total_amount += transaction_amount_to_add
        
        # Mise à jour par statut

        if transaction_status not in summary.by_status:
            summary.by_status[transaction_status] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_status[transaction_status].count += 1
        summary.by_status[transaction_status].total_amount += transaction_amount_to_add

    def _update_id_summary_with_planned(self, planned_transaction: Up2PayPlannedTransaction) -> None:
        """Met à jour le résumé par ID avec une transaction planifiée."""
        transaction_id = self._extract_id_from_reference(planned_transaction.reference)
        
        if transaction_id not in self.summaries_by_id:
            self.summaries_by_id[transaction_id] = IdPaymentSummary(
                id=transaction_id,
                total_count=0,
                total_amount=Decimal('0'),
                by_type={},
                by_status={},
                transactions=[]
            )
        
        summary = self.summaries_by_id[transaction_id]
        
        # Calculer le montant total planifié (montant × nombre de paiements restants)
        total_planned_amount = planned_transaction.total_planned_amount
        remaining_count = planned_transaction.remaining_payments_count
        
        # Mise à jour des totaux si le statut n'est pas "Resilié"
        if planned_transaction.status.lower() != "resilié":
            summary.total_amount += total_planned_amount
        summary.total_count += remaining_count
        
        # Mise à jour par type (Abonnement)
        transaction_type = f"Abonnement - {planned_transaction.type} - {planned_transaction.status}"
        if transaction_type not in summary.by_type:
            summary.by_type[transaction_type] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_type[transaction_type].count += remaining_count
        summary.by_type[transaction_type].total_amount += total_planned_amount
        
        # Mise à jour par statut de l'abonnement
        transaction_status = f"{planned_transaction.type} - {planned_transaction.status}"
        if transaction_status not in summary.by_status:
            summary.by_status[transaction_status] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_status[transaction_status].count += remaining_count
        summary.by_status[transaction_status].total_amount += total_planned_amount
    
    def _update_summary_with_planned(self, planned_transaction: Up2PayPlannedTransaction) -> None:
        """Met à jour le résumé pour la référence de la transaction planifiée."""
        reference = planned_transaction.reference
        
        if reference not in self.summaries_by_reference:
            self.summaries_by_reference[reference] = ReferencePaymentSummary(
                reference=reference,
                total_count=0,
                total_amount=Decimal('0'),
                by_type={},
                by_status={},
                transactions=[]
            )
        
        summary = self.summaries_by_reference[reference]
        
        # Calculer le montant total planifié (montant × nombre de paiements restants)
        total_planned_amount = planned_transaction.total_planned_amount
        remaining_count = planned_transaction.remaining_payments_count
        
        # Mise à jour des totaux si le status n'est pas "Resilié"
        if planned_transaction.status.lower() != "resilié":
            summary.total_amount += total_planned_amount
        summary.total_count += remaining_count
        
        # Mise à jour par type (Abonnement)
        transaction_type = f"Abonnement - {planned_transaction.type} - {planned_transaction.status}"
        if transaction_type not in summary.by_type:
            summary.by_type[transaction_type] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_type[transaction_type].count += remaining_count
        summary.by_type[transaction_type].total_amount += total_planned_amount
        
         # Mise à jour par statut de l'abonnement
        transaction_status = f"{planned_transaction.type} - {planned_transaction.status}"
        if transaction_status not in summary.by_status:
            summary.by_status[transaction_status] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_status[transaction_status].count += remaining_count
        summary.by_status[transaction_status].total_amount += total_planned_amount

    def get_all_summaries(self) -> Dict[str, ReferencePaymentSummary]:
        """Retourne tous les résumés par référence."""
        return self.summaries_by_reference.copy()

    def get_all_id_summaries(self) -> Dict[str, IdPaymentSummary]:
        """Retourne tous les résumés par ID."""
        return self.summaries_by_id.copy()
    
    def print_id_summary_report(self) -> None:
        """Affiche un rapport de résumé des paiements par ID et statut."""
        print("=== Rapport de résumé des paiements Up2Pay par ID ===")
        print(f"Nombre total de transactions: {len(self.transactions)}")
        print(f"Nombre d'IDs uniques: {len(self.summaries_by_id)}")
        print()
        
        for transaction_id, summary in sorted(self.summaries_by_id.items()):
            print(f"ID: {transaction_id}")
            print(f"  Total: {summary.total_count} transactions, {summary.total_amount}€")
            
            if summary.by_type:
                print("  Par type:")
                for type_name, type_summary in sorted(summary.by_type.items()):
                    print(f"    {type_name}: {type_summary.count} transactions, {type_summary.total_amount}€")
            
            if summary.by_status:
                print("  Par statut:")
                for status_name, status_summary in sorted(summary.by_status.items()):
                    print(f"    {status_name}: {status_summary.count} transactions, {status_summary.total_amount}€")
            print()
    
    def print_summary_report(self) -> None:
        """Affiche un rapport de résumé des paiements."""
        print("=== Rapport de résumé des paiements Up2Pay ===")
        print(f"Nombre total de transactions: {len(self.transactions)}")
        print(f"Nombre total de transactions planifiées: {len(self.planned_transactions)}")
        print(f"Nombre de références uniques: {len(self.summaries_by_reference)}")
        print()
        
        for reference, summary in self.summaries_by_reference.items():
            print(f"Référence: {reference}")
            print(f"  Nombre de transactions: {summary.total_count}")
            print(f"  Montant total: {summary.total_amount}")
            
            if summary.by_type:
                print("  Par type:")
                for type_name, type_summary in summary.by_type.items():
                    print(f"    {type_name}: {type_summary.count} transactions, {type_summary.total_amount}€")
            
            if summary.by_status:
                print("  Par statut:")
                for status_name, status_summary in summary.by_status.items():
                    print(f"    {status_name}: {status_summary.count} transactions, {status_summary.total_amount}€")
            print()