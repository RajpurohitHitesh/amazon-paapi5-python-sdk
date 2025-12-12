from typing import List, Optional
from dataclasses import dataclass, field
from ..resources import validate_resources
from .offersv2 import OffersV2

@dataclass
class GetVariationsRequest:
    asin: str
    variation_page: int = 1
    partner_tag: str = ""
    partner_type: str = "Associates"
    resources: List[str] = None

    def __post_init__(self):
        if self.resources is None:
            self.resources = ["VariationSummary.VariationDimension", "ItemInfo.Title"]
        validate_resources("GetVariations", self.resources)

    def to_dict(self) -> dict:
        return {
            "ASIN": self.asin,
            "VariationPage": self.variation_page,
            "PartnerTag": self.partner_tag,
            "PartnerType": self.partner_type,
            "Resources": self.resources,
        }

@dataclass
class Variation:
    asin: str
    dimensions: Optional[List[str]] = None
    title: Optional[str] = None
    raw_data: dict = field(default_factory=dict, repr=False)
    offersv2: Optional[OffersV2] = None

    @classmethod
    def from_dict(cls, item_data: dict) -> 'Variation':
        """Create Variation instance from API response dict with full OffersV2 support"""
        return cls(
            asin=item_data.get("ASIN", ""),
            dimensions=item_data.get("VariationSummary", {}).get("VariationDimension", []),
            title=item_data.get("ItemInfo", {}).get("Title", {}).get("DisplayValue"),
            raw_data=item_data,
            offersv2=OffersV2.from_dict(item_data.get("OffersV2"))
        )

@dataclass
class GetVariationsResponse:
    variations: List[Variation]

    @classmethod
    def from_dict(cls, data: dict) -> 'GetVariationsResponse':
        variations = [
            Variation.from_dict(item)
            for item in data.get("VariationsResult", {}).get("Items", [])
        ]
        return cls(variations=variations)