from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib
import json
from typing import List, Dict, Any, Tuple

class CryptoService:
    def __init__(self):
        self.key_size = 32  # 256 bits
        self.block_size = 16  # 128 bits
    
    def generate_key(self) -> str:
        """Generate a random encryption key"""
        key = get_random_bytes(self.key_size)
        return base64.b64encode(key).decode('utf-8')
    
    def encrypt_data(self, data: str, key: str) -> str:
        """Encrypt data using AES-256"""
        try:
            key_bytes = base64.b64decode(key)
            
            iv = get_random_bytes(self.block_size)
            
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
            
            data_bytes = data.encode('utf-8')
            padded_data = pad(data_bytes, self.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            result = iv + encrypted_data
            
            return base64.b64encode(result).decode('utf-8')
        except Exception as e:
            print(f"Encryption error: {e}")
            return ""
    
    def decrypt_data(self, encrypted_data: str, key: str) -> str:
        """Decrypt data using AES-256"""
        try:
            key_bytes = base64.b64decode(key)
            data_bytes = base64.b64decode(encrypted_data)
            
            iv = data_bytes[:self.block_size]
            ciphertext = data_bytes[self.block_size:]
            
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
            
            decrypted_data = cipher.decrypt(ciphertext)
            unpadded_data = unpad(decrypted_data, self.block_size)
            
            return unpadded_data.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""
    
    def hash_data(self, data: str) -> str:
        """Create a hash of data"""
        data_bytes = data.encode('utf-8')
        hash_obj = hashlib.sha256(data_bytes)
        return hash_obj.hexdigest()
    
    def create_shares(self, secret: str, n: int, k: int) -> List[Tuple[int, bytes]]:
        """Split a secret into n shares, requiring k shares to reconstruct"""
        try:
            secret_bytes = secret.encode('utf-8')
            shares = Shamir.split(k, n, secret_bytes)
            return shares
        except Exception as e:
            print(f"Error creating shares: {e}")
            return []
    
    def combine_shares(self, shares: List[Tuple[int, bytes]]) -> str:
        """Combine shares to reconstruct the secret"""
        try:
            secret_bytes = Shamir.combine(shares)
            return secret_bytes.decode('utf-8')
        except Exception as e:
            print(f"Error combining shares: {e}")
            return ""
    
    def homomorphic_add(self, encrypted_values: List[str], key: str) -> str:
        """
        Simulate homomorphic addition for the prototype
        
        Note: This is a simplified simulation for the prototype.
        Real homomorphic encryption would use libraries like SEAL or HElib.
        """
        try:
            values = [float(self.decrypt_data(enc_val, key)) for enc_val in encrypted_values]
            
            result = sum(values)
            
            return self.encrypt_data(str(result), key)
        except Exception as e:
            print(f"Homomorphic addition error: {e}")
            return ""
    
    def homomorphic_multiply(self, encrypted_value: str, scalar: float, key: str) -> str:
        """
        Simulate homomorphic multiplication for the prototype
        
        Note: This is a simplified simulation for the prototype.
        Real homomorphic encryption would use libraries like SEAL or HElib.
        """
        try:
            value = float(self.decrypt_data(encrypted_value, key))
            
            result = value * scalar
            
            return self.encrypt_data(str(result), key)
        except Exception as e:
            print(f"Homomorphic multiplication error: {e}")
            return ""

crypto_service = CryptoService()
