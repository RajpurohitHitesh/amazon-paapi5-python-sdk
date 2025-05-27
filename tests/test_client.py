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
def config_no_encryption():
    return Config(
        access_key="test_key",
        secret_key="test_secret",
        partner_tag="test_tag",
        marketplace="www.amazon.com",
    )

@pytest.fixture
def client(config):
    return Client(config)

@pytest.fixture
def client_no_encryption(config_no_encryption):
    return Client(config_no_encryption)

def test_client_initialization_with_encryption(client, config):
    """Test client initialization with encryption enabled."""
    # With encryption, the config values will be encrypted
    assert client.config.access_key != "test_key"  # Should be encrypted
    assert client.config.throttle_delay == pytest.approx(1.0)
    assert isinstance(client.signature, Signature)
    
    # The signature should use the decrypted credentials
    assert client.signature.access_key == "test_key"
    assert client.signature.region == "us-east-1"
    
    # Verify credential manager exists
    assert client.credential_manager is not None
    
    # Test decryption works
    decrypted = client.credential_manager.decrypt_credentials({
        'access_key': client.config.access_key,
        'secret_key': client.config.secret_key
    })
    assert decrypted['access_key'] == "test_key"
    assert decrypted['secret_key'] == "test_secret"

def test_client_initialization_without_encryption(client_no_encryption, config_no_encryption):
    """Test client initialization without encryption."""
    # Without encryption, the config values should remain as-is
    assert client_no_encryption.config.access_key == "test_key"
    assert client_no_encryption.config.secret_key == "test_secret"
    assert client_no_encryption.config.throttle_delay == pytest.approx(1.0)
    assert isinstance(client_no_encryption.signature, Signature)
    assert client_no_encryption.signature.access_key == "test_key"
    assert client_no_encryption.signature.region == "us-east-1"
    
    # Verify no credential manager exists
    assert client_no_encryption.credential_manager is None

# Keep the original test name but fix it to work without encryption
def test_client_initialization(client_no_encryption, config_no_encryption):
    """Original test - now uses no encryption to maintain backward compatibility."""
    assert client_no_encryption.config.access_key == "test_key"
    assert client_no_encryption.config.throttle_delay == pytest.approx(1.0)
    assert isinstance(client_no_encryption.signature, Signature)
    assert client_no_encryption.signature.access_key == "test_key"
    assert client_no_encryption.signature.region == "us-east-1"