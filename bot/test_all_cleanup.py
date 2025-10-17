#!/usr/bin/env python3
"""
Test various problematic response patterns to ensure cleanup works
"""

import re

def extract_final_response(text: str) -> str:
    """Extract final response, removing thinking tags and technical data"""
    if not text:
        return ""
    
    # Remove thinking tags and their content (various formats)
    text = re.sub(r'<think>.*?</think>\s*', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<thinking>.*?</thinking>\s*', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove common thinking prefixes/patterns that models use
    text = re.sub(r'^(Okay|Alright|Let me think|First|So),?\s+let\'?s.*?\.\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\.depart[A-Z]\w+\s+', '', text)  # Remove .departOkay style prefixes
    text = re.sub(r'^[A-Z][a-z]+,?\s+let\'?s (try to |figure out|see).*?\.\s*', '', text, flags=re.IGNORECASE)
    
    # Remove lines that start with internal reasoning patterns
    text = re.sub(r'^.*?(I need to|I should|First,|Let me|The user).*?$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove JSON blocks
    text = re.sub(r'```json.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    
    # Remove specific technical patterns
    text = re.sub(r'rating:\s*\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'score:\s*\d+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\d+/10', '', text)
    
    # Remove JSON-like structures that span multiple lines
    text = re.sub(r'\{[^}]*\n[^}]*\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\[[^\]]*\n[^\]]*]', '', text, flags=re.DOTALL)
    
    # Remove any remaining markdown formatting
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Remove italic
    text = re.sub(r'`([^`]+)`', r'\1', text)      # Remove inline code
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)  # Remove headers
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)  # Remove numbered lists
    text = re.sub(r'^-\s*', '', text, flags=re.MULTILINE)   # Remove bullet points
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def additional_cleanup(response_text: str) -> str:
    """Additional cleanup layer"""
    thinking_starters = [
        r'^Okay,?\s+let\'?s try to figure out.*?\.?\s*',
        r'^Alright,?\s+let me see.*?\.?\s*',
        r'^Let me think about this.*?\.?\s*',
        r'^First,?\s+I need to.*?\.?\s*',
        r'^So,?\s+the user.*?\.?\s*',
        r'^\.depart\w+\s*',
        r'^They provided.*?\.?\s*',
        r'^The user might be.*?\.?\s*',
    ]
    
    for pattern in thinking_starters:
        response_text = re.sub(pattern, '', response_text, flags=re.IGNORECASE | re.DOTALL)
        if response_text:
            response_text = response_text.strip()
    
    # If response still starts with thinking-like content
    if response_text and any(word in response_text[:50].lower() for word in ['they', 'the user', 'provided', 'might be', 'looking for']):
        sentences = response_text.split('.')
        for i, sentence in enumerate(sentences):
            if any(emoji in sentence for emoji in ['🌙', '✨', '💫', '🌻', '💖', '🙏', '🌞', '🌿', '💕']) or \
               any(word in sentence.lower() for word in ['hey', 'hi there', 'lovely', 'beautiful']):
                response_text = '.'.join(sentences[i:]).strip()
                break
    
    return response_text

# Test cases
test_cases = [
    {
        "name": "Original problem",
        "input": ".departOkay, let's try to figure out what the user is asking for here. They provided a lot of data about a birth chart and monthly career summaries. The user might be looking for an analysis or interpretation of their birth chart and how it relates to their career in different months. First, I need to parse the data.",
        "expected": ""
    },
    {
        "name": "Thinking tags with good response",
        "input": "<think>User asked about career. Need to call career prediction.</think>\n\nHey! This is a great time for career growth 🌟 The stars are aligning for professional success. Trust your instincts! 💫",
        "expected": "Hey! This is a great time for career growth 🌟 The stars are aligning for professional success. Trust your instincts! 💫"
    },
    {
        "name": "Mixed thinking and response",
        "input": "First, I need to analyze this. The user wants career advice. Hey lovely! Your career sector is looking bright today ✨ Venus is bringing opportunities. Stay positive! 🌿",
        "expected": "Hey lovely! Your career sector is looking bright today ✨ Venus is bringing opportunities. Stay positive! 🌿"
    },
    {
        "name": "Technical data with ratings",
        "input": "Career rating: 8/10. Venus in 10th house (score: 7). Hey! Your career is on fire right now 🔥 Great things ahead! ✨",
        "expected": "Hey! Your career is on fire right now 🔥 Great things ahead! ✨"
    },
    {
        "name": "Just thinking, no response",
        "input": "Okay, let's see what the user wants. They are asking about career changes.",
        "expected": ""
    }
]

print("="*80)
print("RESPONSE CLEANUP TESTS")
print("="*80)

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. {test['name']}")
    print("-" * 80)
    print(f"Input: {test['input'][:100]}...")
    
    result = extract_final_response(test['input'])
    result = additional_cleanup(result)
    
    print(f"\nOutput: {result if result else '(empty)'}")
    print(f"Length: {len(result)} chars")
    
    if test['expected'] == "":
        status = "✅ PASS" if not result or len(result) < 20 else "❌ FAIL"
    else:
        status = "✅ PASS" if result.strip() == test['expected'].strip() else "❌ FAIL"
    
    print(f"Status: {status}")
    print("="*80)

print("\n✅ All cleanup mechanisms tested!")
