# Migration Guide: Offers V1 → OffersV2

## Why Migrate?

| Feature | Offers V1 (Deprecated) | OffersV2 (Current) |
|---------|----------------------|-------------------|
| **Status** | ⚠️ Being Deprecated | ✅ Active & Recommended |
| **Reliability** | Lower | ✅ Higher |
| **Data Quality** | Basic | ✅ Enhanced |
| **Deal Information** | ❌ Limited | ✅ Full Support |
| **Prime Deals** | ❌ Basic | ✅ Prime Exclusive Support |
| **Merchant Details** | ❌ Name only | ✅ ID + Name |
| **Price Details** | ❌ Basic | ✅ Enhanced with Savings |
| **Availability** | ❌ Basic | ✅ Detailed with Message |
| **Future Features** | ❌ No new features | ✅ All new features |

## Quick Comparison

### OLD WAY (Offers V1) - ⚠️ DEPRECATED

```python
from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_items import GetItemsRequest

config = Config(
    access_key='YOUR_ACCESS_KEY',
    secret_key='YOUR_SECRET_KEY',
    partner_tag='YOUR_PARTNER_TAG',
    marketplace='US'
)

client = Client(config)

# OLD - Using Offers V1
request = GetItemsRequest(
    item_ids=['B00MNV8E0C'],
    resources=[
        'Offers.Listings.Condition',
        'Offers.Listings.Price',
        'Offers.Listings.DeliveryInfo.IsPrimeEligible',
        'Offers.Listings.MerchantInfo'
    ]
)

response = client.get_items(request)
item = response.items[0]

# Accessing old Offers (raw dictionary)
offers = item.raw_data.get('Offers', {})
price = offers.get('Listings', [{}])[0].get('Price', {}).get('Amount')
```

### NEW WAY (OffersV2) - ✅ RECOMMENDED

```python
from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_items import GetItemsRequest

config = Config(
    access_key='YOUR_ACCESS_KEY',
    secret_key='YOUR_SECRET_KEY',
    partner_tag='YOUR_PARTNER_TAG',
    marketplace='US'
)

client = Client(config)

# NEW - Using OffersV2
request = GetItemsRequest(
    item_ids=['B00MNV8E0C'],
    resources=[
        'OffersV2.Listings.Condition',
        'OffersV2.Listings.Price',
        'OffersV2.Listings.Availability',
        'OffersV2.Listings.MerchantInfo',
        'OffersV2.Listings.DealDetails',
        'OffersV2.Listings.IsBuyBoxWinner'
    ]
)

response = client.get_items(request)
item = response.items[0]

# Accessing new OffersV2 (strongly typed objects)
offersv2 = item.offersv2
buy_box_winner = offersv2.get_buy_box_winner()
price = buy_box_winner.price.money.display_amount
```

## Step-by-Step Migration

### Step 1: Update Resource Names

Replace all `Offers.` with `OffersV2.` in your Resources list:

| Old (V1) | New (V2) |
|----------|----------|
| `Offers.Listings.Condition` | `OffersV2.Listings.Condition` |
| `Offers.Listings.Price` | `OffersV2.Listings.Price` |
| `Offers.Listings.MerchantInfo` | `OffersV2.Listings.MerchantInfo` |
| `Offers.Listings.IsBuyBoxWinner` | `OffersV2.Listings.IsBuyBoxWinner` |

### Step 2: Update Code to Use Typed Objects

**Before (V1 - Dictionary Access):**
```python
offers = item.raw_data.get('Offers', {})
price = offers.get('Listings', [{}])[0].get('Price', {}).get('Amount')
merchant = offers.get('Listings', [{}])[0].get('MerchantInfo', {}).get('Name')
condition = offers.get('Listings', [{}])[0].get('Condition', {}).get('Value')
```

**After (V2 - Typed Objects):**
```python
offersv2 = item.offersv2
listing = offersv2.get_buy_box_winner()
price = listing.price.money.amount
merchant = listing.merchant_info.name
condition = listing.condition.value
```

### Step 3: Update DeliveryInfo (NOT Available in V2)

⚠️ **Important:** DeliveryInfo fields are NOT available in OffersV2. If you need:
- `IsPrimeEligible`
- `IsFreeShippingEligible`
- `IsAmazonFulfilled`

You must continue using Offers V1 for these fields, or use both APIs together.

**Workaround - Use Both APIs:**
```python
resources = [
    # OffersV2 for pricing and deals
    'OffersV2.Listings.Price',
    'OffersV2.Listings.DealDetails',
    # Offers V1 for delivery info
    'Offers.Listings.DeliveryInfo.IsPrimeEligible'
]
```

### Step 4: Use New Features

Take advantage of OffersV2 exclusive features:

#### Deal Information

```python
offersv2 = item.offersv2
deal_listings = offersv2.get_deal_listings()

for listing in deal_listings:
    deal = listing.deal_details
    print(f"Deal Badge: {deal.badge}")
    print(f"Access Type: {deal.access_type}")
    print(f"Ends: {deal.end_time}")
```

#### Enhanced Savings

```python
listing = offersv2.get_buy_box_winner()
price = listing.price

# Current price
print(f"Price: {price.money.display_amount}")

# Savings with percentage
if price.savings:
    print(f"Save: {price.savings.money.display_amount} ({price.savings.percentage}%)")

# Original price
if price.saving_basis:
    print(f"{price.saving_basis.saving_basis_type_label}: {price.saving_basis.money.display_amount}")
```

#### Merchant ID

```python
merchant = listing.merchant_info
print(f"Merchant: {merchant.name}")
print(f"ID: {merchant.id}")  # NEW in V2!
```

#### Detailed Availability

```python
availability = listing.availability
print(f"Type: {availability.type}")
print(f"Message: {availability.message}")  # NEW in V2!
print(f"Min: {availability.min_order_quantity}")
print(f"Max: {availability.max_order_quantity}")
```

## Complete Resource List Comparison

### Offers V1 Resources (Deprecated)
```python
resources = [
    'Offers.Listings.Availability.MaxOrderQuantity',
    'Offers.Listings.Availability.Message',
    'Offers.Listings.Availability.MinOrderQuantity',
    'Offers.Listings.Availability.Type',
    'Offers.Listings.Condition.Value',
    'Offers.Listings.Condition.ConditionNote',
    'Offers.Listings.Condition.SubCondition',
    'Offers.Listings.DeliveryInfo.IsAmazonFulfilled',      # Not in V2
    'Offers.Listings.DeliveryInfo.IsFreeShippingEligible', # Not in V2
    'Offers.Listings.DeliveryInfo.IsPrimeEligible',        # Not in V2
    'Offers.Listings.IsBuyBoxWinner',
    'Offers.Listings.LoyaltyPoints.Points',
    'Offers.Listings.MerchantInfo.Name',
    'Offers.Listings.Price',
    'Offers.Summaries.HighestPrice',
    'Offers.Summaries.LowestPrice',
    'Offers.Summaries.OfferCount'
]
```

### OffersV2 Resources (Current)
```python
resources = [
    # Availability
    'OffersV2.Listings.Availability.MaxOrderQuantity',
    'OffersV2.Listings.Availability.Message',
    'OffersV2.Listings.Availability.MinOrderQuantity',
    'OffersV2.Listings.Availability.Type',
    
    # Condition
    'OffersV2.Listings.Condition.ConditionNote',
    'OffersV2.Listings.Condition.SubCondition',
    'OffersV2.Listings.Condition.Value',
    
    # Deal Details (NEW!)
    'OffersV2.Listings.DealDetails.AccessType',
    'OffersV2.Listings.DealDetails.Badge',
    'OffersV2.Listings.DealDetails.EarlyAccessDurationInMilliseconds',
    'OffersV2.Listings.DealDetails.EndTime',
    'OffersV2.Listings.DealDetails.PercentClaimed',
    'OffersV2.Listings.DealDetails.StartTime',
    
    # Other
    'OffersV2.Listings.IsBuyBoxWinner',
    'OffersV2.Listings.LoyaltyPoints.Points',
    
    # Merchant Info (Enhanced!)
    'OffersV2.Listings.MerchantInfo.Id',   # NEW!
    'OffersV2.Listings.MerchantInfo.Name',
    
    # Price (Enhanced!)
    'OffersV2.Listings.Price.Money',
    'OffersV2.Listings.Price.PricePerUnit',
    'OffersV2.Listings.Price.SavingBasis.Money',
    'OffersV2.Listings.Price.SavingBasis.SavingBasisType',
    'OffersV2.Listings.Price.SavingBasis.SavingBasisTypeLabel',
    'OffersV2.Listings.Price.Savings.Money',
    'OffersV2.Listings.Price.Savings.Percentage',
    
    # Type and MAP
    'OffersV2.Listings.Type',
    'OffersV2.Listings.ViolatesMAP'
]
```

## Common Migration Patterns

### Pattern 1: Get Best Price

**Before (V1):**
```python
offers = item.raw_data.get('Offers', {})
best_price = float('inf')
for listing in offers.get('Listings', []):
    price = listing.get('Price', {}).get('Amount', float('inf'))
    if price < best_price:
        best_price = price
```

**After (V2):**
```python
offersv2 = item.offersv2
buy_box_winner = offersv2.get_buy_box_winner()
best_price = buy_box_winner.price.money.amount if buy_box_winner else None
```

### Pattern 2: Check Prime Eligibility

**Before (V1):**
```python
offers = item.raw_data.get('Offers', {})
is_prime = offers.get('Listings', [{}])[0].get('DeliveryInfo', {}).get('IsPrimeEligible', False)
```

**After (V2):**
```python
# Option 1: Check for Prime Exclusive Deal
offersv2 = item.offersv2
buy_box_winner = offersv2.get_buy_box_winner()
deal = buy_box_winner.deal_details if buy_box_winner else None
is_prime_exclusive = deal and deal.access_type == 'PRIME_EXCLUSIVE'

# Option 2: Continue using Offers V1 for DeliveryInfo (until V2 supports it)
offers = item.raw_data.get('Offers', {})
is_prime = offers.get('Listings', [{}])[0].get('DeliveryInfo', {}).get('IsPrimeEligible', False)
```

### Pattern 3: Get All Available Prices

**Before (V1):**
```python
offers = item.raw_data.get('Offers', {})
prices = []
for listing in offers.get('Listings', []):
    price = listing.get('Price', {}).get('DisplayAmount', 'N/A')
    prices.append(price)
```

**After (V2):**
```python
offersv2 = item.offersv2
prices = []
for listing in offersv2.listings:
    money = listing.price.money if listing.price else None
    if money:
        prices.append(money.display_amount)
```

### Pattern 4: Find Lightning Deals

**V1 - Not Available**

**V2 - Built-in Support:**
```python
offersv2 = item.offersv2
lightning_deals = offersv2.get_lightning_deals()

for listing in lightning_deals:
    deal = listing.deal_details
    print(f"Lightning Deal: {deal.badge}")
    print(f"Ends: {deal.end_time}")
```

## Testing Your Migration

Create a test to ensure both V1 and V2 return similar data:

```python
from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_items import GetItemsRequest

config = Config(...)
client = Client(config)

# Test with both
asin = 'B00MNV8E0C'

# V1 Request
request_v1 = GetItemsRequest(
    item_ids=[asin],
    resources=['Offers.Listings.Price', 'Offers.Listings.Condition']
)

# V2 Request
request_v2 = GetItemsRequest(
    item_ids=[asin],
    resources=['OffersV2.Listings.Price', 'OffersV2.Listings.Condition']
)

response_v1 = client.get_items(request_v1)
response_v2 = client.get_items(request_v2)

item_v1 = response_v1.items[0]
item_v2 = response_v2.items[0]

# Compare
offers_v1 = item_v1.raw_data.get('Offers', {})
offersv2 = item_v2.offersv2

v1_price = offers_v1.get('Listings', [{}])[0].get('Price', {}).get('DisplayAmount', 'N/A')
v2_price = offersv2.get_buy_box_winner().price.money.display_amount if offersv2.get_buy_box_winner() else 'N/A'

print(f"V1 Price: {v1_price}")
print(f"V2 Price: {v2_price}")
```

## Checklist

- [ ] Updated all `Offers.` resources to `OffersV2.`
- [ ] Replaced dictionary access with typed object methods
- [ ] Updated code to use `item.offersv2` instead of `item.raw_data['Offers']`
- [ ] Handled DeliveryInfo migration (if needed)
- [ ] Tested with OffersV2 helper methods (get_buy_box_winner, get_deal_listings)
- [ ] Updated deal detection to use DealDetails
- [ ] Tested Prime Exclusive deal handling
- [ ] Verified all price and savings calculations
- [ ] Updated merchant info access (added ID support)
- [ ] Tested availability messages and types

**Start migrating today!** OffersV2 is the future of Amazon PA-API offers. 🚀
