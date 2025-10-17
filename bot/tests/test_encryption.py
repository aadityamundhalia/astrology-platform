"""Test chat encryption functionality"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.encryption import ChatEncryption

def test_encryption():
    """Test encryption and decryption"""
    print("\n🔐 Testing Chat Encryption\n")
    
    encryption = ChatEncryption()
    
    test_messages = [
        "Hello, how are you?",
        "My birth details are sensitive!",
        "This is a longer message with more content to encrypt and see how it handles various lengths.",
        "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
        "Unicode: 你好世界 🌟✨🔮"
    ]
    
    passed = 0
    failed = 0
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: ", end="")
        
        try:
            # Encrypt
            encrypted = encryption.encrypt(message)
            
            # Check it's different
            if encrypted == message:
                print(f"❌ FAIL - Message not encrypted")
                print(f"   Original: {message[:50]}")
                failed += 1
                continue
            
            # Check it's base64-like
            if not encryption.is_encrypted(encrypted):
                print(f"❌ FAIL - Doesn't look encrypted")
                failed += 1
                continue
            
            # Decrypt
            decrypted = encryption.decrypt(encrypted)
            
            # Verify
            if decrypted == message:
                print(f"✅ PASS")
                print(f"   Original: {message[:50]}")
                print(f"   Encrypted: {encrypted[:60]}...")
                print(f"   Decrypted: {decrypted[:50]}")
                passed += 1
            else:
                print(f"❌ FAIL - Decryption mismatch")
                print(f"   Original: {message[:50]}")
                print(f"   Decrypted: {decrypted[:50]}")
                failed += 1
        except Exception as e:
            print(f"❌ FAIL - Exception: {e}")
            failed += 1
        
        print()
    
    print(f"📊 Results: {passed} passed, {failed} failed\n")
    return failed == 0

if __name__ == "__main__":
    success = test_encryption()
    sys.exit(0 if success else 1)