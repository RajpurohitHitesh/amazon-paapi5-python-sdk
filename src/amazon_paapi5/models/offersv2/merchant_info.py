"""
MerchantInfo model for OffersV2
Specifies merchant information of an offer
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class MerchantInfo:
    """
    Merchant/seller information including ID and name
    """
    id: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['MerchantInfo']:
        """Create MerchantInfo instance from API response dict"""
        if not data:
            return None
        
        return cls(
            id=data.get('Id'),
            name=data.get('Name')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.id is not None:
            result['Id'] = self.id
        if self.name is not None:
            result['Name'] = self.name
        return result
