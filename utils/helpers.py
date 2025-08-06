
from rapidfuzz import process
import re
from datetime import datetime

def normalize_month(month_input):
    """
    Normalize month input to a standardized format
    
    Args:
        month_input (str): User input for month (e.g., "jan", "January 2024", "01/2024")
    
    Returns:
        str: Normalized month in format "Month YYYY" (e.g., "January 2024")
    """
    if not month_input or not isinstance(month_input, str):
        current_date = datetime.now()
        return f"{current_date.strftime('%B')} {current_date.year}"
    
    month_input = month_input.strip()
    current_year = datetime.now().year
    
    # Month names for fuzzy matching
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Pattern 1: "Month YYYY" or "Month" 
    month_year_pattern = r'^([a-zA-Z]+)\s*(\d{4})?$'
    match = re.match(month_year_pattern, month_input)
    if match:
        month_part = match.group(1)
        year_part = match.group(2) if match.group(2) else str(current_year)
        
        # Fuzzy match the month
        best_match = process.extractOne(month_part.capitalize(), month_names)
        if best_match and best_match[1] >= 60:  # 60% similarity threshold
            return f"{best_match[0]} {year_part}"
    
    # Pattern 2: "MM/YYYY" or "MM-YYYY"
    numeric_pattern = r'^(\d{1,2})[\/\-](\d{4})$'
    match = re.match(numeric_pattern, month_input)
    if match:
        month_num = int(match.group(1))
        year_part = match.group(2)
        if 1 <= month_num <= 12:
            return f"{month_names[month_num - 1]} {year_part}"
    
    # Pattern 3: Just numbers (assume current year)
    if month_input.isdigit():
        month_num = int(month_input)
        if 1 <= month_num <= 12:
            return f"{month_names[month_num - 1]} {current_year}"
    
    # Fallback: try fuzzy matching with current year
    best_match = process.extractOne(month_input.capitalize(), month_names)
    if best_match and best_match[1] >= 50:
        return f"{best_match[0]} {current_year}"
    
    # Final fallback: current month and year
    current_date = datetime.now()
    return f"{current_date.strftime('%B')} {current_date.year}"
