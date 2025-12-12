from typing import List, Optional
from dataclasses import dataclass, field
from ..resources import validate_resources
from ..exceptions import InvalidParameterException
from .offersv2 import OffersV2

@dataclass
class GetItemsRequest:
    item_ids: List[str]
    partner_tag: str = ""
    partner_type: str = "Associates"
    resources: List[str] = None

    def __post_init__(self):
        if self.resources is None:
            self.resources = ["ItemInfo.Title", "Offers.Listings.Price"]
        validate_resources("GetItems", self.resources)
        if len(self.item_ids) > 10:
            raise InvalidParameterException("GetItems supports up to 10 ASINs per request.")
        if not self.item_ids:
            raise InvalidParameterException("At least one item_id is required.")

    def to_dict(self) -> dict:
        return {
            "ItemIds": self.item_ids,
            "PartnerTag": self.partner_tag,
            "PartnerType": self.partner_type,
            "Resources": self.resources,
        }

@dataclass
class Item:
    asin: str
    title: Optional[str] = None
    price: Optional[float] = None
    detail_page_url: Optional[str] = None
    raw_data: dict = field(default_factory=dict, repr=False)
    offersv2: Optional[OffersV2] = None

    @classmethod
    def from_dict(cls, item_data: dict) -> 'Item':
        """Create Item instance from API response dict with full OffersV2 support"""
        return cls(
            asin=item_data.get("ASIN", ""),
            title=item_data.get("ItemInfo", {}).get("Title", {}).get("DisplayValue"),
            price=item_data.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("Amount"),
            detail_page_url=item_data.get("DetailPageURL"),
            raw_data=item_data,
            offersv2=OffersV2.from_dict(item_data.get("OffersV2"))
        )

@dataclass
class GetItemsResponse:
    items: List[Item]

    @classmethod
    def from_dict(cls, data: dict) -> 'GetItemsResponse':
        items = [
            Item.from_dict(item)
            for item in data.get("ItemsResult", {}).get("Items", [])
        ]
        return cls(items=items)