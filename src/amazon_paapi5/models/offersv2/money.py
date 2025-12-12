"""
Money model for OffersV2
Common struct used for representing money
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Money:
    """
    Money representation with amount, currency and display format
    """
    amount: Optional[float] = None
    currency: Optional[str] = None
    display_amount: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['Money']:
        """Create Money instance from API response dict"""
        if not data:
            return None
        
        return cls(
            amount=float(data['Amount']) if 'Amount' in data else None,
            currency=data.get('Currency'),
            display_amount=data.get('DisplayAmount')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.amount is not None:
            result['Amount'] = self.amount
        if self.currency is not None:
            result['Currency'] = self.currency
        if self.display_amount is not None:
            result['DisplayAmount'] = self.display_amount
        return result
