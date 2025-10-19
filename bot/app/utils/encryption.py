"""Chat encryption utilities using Fernet with compression"""
import logging
import zlib
from cryptography.fernet import Fernet, InvalidToken
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ChatEncryption:
    """Handle chat message encryption and decryption with compression"""
    
    def __init__(self):
        try:
            self.cipher = Fernet(settings.chat_encryption_key.encode())
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def encrypt(self, plaintext: str) -> str:
        """
        Compress and encrypt a message
        
        Args:
            plaintext: The message to encrypt
            
        Returns:
            Compressed and encrypted message as base64 string
        """
        try:
            if not plaintext:
                return ""
            
            # Compress first (level=9 for maximum compression)
            compressed = zlib.compress(plaintext.encode(), level=9)
            
            # Then encrypt the compressed data
            encrypted = self.cipher.encrypt(compressed)
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt and decompress a message
        
        Args:
            ciphertext: The encrypted message
            
        Returns:
            Decrypted and decompressed plaintext message
        """
        try:
            if not ciphertext:
                return ""
            
            # Decrypt first
            decrypted = self.cipher.decrypt(ciphertext.encode())
            
            # Then decompress
            try:
                decompressed = zlib.decompress(decrypted)
                return decompressed.decode()
            except zlib.error:
                # Backward compatibility: if decompression fails, 
                # assume it's an old uncompressed encrypted message
                logger.warning("Decompression failed - attempting to read as uncompressed")
                return decrypted.decode()
                
        except InvalidToken:
            logger.error("Invalid encryption token - message cannot be decrypted")
            return "[ENCRYPTED - Cannot decrypt]"
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return "[ENCRYPTED - Decryption error]"
    
    def is_encrypted(self, text: str) -> bool:
        """
        Check if text appears to be encrypted (Fernet format)
        
        Args:
            text: The text to check
            
        Returns:
            True if text appears encrypted
        """
        try:
            # Fernet tokens start with 'gAAAAA' when base64 encoded
            return text.startswith('gAAAAA') and len(text) > 50
        except:
            return False

# Global instance
_encryption = None

def get_encryption() -> ChatEncryption:
    """Get or create encryption instance"""
    global _encryption
    if _encryption is None:
        _encryption = ChatEncryption()
    return _encryption