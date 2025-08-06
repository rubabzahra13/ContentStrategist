# === FILE: core/calendar_generator.py ===
from openai import OpenAI
from utils.config import OPENAI_API_KEY
import calendar
import re

client = OpenAI(api_key=OPENAI_API_KEY)

def get_days_in_month(month_year_str):
    """Extract month and year, return number of days in that month"""
    try:
        # Extract month name and year
        parts = month_year_str.split()
        month_name = parts[0]
        year = int(parts[1]) if len(parts) > 1 else 2024
        
        # Convert month name to number
        month_names = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        month_num = month_names.get(month_name, 1)
        return calendar.monthrange(year, month_num)[1]
    except:
        return 30  # Default fallback

def generate_calendar(trends, month):
    """Generate content calendar with proper day count for the month"""
    
    if not trends:
        trends = ["AI tools for entrepreneurs", "business scaling strategies", "viral content formats"]
    
    # Get correct number of days for the month
    days_in_month = get_days_in_month(month)
    
    # Use conservative token limits to stay well under 8192 total
    if days_in_month > 20:
        model = "gpt-3.5-turbo"
        max_tokens = 2800  # Much safer limit
    else:
        model = "gpt-4"
        max_tokens = 2500  # Conservative for smaller months
    
    prompt = f"""
Create {days_in_month} Instagram Reels for AI entrepreneurs ({month}).

Trends: {', '.join(trends[:3])}

Format: Day X | "Title" | Hook | Body | CTA | Format | Audio | Hashtags | Production | Optimization

Generate ALL {days_in_month} days (no shortcuts). Topics: AI tools, automation, scaling.
"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=max_tokens
        )

        calendar_text = response.choices[0].message.content.strip()

        # Validate response has content and proper format
        if not calendar_text:
            raise ValueError("❌ OpenAI returned empty response")
            
        # Check if it has the expected format
        lines_with_pipes = [line for line in calendar_text.split('\n') if '|' in line and 'Day ' in line]
        
        print(f"📊 Generated {len(lines_with_pipes)} content rows for {days_in_month}-day month")
        
        if len(lines_with_pipes) < days_in_month - 5:  # Allow some tolerance
            print(f"⚠️ Warning: Expected ~{days_in_month} content rows, got {len(lines_with_pipes)}")
        
        return calendar_text
        
    except Exception as e:
        raise ValueError(f"❌ Error generating calendar: {str(e)}")
