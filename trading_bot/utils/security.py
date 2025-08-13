import os
from cryptography.fernet import Fernet

# It is recommended to store this key in a secure location,
# for example, as an environment variable or using a secret management service.
# For this project, we will assume it's loaded from a config file or env variable.
# A new key can be generated using generate_key() and should be saved securely.

def generate_key() -> bytes:
    """
    Generates a new Fernet key for encryption.
    This key must be kept secret and secure.
    """
    return Fernet.generate_key()

def encrypt_message(message: str, key: bytes) -> bytes:
    """
    Encrypts a message using the provided key.
    The message is first encoded to bytes.
    """
    if not isinstance(message, str):
        raise TypeError("Message must be a string.")
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode('utf-8'))
    return encrypted_message

def decrypt_message(encrypted_message: bytes, key: bytes) -> str:
    """
    Decrypts an encrypted message using the provided key.
    The decrypted message is returned as a string.
    """
    if not isinstance(encrypted_message, bytes):
        raise TypeError("Encrypted message must be bytes.")
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message.decode('utf-8')

if __name__ == '__main__':
    # Example usage:
    # 1. Generate a key. In a real application, you would do this once
    #    and store the key securely.
    secret_key = generate_key()
    print(f"Generated Secret Key: {secret_key.decode()}")
    print("-" * 30)

    # 2. The data you want to protect (e.g., a broker API secret)
    api_secret = "my_super_secret_api_token_12345"
    print(f"Original API Secret: {api_secret}")
    print("-" * 30)

    # 3. Encrypt the data
    encrypted_secret = encrypt_message(api_secret, secret_key)
    print(f"Encrypted Secret: {encrypted_secret}")
    print("-" * 30)

    # 4. Decrypt the data
    decrypted_secret = decrypt_message(encrypted_secret, secret_key)
    print(f"Decrypted Secret: {decrypted_secret}")
    print("-" * 30)

    # Verification
    assert api_secret == decrypted_secret
    print("✅ Encryption and decryption successful.")
