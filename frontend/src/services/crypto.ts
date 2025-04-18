/**
 * Frontend Crypto Service
 * 
 * This service provides cryptographic functions for the frontend application,
 * including encryption, decryption, and key generation.
 */


class CryptoService {
  /**
   * Generate a random encryption key
   * @returns A random encryption key as a string
   */
  generateKey(): string {
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * Encrypt data using the provided key
   * @param data The data to encrypt (string or ArrayBuffer)
   * @param key The encryption key
   * @returns The encrypted data as a string or ArrayBuffer
   */
  encryptData(data: string | ArrayBuffer, key: string): string | ArrayBuffer {
    if (data instanceof ArrayBuffer) {
      const dataView = new Uint8Array(data);
      const keyBytes = new TextEncoder().encode(key);
      const result = new Uint8Array(dataView.length);
      
      for (let i = 0; i < dataView.length; i++) {
        result[i] = dataView[i] ^ keyBytes[i % keyBytes.length];
      }
      
      return result.buffer;
    }
    
    const dataChars = data.split('').map(char => char.charCodeAt(0));
    
    const keyChars: number[] = [];
    for (let i = 0; i < dataChars.length; i++) {
      keyChars.push(key.charCodeAt(i % key.length));
    }
    
    const encryptedChars = dataChars.map((char, i) => char ^ keyChars[i]);
    
    return btoa(String.fromCharCode(...encryptedChars));
  }

  /**
   * Decrypt data using the provided key
   * @param encryptedData The encrypted data as a string
   * @param key The encryption key
   * @returns The decrypted data as a string
   */
  decryptData(encryptedData: string, key: string): string {
    try {
      const encryptedChars = atob(encryptedData).split('').map(char => char.charCodeAt(0));
      
      const keyChars: number[] = [];
      for (let i = 0; i < encryptedChars.length; i++) {
        keyChars.push(key.charCodeAt(i % key.length));
      }
      
      const decryptedChars = encryptedChars.map((char, i) => char ^ keyChars[i]);
      
      return String.fromCharCode(...decryptedChars);
    } catch (error) {
      console.error('Error decrypting data:', error);
      return '';
    }
  }

  /**
   * Hash data using SHA-256
   * @param data The data to hash
   * @returns A promise that resolves to the hash as a hex string
   */
  async hashData(data: string): Promise<string> {
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }
}

export const crypto_service = new CryptoService();
