"""
Encryption utilities for securely storing sensitive data like OAuth tokens
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def get_encryption_key() -> bytes:
    """
    Get or generate the encryption key for token storage
    Uses environment variable or generates a key (for development)
    """
    key_env = os.getenv('ENCRYPTION_KEY')

    if key_env:
        # Use provided key
        return base64.urlsafe_b64decode(key_env)
    else:
        # Generate key from a password (for development only)
        # In production, always use ENCRYPTION_KEY environment variable
        password = os.getenv('ENCRYPTION_PASSWORD', 'dev_default_password_change_in_production')
        salt = b'unitasa_social_tokens_salt'

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key


def encrypt_data(data: str) -> str:
    """
    Encrypt sensitive data (like OAuth tokens)

    Args:
        data: The string data to encrypt

    Returns:
        Base64 encoded encrypted data
    """
    if not data:
        return ""

    key = get_encryption_key()
    f = Fernet(key)

    # Encrypt the data
    encrypted_data = f.encrypt(data.encode())

    # Return as base64 string for database storage
    return base64.urlsafe_b64encode(encrypted_data).decode()


def decrypt_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data

    Args:
        encrypted_data: Base64 encoded encrypted data

    Returns:
        Decrypted string data
    """
    if not encrypted_data:
        return ""

    key = get_encryption_key()
    f = Fernet(key)

    try:
        # Decode from base64 and decrypt
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
        decrypted_bytes = f.decrypt(encrypted_bytes)

        return decrypted_bytes.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt data: {e}")


def hash_token(token: str) -> str:
    """
    Create a hash of a token for comparison purposes
    (without storing the actual token)

    Args:
        token: The token to hash

    Returns:
        SHA256 hash of the token
    """
    return hashlib.sha256(token.encode()).hexdigest()


# Test functions
def test_encryption():
    """Test encryption/decryption functions"""
    test_data = "test_oauth_token_12345"

    # Test encryption
    encrypted = encrypt_data(test_data)
    print(f"Original: {test_data}")
    print(f"Encrypted: {encrypted}")

    # Test decryption
    decrypted = decrypt_data(encrypted)
    print(f"Decrypted: {decrypted}")

    # Verify
    assert decrypted == test_data, "Encryption/decryption failed"
    print("✓ Encryption test passed")


if __name__ == "__main__":
    test_encryption()