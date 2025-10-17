"""Test profanity filter"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.profanity_filter import contains_profanity, is_rude_or_aggressive

def test_profanity_detection():
    """Test profanity detection"""
    print("\n🧪 Testing Profanity Detection\n")
    
    test_cases = [
        # (text, should_detect, description)
        ("fuck you", True, "Direct profanity"),
        ("you're a bitch", True, "Direct profanity"),
        ("this is bullshit", True, "Direct profanity"),
        ("shut up stupid bot", True, "Aggressive language"),
        ("you're useless", True, "Insult"),
        ("this sucks", True, "Vulgar"),
        ("How is my day?", False, "Normal question"),
        ("Tell me about love", False, "Normal request"),
        ("Thank you so much!", False, "Polite message"),
        ("I'm frustrated with this", False, "Expression without profanity"),
    ]
    
    passed = 0
    failed = 0
    
    for text, should_detect, description in test_cases:
        is_rude, reason = is_rude_or_aggressive(text)
        
        if is_rude == should_detect:
            print(f"✅ PASS: {description}")
            print(f"   Text: '{text}'")
            if is_rude:
                print(f"   Detected: {reason}")
            passed += 1
        else:
            print(f"❌ FAIL: {description}")
            print(f"   Text: '{text}'")
            print(f"   Expected: {should_detect}, Got: {is_rude}")
            failed += 1
        print()
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0

def main():
    """Main entry point for test runner"""
    return test_profanity_detection()

if __name__ == "__main__":
    success = test_profanity_detection()
    sys.exit(0 if success else 1)