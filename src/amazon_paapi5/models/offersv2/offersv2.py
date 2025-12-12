"""
OffersV2 model
Main container for offer listings
"""

from typing import List, Optional
from dataclasses import dataclass, field
from .offer_listing import OfferListing


@dataclass
class OffersV2:
    """
    Main OffersV2 container with various resources related to offer listings
    
    Provides improved reliability and data quality compared to Offers V1.
    All new Item Offer features will be added to OffersV2 only.
    """
    listings: List[OfferListing] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> Optional['OffersV2']:
        """Create OffersV2 instance from API response dict"""
        if not data:
            return None
        
        listings = []
        if 'Listings' in data and isinstance(data['Listings'], list):
            for listing_data in data['Listings']:
                listing = OfferListing.from_dict(listing_data)
                if listing:
                    listings.append(listing)
        
        return cls(listings=listings)

    def get_buy_box_winner(self) -> Optional[OfferListing]:
        """
        Get the BuyBox winner listing (if exists)
        This is the best offer recommended by Amazon
        """
        for listing in self.listings:
            if listing.is_buy_box_winner:
                return listing
        return None

    def get_deal_listings(self) -> List[OfferListing]:
        """
        Get all listings that have active deals
        """
        return [listing for listing in self.listings if listing.has_deal()]

    def get_lightning_deals(self) -> List[OfferListing]:
        """
        Get all Lightning Deal listings
        """
        return [listing for listing in self.listings if listing.is_lightning_deal()]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'Listings': [listing.to_dict() for listing in self.listings]
        }
