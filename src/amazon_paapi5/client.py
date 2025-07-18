import asyncio
import time
from typing import Any, Optional, Dict
import requests
import aiohttp
import json
import hashlib
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

    def _create_cache_key(self, operation: str, payload: dict) -> str:
        """
        Create a cache key from the operation and payload.
        Handles unhashable types like lists by converting them to hashable equivalents.
        """
        try:
            # Use JSON serialization with sorted keys for consistent hash generation
            payload_str = json.dumps(payload, sort_keys=True)
            payload_hash = hashlib.md5(payload_str.encode()).hexdigest()
            return f"{operation}:{payload_hash}"
        except (TypeError, ValueError) as e:
            # Fallback to string representation if JSON serialization fails
            self.logger.warning(f"Failed to serialize payload for cache key: {e}")
            payload_str = str(sorted(payload.items()))
            payload_hash = hashlib.md5(payload_str.encode()).hexdigest()
            return f"{operation}:{payload_hash}"

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
        """Log response details and update performance metrics."""
        self.logger.debug(
            f"Received response from {endpoint} with status {status_code} in {response_time:.2f}s",
            extra={
                'endpoint': endpoint,
                'status_code': status_code,
                'response_time': response_time,
                'marketplace': self.config.marketplace
            }
        )
        
        # Update performance metrics if monitoring is enabled
        if hasattr(self, 'performance_monitor'):
            self.performance_monitor.record_api_request(
                endpoint=endpoint,
                response_time=response_time,
                status_code=status_code
            )

    @measure_performance(monitor=performance_monitor)
    def search_items(self, request: SearchItemsRequest) -> SearchItemsResponse:
        """Search items by keywords."""
        endpoint = f"{self.base_url}/searchitems"
        payload = request.to_dict()
        
        # Check cache first
        cache_key = self._create_cache_key("search_items", payload)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Using cached response for SearchItems")
            return cached_response
        
        # Make API call
        self._log_request(endpoint, payload)
        with self.throttler:
            start_time = time.time()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "amazon-paapi5-python-sdk/1.0.5"
            }
            
            # Add AWS authentication headers
            signed_headers = self.signature.sign_request(
                url=endpoint,
                method="POST",
                payload=payload,
                headers=headers
            )
            
            response = self.session.post(
                endpoint, 
                headers=signed_headers,
                json=payload
            )
            
            response_time = time.time() - start_time
            self._log_response(endpoint, response.status_code, response_time)
            
        # Handle response
        if response.status_code != 200:
            self._handle_error_response(response)
            
        data = response.json()
        search_response = SearchItemsResponse.from_dict(data)
        
        # Cache response
        self.cache.set(cache_key, search_response)
        
        return search_response
    
    async def search_items_async(self, request: SearchItemsRequest) -> SearchItemsResponse:
        """Search items by keywords asynchronously."""
        endpoint = f"{self.base_url}/searchitems"
        payload = request.to_dict()
        
        # Check cache first
        cache_key = self._create_cache_key("search_items", payload)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Using cached response for SearchItems (async)")
            return cached_response
        
        # Create session if needed
        if self.async_session is None:
            self.async_session = aiohttp.ClientSession()
        
        # Make API call
        self._log_request(endpoint, payload)
        async with self.throttler:
            start_time = time.time()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "amazon-paapi5-python-sdk/1.0.5"
            }
            
            # Add AWS authentication headers
            signed_headers = self.signature.sign_request(
                url=endpoint,
                method="POST",
                payload=payload,
                headers=headers
            )
            
            async with self.async_session.post(
                endpoint, 
                headers=signed_headers,
                json=payload
            ) as response:
                response_time = time.time() - start_time
                self._log_response(endpoint, response.status, response_time)
                
                # Handle response
                if response.status != 200:
                    text = await response.text()
                    self._handle_error_response_async(response.status, text)
                
                data = await response.json()
                search_response = SearchItemsResponse.from_dict(data)
                
                # Cache response
                self.cache.set(cache_key, search_response)
                
                return search_response
    
    @measure_performance(monitor=performance_monitor)
    def get_items(self, request: GetItemsRequest) -> GetItemsResponse:
        """Get items by ASINs."""
        endpoint = f"{self.base_url}/getitems"
        payload = request.to_dict()
        
        # Check cache first
        cache_key = self._create_cache_key("get_items", payload)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Using cached response for GetItems")
            return cached_response
        
        # Make API call
        self._log_request(endpoint, payload)
        with self.throttler:
            start_time = time.time()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "amazon-paapi5-python-sdk/1.0.5"
            }
            
            # Add AWS authentication headers
            signed_headers = self.signature.sign_request(
                url=endpoint,
                method="POST",
                payload=payload,
                headers=headers
            )
            
            response = self.session.post(
                endpoint, 
                headers=signed_headers,
                json=payload
            )
            
            response_time = time.time() - start_time
            self._log_response(endpoint, response.status_code, response_time)
            
        # Handle response
        if response.status_code != 200:
            self._handle_error_response(response)
            
        data = response.json()
        items_response = GetItemsResponse.from_dict(data)
        
        # Cache response
        self.cache.set(cache_key, items_response)
        
        return items_response
    
    async def get_items_async(self, request: GetItemsRequest) -> GetItemsResponse:
        """Get items by ASINs asynchronously."""
        endpoint = f"{self.base_url}/getitems"
        payload = request.to_dict()
        
        # Check cache first
        cache_key = self._create_cache_key("get_items", payload)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Using cached response for GetItems (async)")
            return cached_response
        
        # Create session if needed
        if self.async_session is None:
            self.async_session = aiohttp.ClientSession()
        
        # Make API call
        self._log_request(endpoint, payload)
        async with self.throttler:
            start_time = time.time()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "amazon-paapi5-python-sdk/1.0.5"
            }
            
            # Add AWS authentication headers
            signed_headers = self.signature.sign_request(
                url=endpoint,
                method="POST",
                payload=payload,
                headers=headers
            )
            
            async with self.async_session.post(
                endpoint, 
                headers=signed_headers,
                json=payload
            ) as response:
                response_time = time.time() - start_time
                self._log_response(endpoint, response.status, response_time)
                
                # Handle response
                if response.status != 200:
                    text = await response.text()
                    self._handle_error_response_async(response.status, text)
                
                data = await response.json()
                items_response = GetItemsResponse.from_dict(data)
                
                # Cache response
                self.cache.set(cache_key, items_response)
                
                return items_response
    
    @measure_performance(monitor=performance_monitor)
    def get_variations(self, request: GetVariationsRequest) -> GetVariationsResponse:
        """Get variations for an ASIN."""
        endpoint = f"{self.base_url}/getvariations"
        payload = request.to_dict()
        
        # Check cache first
        cache_key = self._create_cache_key("get_variations", payload)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Using cached response for GetVariations")
            return cached_response
        
        # Make API call
        self._log_request(endpoint, payload)
        with self.throttler:
            start_time = time.time()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "amazon-paapi5-python-sdk/1.0.5"
            }
            
            # Add AWS authentication headers
            signed_headers = self.signature.sign_request(
                url=endpoint,
                method="POST",
                payload=payload,
                headers=headers
            )
            
            response = self.session.post(
                endpoint, 
                headers=signed_headers,
                json=payload
            )
            
            response_time = time.time() - start_time
            self._log_response(endpoint, response.status_code, response_time)
            
        # Handle response
        if response.status_code != 200:
            self._handle_error_response(response)
            
        data = response.json()
        variations_response = GetVariationsResponse.from_dict(data)
        
        # Cache response
        self.cache.set(cache_key, variations_response)
        
        return variations_response
    
    async def get_variations_async(self, request: GetVariationsRequest) -> GetVariationsResponse:
        """Get variations for an ASIN asynchronously."""
        endpoint = f"{self.base_url}/getvariations"
        payload = request.to_dict()
        
        # Check cache first
        cache_key = self._create_cache_key("get_variations", payload)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Using cached response for GetVariations (async)")
            return cached_response
        
        # Create session if needed
        if self.async_session is None:
            self.async_session = aiohttp.ClientSession()
        
        # Make API call
        self._log_request(endpoint, payload)
        async with self.throttler:
            start_time = time.time()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "amazon-paapi5-python-sdk/1.0.5"
            }
            
            # Add AWS authentication headers
            signed_headers = self.signature.sign_request(
                url=endpoint,
                method="POST",
                payload=payload,
                headers=headers
            )
            
            async with self.async_session.post(
                endpoint, 
                headers=signed_headers,
                json=payload
            ) as response:
                response_time = time.time() - start_time
                self._log_response(endpoint, response.status, response_time)
                
                # Handle response
                if response.status != 200:
                    text = await response.text()
                    self._handle_error_response_async(response.status, text)
                
                data = await response.json()
                variations_response = GetVariationsResponse.from_dict(data)
                
                # Cache response
                self.cache.set(cache_key, variations_response)
                
                return variations_response
    
    @measure_performance(monitor=performance_monitor)
    def get_browse_nodes(self, request: GetBrowseNodesRequest) -> GetBrowseNodesResponse:
        """Get browse nodes by IDs."""
        endpoint = f"{self.base_url}/getbrowsenodes"
        payload = request.to_dict()
        
        # Check cache first
        cache_key = self._create_cache_key("get_browse_nodes", payload)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Using cached response for GetBrowseNodes")
            return cached_response
        
        # Make API call
        self._log_request(endpoint, payload)
        with self.throttler:
            start_time = time.time()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "amazon-paapi5-python-sdk/1.0.5"
            }
            
            # Add AWS authentication headers
            signed_headers = self.signature.sign_request(
                url=endpoint,
                method="POST",
                payload=payload,
                headers=headers
            )
            
            response = self.session.post(
                endpoint, 
                headers=signed_headers,
                json=payload
            )
            
            response_time = time.time() - start_time
            self._log_response(endpoint, response.status_code, response_time)
            
        # Handle response
        if response.status_code != 200:
            self._handle_error_response(response)
            
        data = response.json()
        browse_nodes_response = GetBrowseNodesResponse.from_dict(data)
        
        # Cache response
        self.cache.set(cache_key, browse_nodes_response)
        
        return browse_nodes_response
    
    async def get_browse_nodes_async(self, request: GetBrowseNodesRequest) -> GetBrowseNodesResponse:
        """Get browse nodes by IDs asynchronously."""
        endpoint = f"{self.base_url}/getbrowsenodes"
        payload = request.to_dict()
        
        # Check cache first
        cache_key = self._create_cache_key("get_browse_nodes", payload)
        cached_response = self.cache.get(cache_key)
        if cached_response:
            self.logger.debug("Using cached response for GetBrowseNodes (async)")
            return cached_response
        
        # Create session if needed
        if self.async_session is None:
            self.async_session = aiohttp.ClientSession()
        
        # Make API call
        self._log_request(endpoint, payload)
        async with self.throttler:
            start_time = time.time()
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "User-Agent": "amazon-paapi5-python-sdk/1.0.5"
            }
            
            # Add AWS authentication headers
            signed_headers = self.signature.sign_request(
                url=endpoint,
                method="POST",
                payload=payload,
                headers=headers
            )
            
            async with self.async_session.post(
                endpoint, 
                headers=signed_headers,
                json=payload
            ) as response:
                response_time = time.time() - start_time
                self._log_response(endpoint, response.status, response_time)
                
                # Handle response
                if response.status != 200:
                    text = await response.text()
                    self._handle_error_response_async(response.status, text)
                
                data = await response.json()
                browse_nodes_response = GetBrowseNodesResponse.from_dict(data)
                
                # Cache response
                self.cache.set(cache_key, browse_nodes_response)
                
                return browse_nodes_response
    
    def _handle_error_response(self, response):
        """Handle error responses from the API."""
        try:
            error_data = response.json()
            error_message = error_data.get("Errors", [{}])[0].get("Message", "Unknown error")
            error_code = error_data.get("Errors", [{}])[0].get("Code", "Unknown")
        except:
            error_message = response.text
            error_code = str(response.status_code)
        
        status_code = response.status_code
        
        if status_code == 401:
            raise AuthenticationException(
                f"Authentication failed: {error_message}",
                error_code=error_code,
                status_code=status_code
            )
        elif status_code == 429:
            raise ThrottleException(
                f"Rate limit exceeded: {error_message}",
                error_code=error_code,
                status_code=status_code
            )
        elif 400 <= status_code < 500:
            raise InvalidParameterException(
                f"Invalid request: {error_message}",
                error_code=error_code,
                status_code=status_code
            )
        elif status_code >= 500:
            raise NetworkException(
                f"Server error: {error_message}",
                error_code=error_code,
                status_code=status_code
            )
        else:
            raise AmazonAPIException(
                f"API error: {error_message}",
                error_code=error_code,
                status_code=status_code
            )
    
    def _handle_error_response_async(self, status, text):
        """Handle error responses from the API for async requests."""
        try:
            error_data = json.loads(text)
            error_message = error_data.get("Errors", [{}])[0].get("Message", "Unknown error")
            error_code = error_data.get("Errors", [{}])[0].get("Code", "Unknown")
        except:
            error_message = text
            error_code = str(status)
        
        if status == 401:
            raise AuthenticationException(
                f"Authentication failed: {error_message}",
                error_code=error_code,
                status_code=status
            )
        elif status == 429:
            raise ThrottleException(
                f"Rate limit exceeded: {error_message}",
                error_code=error_code,
                status_code=status
            )
        elif 400 <= status < 500:
            raise InvalidParameterException(
                f"Invalid request: {error_message}",
                error_code=error_code,
                status_code=status
            )
        elif status >= 500:
            raise NetworkException(
                f"Server error: {error_message}",
                error_code=error_code,
                status_code=status
            )
        else:
            raise AmazonAPIException(
                f"API error: {error_message}",
                error_code=error_code,
                status_code=status
            )

    async def close(self):
        """Close the client and release resources."""
        if self.async_session:
            await self.async_session.close()
            self.async_session = None
        
        self.session.close()
