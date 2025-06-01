from typing import Optional

class Config:
    MARKETPLACES = {
        'www.amazon.com': {'region': 'us-east-1', 'host': 'webservices.amazon.com'},
        'www.amazon.co.uk': {'region': 'eu-west-1', 'host': 'webservices.amazon.co.uk'},
        'www.amazon.de': {'region': 'eu-west-1', 'host': 'webservices.amazon.de'},
        'www.amazon.fr': {'region': 'eu-west-1', 'host': 'webservices.amazon.fr'},
        'www.amazon.co.jp': {'region': 'us-west-2', 'host': 'webservices.amazon.co.jp'},
        'www.amazon.ca': {'region': 'us-east-1', 'host': 'webservices.amazon.ca'},
        'www.amazon.com.au': {'region': 'us-west-2', 'host': 'webservices.amazon.com.au'},
        'www.amazon.in': {'region': 'us-east-1', 'host': 'webservices.amazon.in'},
        'www.amazon.com.br': {'region': 'us-east-1', 'host': 'webservices.amazon.com.br'},
        'www.amazon.it': {'region': 'eu-west-1', 'host': 'webservices.amazon.it'},
        'www.amazon.es': {'region': 'eu-west-1', 'host': 'webservices.amazon.es'},
        'www.amazon.com.mx': {'region': 'us-east-1', 'host': 'webservices.amazon.com.mx'},
        'www.amazon.nl': {'region': 'eu-west-1', 'host': 'webservices.amazon.nl'},
        'www.amazon.sg': {'region': 'us-west-2', 'host': 'webservices.amazon.sg'},
        'www.amazon.ae': {'region': 'eu-west-1', 'host': 'webservices.amazon.ae'},
        'www.amazon.sa': {'region': 'eu-west-1', 'host': 'webservices.amazon.sa'},
        'www.amazon.com.tr': {'region': 'eu-west-1', 'host': 'webservices.amazon.com.tr'},
        'www.amazon.se': {'region': 'eu-west-1', 'host': 'webservices.amazon.se'},
    }

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        partner_tag: str,
        marketplace: str = "www.amazon.com",
        encryption_key: Optional[str] = None,
        throttle_delay: float = 1.0,
        cache_ttl: int = 3600,
        use_file_cache: bool = True,
        cache_base_path: str = "/root",
        use_redis_cache: bool = False,
        redis_url: str = "redis://localhost:6379",
    ):
        """
        Initialize Amazon PA API configuration.
        
        Args:
            access_key: Amazon PA API access key
            secret_key: Amazon PA API secret key
            partner_tag: Amazon Associate tag
            marketplace: Amazon marketplace URL (default: www.amazon.com)
            encryption_key: Optional key for encrypting credentials
            throttle_delay: Delay between API requests in seconds
            cache_ttl: Cache time-to-live in seconds
            use_file_cache: Whether to use file-based caching
            cache_base_path: Base path for file cache
            use_redis_cache: Whether to use Redis caching
            redis_url: Redis connection URL
        """
        self.access_key = access_key
        self.secret_key = secret_key
        self.partner_tag = partner_tag
        self.encryption_key = encryption_key
        self.throttle_delay = throttle_delay
        self.cache_ttl = cache_ttl
        self.use_file_cache = use_file_cache
        self.cache_base_path = cache_base_path
        self.use_redis_cache = use_redis_cache
        self.redis_url = redis_url
        self.set_marketplace(marketplace)

    def set_marketplace(self, marketplace: str) -> None:
        """
        Set the marketplace and update region and host accordingly.
        
        Args:
            marketplace: Marketplace URL
            
        Raises:
            ValueError: If marketplace is not supported
        """
        if marketplace not in self.MARKETPLACES:
            raise ValueError(f"Unsupported marketplace: {marketplace}")
        self.marketplace = marketplace
        self.region = self.MARKETPLACES[marketplace]['region']
        self.host = self.MARKETPLACES[marketplace]['host']

    def get_cache_config(self) -> dict:
        """Get cache configuration parameters."""
        return {
            'ttl': self.cache_ttl,
            'use_redis': self.use_redis_cache,
            'use_file': self.use_file_cache,
            'base_path': self.cache_base_path,
            'redis_url': self.redis_url
        }