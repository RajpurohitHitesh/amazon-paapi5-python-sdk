"""
Price model for OffersV2
Specifies buying price of an offer
"""

from typing import Optional
from dataclasses import dataclass
from .money import Money
from .saving_basis import SavingBasis
from .savings import Savings


@dataclass
class Price:
    """
    Complete pricing information including current price, savings, and unit pricing
    
    Note: Price represents the price shown for a logged-in Amazon user 
    with an in-marketplace shipping address
    """
    money: Optional[Money] = None
    price_per_unit: Optional[Money] = None
    saving_basis: Optional[SavingBasis] = None
    savings: Optional[Savings] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['Price']:
        """Create Price instance from API response dict"""
        if not data:
            return None
        
        return cls(
            money=Money.from_dict(data.get('Money')),
            price_per_unit=Money.from_dict(data.get('PricePerUnit')),
            saving_basis=SavingBasis.from_dict(data.get('SavingBasis')),
            savings=Savings.from_dict(data.get('Savings'))
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.money is not None:
            result['Money'] = self.money.to_dict()
        if self.price_per_unit is not None:
            result['PricePerUnit'] = self.price_per_unit.to_dict()
        if self.saving_basis is not None:
            result['SavingBasis'] = self.saving_basis.to_dict()
        if self.savings is not None:
            result['Savings'] = self.savings.to_dict()
        return result
