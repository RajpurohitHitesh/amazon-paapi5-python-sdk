import pytest
from amazon_paapi5.client import Client
from amazon_paapi5.config import Config
from amazon_paapi5.signature import Signature

@pytest.fixture
def config():
    return Config(
        access_key="test_key",
        secret_key="test_secret",
        partner_tag="test_tag",
        encryption_key="test_encryption",
        marketplace="www.amazon.com",
    )

@pytest.fixture
def client(config):
    return Client(config)

def test_client_initialization(client, config):
    assert client.config.access_key == "test_key"
    assert client.config.throttle_delay == pytest.approx(1.0)
    assert isinstance(client.signature, Signature)
    assert client.signature.access_key == "test_key"
    assert client.signature.region == "us-east-1"