"""
OffersV2 models for Amazon PA-API 5.0
Provides improved reliability and data quality compared to Offers V1
"""

from .money import Money
from .availability import Availability
from .condition import Condition
from .deal_details import DealDetails
from .loyalty_points import LoyaltyPoints
from .merchant_info import MerchantInfo
from .saving_basis import SavingBasis
from .savings import Savings
from .price import Price
from .offer_listing import OfferListing
from .offersv2 import OffersV2

__all__ = [
    'Money',
    'Availability',
    'Condition',
    'DealDetails',
    'LoyaltyPoints',
    'MerchantInfo',
    'SavingBasis',
    'Savings',
    'Price',
    'OfferListing',
    'OffersV2',
]
