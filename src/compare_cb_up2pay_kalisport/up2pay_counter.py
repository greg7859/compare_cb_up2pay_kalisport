from typing import Dict, List
from decimal import Decimal
import re
from .models import Up2PayTransaction, PaymentSummary, ReferencePaymentSummary, IdPaymentSummary


class Up2PayCounter:
    """Classe pour compter et analyser les paiements Up2Pay par référence."""
    
    def __init__(self):
        self.transactions: List[Up2PayTransaction] = []
        self.summaries_by_reference: Dict[str, ReferencePaymentSummary] = {}
        self.summaries_by_id: Dict[str, IdPaymentSummary] = {}
    
    def add_transaction(self, transaction: Up2PayTransaction) -> None:
        """Ajoute une transaction à l'analyse."""
        self.transactions.append(transaction)
        self._update_summary(transaction)
        self._update_id_summary(transaction)
    
    def add_transactions(self, transactions: List[Up2PayTransaction]) -> None:
        """Ajoute plusieurs transactions à l'analyse."""
        for transaction in transactions:
            self.add_transaction(transaction)
    
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
        
        # Mise à jour des totaux
        summary.total_count += 1
        summary.total_amount += transaction.amount
        summary.transactions.append(transaction)
        
        # Mise à jour par type
        transaction_type = transaction.type
        if transaction_type not in summary.by_type:
            summary.by_type[transaction_type] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_type[transaction_type].count += 1
        summary.by_type[transaction_type].total_amount += transaction.amount
        
        # Mise à jour par statut
        transaction_status = transaction.status
        if transaction_status not in summary.by_status:
            summary.by_status[transaction_status] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_status[transaction_status].count += 1
        summary.by_status[transaction_status].total_amount += transaction.amount
    
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
        
        # Mise à jour des totaux
        summary.total_count += 1
        summary.total_amount += transaction.amount
        summary.transactions.append(transaction)
        
        # Mise à jour par type
        transaction_type = transaction.type
        if transaction_type not in summary.by_type:
            summary.by_type[transaction_type] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_type[transaction_type].count += 1
        summary.by_type[transaction_type].total_amount += transaction.amount
        
        # Mise à jour par statut
        transaction_status = transaction.status
        if transaction_status not in summary.by_status:
            summary.by_status[transaction_status] = PaymentSummary(
                count=0,
                total_amount=Decimal('0')
            )
        summary.by_status[transaction_status].count += 1
        summary.by_status[transaction_status].total_amount += transaction.amount
    
    def get_summary_by_id(self, transaction_id: str) -> IdPaymentSummary:
        """Retourne le résumé pour un ID donné."""
        return self.summaries_by_id.get(transaction_id)
    
    def get_all_id_summaries(self) -> Dict[str, IdPaymentSummary]:
        """Retourne tous les résumés par ID."""
        return self.summaries_by_id.copy()
    
    def get_ids_by_status(self, status: str) -> List[str]:
        """Retourne les IDs qui ont des transactions avec un statut donné."""
        return [
            transaction_id for transaction_id, summary in self.summaries_by_id.items()
            if status in summary.by_status
        ]
    
    def get_ids_by_type(self, transaction_type: str) -> List[str]:
        """Retourne les IDs qui ont des transactions d'un type donné."""
        return [
            transaction_id for transaction_id, summary in self.summaries_by_id.items()
            if transaction_type in summary.by_type
        ]
    
    def get_total_amount_by_id_and_status(self, transaction_id: str, status: str) -> Decimal:
        """Retourne le montant total pour un ID et un statut donnés."""
        summary = self.get_summary_by_id(transaction_id)
        if summary and status in summary.by_status:
            return summary.by_status[status].total_amount
        return Decimal('0')
    
    def get_count_by_id_and_status(self, transaction_id: str, status: str) -> int:
        """Retourne le nombre de transactions pour un ID et un statut donnés."""
        summary = self.get_summary_by_id(transaction_id)
        if summary and status in summary.by_status:
            return summary.by_status[status].count
        return 0
    
    def get_total_amount_by_id_and_type(self, transaction_id: str, transaction_type: str) -> Decimal:
        """Retourne le montant total pour un ID et un type donnés."""
        summary = self.get_summary_by_id(transaction_id)
        if summary and transaction_type in summary.by_type:
            return summary.by_type[transaction_type].total_amount
        return Decimal('0')
    
    def get_count_by_id_and_type(self, transaction_id: str, transaction_type: str) -> int:
        """Retourne le nombre de transactions pour un ID et un type donnés."""
        summary = self.get_summary_by_id(transaction_id)
        if summary and transaction_type in summary.by_type:
            return summary.by_type[transaction_type].count
        return 0
    
    def get_ids_with_multiple_transactions(self) -> List[str]:
        """Retourne les IDs qui ont plusieurs transactions."""
        return [
            transaction_id for transaction_id, summary in self.summaries_by_id.items()
            if summary.total_count > 1
        ]
    
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
    
    def get_summary_by_reference(self, reference: str) -> ReferencePaymentSummary:
        """Retourne le résumé pour une référence donnée."""
        return self.summaries_by_reference.get(reference)
    
    def get_all_summaries(self) -> Dict[str, ReferencePaymentSummary]:
        """Retourne tous les résumés par référence."""
        return self.summaries_by_reference.copy()
    
    def get_references_with_multiple_transactions(self) -> List[str]:
        """Retourne les références qui ont plusieurs transactions."""
        return [
            ref for ref, summary in self.summaries_by_reference.items()
            if summary.total_count > 1
        ]
    
    def get_references_by_type(self, transaction_type: str) -> List[str]:
        """Retourne les références qui ont des transactions d'un type donné."""
        return [
            ref for ref, summary in self.summaries_by_reference.items()
            if transaction_type in summary.by_type
        ]
    
    def get_references_by_status(self, status: str) -> List[str]:
        """Retourne les références qui ont des transactions avec un statut donné."""
        return [
            ref for ref, summary in self.summaries_by_reference.items()
            if status in summary.by_status
        ]
    
    def get_total_amount_by_type(self, reference: str, transaction_type: str) -> Decimal:
        """Retourne le montant total pour une référence et un type donnés."""
        summary = self.get_summary_by_reference(reference)
        if summary and transaction_type in summary.by_type:
            return summary.by_type[transaction_type].total_amount
        return Decimal('0')
    
    def get_total_amount_by_status(self, reference: str, status: str) -> Decimal:
        """Retourne le montant total pour une référence et un statut donnés."""
        summary = self.get_summary_by_reference(reference)
        if summary and status in summary.by_status:
            return summary.by_status[status].total_amount
        return Decimal('0')
    
    def print_summary_report(self) -> None:
        """Affiche un rapport de résumé des paiements."""
        print("=== Rapport de résumé des paiements Up2Pay ===")
        print(f"Nombre total de transactions: {len(self.transactions)}")
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