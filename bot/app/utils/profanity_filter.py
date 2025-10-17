"""Profanity detection and filtering"""
import re
from typing import Tuple

# Common profanity words and patterns (extend as needed)
PROFANITY_WORDS = {
    'fuck', 'fucking', 'fucker', 'fucked', 'fuk', 'fck',
    'shit', 'shitty', 'bullshit', 'bitch', 'bitches',
    'ass', 'asshole', 'bastard', 'damn', 'dammit',
    'hell', 'crap', 'dick', 'cock', 'pussy',
    'whore', 'slut', 'piss', 'pissed',
    'suck', 'sucks', 'sucked',  # Add these
    # Add more as needed
}

# Patterns to catch variations (l33t speak, spacing, etc.)
PROFANITY_PATTERNS = [
    r'f+u+c+k+',
    r'sh+i+t+',
    r'b+i+t+c+h+',
    r'a+s+s+h+o+l+e+',
    r'd+a+m+n+',
    r's+u+c+k+s?',  # Add this
]

def contains_profanity(text: str) -> Tuple[bool, str]:
    """
    Check if text contains profanity
    
    Returns:
        Tuple[bool, str]: (has_profanity, matched_word)
    """
    if not text:
        return False, ""
    
    # Normalize text
    text_lower = text.lower()
    
    # Remove common obfuscation
    text_normalized = text_lower.replace('*', '').replace('@', 'a').replace('$', 's')
    text_normalized = re.sub(r'\s+', '', text_normalized)  # Remove spaces
    
    # Check exact words
    words = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        if word in PROFANITY_WORDS:
            return True, word
    
    # Check patterns
    for pattern in PROFANITY_PATTERNS:
        if re.search(pattern, text_normalized):
            match = re.search(pattern, text_normalized)
            return True, match.group() if match else "profanity"
    
    return False, ""

def is_rude_or_aggressive(text: str) -> Tuple[bool, str]:
    """
    Detect rude or aggressive language beyond just profanity
    
    Returns:
        Tuple[bool, str]: (is_rude, reason)
    """
    if not text:
        return False, ""
    
    text_lower = text.lower()
    
    # Check profanity first
    has_profanity, word = contains_profanity(text)
    if has_profanity:
        return True, f"profanity: {word}"
    
    # Check aggressive patterns (removed 'suck' from here since it's in profanity)
    aggressive_patterns = [
        (r'\bshut up\b', "aggressive command"),
        (r'\bstupid\b', "insult"),
        (r'\bidiot\b', "insult"),
        (r'\buseless\b', "insult"),
        (r'\bdumb\b', "insult"),
        (r'\bworthless\b', "insult"),
        (r'\bgarbage\b', "insult"),
        (r'\btrash\b', "insult"),
    ]
    
    for pattern, reason in aggressive_patterns:
        if re.search(pattern, text_lower):
            return True, reason
    
    return False, ""