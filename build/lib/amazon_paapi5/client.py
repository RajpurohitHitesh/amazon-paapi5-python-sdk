import asyncio
import time
from typing import Any, Optional, Dict
import requests
import aiohttp
import json
from datetime import datetime, timezone
import logging
from .config import Config
from .signature import Signature
from .resources import validate_resources
from .models.search_items import SearchItemsRequest, SearchItemsResponse
from .models.get_items import GetItemsRequest, GetItemsResponse
from .models.get_variations import GetVariationsRequest, GetVariationsResponse
from .models.get_browse_nodes import GetBrowseNodesRequest, GetBrowseNodesResponse
from .utils.throttling import Throttler
from .utils.cache import Cache
from .security.credential_manager import CredentialManager
from .monitoring import performance_monitor, measure_performance
from .exceptions import (
    AmazonAPIException,
    AuthenticationException,
    ThrottleException,
    InvalidParameterException,
    ResourceValidationException,
    NetworkException,
    SecurityException
)

class Client:
    """Amazon PA-API 5.0 Client with enhanced security and monitoring."""

    def __init__(self, 
                 config: Config, 
                 logger: Optional[logging.Logger] = None,
                 custom_cache: Optional[Cache] = None):
        """
        Initialize the Amazon PA-API client.
        
        Args:
            config: Configuration object
            logger: Optional logger instance
            custom_cache: Optional custom cache implementation
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self._initialize_time = datetime.utcnow().isoformat()
        self._request_count = 0
        
        # Initialize credential manager if encryption key is provided
        self.credential_manager = None
        if hasattr(config, 'encryption_key') and config.encryption_key:
            try:
                self.credential_manager = CredentialManager(config.encryption_key)
                encrypted_credentials = self.credential_manager.encrypt_credentials({
                    'access_key': config.access_key,
                    'secret_key': config.secret_key
                })
                config.access_key = encrypted_credentials['access_key']
                config.secret_key = encrypted_credentials['secret_key']
            except SecurityException as e:
                self.logger.error(f"Failed to initialize credential encryption: {str(e)}")
                raise
        
        # Initialize components
        self.throttler = Throttler(
            delay=config.throttle_delay,
            max_retries=getattr(config, 'max_retries', 3)
        )
        
        self.cache = custom_cache or Cache(**config.get_cache_config())
        
        # Get decrypted credentials for signature
        credentials = (
            self.credential_manager.decrypt_credentials({
                'access_key': config.access_key,
                'secret_key': config.secret_key
            })
            if self.credential_manager
            else {'access_key': config.access_key, 'secret_key': config.secret_key}
        )
        
        self.signature = Signature(
            credentials['access_key'],
            credentials['secret_key'],
            config.region
        )
        
        self.base_url = f"https://{config.host}/paapi5"
        self.session = requests.Session()
        self.async_session = None
        
        self.logger.info(
            f"Initialized Amazon PAAPI client for marketplace: {config.marketplace}"
        )

    def _log_request(self, endpoint: str, payload: dict) -> None:
        """Log request details."""
        self._request_count += 1
        self.logger.debug(
            f"Making request to {endpoint}",
            extra={
                'endpoint': endpoint,
                'marketplace': self.config.marketplace,
                'request_number': self._request_count
            }
        )

    def _log_response(self, endpoint: str, status_code: int, response_time: float) -> None:
        """Log response details."""
        self.logger.debug(
            f"Received response from {endpoint}",
            extra={
                'endpoint': endpoint,
                'status_code': status_code,
                'response_time': response_time,
                'cache_stats': self.cache.get_stats()
            }
        )

    @measure_performance(monitor=performance_monitor)
    def _make_request(self, endpoint: str, payload: dict) -> dict:
        """Make a synchronous API request with enhanced error handling."""
        self._log_request(endpoint, payload)
        start_time = time.time()
        
        try:
            validate_resources(endpoint, payload.get('Resources', []))
            authorization = self.signature.generate(
                'POST',
                self.config.host,
                f"/paapi5/{endpoint}",
                payload
            )
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": authorization,
                "x-amz-date": datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
                "Accept-Encoding": "gzip",
                "User-Agent": f"AmazonPAAPI5-Python-SDK/1.0.5 (Language=Python/{'.'.join(map(str, __import__('sys').version_info[:3]))})"
            }
            
            response = self.session.post(
                f"{self.base_url}/{endpoint}",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            execution_time = time.time() - start_time
            performance_monitor.record_api_request(endpoint, execution_time, response.status_code)
            self._log_response(endpoint, response.status_code, execution_time)
            
            if response.status_code != 200:
                error_response = response.json() if response.content else {}
                if response.status_code == 401:
                    raise AuthenticationException(
                        message=error_response.get('message', 'Authentication failed'),
                        response_errors=error_response.get('errors')
                    )
                elif response.status_code == 429:
                    retry_after = response.headers.get('Retry-After')
                    exception = ThrottleException(
                        message=error_response.get('message', 'Rate limit exceeded'),
                        response_errors=error_response.get('errors')
                    )
                    if retry_after:
                        exception.set_retry_after(int(retry_after))
                    raise exception
                elif response.status_code == 400:
                    raise InvalidParameterException(
                        message=error_response.get('message', 'Invalid parameters'),
                        response_errors=error_response.get('errors')
                    )
                raise AmazonAPIException(
                    message=f"Request failed with status {response.status_code}",
                    response_errors=error_response.get('errors')
                )
            
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"Network error: {str(e)}", exc_info=True)
            raise NetworkException(str(e), original_error=e)
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise

    @measure_performance(monitor=performance_monitor)
    async def _make_async_request(self, endpoint: str, payload: dict) -> dict:
        """Make an asynchronous API request with enhanced error handling."""
        self._log_request(endpoint, payload)
        start_time = time.time()
        
        if self.async_session is None:
            self.async_session = aiohttp.ClientSession()
        
        try:
            validate_resources(endpoint, payload.get('Resources', []))
            authorization = self.signature.generate(
                'POST',
                self.config.host,
                f"/paapi5/{endpoint}",
                payload
            )
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": authorization,
                "x-amz-date": datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
                "Accept-Encoding": "gzip",
                "User-Agent": f"AmazonPAAPI5-Python-SDK/1.0.5 (Async)"
            }
            
            async with self.async_session.post(
                f"{self.base_url}/{endpoint}",
                json=payload,
                headers=headers,
                timeout=30
            ) as response:
                execution_time = time.time() - start_time
                performance_monitor.record_api_request(endpoint, execution_time, response.status)
                self._log_response(endpoint, response.status, execution_time)
                
                if response.status != 200:
                    error_response = await response.json() if response.content else {}
                    if response.status == 401:
                        raise AuthenticationException(
                            message=error_response.get('message', 'Authentication failed'),
                            response_errors=error_response.get('errors')
                        )
                    elif response.status == 429:
                        retry_after = response.headers.get('Retry-After')
                        exception = ThrottleException(
                            message=error_response.get('message', 'Rate limit exceeded'),
                            response_errors=error_response.get('errors')
                        )
                        if retry_after:
                            exception.set_retry_after(int(retry_after))
                        raise exception
                    elif response.status == 400:
                        raise InvalidParameterException(
                            message=error_response.get('message', 'Invalid parameters'),
                            response_errors=error_response.get('errors')
                        )
                    raise AmazonAPIException(
                        message=f"Request failed with status {response.status}",
                        response_errors=error_response.get('errors')
                    )
                
                return await response.json()
                
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.logger.error(f"Async network error: {str(e)}", exc_info=True)
            raise NetworkException(str(e), original_error=e)
        except Exception as e:
            self.logger.error(f"Async request failed: {str(e)}", exc_info=True)
            raise

    async def __aenter__(self):
        """Support async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close async session on exit."""
        if self.async_session:
            await self.async_session.close()

    # All the API methods with @measure_performance decorator
    @measure_performance(monitor=performance_monitor)
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

    @measure_performance(monitor=performance_monitor)
    async def search_items_async(self, request: SearchItemsRequest) -> SearchItemsResponse:
        """Asynchronous version of search_items."""
        cache_key = f"search_items_{request.keywords}_{request.search_index}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return SearchItemsResponse.from_dict(cached_response)

        async with self.throttler:
            payload = request.to_dict()
            response = await self._make_async_request("searchitems", payload)
            self.cache.set(cache_key, response)
            return SearchItemsResponse.from_dict(response)

    @measure_performance(monitor=performance_monitor)
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

    @measure_performance(monitor=performance_monitor)
    async def get_items_async(self, request: GetItemsRequest) -> GetItemsResponse:
        """Asynchronous version of get_items."""
        cache_key = f"get_items_{'_'.join(request.item_ids)}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetItemsResponse.from_dict(cached_response)

        async with self.throttler:
            payload = request.to_dict()
            response = await self._make_async_request("getitems", payload)
            self.cache.set(cache_key, response)
            return GetItemsResponse.from_dict(response)

    @measure_performance(monitor=performance_monitor)
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

    @measure_performance(monitor=performance_monitor)
    async def get_variations_async(self, request: GetVariationsRequest) -> GetVariationsResponse:
        """Asynchronous version of get_variations."""
        cache_key = f"get_variations_{request.asin}_{request.variation_page}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetVariationsResponse.from_dict(cached_response)

        async with self.throttler:
            payload = request.to_dict()
            response = await self._make_async_request("getvariations", payload)
            self.cache.set(cache_key, response)
            return GetVariationsResponse.from_dict(response)

    @measure_performance(monitor=performance_monitor)
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

    @measure_performance(monitor=performance_monitor)
    async def get_browse_nodes_async(self, request: GetBrowseNodesRequest) -> GetBrowseNodesResponse:
        """Asynchronous version of get_browse_nodes."""
        cache_key = f"get_browse_nodes_{'_'.join(request.browse_node_ids)}"
        cached_response = self.cache.get(cache_key)
        if cached_response:
            return GetBrowseNodesResponse.from_dict(cached_response)

        async with self.throttler:
            payload = request.to_dict()
            response = await self._make_async_request("getbrowsenodes", payload)
            self.cache.set(cache_key, response)
            return GetBrowseNodesResponse.from_dict(response)

    def get_metrics(self) -> Dict:
        """Get performance metrics."""
        return {
            'initialization_time': self._initialize_time,
            'total_requests': self._request_count,
            'cache_stats': self.cache.get_stats(),
            'performance_metrics': performance_monitor.get_metrics(),
            'performance_summary': performance_monitor.get_performance_summary()
        }