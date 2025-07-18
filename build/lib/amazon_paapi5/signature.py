import hmac
import hashlib
import json
from datetime import datetime, timezone
import urllib.parse

class Signature:
    def __init__(self, access_key: str, secret_key: str, region: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.service = 'ProductAdvertisingAPI'
        self.algorithm = 'AWS4-HMAC-SHA256'

    def generate(self, method: str, host: str, path: str, payload: dict) -> str:
        """Generate AWS V4 signature for the request."""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        date = timestamp[:8]

        # Step 1: Create canonical request
        payload_hash = hashlib.sha256(json.dumps(payload).encode()).hexdigest()
        canonical_request = f"{method}\n{path}\n\nhost:{host}\n\nhost\n{payload_hash}"
        canonical_request_hash = hashlib.sha256(canonical_request.encode()).hexdigest()

        # Step 2: Create string to sign
        credential_scope = f"{date}/{self.region}/{self.service}/aws4_request"
        string_to_sign = f"{self.algorithm}\n{timestamp}\n{credential_scope}\n{canonical_request_hash}"

        # Step 3: Calculate signature
        k_date = hmac.new(f"AWS4{self.secret_key}".encode(), date.encode(), hashlib.sha256).digest()
        k_region = hmac.new(k_date, self.region.encode(), hashlib.sha256).digest()
        k_service = hmac.new(k_region, self.service.encode(), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, b'aws4_request', hashlib.sha256).digest()
        signature = hmac.new(k_signing, string_to_sign.encode(), hashlib.sha256).hexdigest()

        # Step 4: Create authorization header
        authorization = (
            f"{self.algorithm} Credential={self.access_key}/{credential_scope}, "
            f"SignedHeaders=host, Signature={signature}"
        )
        return authorization

    def sign_request(self, url: str, method: str, payload: dict, headers: dict) -> dict:
        """Sign the request and return headers with authorization."""
        # Parse URL to get host and path
        parsed_url = urllib.parse.urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path if parsed_url.path else '/'
        
        # Generate authorization header using existing generate method
        authorization = self.generate(method, host, path, payload)
        
        # Add authorization to headers (create copy to avoid modifying original)
        signed_headers = headers.copy()
        signed_headers['Authorization'] = authorization
        
        return signed_headers
