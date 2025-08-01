# Amazon PA-API 5.0 Python SDK

[![PyPI](https://img.shields.io/pypi/v/amazon-paapi5-python-sdk?color=%231182C2&label=PyPI)](https://pypi.org/project/amazon-paapi5-python-sdk/)
[![Python](https://img.shields.io/badge/Python->3.9-%23FFD140)](https://www.python.org/)
[![Amazon API](https://img.shields.io/badge/Amazon%20API-5.0-%23FD9B15)](https://webservices.amazon.com/paapi5/documentation/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/amazon-paapi5-python-sdk?label=Installs)](https://pypi.org/project/amazon-paapi5-python-sdk/)
![Static Badge](https://img.shields.io/badge/License-Apache_2.0-blue)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=RajpurohitHitesh_amazon-paapi5-python-sdk&metric=bugs)](https://sonarcloud.io/summary/new_code?id=RajpurohitHitesh_amazon-paapi5-python-sdk)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=RajpurohitHitesh_amazon-paapi5-python-sdk&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=RajpurohitHitesh_amazon-paapi5-python-sdk)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=RajpurohitHitesh_amazon-paapi5-python-sdk&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=RajpurohitHitesh_amazon-paapi5-python-sdk)
[![Python application](https://github.com/RajpurohitHitesh/amazon-paapi5-python-sdk/actions/workflows/python-app.yml/badge.svg)](https://github.com/RajpurohitHitesh/amazon-paapi5-python-sdk/actions/workflows/python-app.yml)
[![Python Package using Conda](https://github.com/RajpurohitHitesh/amazon-paapi5-python-sdk/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/RajpurohitHitesh/amazon-paapi5-python-sdk/actions/workflows/python-package-conda.yml)
[![Python package](https://github.com/RajpurohitHitesh/amazon-paapi5-python-sdk/actions/workflows/python-package.yml/badge.svg)](https://github.com/RajpurohitHitesh/amazon-paapi5-python-sdk/actions/workflows/python-package.yml)

Welcome to the **Amazon PA-API 5.0 Python SDK**, a lightweight and powerful library designed to help developers interact with Amazon’s Product Advertising API (PA-API) 5.0. This SDK makes it easy to fetch product details, search for items, retrieve variations, and explore browse nodes on Amazon’s marketplace, all while handling complex tasks like authentication, rate limiting, and caching for you. Whether you’re a beginner or an experienced coder, this guide will walk you through everything you need to know to use this library effectively.

This SDK is a Python equivalent of the PHP SDK ([amazon-paapi5-php-sdk](https://github.com/RajpurohitHitesh/amazon-paapi5-php-sdk)) by me ([Hitesh Rajpurohit](https://github.com/RajpurohitHitesh)), built to provide the same functionality with Python’s simplicity and flexibility.


## Table of Contents

- [What is the Amazon PA-API 5.0?](#what-is-the-amazon-pa-api-50)
- [Features](#features)
- [Installation](#installation)
- [Getting Started](#getting-started)
  - [Basic Usage Example](#basic-usage-example)
  - [Asynchronous Example](#asynchronous-example)
  - [Batch Processing Example](#batch-processing-example)
- [Supported Marketplaces](#supported-marketplaces)
- [File Structure](#file-structure)
- [How the SDK Works](#how-the-sdk-works)
- [Advanced Features](#advanced-features)
  - [Caching with Redis](#caching-with-redis)
  - [Custom Throttling](#custom-throttling)
  - [Custom Resources](#custom-resources)
  - [Gzip Compression and Connection Reuse](#gzip-compression-and-connection-reuse)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Comparison with PHP SDK](#comparison-with-php-sdk)
- [License](#license)
- [Contributing](#contributing)
- [Support](#support)


## What is the Amazon PA-API 5.0?

The Amazon Product Advertising API (PA-API) 5.0 is a tool provided by Amazon for developers, particularly those in the Amazon Associates (affiliate) program. It allows you to:
- Search for products on Amazon (e.g., “laptops” in the Electronics category).
- Retrieve details about specific products using their ASINs (Amazon Standard Identification Numbers).
- Get variations of a product (e.g., different sizes or colors of a shirt).
- Explore browse nodes (categories like “Books” or “Electronics”) to understand Amazon’s product hierarchy.

This SDK simplifies these tasks by providing a clean, Pythonic interface, handling authentication, and ensuring your requests comply with Amazon’s strict rate limits.

## Features

This SDK is packed with features to make your integration with PA-API 5.0 seamless:

1. **Supported Operations**:
   - **SearchItems**: Search for products by keywords and category (e.g., “Laptop” in Electronics).
   - **GetItems**: Fetch details for specific products using ASINs, with batch processing for up to 10 ASINs.
   - **GetVariations**: Retrieve variations of a product (e.g., different colors of a phone).
   - **GetBrowseNodes**: Get information about Amazon’s product categories (browse nodes), with support for multiple IDs.

2. **Smart Throttling**:
   - Automatically spaces out API requests to avoid hitting Amazon’s rate limits.
   - Uses exponential backoff (retries with increasing delays) if a request fails due to rate limits.
   - Manages a request queue to prevent overloading the API.

3. **Caching**:
   - Stores API responses to reduce redundant requests, saving API quota and improving performance.
   - Supports in-memory caching (using `cachetools`) and Redis caching (optional).
   - Configurable Time-To-Live (TTL) for cached data (default: 1 hour).

4. **Asynchronous Support**:
   - Supports non-blocking API calls using Python’s `asyncio` and `aiohttp`, ideal for high-performance applications.
   - Provides async methods (e.g., `search_items_async`) alongside synchronous methods.

5. **Type-Safe Objects**:
   - Uses Python’s `dataclasses` to create structured, type-safe request and response objects.
   - Ensures code is easy to write and debug, with IDE support for auto-completion.

6. **AWS V4 Signature Authentication**:
   - Generates secure AWS V4 signatures for all API requests, using your access key, secret key, and encryption key.
   - Handles the complex authentication process required by PA-API 5.0.

7. **Marketplace Support**:
   - Supports 18 Amazon marketplaces, each with its own region and host (e.g., `www.amazon.in` for India, `www.amazon.co.uk` for the UK).
   - Automatically configures the correct region and host when you select a marketplace.

8. **Resource Validation**:
   - Validates API request resources (e.g., `ItemInfo.Title`, `Offers.Listings.Price`) to ensure only valid data is requested.
   - Prevents errors due to invalid resource specifications.

9. **Error Handling**:
   - Provides a custom exception hierarchy (`AmazonAPIException`, `AuthenticationException`, `ThrottleException`, etc.) for clear error messages and recovery suggestions.
   - Gracefully handles network issues and API response errors.

10. **Performance Optimizations**:
    - **Batch Processing**: Fetch up to 10 ASINs in a single `GetItems` request or multiple browse node IDs in `GetBrowseNodes` to reduce API calls.
    - **Gzip Compression**: Requests compressed responses to minimize network overhead.
    - **Connection Reuse**: Uses persistent HTTP connections for faster requests.
    - **Memory Efficiency**: Optimized parsing and type-safe objects minimize memory usage.

11. **Modular Design**:
    - Organized into clear modules (`client`, `config`, `models`, `utils`) for easy maintenance and extension.
    - Each module has a specific role, making the codebase easy to understand.

12. **Comprehensive Testing**:
    - Includes unit tests for all major components (client, models, caching, config) using `pytest`.
    - Ensures the library is reliable and bug-free.

13. **Beginner-Friendly Examples**:
    - Provides example scripts for all operations (`search_items.py`, `get_items.py`, etc.) to help you get started quickly.
    - Includes both synchronous and asynchronous examples.

14. **Minimal Dependencies**:
    - Requires only `requests`, `aiohttp`, `cachetools`, and optional `redis` for caching.
    - Keeps your project lightweight and easy to set up.

15. **Apache-2.0 License**:
    - Open-source with a permissive license, allowing you to use, modify, and distribute the library freely.

## Installation

To use the SDK, you need Python 3.9 or higher. Follow these steps:

1. **Install the SDK**:
   ```bash
   pip install amazon-paapi5-python-sdk
   ```
   This installs the core dependencies (`requests`, `aiohttp`, `cachetools`).

2. **Optional: Install Redis Support**:
   If you want to use Redis for caching, install the `redis` extra:
   ```bash
   pip install amazon-paapi5-python-sdk[redis]
   ```

3. **Verify Installation**:
   Run the following command to check if the SDK is installed:
   ```bash
   python -c "import amazon_paapi5; print(amazon_paapi5.__version__)"
   ```
   It should output `1.0.5`.

## Getting Started

To use the SDK, you need an Amazon Associates account with access to PA-API 5.0 credentials:
- **Access Key**: Your API access key.
- **Secret Key**: Your API secret key.
- **Partner Tag**: Your Amazon Associates tag (e.g., `yourtag-20`).
- **Encryption Key**: Used for AWS V4 signature generation (often the same as the secret key or a separate key).

### Basic Usage Example

Here’s a simple example to search for laptops in the Electronics category on Amazon India:

```python
from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.search_items import SearchItemsRequest

# Step 1: Configure the SDK
config = Config(
    access_key="YOUR_ACCESS_KEY",        # Replace with your access key
    secret_key="YOUR_SECRET_KEY",        # Replace with your secret key
    partner_tag="YOUR_PARTNER_TAG",      # Replace with your partner tag
    encryption_key="YOUR_ENCRYPTION_KEY",# Replace with your encryption key
    marketplace="www.amazon.in",         # Use India marketplace
)

# Step 2: Create a client
client = Client(config)

# Step 3: Create a search request
request = SearchItemsRequest(
    keywords="Laptop",                   # Search term
    search_index="Electronics",          # Category
    item_count=10,                      # Number of results
    partner_tag=config.partner_tag,      # Your partner tag
)

# Step 4: Make the API call
try:
    response = client.search_items(request)
    print("Search completed successfully!")
    for item in response.items:
        print(f"ASIN: {item.asin}, Title: {item.title}, Price: {item.price}, URL: {item.detail_page_url}")
except Exception as e:
    print(f"Error: {str(e)}")
```

This code:
- Configures the SDK for the Indian marketplace.
- Searches for “Laptop” in the Electronics category.
- Prints the ASIN, title, price, and URL for each result.

### Asynchronous Example

For better performance in applications with many API calls, use the asynchronous method:

```python
import asyncio
from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.search_items import SearchItemsRequest

async def main():
    config = Config(
        access_key="YOUR_ACCESS_KEY",
        secret_key="YOUR_SECRET_KEY",
        partner_tag="YOUR_PARTNER_TAG",
        encryption_key="YOUR_ENCRYPTION_KEY",
        marketplace="www.amazon.in",
    )
    client = Client(config)
    request = SearchItemsRequest(
        keywords="Laptop",
        search_index="Electronics",
        item_count=10,
        partner_tag=config.partner_tag,
    )
    try:
        response = await client.search_items_async(request)
        for item in response.items:
            print(f"Async - ASIN: {item.asin}, Title: {item.title}")
    except Exception as e:
        print(f"Error: {str(e)}")

asyncio.run(main())
```

This uses `search_items_async` to make a non-blocking API call.

### Batch Processing Example

The SDK supports batch processing to fetch multiple items in a single request, reducing API calls. Here’s an example to fetch up to 10 ASINs:

```python
from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.models.get_items import GetItemsRequest

config = Config(
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    partner_tag="YOUR_PARTNER_TAG",
    encryption_key="YOUR_ENCRYPTION_KEY",
    marketplace="www.amazon.in",
)

client = Client(config)

request = GetItemsRequest(
    item_ids=["B08L5V9T6R", "B07XVMJF2L", "B09F3T2K7P"],  # Up to 10 ASINs
    partner_tag=config.partner_tag,
    resources=["ItemInfo.Title", "Offers.Listings.Price", "Images.Primary.Medium"],
)

try:
    response = client.get_items(request)
    print("Batch GetItems completed successfully!")
    for item in response.items:
        print(f"ASIN: {item.asin}, Title: {item.title}, Price: {item.price}")
except Exception as e:
    print(f"Error: {str(e)}")
```

This fetches details for multiple ASINs in one API call, improving efficiency.

## Supported Marketplaces

The SDK supports 18 Amazon marketplaces, each with its own region and host. When you set a `marketplace` in the `Config`, the SDK automatically configures the correct `region` and `host`. Here’s the full list:

| Marketplace | Region      | Host                            |
|-------------|-------------|---------------------------------|
| www.amazon.com | us-east-1   | webservices.amazon.com         |
| www.amazon.co.uk | eu-west-1   | webservices.amazon.co.uk       |
| www.amazon.de | eu-west-1   | webservices.amazon.de          |
| www.amazon.fr | eu-west-1   | webservices.amazon.fr          |
| www.amazon.co.jp | us-west-2   | webservices.amazon.co.jp       |
| www.amazon.ca | us-east-1   | webservices.amazon.ca           |
| www.amazon.com.au | us-west-2   | webservices.amazon.com.au      |
| www.amazon.in | us-east-1   | webservices.amazon.in          |
| www.amazon.com.br | us-east-1   | webservices.amazon.com.br      |
| www.amazon.it | eu-west-1   | webservices.amazon.it          |
| www.amazon.es | eu-west-1   | webservices.amazon.es          |
| www.amazon.com.mx | us-east-1   | webservices.amazon.com.mx      |
| www.amazon.nl | eu-west-1   | webservices.amazon.nl          |
| www.amazon.sg | us-west-2   | webservices.amazon.sg          |
| www.amazon.ae | eu-west-1   | webservices.amazon.ae          |
| www.amazon.sa | eu-west-1   | webservices.amazon.sa          |
| www.amazon.com.tr | eu-west-1   | webservices.amazon.com.tr      |
| www.amazon.se | eu-west-1   | webservices.amazon.se          |

Example: Switch to the UK marketplace dynamically:

```python
config.set_marketplace("www.amazon.co.uk")  # Updates region to 'eu-west-1' and host to 'webservices.amazon.co.uk'
```

## File Structure

The SDK is organized into a clear, modular structure. Here’s what each part does:

- **`src/amazon_paapi5/`**: The main library code.
  - `__init__.py`: Defines the library version (`1.0.5`).
  - `client.py`: The core `Client` class that handles API requests, throttling, caching, and signature generation.
  - `config.py`: Manages configuration (credentials, marketplace, throttling delay) and supports 18 marketplaces.
  - `signature.py`: Generates AWS V4 signatures for secure API authentication.
  - `resources.py`: Defines and validates valid API resources (e.g., `ItemInfo.Title`).
  - `models/`:
    - `__init__.py`: Empty file to make `models/` a package.
    - `search_items.py`: Defines `SearchItemsRequest` and `SearchItemsResponse` for searching products.
    - `get_items.py`: Defines `GetItemsRequest` and `GetItemsResponse` for fetching product details.
    - `get_variations.py`: Defines `GetVariationsRequest` and `GetVariationsResponse` for product variations.
    - `get_browse_nodes.py`: Defines `GetBrowseNodesRequest` and `GetBrowseNodesResponse` for browse nodes.
  - `utils/`:
    - `__init__.py`: Empty file to make `utils/` a package.
    - `throttling.py`: Implements the `Throttler` class for smart throttling with exponential backoff and queue management.
    - `cache.py`: Implements the `Cache` class for in-memory and Redis caching.
    - `async_helper.py`: Provides utilities for running async functions.
  - `exceptions.py`: Defines custom exceptions (`AmazonAPIException`, `AuthenticationException`, etc.) for error handling.

- **`tests/`**: Unit tests to ensure the library works correctly.
  - `__init__.py`: Empty file to make `tests/` a package.
  - `test_client.py`: Tests the `Client` class and signature generation.
  - `test_search_items.py`: Tests the `SearchItems` operation.
  - `test_get_items.py`: Tests the `GetItems` operation.
  - `test_get_variations.py`: Tests the `GetVariations` operation.
  - `test_get_browse_nodes.py`: Tests the `GetBrowseNodes` operation.
  - `test_cache.py`: Tests the caching functionality.
  - `test_config.py`: Tests the marketplace configuration.

- **`examples/`**: Example scripts to help you get started.
  - `search_items.py`: Shows how to search for products (sync and async).
  - `get_items.py`: Shows how to fetch product details by ASIN with batch processing.
  - `get_variations.py`: Shows how to get product variations.
  - `get_browse_nodes.py`: Shows how to retrieve browse node information.

- **`setup.py`**: Configures the library for installation via `pip`.
- **`requirements.txt`**: Lists dependencies (`requests`, `aiohttp`, `cachetools`, `redis`, `pytest`).
- **`.gitignore`**: Ignores unnecessary files (e.g., `__pycache__`, `venv/`).
- **`README.md`**: This file, providing comprehensive documentation.
- **`CONTRIBUTING.md`**: Instructions for contributing to the project.
- **`LICENSE`**: Apache-2.0 License file.

## How the SDK Works

Let’s break down how the SDK handles a typical API request, so even a new coder can understand the flow:

1. **Configuration**:
   - You create a `Config` object with your credentials (`access_key`, `secret_key`, `partner_tag`, `encryption_key`) and a `marketplace` (e.g., `www.amazon.in`).
   - The `Config` class uses the `MARKETPLACES` dictionary to set the correct `region` (e.g., `us-east-1`) and `host` (e.g., `webservices.amazon.in`).

2. **Client Creation**:
   - The `Client` class takes the `Config` object and initializes:
     - A `Throttler` for rate limiting.
     - A `Cache` for storing responses (in-memory or Redis).
     - A `Signature` object for AWS V4 signature generation.
     - HTTP sessions for connection reuse.

3. **Request Preparation**:
   - You create a request object (e.g., `SearchItemsRequest`) with parameters like `keywords` and `search_index`.
   - The request object validates resources (using `resources.py`) and converts to a dictionary for the API call.

4. **API Call**:
   - The `Client` generates an AWS V4 signature (using `signature.py`) for authentication.
   - The `Throttler` ensures the request doesn’t exceed rate limits, using a delay, exponential backoff, or queue.
   - The request is sent using `requests` (sync) or `aiohttp` (async), with Gzip compression and connection reuse.
   - The response is cached (using `cache.py`) to avoid repeated calls.

5. **Response Handling**:
   - The response is parsed into a type-safe object (e.g., `SearchItemsResponse`) with fields like `items`.
   - If an error occurs, a specific exception (e.g., `ThrottleException`) is raised with recovery suggestions.

## Advanced Features

### Caching with Redis
To use Redis for caching (instead of in-memory), initialize the client with Redis enabled:

```python
client = Client(config)
client.cache = client.cache.__class__(ttl=3600, use_redis=True, redis_url="redis://localhost:6379")
```

This stores API responses in a Redis server, useful for large-scale applications.

### Custom Throttling
Adjust the throttling delay or retry settings in the `Config`:

```python
config = Config(
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    partner_tag="YOUR_PARTNER_TAG",
    encryption_key="YOUR_ENCRYPTION_KEY",
    marketplace="www.amazon.in",
    throttle_delay=2.0,  # 2-second delay between requests
)
```

### Custom Resources
Specify custom resources in your request:

```python
request = SearchItemsRequest(
    keywords="Laptop",
    search_index="Electronics",
    partner_tag=config.partner_tag,
    resources=["ItemInfo.Title", "Images.Primary.Medium"],
)
```

The SDK validates these resources to ensure they’re valid for the operation.

### Gzip Compression and Connection Reuse
The SDK optimizes network performance by:
- Requesting Gzip-compressed responses to reduce data transfer size.
- Reusing HTTP connections via `requests.Session` (sync) and `aiohttp.ClientSession` (async) for faster requests.

These features are enabled automatically and require no configuration.

## Running Tests

To verify the SDK works correctly, run the unit tests:

1. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run tests with `pytest`:
   ```bash
   pytest tests/
   ```

The tests cover client initialization, request validation, caching, and configuration.

## Troubleshooting

- **Rate Limit Errors (`ThrottleException`)**: Increase the `throttle_delay` in `Config` or check your API quota in your Amazon Associates account.
- **Authentication Errors (`AuthenticationException`)**: Ensure your `access_key`, `secret_key`, `partner_tag`, and `encryption_key` are correct.
- **Invalid Parameters (`InvalidParameterException`)**: Check that your request parameters (e.g., `item_ids`, `browse_node_ids`) are valid and within limits (e.g., max 10 ASINs).
- **Invalid Resources (`ResourceValidationException`)**: Use only supported resources listed in `resources.py`.
- **Redis Connection Issues**: Verify your Redis server is running and the `redis_url` is correct.

## Comparison with PHP SDK

This Python SDK is designed to match the functionality of the PHP SDK ([amazon-paapi5-php-sdk](https://github.com/RajpurohitHitesh/amazon-paapi5-php-sdk)):

- **Operations**: Both support `SearchItems`, `GetItems`, `GetVariations`, `GetBrowseNodes`.
- **Throttling**: Both use exponential backoff and queue management.
- **Caching**: The PHP SDK uses PSR-6; the Python SDK uses `cachetools` and Redis, providing equivalent functionality.
- **Async Support**: The PHP SDK uses Guzzle promises; the Python SDK uses `aiohttp` with `asyncio`.
- **Authentication**: Both implement AWS V4 signatures.
- **Marketplaces**: Both support the same 18 marketplaces.
- **Type Safety**: The PHP SDK uses strict typing; the Python SDK uses `dataclasses`.
- **Performance**: Both support batch processing (up to 10 ASINs), Gzip compression, connection reuse, and memory-efficient parsing.
- **Error Handling**: Both provide custom exception hierarchies for detailed error reporting.

The Python SDK is tailored for Python developers, leveraging Python’s ecosystem while maintaining the same robustness and ease of use as the PHP SDK.[](https://packagist.org/packages/rajpurohithitesh/amazon-paapi5-sdk)[](https://packagist.org/packages/rajpurohithitesh/amazon-paapi5-php-sdk)

## License

This SDK is licensed under the [Apache-2.0 License](LICENSE), which allows you to use, modify, and distribute the code freely, as long as you include the license in your project.

## Contributing

We welcome contributions from the community! Whether you’re fixing a bug, adding a feature, or improving documentation, check out the [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed instructions on how to get started.

## Support

If you have questions or run into issues:
- Open an issue on [GitHub](https://github.com/rajpurohithitesh/amazon-paapi5-python-sdk).
- Check the Amazon Associates documentation for PA-API 5.0 details.
- Reach out to the maintainer, Hitesh Rajpurohit, via GitHub.

Happy coding, and enjoy building with the Amazon PA-API 5.0 Python SDK!
