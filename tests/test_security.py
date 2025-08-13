import unittest
from trading_bot.utils.security import generate_key, encrypt_message, decrypt_message

class TestSecurity(unittest.TestCase):
    """
    Tests for the security utility functions.
    """

    def test_encryption_decryption_cycle(self):
        """
        Tests that a message can be encrypted and then decrypted back to its original form.
        """
        # 1. Generate a key
        key = generate_key()

        # 2. Define a sample message
        original_message = "This is a very secret API key: 12345-abcde"

        # 3. Encrypt the message
        encrypted_message = encrypt_message(original_message, key)

        # Ensure the encrypted message is not the same as the original
        self.assertNotEqual(original_message.encode(), encrypted_message)

        # 4. Decrypt the message
        decrypted_message = decrypt_message(encrypted_message, key)

        # 5. Assert that the decrypted message matches the original
        self.assertEqual(original_message, decrypted_message)

    def test_type_errors(self):
        """
        Tests that the functions raise TypeErrors for incorrect input types.
        """
        key = generate_key()
        with self.assertRaises(TypeError):
            encrypt_message(b"this is bytes", key) # Should be string

        with self.assertRaises(TypeError):
            decrypt_message("this is a string", key) # Should be bytes

if __name__ == '__main__':
    unittest.main()
