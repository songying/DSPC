"""
Homomorphic Encryption Module for Privacy Data Protocol

This module implements a simplified homomorphic encryption scheme for privacy-preserving
computation on browser history data. It uses the Paillier cryptosystem, which allows
for addition operations on encrypted data.

For a production system, more advanced libraries like Microsoft SEAL or HElib would be used.
"""

import random
import math
import json
from typing import Dict, List, Any, Tuple, Union, Optional
import numpy as np
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

class PaillierCrypto:
    """
    A simplified implementation of the Paillier cryptosystem for homomorphic encryption.
    
    This allows performing addition operations on encrypted data without decrypting it first.
    """
    
    def __init__(self, key_size: int = 1024):
        """Initialize the Paillier cryptosystem with a given key size."""
        self.key_size = key_size
        self.p, self.q = self._generate_primes(key_size // 2)
        self.n = self.p * self.q
        self.n_squared = self.n * self.n
        self.g = self.n + 1  # Simplification: g = n + 1 works and is efficient
        self.lambda_val = self._lcm(self.p - 1, self.q - 1)
        
        self.mu = self._mod_inverse(self._L(pow(self.g, self.lambda_val, self.n_squared), self.n), self.n)
    
    def _generate_primes(self, bits: int) -> Tuple[int, int]:
        """Generate two random prime numbers of the specified bit length."""
        key = RSA.generate(2 * bits)
        return key.p, key.q
    
    def _lcm(self, a: int, b: int) -> int:
        """Calculate the least common multiple of a and b."""
        return a * b // math.gcd(a, b)
    
    def _L(self, x: int, n: int) -> int:
        """L function for Paillier: L(x) = (x-1)/n."""
        return (x - 1) // n
    
    def _mod_inverse(self, a: int, m: int) -> int:
        """Calculate the modular multiplicative inverse of a modulo m."""
        g, x, y = self._extended_gcd(a, m)
        if g != 1:
            raise Exception('Modular inverse does not exist')
        else:
            return x % m
    
    def _extended_gcd(self, a: int, b: int) -> Tuple[int, int, int]:
        """Extended Euclidean Algorithm to find gcd and coefficients."""
        if a == 0:
            return b, 0, 1
        else:
            gcd, x, y = self._extended_gcd(b % a, a)
            return gcd, y - (b // a) * x, x
    
    def encrypt(self, plaintext: int) -> int:
        """
        Encrypt a plaintext message using the Paillier cryptosystem.
        
        Args:
            plaintext: Integer message to encrypt (must be < n)
            
        Returns:
            Encrypted ciphertext
        """
        if plaintext >= self.n:
            raise ValueError(f"Plaintext {plaintext} is too large for modulus {self.n}")
        
        r = random.randint(1, self.n - 1)
        while math.gcd(r, self.n) != 1:
            r = random.randint(1, self.n - 1)
        
        c = (pow(self.g, plaintext, self.n_squared) * pow(r, self.n, self.n_squared)) % self.n_squared
        return c
    
    def decrypt(self, ciphertext: int) -> int:
        """
        Decrypt a ciphertext message using the Paillier cryptosystem.
        
        Args:
            ciphertext: Encrypted message
            
        Returns:
            Decrypted plaintext
        """
        x = pow(ciphertext, self.lambda_val, self.n_squared)
        plaintext = (self._L(x, self.n) * self.mu) % self.n
        return plaintext
    
    def add_encrypted(self, ciphertext1: int, ciphertext2: int) -> int:
        """
        Add two encrypted values homomorphically.
        
        Args:
            ciphertext1: First encrypted value
            ciphertext2: Second encrypted value
            
        Returns:
            Encrypted sum
        """
        return (ciphertext1 * ciphertext2) % self.n_squared
    
    def add_constant(self, ciphertext: int, constant: int) -> int:
        """
        Add a constant to an encrypted value.
        
        Args:
            ciphertext: Encrypted value
            constant: Constant to add
            
        Returns:
            Encrypted result of the addition
        """
        return (ciphertext * pow(self.g, constant, self.n_squared)) % self.n_squared
    
    def multiply_constant(self, ciphertext: int, constant: int) -> int:
        """
        Multiply an encrypted value by a constant.
        
        Args:
            ciphertext: Encrypted value
            constant: Constant to multiply by
            
        Returns:
            Encrypted result of the multiplication
        """
        return pow(ciphertext, constant, self.n_squared)
    
    def get_public_key(self) -> Dict[str, int]:
        """Get the public key components."""
        return {
            "n": self.n,
            "g": self.g
        }
    
    def get_private_key(self) -> Dict[str, int]:
        """Get the private key components."""
        return {
            "lambda": self.lambda_val,
            "mu": self.mu
        }


class PrivacyPreservingAnalytics:
    """
    Implements privacy-preserving analytics on browser history data using
    homomorphic encryption.
    """
    
    def __init__(self, crypto: Optional[PaillierCrypto] = None):
        """
        Initialize the analytics engine with a cryptosystem.
        
        Args:
            crypto: Optional PaillierCrypto instance. If None, a new one will be created.
        """
        self.crypto = crypto if crypto is not None else PaillierCrypto()
        
        self.site_categories = {
            "short_video": [
                "tiktok.com", "youtube.com/shorts", "instagram.com/reels", 
                "snapchat.com", "vimeo.com/shorts", "triller.co", "byte.co",
                "dubsmash.com", "likee.com", "funimate.com"
            ],
            "ecommerce": [
                "amazon.com", "ebay.com", "walmart.com", "aliexpress.com", 
                "etsy.com", "shopify.com", "bestbuy.com", "target.com",
                "newegg.com", "wayfair.com", "overstock.com", "homedepot.com"
            ]
        }
    
    def encrypt_user_data(self, user_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Encrypt user browsing data for privacy-preserving analysis.
        
        Args:
            user_data: List of browsing events for a user
            
        Returns:
            Dictionary with encrypted analytics data
        """
        total_visits = len(user_data)
        short_video_visits = 0
        ecommerce_visits = 0
        ecommerce_after_video = 0
        
        last_was_video = False
        
        for i, event in enumerate(user_data):
            site = event["site"]
            
            is_video = any(video_site in site for video_site in self.site_categories["short_video"])
            if is_video:
                short_video_visits += 1
                last_was_video = True
            
            is_ecommerce = any(ecomm_site in site for ecomm_site in self.site_categories["ecommerce"])
            if is_ecommerce:
                ecommerce_visits += 1
                
                if last_was_video:
                    ecommerce_after_video += 1
            
            if not is_video:
                last_was_video = False
        
        encrypted_total = self.crypto.encrypt(total_visits)
        encrypted_video = self.crypto.encrypt(short_video_visits)
        encrypted_ecommerce = self.crypto.encrypt(ecommerce_visits)
        encrypted_ecommerce_after_video = self.crypto.encrypt(ecommerce_after_video)
        
        return {
            "encrypted_total_visits": encrypted_total,
            "encrypted_short_video_visits": encrypted_video,
            "encrypted_ecommerce_visits": encrypted_ecommerce,
            "encrypted_ecommerce_after_video": encrypted_ecommerce_after_video
        }
    
    def aggregate_encrypted_data(self, encrypted_user_data: List[Dict[str, int]]) -> Dict[str, int]:
        """
        Aggregate encrypted data from multiple users.
        
        Args:
            encrypted_user_data: List of encrypted data from multiple users
            
        Returns:
            Dictionary with aggregated encrypted data
        """
        if not encrypted_user_data:
            return {}
        
        aggregated = {
            "encrypted_total_visits": encrypted_user_data[0]["encrypted_total_visits"],
            "encrypted_short_video_visits": encrypted_user_data[0]["encrypted_short_video_visits"],
            "encrypted_ecommerce_visits": encrypted_user_data[0]["encrypted_ecommerce_visits"],
            "encrypted_ecommerce_after_video": encrypted_user_data[0]["encrypted_ecommerce_after_video"]
        }
        
        for user_data in encrypted_user_data[1:]:
            aggregated["encrypted_total_visits"] = self.crypto.add_encrypted(
                aggregated["encrypted_total_visits"], 
                user_data["encrypted_total_visits"]
            )
            
            aggregated["encrypted_short_video_visits"] = self.crypto.add_encrypted(
                aggregated["encrypted_short_video_visits"], 
                user_data["encrypted_short_video_visits"]
            )
            
            aggregated["encrypted_ecommerce_visits"] = self.crypto.add_encrypted(
                aggregated["encrypted_ecommerce_visits"], 
                user_data["encrypted_ecommerce_visits"]
            )
            
            aggregated["encrypted_ecommerce_after_video"] = self.crypto.add_encrypted(
                aggregated["encrypted_ecommerce_after_video"], 
                user_data["encrypted_ecommerce_after_video"]
            )
        
        return aggregated
    
    def decrypt_and_analyze(self, aggregated_data: Dict[str, int]) -> Dict[str, Union[int, float]]:
        """
        Decrypt aggregated data and compute analytics.
        
        Args:
            aggregated_data: Dictionary with aggregated encrypted data
            
        Returns:
            Dictionary with decrypted analytics results
        """
        total_visits = self.crypto.decrypt(aggregated_data["encrypted_total_visits"])
        short_video_visits = self.crypto.decrypt(aggregated_data["encrypted_short_video_visits"])
        ecommerce_visits = self.crypto.decrypt(aggregated_data["encrypted_ecommerce_visits"])
        ecommerce_after_video = self.crypto.decrypt(aggregated_data["encrypted_ecommerce_after_video"])
        
        short_video_percentage = (short_video_visits / total_visits * 100) if total_visits > 0 else 0
        ecommerce_after_video_percentage = (ecommerce_after_video / short_video_visits * 100) if short_video_visits > 0 else 0
        
        return {
            "total_visits": total_visits,
            "short_video_visits": short_video_visits,
            "ecommerce_visits": ecommerce_visits,
            "ecommerce_after_video": ecommerce_after_video,
            "short_video_percentage": short_video_percentage,
            "ecommerce_after_video_percentage": ecommerce_after_video_percentage
        }


class PrivacyPreservingComputation:
    """
    Implements privacy-preserving computation on browser history data.
    """
    
    def __init__(self, dataset_path: str = "browser_history_test_dataset.json"):
        """
        Initialize the computation engine with a dataset.
        
        Args:
            dataset_path: Path to the dataset metadata file
        """
        self.dataset_path = dataset_path
        self.crypto = PaillierCrypto()
        self.analytics = PrivacyPreservingAnalytics(self.crypto)
        
        with open(dataset_path, 'r') as f:
            self.dataset_metadata = json.load(f)
    
    def analyze_short_video_preference(self, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Analyze what percentage of users primarily view short videos.
        
        Args:
            sample_size: Number of users to sample for analysis
            
        Returns:
            Dictionary with analysis results
        """
        print(f"Analyzing short video preference for {sample_size} users...")
        
        all_user_ids = list(self.dataset_metadata["users"].keys())
        sample_user_ids = random.sample(all_user_ids, min(sample_size, len(all_user_ids)))
        
        encrypted_user_data = []
        users_primarily_video = 0
        
        for user_id in sample_user_ids:
            user_metadata = self.dataset_metadata["users"][user_id]
            
            with open(user_metadata["data_file"], 'r') as f:
                user_data = json.load(f)
            
            encrypted_data = self.analytics.encrypt_user_data(user_data)
            encrypted_user_data.append(encrypted_data)
            
            total_visits = len(user_data)
            short_video_visits = sum(1 for event in user_data 
                                    if any(video_site in event["site"] 
                                          for video_site in self.analytics.site_categories["short_video"]))
            
            if short_video_visits / total_visits > 0.5:
                users_primarily_video += 1
        
        aggregated_data = self.analytics.aggregate_encrypted_data(encrypted_user_data)
        
        results = self.analytics.decrypt_and_analyze(aggregated_data)
        
        results["users_sampled"] = len(sample_user_ids)
        results["users_primarily_video"] = users_primarily_video
        results["users_primarily_video_percentage"] = users_primarily_video / len(sample_user_ids) * 100
        
        return results
    
    def analyze_ecommerce_after_video(self, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Analyze what percentage of users visit e-commerce platforms after viewing short videos.
        
        Args:
            sample_size: Number of users to sample for analysis
            
        Returns:
            Dictionary with analysis results
        """
        print(f"Analyzing e-commerce after video behavior for {sample_size} users...")
        
        all_user_ids = list(self.dataset_metadata["users"].keys())
        sample_user_ids = random.sample(all_user_ids, min(sample_size, len(all_user_ids)))
        
        encrypted_user_data = []
        users_with_pattern = 0
        
        for user_id in sample_user_ids:
            user_metadata = self.dataset_metadata["users"][user_id]
            
            with open(user_metadata["data_file"], 'r') as f:
                user_data = json.load(f)
            
            encrypted_data = self.analytics.encrypt_user_data(user_data)
            encrypted_user_data.append(encrypted_data)
            
            has_pattern = False
            last_was_video = False
            
            for event in user_data:
                site = event["site"]
                
                is_video = any(video_site in site for video_site in self.analytics.site_categories["short_video"])
                
                is_ecommerce = any(ecomm_site in site for ecomm_site in self.analytics.site_categories["ecommerce"])
                
                if last_was_video and is_ecommerce:
                    has_pattern = True
                    break
                
                last_was_video = is_video
            
            if has_pattern:
                users_with_pattern += 1
        
        aggregated_data = self.analytics.aggregate_encrypted_data(encrypted_user_data)
        
        results = self.analytics.decrypt_and_analyze(aggregated_data)
        
        results["users_sampled"] = len(sample_user_ids)
        results["users_with_pattern"] = users_with_pattern
        results["users_with_pattern_percentage"] = users_with_pattern / len(sample_user_ids) * 100
        
        return results
    
    def run_full_analysis(self, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Run a complete analysis on the dataset.
        
        Args:
            sample_size: Number of users to sample for analysis
            
        Returns:
            Dictionary with all analysis results
        """
        try:
            with open(self.dataset_path, 'r') as f:
                pass
        except FileNotFoundError:
            print("Dataset not found. Generating a small test dataset...")
            from data_generator import generate_small_test_dataset
            generate_small_test_dataset(num_users=sample_size, events_per_user=1000)
            
            with open(self.dataset_path, 'r') as f:
                self.dataset_metadata = json.load(f)
        
        video_results = self.analyze_short_video_preference(sample_size)
        ecommerce_results = self.analyze_ecommerce_after_video(sample_size)
        
        return {
            "short_video_analysis": video_results,
            "ecommerce_after_video_analysis": ecommerce_results,
            "dataset_info": {
                "total_users": len(self.dataset_metadata["users"]),
                "sampled_users": sample_size,
                "date_range": self.dataset_metadata["metadata"]["date_range"]
            }
        }


if __name__ == "__main__":
    computation = PrivacyPreservingComputation()
    results = computation.run_full_analysis(sample_size=100)
    
    print("\nAnalysis Results:")
    print(f"Dataset: {results['dataset_info']['total_users']} users, sampled {results['dataset_info']['sampled_users']}")
    print(f"Date range: {results['dataset_info']['date_range']}")
    
    print("\nShort Video Analysis:")
    video_results = results["short_video_analysis"]
    print(f"Total visits: {video_results['total_visits']}")
    print(f"Short video visits: {video_results['short_video_visits']} ({video_results['short_video_percentage']:.2f}%)")
    print(f"Users primarily viewing short videos: {video_results['users_primarily_video']} ({video_results['users_primarily_video_percentage']:.2f}%)")
    
    print("\nE-commerce After Video Analysis:")
    ecommerce_results = results["ecommerce_after_video_analysis"]
    print(f"Short video visits: {ecommerce_results['short_video_visits']}")
    print(f"E-commerce visits after videos: {ecommerce_results['ecommerce_after_video']} ({ecommerce_results['ecommerce_after_video_percentage']:.2f}%)")
    print(f"Users with video-to-ecommerce pattern: {ecommerce_results['users_with_pattern']} ({ecommerce_results['users_with_pattern_percentage']:.2f}%)")
