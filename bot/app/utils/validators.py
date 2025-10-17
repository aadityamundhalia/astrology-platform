"""Validation utilities"""
import re

def validate_birth_data(date_str: str, time_str: str, place_str: str) -> bool:
    """Validate birth data format"""
    if not all([date_str, time_str, place_str]):
        return False
    
    if not re.match(r'\d{4}-\d{2}-\d{2}', str(date_str)):
        return False
    
    if not re.match(r'\d{2}:\d{2}', str(time_str)):
        return False
    
    if ',' not in str(place_str):
        return False
    
    return True