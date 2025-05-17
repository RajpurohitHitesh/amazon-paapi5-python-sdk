from typing import List, Optional
from dataclasses import dataclass
from ..resources import validate_resources

@dataclass
class SearchItemsRequest:
    keywords: str
    search_index: str
    item_count: int = 10
    partner_tag: str = ""
    partner_type: str = "Associates"
    resources: List[str] = None

    def __post_init__(self):
        if self.resources is None:
            self.resources = ["ItemInfo.Title", "Offers.Listings.Price"]
        validate_resources("SearchItems", self.resources)

    def to_dict(self) -> dict:
        return {
            "Keywords": self.keywords,
            "SearchIndex": self.search_index,
            "ItemCount": self.item_count,
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

@dataclass
class SearchItemsResponse:
    items: List[Item]

    @classmethod
    def from_dict(cls, data: dict) -> 'SearchItemsResponse':
        items = [
            Item(
                asin=item["ASIN"],
                title=item.get("ItemInfo", {}).get("Title", {}).get("DisplayValue"),
                price=item.get("Offers", {}).get("Listings", [{}])[0].get("Price", {}).get("Amount"),
                detail_page_url=item.get("DetailPageURL"),
            )
            for item in data.get("SearchResult", {}).get("Items", [])
        ]
        return cls(items=items)