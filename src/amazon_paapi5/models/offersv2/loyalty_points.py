"""
LoyaltyPoints model for OffersV2
Loyalty Points (Amazon Japan only)
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class LoyaltyPoints:
    """
    Loyalty points associated with an offer
    Currently only supported in the Japan marketplace
    """
    points: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['LoyaltyPoints']:
        """Create LoyaltyPoints instance from API response dict"""
        if not data:
            return None
        
        return cls(
            points=int(data['Points']) if 'Points' in data else None
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.points is not None:
            result['Points'] = self.points
        return result
