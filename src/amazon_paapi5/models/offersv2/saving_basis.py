"""
SavingBasis model for OffersV2
Reference value which is used to calculate savings against
"""

from typing import Optional
from dataclasses import dataclass
from .money import Money


@dataclass
class SavingBasis:
    """
    Reference pricing for savings calculations
    
    Valid SavingBasisType values:
    - LIST_PRICE
    - LOWEST_PRICE
    - LOWEST_PRICE_STRIKETHROUGH
    - WAS_PRICE
    """
    money: Optional[Money] = None
    saving_basis_type: Optional[str] = None
    saving_basis_type_label: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['SavingBasis']:
        """Create SavingBasis instance from API response dict"""
        if not data:
            return None
        
        return cls(
            money=Money.from_dict(data.get('Money')),
            saving_basis_type=data.get('SavingBasisType'),
            saving_basis_type_label=data.get('SavingBasisTypeLabel')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.money is not None:
            result['Money'] = self.money.to_dict()
        if self.saving_basis_type is not None:
            result['SavingBasisType'] = self.saving_basis_type
        if self.saving_basis_type_label is not None:
            result['SavingBasisTypeLabel'] = self.saving_basis_type_label
        return result
