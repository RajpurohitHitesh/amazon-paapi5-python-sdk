"""
Example: Using OffersV2 API with GetItems

This example demonstrates how to use the Amazon PA-API 5.0 OffersV2 API
to retrieve detailed offer information including prices, deals, availability,
merchant information, and more.

OffersV2 provides improved reliability and data quality compared to the original
Offers API and includes new features like deal information and enhanced price data.
"""

from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_items import GetItemsRequest


def display_offer_listing(listing):
    """Helper function to display offer listing details"""
    
    # Price information
    if listing.price:
        price = listing.price
        if price.money:
            print(f"  Price: {price.money.display_amount} ({price.money.currency})")
        
        # Savings
        if price.savings:
            savings = price.savings
            if savings.money:
                print(f"  Save: {savings.money.display_amount}", end="")
            if savings.percentage:
                print(f" ({savings.percentage}%)")
            else:
                print()
        
        # Original price (Saving Basis)
        if price.saving_basis:
            basis = price.saving_basis
            if basis.money:
                label = basis.saving_basis_type_label or "Was"
                print(f"  {label}: {basis.money.display_amount}")
        
        # Price per unit
        if price.price_per_unit:
            print(f"  Unit Price: {price.price_per_unit.display_amount}")
    
    # Availability
    if listing.availability:
        avail = listing.availability
        print(f"  Availability: {avail.type}")
        if avail.message:
            print(f"  Status: {avail.message}")
        if avail.min_order_quantity:
            print(f"  Min Order: {avail.min_order_quantity}")
        if avail.max_order_quantity:
            print(f"  Max Order: {avail.max_order_quantity}")
    
    # Condition
    if listing.condition:
        cond = listing.condition
        print(f"  Condition: {cond.value}")
        if cond.sub_condition and cond.sub_condition != "Unknown":
            print(f"  Sub-Condition: {cond.sub_condition}")
        if cond.condition_note:
            print(f"  Note: {cond.condition_note}")
    
    # Merchant
    if listing.merchant_info:
        merchant = listing.merchant_info
        print(f"  Merchant: {merchant.name}")
        if merchant.id:
            print(f"  Merchant ID: {merchant.id}")
    
    # Deal Details
    if listing.deal_details:
        deal = listing.deal_details
        print(f"\n  ** DEAL INFORMATION **")
        if deal.badge:
            print(f"  Badge: {deal.badge}")
        if deal.access_type:
            print(f"  Access: {deal.access_type}")
        if deal.start_time:
            print(f"  Starts: {deal.start_time}")
        if deal.end_time:
            print(f"  Ends: {deal.end_time}")
        if deal.percent_claimed:
            print(f"  Claimed: {deal.percent_claimed}%")
        if deal.early_access_duration_in_milliseconds:
            minutes = deal.early_access_duration_in_milliseconds // 60000
            print(f"  Early Access: {minutes} minutes")
    
    # BuyBox Winner
    if listing.is_buy_box_winner:
        print(f"  ✓ BuyBox Winner")
    
    # Listing Type
    if listing.type:
        print(f"  Type: {listing.type}")
    
    # MAP violation
    if listing.violates_map:
        print(f"  ⚠ Violates MAP")
    
    # Loyalty Points (Japan only)
    if listing.loyalty_points and listing.loyalty_points.points:
        print(f"  Loyalty Points: {listing.loyalty_points.points}")


# Configure your API credentials
config = Config(
    access_key='YOUR_ACCESS_KEY',
    secret_key='YOUR_SECRET_KEY',
    partner_tag='YOUR_PARTNER_TAG',
    marketplace='US'  # or other marketplace
)

client = Client(config)

# Create a GetItems request with OffersV2 resources
request = GetItemsRequest(
    item_ids=['B00MNV8E0C'],  # Example ASIN
    resources=[
        'ItemInfo.Title',
        # Availability resources
        'OffersV2.Listings.Availability.MaxOrderQuantity',
        'OffersV2.Listings.Availability.Message',
        'OffersV2.Listings.Availability.MinOrderQuantity',
        'OffersV2.Listings.Availability.Type',
        # Condition resources
        'OffersV2.Listings.Condition.ConditionNote',
        'OffersV2.Listings.Condition.SubCondition',
        'OffersV2.Listings.Condition.Value',
        # Deal resources
        'OffersV2.Listings.DealDetails.AccessType',
        'OffersV2.Listings.DealDetails.Badge',
        'OffersV2.Listings.DealDetails.EarlyAccessDurationInMilliseconds',
        'OffersV2.Listings.DealDetails.EndTime',
        'OffersV2.Listings.DealDetails.PercentClaimed',
        'OffersV2.Listings.DealDetails.StartTime',
        # Other resources
        'OffersV2.Listings.IsBuyBoxWinner',
        'OffersV2.Listings.LoyaltyPoints.Points',
        'OffersV2.Listings.MerchantInfo.Id',
        'OffersV2.Listings.MerchantInfo.Name',
        # Price resources
        'OffersV2.Listings.Price.Money',
        'OffersV2.Listings.Price.PricePerUnit',
        'OffersV2.Listings.Price.SavingBasis.Money',
        'OffersV2.Listings.Price.SavingBasis.SavingBasisType',
        'OffersV2.Listings.Price.SavingBasis.SavingBasisTypeLabel',
        'OffersV2.Listings.Price.Savings.Money',
        'OffersV2.Listings.Price.Savings.Percentage',
        'OffersV2.Listings.Type',
        'OffersV2.Listings.ViolatesMAP',
    ]
)

try:
    # Get the items
    response = client.get_items(request)
    
    # Process each item
    for item in response.items:
        print(f"\n{'='*80}")
        print(f"ASIN: {item.asin}")
        print(f"Title: {item.title}")
        print(f"URL: {item.detail_page_url}")
        
        # Access OffersV2 data
        if item.offersv2:
            offersv2 = item.offersv2
            print(f"\n--- OFFERSV2 DATA ---")
            
            # Get BuyBox Winner
            buy_box_winner = offersv2.get_buy_box_winner()
            if buy_box_winner:
                print(f"\n*** BUYBOX WINNER ***")
                display_offer_listing(buy_box_winner)
            
            # Get all listings
            print(f"\nTotal Listings: {len(offersv2.listings)}")
            for idx, listing in enumerate(offersv2.listings, 1):
                print(f"\n--- Listing #{idx} ---")
                display_offer_listing(listing)
            
            # Get listings with deals
            deal_listings = offersv2.get_deal_listings()
            if deal_listings:
                print(f"\n=== LISTINGS WITH DEALS ({len(deal_listings)}) ===")
                for idx, listing in enumerate(deal_listings, 1):
                    print(f"\n--- Deal #{idx} ---")
                    display_offer_listing(listing)
            
            # Get Lightning Deals
            lightning_deals = offersv2.get_lightning_deals()
            if lightning_deals:
                print(f"\n=== LIGHTNING DEALS ({len(lightning_deals)}) ===")
                for idx, listing in enumerate(lightning_deals, 1):
                    print(f"\n--- Lightning Deal #{idx} ---")
                    display_offer_listing(listing)

except Exception as e:
    print(f"Error: {e}")


if __name__ == "__main__":
    print("Amazon PA-API 5.0 OffersV2 Example")
    print("Please configure your API credentials before running this example")
