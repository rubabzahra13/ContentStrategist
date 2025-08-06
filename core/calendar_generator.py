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
    
    # If it's a large month, use gpt-3.5-turbo which is better at following instructions
    if days_in_month > 20:
        model = "gpt-3.5-turbo"
        max_tokens = 4000
    else:
        model = "gpt-4"
        max_tokens = 3500
    
    prompt = f"""
You are creating Instagram Reels calendar for AI entrepreneurs. Month: {month} ({days_in_month} days)

TRENDS: {', '.join(trends)}

OUTPUT FORMAT (use this EXACT format for ALL {days_in_month} days):
Day X | "Title" | Hook | Body | CTA | Format | Audio | Hashtags | Production | Optimization

RULES:
1. Generate ALL {days_in_month} days (Day 1 through Day {days_in_month})
2. NO shortcuts like "continue pattern" or "repeat format"
3. Each day must be unique content
4. Focus on AI tools, automation, business scaling

Generate Day 1 through Day {days_in_month} now:
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
