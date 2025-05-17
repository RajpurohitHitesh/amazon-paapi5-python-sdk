import asyncio
import time
from typing import Any
import requests
import aiohttp
import json
from datetime import datetime, timezone
from .config import Config
from .signature import Signature
from .resources import validate_resources
from .models.search_items import SearchItemsRequest, SearchItemsResponse
from .models.get_items import GetItemsRequest, GetItemsResponse
from .models.get_variations import GetVariationsRequest, GetVariationsResponse
from .models.get_browse_nodes import GetBrowseNodesRequest, GetBrowseNodesResponse
from .utils.throttling import Throttler
from .utils.cache import Cache
from .exceptions import AmazonAPIException, AuthenticationException, ThrottleException, InvalidParameterException, ResourceValidationException

class Client:
    def __init__(self, config: Config):
        self.config = config
        self.throttler = Throttler(delay=config.throttle_delay)
        self.cache = Cache()
        self.signature = Signature(config.access_key, config.secret_key, config.region)
        self.base_url = f"https://{config.host}/paapi5"
        # Initialize session for connection reuse
        self.session = requests.Session()
        self.async_session = None  # Lazy initialization for async session

    def _make_request(self, endpoint: str, payload: dict) -> dict:
        """Make a synchronous API request with signature, throttling, and caching."""
        validate_resources(endpoint, payload.get('Resources', []))
        authorization = self.signature.generate('POST', self.config.host, f"/paapi5/{endpoint}", payload)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
            "x-amz-date": datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
            "Accept-Encoding": "gzip",  # Request Gzip compression
        }
        try:
            response = self.session.post(
                f"{self.base_url}/{endpoint}",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            if response.status_code == 401:
                raise AuthenticationException()
            elif response.status_code == 429:
                raise ThrottleException()
            elif response.status_code == 400:
                raise InvalidParameterException()
            raise AmazonAPIException(f"Request failed: {str(e)}")

    async def _make_async_request(self, endpoint: str, payload: dict) -> dict:
        """Make an asynchronous API request with signature, throttling, and caching."""
        validate_resources(endpoint, payload.get('Resources', []))
        authorization = self.signature.generate('POST', self.config.host, f"/paapi5/{endpoint}", payload)
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
            "x-amz-date": datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
            "Accept-Encoding": "gzip",  # Request Gzip compression
        }
        if self.async_session is None:
            self.async_session = aiohttp.ClientSession()
        try:
            async with self.async_session.post(
                f"{self.base_url}/{endpoint}",
                json=payload,
                headers=headers,
            ) as response:
                if response.status == 401:
                    raise AuthenticationException()
                elif response.status == 429:
                    raise ThrottleException()
                elif response.status == 400:
                    raise InvalidParameterException()
                if response.status != 200:
                    raise AmazonAPIException(f"Async request failed: {response.status}")
                return await response.json()
        except aiohttp.ClientError as e:
            raise AmazonAPIException(f"Async request failed: {str(e)}")

    async def __aenter__(self):
        """Support async context manager for proper session cleanup."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close async session on context manager exit."""
        if self.async_session:
            await self.async_session.close()

    def search_items(self, request: SearchItemsRequest) -> SearchItemsResponse:
        """Search for products by keywords and category."""
        cache_key = f"search_items_{request.keywords}_{request.search_index}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return SearchItemsResponse.from_dict(cached_response)

        with self.throttler:
            payload = request.to_dict()
            response = self._make_request("searchitems", payload)
            self.cache.set(cache_key, response)
            return SearchItemsResponse.from_dict(response)

    async def search_items_async(self, request: SearchItemsRequest) -> SearchItemsResponse:
        """Asynchronously search for products by keywords and category."""
        cache_key = f"search_items_{request.keywords}_{request.search_index}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return SearchItemsResponse.from_dict(cached_response)

        async with self.throttler:
            payload = request.to_dict()
            response = await self._make_async_request("searchitems", payload)
            self.cache.set(cache_key, response)
            return SearchItemsResponse.from_dict(response)

    def get_items(self, request: GetItemsRequest) -> GetItemsResponse:
        """Fetch details for specific ASINs (up to 10)."""
        cache_key = f"get_items_{'_'.join(request.item_ids)}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetItemsResponse.from_dict(cached_response)

        with self.throttler:
            payload = request.to_dict()
            response = self._make_request("getitems", payload)
            self.cache.set(cache_key, response)
            return GetItemsResponse.from_dict(response)

    async def get_items_async(self, request: GetItemsRequest) -> GetItemsResponse:
        """Asynchronously fetch details for specific ASINs (up to 10)."""
        cache_key = f"get_items_{'_'.join(request.item_ids)}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetItemsResponse.from_dict(cached_response)

        async with self.throttler:
            payload = request.to_dict()
            response = await self._make_async_request("getitems", payload)
            self.cache.set(cache_key, response)
            return GetItemsResponse.from_dict(response)

    def get_variations(self, request: GetVariationsRequest) -> GetVariationsResponse:
        """Fetch variations for a specific ASIN."""
        cache_key = f"get_variations_{request.asin}_{request.variation_page}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetVariationsResponse.from_dict(cached_response)

        with self.throttler:
            payload = request.to_dict()
            response = self._make_request("getvariations", payload)
            self.cache.set(cache_key, response)
            return GetVariationsResponse.from_dict(response)

    async def get_variations_async(self, request: GetVariationsRequest) -> GetVariationsResponse:
        """Asynchronously fetch variations for a specific ASIN."""
        cache_key = f"get_variations_{request.asin}_{request.variation_page}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetVariationsResponse.from_dict(cached_response)

        async with self.throttler:
            payload = request.to_dict()
            response = await self._make_async_request("getvariations", payload)
            self.cache.set(cache_key, response)
            return GetVariationsResponse.from_dict(response)

    def get_browse_nodes(self, request: GetBrowseNodesRequest) -> GetBrowseNodesResponse:
        """Fetch details for specific browse node IDs."""
        cache_key = f"get_browse_nodes_{'_'.join(request.browse_node_ids)}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetBrowseNodesResponse.from_dict(cached_response)

        with self.throttler:
            payload = request.to_dict()
            response = self._make_request("getbrowsenodes", payload)
            self.cache.set(cache_key, response)
            return GetBrowseNodesResponse.from_dict(response)

    async def get_browse_nodes_async(self, request: GetBrowseNodesRequest) -> GetBrowseNodesResponse:
        """Asynchronously fetch details for specific browse node IDs."""
        cache_key = f"get_browse_nodes_{'_'.join(request.browse_node_ids)}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetBrowseNodesResponse.from_dict(cached_response)

        async with self.throttler:
            payload = request.to_dict()
            response = await self._make_async_request("getbrowsenodes", payload)
            self.cache.set(cache_key, response)
            return GetBrowseNodesResponse.from_dict(response)