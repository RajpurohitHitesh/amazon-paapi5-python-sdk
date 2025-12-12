"""
OfferListing model for OffersV2
Specifies an individual offer listing for a product
"""

from typing import Optional
from dataclasses import dataclass
from .availability import Availability
from .condition import Condition
from .deal_details import DealDetails
from .loyalty_points import LoyaltyPoints
from .merchant_info import MerchantInfo
from .price import Price


@dataclass
class OfferListing:
    """
    Individual offer listing with complete details
    
    Valid Type values:
    - LIGHTNING_DEAL
    - SUBSCRIBE_AND_SAVE
    - None (for regular listings)
    """
    availability: Optional[Availability] = None
    condition: Optional[Condition] = None
    deal_details: Optional[DealDetails] = None
    is_buy_box_winner: Optional[bool] = None
    loyalty_points: Optional[LoyaltyPoints] = None
    merchant_info: Optional[MerchantInfo] = None
    price: Optional[Price] = None
    type: Optional[str] = None
    violates_map: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['OfferListing']:
        """Create OfferListing instance from API response dict"""
        if not data:
            return None
        
        return cls(
            availability=Availability.from_dict(data.get('Availability')),
            condition=Condition.from_dict(data.get('Condition')),
            deal_details=DealDetails.from_dict(data.get('DealDetails')),
            is_buy_box_winner=data.get('IsBuyBoxWinner'),
            loyalty_points=LoyaltyPoints.from_dict(data.get('LoyaltyPoints')),
            merchant_info=MerchantInfo.from_dict(data.get('MerchantInfo')),
            price=Price.from_dict(data.get('Price')),
            type=data.get('Type'),
            violates_map=data.get('ViolatesMAP')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.availability is not None:
            result['Availability'] = self.availability.to_dict()
        if self.condition is not None:
            result['Condition'] = self.condition.to_dict()
        if self.deal_details is not None:
            result['DealDetails'] = self.deal_details.to_dict()
        if self.is_buy_box_winner is not None:
            result['IsBuyBoxWinner'] = self.is_buy_box_winner
        if self.loyalty_points is not None:
            result['LoyaltyPoints'] = self.loyalty_points.to_dict()
        if self.merchant_info is not None:
            result['MerchantInfo'] = self.merchant_info.to_dict()
        if self.price is not None:
            result['Price'] = self.price.to_dict()
        if self.type is not None:
            result['Type'] = self.type
        if self.violates_map is not None:
            result['ViolatesMAP'] = self.violates_map
        return result

    def has_deal(self) -> bool:
        """Check if this listing has an active deal"""
        return self.deal_details is not None
    
    def is_lightning_deal(self) -> bool:
        """Check if this is a Lightning Deal"""
        return self.type == 'LIGHTNING_DEAL'
