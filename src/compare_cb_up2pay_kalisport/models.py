from dataclasses import dataclass
from typing import Dict, List
from decimal import Decimal


@dataclass
class Up2PayTransaction:
    """Modèle pour une transaction Up2Pay."""
    transaction_number: str
    amount: Decimal
    reference: str
    date_time: str
    type: str
    status: str
    
    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'Up2PayTransaction':
        """Crée une transaction Up2Pay à partir d'une ligne CSV."""
        amount_str = row.get('Montant', '').strip().replace(',', '.')
        amount = Decimal(amount_str) if amount_str else Decimal('0')
        
        return cls(
            transaction_number=row.get('Num. transaction', '').strip(),
            amount=amount,
            reference=row.get('Référence commande', '').strip(),
            date_time=row.get('Date & Heure', '').strip(),
            type=row.get('Type de transaction', '').strip(),
            status=row.get('Statut de la transaction', '').strip()
        )


@dataclass
class KalisportPayment:
    """Modèle pour un paiement Kalisport."""
    transaction_number: str
    name: str
    first_name: str
    payment_method: str
    amount: Decimal
    paid: str
    status: str
    payment_date: str
    
    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'KalisportPayment':
        """Crée un paiement Kalisport à partir d'une ligne CSV."""
        amount_str = row.get('MONTANT', '').strip().strip('"').replace(',', '.')
        amount = Decimal(amount_str) if amount_str else Decimal('0')
        
        return cls(
            transaction_number=row.get('NUMERO', '').strip().strip('"'),
            name=row.get('NOM', '').strip().strip('"'),
            first_name=row.get('PRENOM', '').strip().strip('"'),
            payment_method=row.get('MODE_PAIEMENT', '').strip().strip('"'),
            amount=amount,
            paid=row.get('PAYE', '').strip().strip('"'),
            status=row.get('ETAT', '').strip().strip('"'),
            payment_date=row.get('DATE_PAIEMENT', '').strip().strip('"')
        )

@dataclass
class ComparisonPayment:
    """Modèle pour le résultat de comparaison entre Up2Pay et Kalisport."""
    transaction_number: str
    payment_method: str
    reference: str
    name: str
    first_name: str
    up2pay_type: str
    up2pay_amount: float
    kalisport_amount: float
    up2pay_status: str
    kalisport_status: str
    comparison_result: str
    date_time: str

@dataclass
class PaymentSummary:
    """Résumé des paiements par 'groupe' pour une référence donnée."""
    count: int
    total_amount: Decimal
    
    def __post_init__(self):
        if self.total_amount is None:
            self.total_amount = Decimal('0')


@dataclass
class ReferencePaymentSummary:
    """Résumé complet des paiements pour une référence donnée."""
    reference: str
    total_count: int
    total_amount: Decimal
    by_type: Dict[str, PaymentSummary]
    by_status: Dict[str, PaymentSummary]
    transactions: List[Up2PayTransaction]
    
    def __post_init__(self):
        if self.total_amount is None:
            self.total_amount = Decimal('0')
        if self.by_type is None:
            self.by_type = {}
        if self.by_status is None:
            self.by_status = {}
        if self.transactions is None:
            self.transactions = []

@dataclass
class IdPaymentSummary:
    """Résumé complet des paiements pour une référence donnée."""
    id: str
    total_count: int
    total_amount: Decimal
    by_type: Dict[str, PaymentSummary]
    by_status: Dict[str, PaymentSummary]
    transactions: List[Up2PayTransaction]
    
    def __post_init__(self):
        if self.total_amount is None:
            self.total_amount = Decimal('0')
        if self.by_type is None:
            self.by_type = {}
        if self.by_status is None:
            self.by_status = {}
        if self.transactions is None:
            self.transactions = []