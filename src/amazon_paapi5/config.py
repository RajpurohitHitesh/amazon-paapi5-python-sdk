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
        encryption_key: str,
        marketplace: str = "www.amazon.com",
        throttle_delay: float = 1.0,
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.partner_tag = partner_tag
        self.encryption_key = encryption_key
        self.throttle_delay = throttle_delay
        self.set_marketplace(marketplace)

    def set_marketplace(self, marketplace: str) -> None:
        """Set the marketplace and update region and host accordingly."""
        if marketplace not in self.MARKETPLACES:
            raise ValueError(f"Unsupported marketplace: {marketplace}")
        self.marketplace = marketplace
        self.region = self.MARKETPLACES[marketplace]['region']
        self.host = self.MARKETPLACES[marketplace]['host']