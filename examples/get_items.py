from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_items import GetItemsRequest

# Validate credentials
access_key = "<YOUR_ACCESS_KEY>"
secret_key = "<YOUR_SECRET_KEY>"
partner_tag = "<YOUR_PARTNER_TAG>"
encryption_key = "<YOUR_ENCRYPTION_KEY>"

if any(x.startswith("<") and x.endswith(">") for x in [access_key, secret_key, partner_tag, encryption_key]):
    print("ERROR: You need to replace the placeholder values in this example file with your actual credentials.")
    print("Please update the values for access_key, secret_key, partner_tag, and encryption_key.")
    import sys
    sys.exit(1)

# Initialize configuration
config = Config(
    access_key=access_key,
    secret_key=secret_key,
    partner_tag=partner_tag,
    encryption_key=encryption_key,
    marketplace="www.amazon.in",
)

# Create client
client = Client(config)

# Get items by ASINs (batch processing up to 10 ASINs)
request = GetItemsRequest(
    item_ids=["B08L5V9T6R", "B07XVMJF2L", "B09F3T2K7P"],  # Example ASINs
    partner_tag=config.partner_tag,
    resources=["ItemInfo.Title", "Offers.Listings.Price", "Images.Primary.Medium"],
)

try:
    # Synchronous call
    response = client.get_items(request)
    print("GetItems completed successfully (batch processing)!")
    for item in response.items:
        print(f"ASIN: {item.asin}, Title: {item.title}, Price: {item.price}, URL: {item.detail_page_url}")

    # Asynchronous call (example)
    import asyncio
    async def async_get_items():
        response = await client.get_items_async(request)
        for item in response.items:
            print(f"Async - ASIN: {item.asin}, Title: {item.title}")

    asyncio.run(async_get_items())

except Exception as e:
    print(f"Error: {str(e)}")