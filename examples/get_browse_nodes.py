from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_browse_nodes import GetBrowseNodesRequest

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

# Get browse nodes
request = GetBrowseNodesRequest(
    browse_node_ids=["123456", "789012"],
    partner_tag=config.partner_tag,
)

try:
    # Synchronous call
    response = client.get_browse_nodes(request)
    print("GetBrowseNodes completed successfully!")
    for node in response.browse_nodes:
        print(f"ID: {node.id}, Name: {node.name}, Parent ID: {node.parent_id}")

    # Asynchronous call (example)
    import asyncio
    async def async_get_browse_nodes():
        response = await client.get_browse_nodes_async(request)
        for node in response.browse_nodes:
            print(f"Async - ID: {node.id}, Name: {node.name}")

    asyncio.run(async_get_browse_nodes())

except Exception as e:
    print(f"Error: {str(e)}")