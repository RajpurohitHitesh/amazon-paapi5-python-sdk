import pytest
from amazon_paapi5.config import Config

def test_marketplace_config():
    config = Config(
        access_key="test_key",
        secret_key="test_secret",
        partner_tag="test_tag",
        encryption_key="test_encryption",
        marketplace="www.amazon.co.uk",
    )
    assert config.marketplace == "www.amazon.co.uk"
    assert config.region == "eu-west-1"
    assert config.host == "webservices.amazon.co.uk"

    config.set_marketplace("www.amazon.in")
    assert config.marketplace == "www.amazon.in"
    assert config.region == "us-east-1"
    assert config.host == "webservices.amazon.in"

    with pytest.raises(ValueError):
        config.set_marketplace("invalid.marketplace")