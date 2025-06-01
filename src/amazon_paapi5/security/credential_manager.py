from cryptography.fernet import Fernet
import base64
import os
import logging
from typing import Dict, Any, Optional
from ..exceptions import SecurityException

class CredentialManager:
    """Secure credential management with encryption."""
    
    def __init__(self, encryption_key: str = None):
        """
        Initialize with optional encryption key.
        
        Args:
            encryption_key: Optional encryption key for securing credentials
            
        Raises:
            SecurityException: If encryption key is invalid
        """
        self.logger = logging.getLogger(__name__)
        self.encryption_key = encryption_key
        self.fernet = None
        
        if encryption_key:
            try:
                # Use a more secure key derivation method
                from cryptography.hazmat.primitives import hashes
                from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
                
                # Use fixed salt for deterministic key derivation
                salt = b'amazon_paapi5_python_sdk'
                
                # Derive a proper key from the provided encryption key
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode('utf-8')))
                self.fernet = Fernet(key)
                self.logger.info("Successfully initialized credential encryption")
            except Exception as e:
                self.logger.error(f"Failed to initialize encryption: {str(e)}")
                raise SecurityException(
                    "Invalid encryption key format",
                    error_type="invalid_key"
                ) from e

    def encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt sensitive credentials.
        
        Args:
            credentials: Dictionary of credentials to encrypt
            
        Returns:
            Dictionary with encrypted credentials
            
        Raises:
            SecurityException: If encryption fails
        """
        if not self.encryption_key or not self.fernet:
            return credentials
            
        try:
            encrypted = {}
            for key, value in credentials.items():
                if isinstance(value, str):
                    encrypted_value = self.fernet.encrypt(value.encode()).decode()
                    encrypted[key] = encrypted_value
                else:
                    encrypted[key] = value
            return encrypted
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise SecurityException(
                "Failed to encrypt credentials",
                error_type="encryption_failed"
            )

    def decrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt encrypted credentials.
        
        Args:
            credentials: Dictionary of encrypted credentials
            
        Returns:
            Dictionary with decrypted credentials
            
        Raises:
            SecurityException: If decryption fails
        """
        if not self.encryption_key or not self.fernet:
            return credentials
            
        try:
            decrypted = {}
            for key, value in credentials.items():
                if isinstance(value, str):
                    try:
                        decrypted_value = self.fernet.decrypt(value.encode()).decode()
                        decrypted[key] = decrypted_value
                    except:
                        # If decryption fails, assume the value wasn't encrypted
                        decrypted[key] = value
                else:
                    decrypted[key] = value
            return decrypted
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise SecurityException(
                "Failed to decrypt credentials",
                error_type="decryption_failed"
            )

    @staticmethod
    def generate_encryption_key() -> str:
        """
        Generate a secure encryption key.
        
        Returns:
            str: Base64-encoded encryption key
        """
        return base64.urlsafe_b64encode(os.urandom(32)).decode()

    def rotate_encryption_key(self, new_key: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rotate encryption key and re-encrypt credentials.
        
        Args:
            new_key: New encryption key
            credentials: Currently encrypted credentials
            
        Returns:
            Dict: Credentials encrypted with the new key
            
        Raises:
            SecurityException: If rotation fails
        """
        if not self.encryption_key:
            self.encryption_key = new_key
            self.fernet = Fernet(new_key)
            return credentials
            
        try:
            # First decrypt with old key
            decrypted = self.decrypt_credentials(credentials)
            
            # Set up new key
            old_key = self.encryption_key
            self.encryption_key = new_key
            
            # Use more secure key derivation as in __init__
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            
            salt = b'amazon_paapi5_python_sdk'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(new_key.encode('utf-8')))
            
            self.fernet = Fernet(key)
            
            # Re-encrypt with new key
            return self.encrypt_credentials(decrypted)
        except Exception as e:
            # Restore old key in case of failure
            self.encryption_key = old_key if 'old_key' in locals() else None
            self.logger.error(f"Key rotation failed: {str(e)}")
            raise SecurityException(
                "Failed to rotate encryption key",
                error_type="key_rotation_failed"
            )