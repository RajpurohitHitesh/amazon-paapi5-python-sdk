"""
DealDetails model for OffersV2
Specifies deal information of the offer
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class DealDetails:
    """
    Deal information including Lightning Deals and special offers
    
    Valid AccessType values:
    - ALL: Available to all customers
    - PRIME_EARLY_ACCESS: Available to Prime members first, then all customers
    - PRIME_EXCLUSIVE: Available only to Prime members
    
    Badge Examples: "Limited Time Deal", "With Prime", "Black Friday Deal", "Ends In"
    """
    access_type: Optional[str] = None
    badge: Optional[str] = None
    early_access_duration_in_milliseconds: Optional[int] = None
    end_time: Optional[str] = None
    percent_claimed: Optional[int] = None
    start_time: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['DealDetails']:
        """Create DealDetails instance from API response dict"""
        if not data:
            return None
        
        return cls(
            access_type=data.get('AccessType'),
            badge=data.get('Badge'),
            early_access_duration_in_milliseconds=int(data['EarlyAccessDurationInMilliseconds']) 
                if 'EarlyAccessDurationInMilliseconds' in data else None,
            end_time=data.get('EndTime'),
            percent_claimed=int(data['PercentClaimed']) if 'PercentClaimed' in data else None,
            start_time=data.get('StartTime')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.access_type is not None:
            result['AccessType'] = self.access_type
        if self.badge is not None:
            result['Badge'] = self.badge
        if self.early_access_duration_in_milliseconds is not None:
            result['EarlyAccessDurationInMilliseconds'] = self.early_access_duration_in_milliseconds
        if self.end_time is not None:
            result['EndTime'] = self.end_time
        if self.percent_claimed is not None:
            result['PercentClaimed'] = self.percent_claimed
        if self.start_time is not None:
            result['StartTime'] = self.start_time
        return result
