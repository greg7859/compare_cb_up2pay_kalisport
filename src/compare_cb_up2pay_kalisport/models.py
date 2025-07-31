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
class Up2PayPlannedTransaction:
    """Modèle pour une transaction planifiée Up2Pay."""
    subscription_number: str
    status: str
    type: str
    creation_date: str
    reference: str
    expiration_date: str  # Format AAMM
    cardholder_email: str
    amount: Decimal
    currency: str
    remaining_payments: str
    next_debit: str
    contract_number: str
    rank: str
    group: str
    brand: str
    site: str
    
    @property
    def total_planned_amount(self) -> Decimal:
        """Calcule le montant total planifié (montant unitaire × nombre de paiements restants)."""
        try:
            remaining_count = int(self.remaining_payments) if self.remaining_payments else 0
            return self.amount * remaining_count
        except (ValueError, TypeError):
            return Decimal('0')
    
    @property
    def remaining_payments_count(self) -> int:
        """Retourne le nombre de paiements restants sous forme d'entier."""
        try:
            return int(self.remaining_payments) if self.remaining_payments else 0
        except (ValueError, TypeError):
            return 0
     
    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'Up2PayPlannedTransaction':
        """Crée une transaction planifiée Up2Pay à partir d'une ligne CSV."""
        amount_str = row.get('Montant', '').strip().replace(',', '.')
        amount = Decimal(amount_str) if amount_str else Decimal('0')
        
        return cls(
            subscription_number=row.get('Numéro d\'abonnement', '').strip(),
            status=row.get('Statut', '').strip(),
            type=row.get('Type', '').strip(),
            creation_date=row.get('Date de création', '').strip(),
            reference=row.get('Référence commande', '').strip(),
            expiration_date=row.get('Date expiration (AAMM)', '').strip(),
            cardholder_email=row.get('Email porteur', '').strip(),
            amount=amount,
            currency=row.get('Devise', '').strip(),
            remaining_payments=row.get('Paiements restants', '').strip(),
            next_debit=row.get('Prochain débit', '').strip(),
            contract_number=row.get('Num. contrat', '').strip(),
            rank=row.get('Rang', '').strip(),
            group=row.get('Groupe', '').strip(),
            brand=row.get('Enseigne', '').strip(),
            site=row.get('Site', '').strip()
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