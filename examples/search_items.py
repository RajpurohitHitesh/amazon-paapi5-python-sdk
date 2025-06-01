from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.search_items import SearchItemsRequest

# Initialize configuration
config = Config(
    access_key="<YOUR_ACCESS_KEY>",
    secret_key="<YOUR_SECRET_KEY>",
    partner_tag="<YOUR_PARTNER_TAG>",
    encryption_key="<YOUR_ENCRYPTION_KEY>",
    marketplace="www.amazon.in",
)

# Create client with Redis caching
client = Client(config)
client.cache = client.cache.__class__(ttl=3600, use_redis=True, redis_url="redis://localhost:6379")

# Search for products by keywords in a specific category
request = SearchItemsRequest(
    keywords="Laptop",
    search_index="Electronics",
    item_count=10,
    partner_tag=config.partner_tag,
)

try:
    # Synchronous call
    response = client.search_items(request)
    print("Search completed successfully!")
    for item in response.items:
        print(f"ASIN: {item.asin}, Title: {item.title}, Price: {item.price}, URL: {item.detail_page_url}")

    # Asynchronous call (example)
    import asyncio
    async def async_search():
        response = await client.search_items_async(request)
        for item in response.items:
            print(f"Async - ASIN: {item.asin}, Title: {item.title}")

    asyncio.run(async_search())

except Exception as e:
    print(f"Error: {str(e)}")