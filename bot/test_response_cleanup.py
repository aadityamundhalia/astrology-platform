#!/usr/bin/env python3
"""Test the response cleanup logic"""

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

# Test with your problematic output
test_input = """.departOkay, let's try to figure out what the user is asking for here. They provided a lot of data about a birth chart and monthly career summaries. The user might be looking for an analysis or interpretation of their birth chart and how it relates to their career in different months. First, I need to parse the data."""

print("Input:")
print(test_input)
print("\n" + "="*80 + "\n")

result = extract_final_response(test_input)
print("After cleanup:")
print(result)
print("\n" + "="*80 + "\n")

# Additional cleanup for thinking starters
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
    result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.DOTALL)
    if result:
        result = result.strip()

print("After additional thinking cleanup:")
print(result)
print("\nLength:", len(result))

# Test with thinking tags
test_input2 = """<think>
User asked about career change. I need to call the career prediction tool and analyze.
</think>

Hey! This is an exciting time for a career shift 🌟 The stars are showing positive energy around professional transitions, especially moves to more stable government positions. Your chart indicates growth potential and new opportunities opening up. Trust your instincts on this! 💫✨"""

print("\n" + "="*80 + "\n")
print("Test with thinking tags:")
print(test_input2)
print("\n" + "="*80 + "\n")

result2 = extract_final_response(test_input2)
print("After cleanup:")
print(result2)
