# Amazon PA-API 5.0 OffersV2 Implementation

Complete Python implementation of Amazon Product Advertising API 5.0 OffersV2, providing improved reliability and enhanced features compared to the deprecated Offers V1 API.

## Overview

The `OffersV2` resource contains various resources related to offer listings for an item. Amazon recommends using OffersV2 over Offers where possible, as OffersV2 will completely replace the existing Offers API. All new Item Offer features will be added to OffersV2 only.

## Features

### Core Models

The implementation includes the following models in the `amazon_paapi5.models.offersv2` package:

- **OffersV2**: Main container for offer listings
- **OfferListing**: Individual offer listing with all details
- **Price**: Buying price with savings and unit pricing
- **Money**: Common money representation (amount, currency, display)
- **Availability**: Stock status and order quantity limits
- **Condition**: Product condition information
- **DealDetails**: Lightning deals and special offer information
- **MerchantInfo**: Seller/merchant details
- **SavingBasis**: Reference pricing for savings calculations
- **Savings**: Savings amount and percentage
- **LoyaltyPoints**: Loyalty points (Japan marketplace only)

### Key Features

1. **BuyBox Winner Detection**: Easily identify the featured offer
2. **Deal Filtering**: Get only listings with active deals
3. **Rich Price Information**: Access to prices, savings, and unit pricing
4. **Deal Badges**: Get display-ready badge text for deals
5. **Prime Early Access**: Full support for Prime-exclusive deals
6. **Type-Safe**: Strongly typed Python dataclasses with proper null handling

## Installation

The OffersV2 models are included in the `amazon-paapi5-python-sdk` package. No additional installation is required.

## Usage

### Basic Usage

```python
from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_items import GetItemsRequest

# Configure client
config = Config(
    access_key='YOUR_ACCESS_KEY',
    secret_key='YOUR_SECRET_KEY',
    partner_tag='YOUR_PARTNER_TAG',
    marketplace='US'
)

client = Client(config)

# Request with OffersV2 resources
request = GetItemsRequest(
    item_ids=['B00MNV8E0C'],
    resources=[
        'OffersV2.Listings.Price.Money',
        'OffersV2.Listings.Availability.Type',
        'OffersV2.Listings.Condition.Value',
        'OffersV2.Listings.MerchantInfo.Name',
        'OffersV2.Listings.IsBuyBoxWinner',
        # Add more resources as needed
    ]
)

response = client.get_items(request)
item = response.items[0]

# Access OffersV2 data
offersv2 = item.offersv2
```

### Get BuyBox Winner

```python
offersv2 = item.offersv2
buy_box_winner = offersv2.get_buy_box_winner()

if buy_box_winner:
    price = buy_box_winner.price
    print(f"Price: {price.money.display_amount}")
    print(f"Merchant: {buy_box_winner.merchant_info.name}")
```

### Get All Listings

```python
offersv2 = item.offersv2
listings = offersv2.listings

for listing in listings:
    price = listing.price
    availability = listing.availability
    
    print(f"Price: {price.money.display_amount}")
    print(f"Status: {availability.type}")
    
    if listing.is_buy_box_winner:
        print("*** BuyBox Winner ***")
```

### Check for Deals

```python
offersv2 = item.offersv2
deal_listings = offersv2.get_deal_listings()

for listing in deal_listings:
    deal = listing.deal_details
    
    print(f"Deal Badge: {deal.badge}")
    print(f"Access Type: {deal.access_type}")
    
    if deal.end_time:
        print(f"Ends: {deal.end_time}")
    
    if deal.percent_claimed:
        print(f"Claimed: {deal.percent_claimed}%")
```

### Get Price with Savings

```python
listing = offersv2.get_buy_box_winner()
price = listing.price

# Current price
current_price = price.money
print(f"Current: {current_price.display_amount}")

# Savings
if price.savings:
    savings = price.savings
    print(f"Save: {savings.money.display_amount}", end="")
    if savings.percentage:
        print(f" ({savings.percentage}%)")

# Original price
if price.saving_basis:
    saving_basis = price.saving_basis
    print(f"{saving_basis.saving_basis_type_label}: {saving_basis.money.display_amount}")

# Price per unit
if price.price_per_unit:
    print(f"Unit: {price.price_per_unit.display_amount}")
```

### Check Availability

```python
listing = offersv2.get_buy_box_winner()
availability = listing.availability

print(f"Status: {availability.type}")
print(f"Message: {availability.message}")
print(f"Min Order: {availability.min_order_quantity}")
print(f"Max Order: {availability.max_order_quantity}")
```

## Available Resources

When making requests, you can specify which OffersV2 resources to include:

### Listings Resources

- `OffersV2.Listings.Availability.MaxOrderQuantity`
- `OffersV2.Listings.Availability.Message`
- `OffersV2.Listings.Availability.MinOrderQuantity`
- `OffersV2.Listings.Availability.Type`

### Condition Resources

- `OffersV2.Listings.Condition.ConditionNote`
- `OffersV2.Listings.Condition.SubCondition`
- `OffersV2.Listings.Condition.Value`

### Deal Resources

- `OffersV2.Listings.DealDetails.AccessType`
- `OffersV2.Listings.DealDetails.Badge`
- `OffersV2.Listings.DealDetails.EarlyAccessDurationInMilliseconds`
- `OffersV2.Listings.DealDetails.EndTime`
- `OffersV2.Listings.DealDetails.PercentClaimed`
- `OffersV2.Listings.DealDetails.StartTime`

### Other Resources

- `OffersV2.Listings.IsBuyBoxWinner`
- `OffersV2.Listings.LoyaltyPoints.Points`
- `OffersV2.Listings.MerchantInfo.Id`
- `OffersV2.Listings.MerchantInfo.Name`
- `OffersV2.Listings.Type`
- `OffersV2.Listings.ViolatesMAP`

### Price Resources

- `OffersV2.Listings.Price.Money`
- `OffersV2.Listings.Price.PricePerUnit`
- `OffersV2.Listings.Price.SavingBasis.Money`
- `OffersV2.Listings.Price.SavingBasis.SavingBasisType`
- `OffersV2.Listings.Price.SavingBasis.SavingBasisTypeLabel`
- `OffersV2.Listings.Price.Savings.Money`
- `OffersV2.Listings.Price.Savings.Percentage`

## Supported Operations

OffersV2 is available in the following operations:

- **GetItems**: Get offers for specific ASINs
- **SearchItems**: Get offers in search results
- **GetVariations**: Get offers for product variations

## Important Notes

### Availability Types

The `Availability.type` field can have the following values:

- `AVAILABLE_DATE`: Item available on a future date
- `IN_STOCK`: Item is in stock
- `IN_STOCK_SCARCE`: Item in stock but limited quantity
- `LEADTIME`: Item available after lead time
- `OUT_OF_STOCK`: Currently out of stock
- `PREORDER`: Available for pre-order
- `UNAVAILABLE`: Not available
- `UNKNOWN`: Unknown availability

### Deal Access Types

The `DealDetails.access_type` field indicates who can claim the deal:

- `ALL`: Available to all customers
- `PRIME_EARLY_ACCESS`: Available to Prime members first, then all customers
- `PRIME_EXCLUSIVE`: Available only to Prime members

### Condition Values

Product condition can be:

- `New`: New product
- `Used`: Used product
- `Refurbished`: Refurbished product
- `Unknown`: Unknown condition

### SubCondition Values

For used items:

- `LikeNew`: Like new condition
- `VeryGood`: Very good condition
- `Good`: Good condition
- `Acceptable`: Acceptable condition
- `Refurbished`: Refurbished
- `OEM`: OEM product
- `OpenBox`: Open box item
- `Unknown`: Unknown sub-condition

### Offer Types

The `Type` field can be:

- `LIGHTNING_DEAL`: Lightning deal offer
- `SUBSCRIBE_AND_SAVE`: Subscribe and Save offer
- `None`: Regular listing

### Minimum Advertised Price (MAP)

Some manufacturers have a minimum advertised price (MAP). When `violates_map` is `True`, the price is lower than MAP and customers need to add the item to their cart to see the price.

## Benefits Over Offers V1

1. **Better Reliability**: More stable and consistent data
2. **More Features**: Deal information, enhanced pricing, merchant IDs
3. **Type Safety**: Strongly typed dataclasses instead of raw dictionaries
4. **Better Documentation**: Clear field meanings and valid values
5. **Future-Proof**: All new features will be added to OffersV2 only

## Migration from Offers V1

If you're currently using Offers V1, here's a quick migration guide:

### Old Way (Offers V1)

```python
# V1 - Raw dictionary access
price = item.raw_data.get('Offers', {}).get('Listings', [{}])[0].get('Price', {})
amount = price.get('Amount')
```

### New Way (OffersV2)

```python
# V2 - Typed objects
offersv2 = item.offersv2
buy_box = offersv2.get_buy_box_winner()
amount = buy_box.price.money.amount
```

## API Documentation

For the official Amazon PA-API 5.0 OffersV2 documentation, visit:
https://webservices.amazon.com/paapi5/documentation/offersv2.html

## Changelog

### Version 1.2.4 (November 2025)
- Added OffersV2 support for GetVariations

### Version 1.2.3 (November 2025)
- Added OffersV2 support for SearchItems

### Version 1.2.2 (February 2025)
- Added `DealDetails.badge` field
- Initial OffersV2 Python SDK release
- Complete model implementation with all resources

### Version Updates (February 2025)
- Added `Availability.message` field
- Expanded `Availability.type` values
- Added `MerchantInfo.id` field
- Added Prime Early Access support in `DealDetails`

## Examples

Check the `examples/offersv2_example.py` file for a comprehensive example demonstrating all OffersV2 features.

## Support

For issues or questions about this implementation, please open an issue on GitHub.

## License

This implementation follows the same license as the main amazon-paapi5-python-sdk package.
