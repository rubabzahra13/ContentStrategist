# === FILE: utils/helpers.py ===
from rapidfuzz import process
import re
from datetime import datetime

def normalize_month(user_input):
    """
    Normalize month input like 'August 2025', 'Agust 2025', 'ajguzt' etc.
    Returns properly formatted string like 'August 2025'
    """
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Manual mapping for common typos
    typo_map = {
        "agust": "August", "ajguzt": "August", "auzhst": "August", "aughst": "August",
        "julu": "July", "sepember": "September", "ocober": "October",
        "novemer": "November", "decemer": "December", "febuary": "February"
    }
    
    # Extract year (default to current year if not found)
    year_match = re.search(r'\b(20\d{2})\b', user_input)
    year = year_match.group(1) if year_match else str(datetime.now().year)
    
    # Extract month part (remove year and clean)
    month_part = re.sub(r'\b(20\d{2})\b', '', user_input).strip()
    month_words = re.findall(r"[a-zA-Z]+", month_part)
    
    if not month_words:
        return f"January {year}"  # Default fallback
    
    # Try each word to find the best month match
    best_month = None
    best_score = 0
    
    for word in month_words:
        word_lower = word.lower()
        
        # Try manual typo mapping first
        if word_lower in typo_map:
            best_month = typo_map[word_lower]
            best_score = 100  # Perfect match
            break
        
        # Try fuzzy matching
        match, score, _ = process.extractOne(word_lower, [m.lower() for m in months])
        if score > best_score and score >= 50:  # Lowered threshold for better matching
            # Find the original case month name
            for month in months:
                if month.lower() == match:
                    best_month = month
                    best_score = score
                    break
    
    # Use best match or default to January
    normalized_month = best_month if best_month and best_score >= 50 else months[0]
    
    return f"{normalized_month} {year}"
