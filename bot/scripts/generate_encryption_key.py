"""Generate encryption key for chat encryption"""
from cryptography.fernet import Fernet

def generate_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    print("\n" + "="*60)
    print("Chat Encryption Key Generated")
    print("="*60)
    print("\nAdd this to your .env file:")
    print(f"\nCHAT_ENCRYPTION_KEY={key.decode()}")
    print("\n⚠️  IMPORTANT: Keep this key secret and safe!")
    print("⚠️  If you lose this key, encrypted chats cannot be recovered!")
    print("="*60 + "\n")
    return key.decode()

if __name__ == "__main__":
    generate_key()