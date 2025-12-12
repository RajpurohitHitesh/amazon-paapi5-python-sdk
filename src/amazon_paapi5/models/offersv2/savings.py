"""
Savings model for OffersV2
Savings of an offer
"""

from typing import Optional
from dataclasses import dataclass
from .money import Money


@dataclass
class Savings:
    """
    Savings information including amount and percentage
    This is the difference between Price Money and SavingBasis Money
    """
    money: Optional[Money] = None
    percentage: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['Savings']:
        """Create Savings instance from API response dict"""
        if not data:
            return None
        
        return cls(
            money=Money.from_dict(data.get('Money')),
            percentage=int(data['Percentage']) if 'Percentage' in data else None
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.money is not None:
            result['Money'] = self.money.to_dict()
        if self.percentage is not None:
            result['Percentage'] = self.percentage
        return result
