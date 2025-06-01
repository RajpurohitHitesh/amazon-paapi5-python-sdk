from typing import List, Optional
from dataclasses import dataclass
from ..resources import validate_resources

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

@dataclass
class GetVariationsResponse:
    variations: List[Variation]

    @classmethod
    def from_dict(cls, data: dict) -> 'GetVariationsResponse':
        variations = [
            Variation(
                asin=item["ASIN"],
                dimensions=item.get("VariationSummary", {}).get("VariationDimension", []),
                title=item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue"),
            )
            for item in data.get("VariationsResult", {}).get("Items", [])
        ]
        return cls(variations=variations)