"""
Availability model for OffersV2
Specifies availability information about an offer
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Availability:
    """
    Availability information including stock status and order quantity limits
    
    Valid Type values:
    - AVAILABLE_DATE: Item available on a future date
    - IN_STOCK: Item is in stock
    - IN_STOCK_SCARCE: Item in stock but limited quantity
    - LEADTIME: Item available after lead time
    - OUT_OF_STOCK: Currently out of stock
    - PREORDER: Available for pre-order
    - UNAVAILABLE: Not available
    - UNKNOWN: Unknown availability
    """
    max_order_quantity: Optional[int] = None
    message: Optional[str] = None
    min_order_quantity: Optional[int] = None
    type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['Availability']:
        """Create Availability instance from API response dict"""
        if not data:
            return None
        
        return cls(
            max_order_quantity=int(data['MaxOrderQuantity']) if 'MaxOrderQuantity' in data else None,
            message=data.get('Message'),
            min_order_quantity=int(data['MinOrderQuantity']) if 'MinOrderQuantity' in data else None,
            type=data.get('Type')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.max_order_quantity is not None:
            result['MaxOrderQuantity'] = self.max_order_quantity
        if self.message is not None:
            result['Message'] = self.message
        if self.min_order_quantity is not None:
            result['MinOrderQuantity'] = self.min_order_quantity
        if self.type is not None:
            result['Type'] = self.type
        return result
