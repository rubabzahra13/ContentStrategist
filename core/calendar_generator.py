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
    print(f"📅 Requesting {days_in_month} days of content for {month}")
    
    prompt = f"""
Generate EXACTLY {days_in_month} content entries for {month}.

TRENDS: {chr(10).join(trends[:3])}

FORMAT - Each line: Day X | Title | Hook | Body | CTA | Format | Audio | Hashtags | Production | Optimization

EXAMPLE:
Day 1 | "3 AI Tools Replacing $50K Employees" | If you're not using these 3 AI tools, you're losing $10K monthly | Tool 1: ChatGPT saves 15 hours weekly. Tool 2: Claude manages campaigns. Tool 3: Notion AI automates reporting. | Which tool will you implement first? Comment below! | Face-to-cam + screen demo | Trending tech beat | #AItools #entrepreneur #businessgrowth | Bold text overlays, quick transitions | Hook within first 2 seconds

REQUIREMENTS:
1. Generate EXACTLY {days_in_month} entries (Day 1 to Day {days_in_month})
2. Each entry on its own line with 10 sections separated by " | "
3. No headers or extra formatting

THEMES: AI tools, business scaling, viral content, marketing, entrepreneurship

Generate {days_in_month} entries now:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=8000
        )

        calendar_text = response.choices[0].message.content.strip()

        # Validate response has content and proper format
        if not calendar_text:
            raise ValueError("❌ OpenAI returned empty response")
            
        # Check if it has the expected format
        lines_with_pipes = [line for line in calendar_text.split('\n') if '|' in line and line.startswith('Day ')]
        
        print(f"🔍 Generated {len(lines_with_pipes)} content rows (expected {days_in_month})")
        
        # If we didn't get enough content, try to supplement it
        if len(lines_with_pipes) < days_in_month - 2:  # Allow minimal tolerance
            print(f"⚠️ Insufficient content: Expected {days_in_month} rows, got {len(lines_with_pipes)}")
            print("🔄 Attempting to generate missing days...")
            
            missing_days = days_in_month - len(lines_with_pipes)
            start_day = len(lines_with_pipes) + 1
            
            # Generate additional content for missing days
            supplement_prompt = f"""
Generate EXACTLY {missing_days} more content entries starting from Day {start_day} to Day {days_in_month}.

Follow this EXACT format for each line:
Day X | Reel Title | Hook Script | Body Script | Close/CTA | Format | Audio | Hashtags | Production | Optimization

Generate entries for days {start_day} through {days_in_month}:
"""
            
            try:
                supplement_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": supplement_prompt}],
                    temperature=0.7,
                    max_tokens=4000
                )
                
                supplement_text = supplement_response.choices[0].message.content.strip()
                supplement_lines = [line for line in supplement_text.split('\n') if line.startswith('Day ')]
                
                if supplement_lines:
                    calendar_text += "\n" + "\n".join(supplement_lines)
                    lines_with_pipes = [line for line in calendar_text.split('\n') if '|' in line and line.startswith('Day ')]
                    print(f"✅ Supplemented content. Total rows now: {len(lines_with_pipes)}")
                
            except Exception as supplement_error:
                print(f"⚠️ Could not supplement content: {supplement_error}")
        
        return calendar_text
        
    except Exception as e:
        raise ValueError(f"❌ Error generating calendar: {str(e)}")
