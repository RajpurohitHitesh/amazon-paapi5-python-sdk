"""
Condition model for OffersV2
Specifies the condition of the offer
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class Condition:
    """
    Product condition information
    
    Valid Value values: New, Used, Refurbished, Unknown
    Valid SubCondition values: LikeNew, Good, VeryGood, Acceptable, Refurbished, OEM, OpenBox, Unknown
    
    Note: For offers with value "New", there will not be a specified ConditionNote 
    and SubCondition will be Unknown
    """
    condition_note: Optional[str] = None
    sub_condition: Optional[str] = None
    value: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['Condition']:
        """Create Condition instance from API response dict"""
        if not data:
            return None
        
        return cls(
            condition_note=data.get('ConditionNote'),
            sub_condition=data.get('SubCondition'),
            value=data.get('Value')
        )

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        result = {}
        if self.condition_note is not None:
            result['ConditionNote'] = self.condition_note
        if self.sub_condition is not None:
            result['SubCondition'] = self.sub_condition
        if self.value is not None:
            result['Value'] = self.value
        return result
