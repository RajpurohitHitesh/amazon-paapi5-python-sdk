from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_items import GetItemsRequest

# Initialize configuration
config = Config(
    access_key="<YOUR_ACCESS_KEY>",
    secret_key="<YOUR_SECRET_KEY>",
    partner_tag="<YOUR_PARTNER_TAG>",
    encryption_key="<YOUR_ENCRYPTION_KEY>",
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