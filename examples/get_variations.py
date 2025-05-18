from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_variations import GetVariationsRequest

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

# Get variations for an ASIN
request = GetVariationsRequest(
    asin="B08L5V9T6R",
    variation_page=1,
    partner_tag=config.partner_tag,
)

try:
    # Synchronous call
    response = client.get_variations(request)
    print("GetVariations completed successfully!")
    for variation in response.variations:
        print(f"ASIN: {variation.asin}, Title: {variation.title}, Dimensions: {variation.dimensions}")

    # Asynchronous call (example)
    import asyncio
    async def async_get_variations():
        response = await client.get_variations_async(request)
        for variation in response.variations:
            print(f"Async - ASIN: {variation.asin}, Title: {variation.title}")

    asyncio.run(async_get_variations())

except Exception as e:
    print(f"Error: {str(e)}")