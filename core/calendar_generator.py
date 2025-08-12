
from openai import OpenAI
from utils.config import OPENAI_API_KEY
import calendar
import re
from pathlib import Path
import json

# Import transcript analysis functionality
try:
    from core.transcript_analyzer import TranscriptAnalyzer
    TRANSCRIPT_ANALYSIS_AVAILABLE = True
except ImportError:
    TRANSCRIPT_ANALYSIS_AVAILABLE = False

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

def get_transcript_insights():
    """Get insights from analyzed video transcripts"""
    if not TRANSCRIPT_ANALYSIS_AVAILABLE:
        return None
    
    try:
        analyzer = TranscriptAnalyzer()
        insights = analyzer.load_insights()
        
        if insights and insights.get("individual_analyses"):
            return {
                "avg_word_count": int(insights.get("averages", {}).get("word_count", 50)),
                "avg_hook_length": int(insights.get("averages", {}).get("hook_length", 8)),
                "common_phrases": [p[0] for p in insights.get("patterns", {}).get("common_bigrams", [])[:10]],
                "engagement_patterns": insights.get("averages", {}).get("engagement_score", 1),
                "template": analyzer.generate_transcript_template(insights)
            }
    except Exception as e:
        print(f"⚠️ Could not load transcript insights: {e}")
    
    return None

def generate_calendar(trends, month, include_transcripts=True):
    """Generate content calendar with proper day count for the month and optional transcripts"""
    
    if not trends:
        trends = ["AI tools for entrepreneurs", "business scaling strategies", "viral content formats"]
    
    # Get correct number of days for the month
    days_in_month = get_days_in_month(month)
    print(f"📅 Requesting {days_in_month} days of content for {month}")
    
    # Get transcript insights for better content generation
    transcript_insights = get_transcript_insights() if include_transcripts else None
    
    # Use conservative token limits to stay well under 8192 total
    if days_in_month > 20:
        model = "gpt-3.5-turbo"
        max_tokens = 2800  # Much safer limit
    else:
        model = "gpt-4"
        max_tokens = 2500  # Conservative for smaller months
    
    # Enhanced prompt with transcript insights
    base_format = "Day X | \"Title\" | Hook | Body | CTA | Format | Audio | Hashtags | Production | Optimization"
    
    if include_transcripts and transcript_insights:
        # Include transcript column and insights
        enhanced_format = base_format + " | Transcript"
        
        common_phrases_text = ", ".join(transcript_insights["common_phrases"][:5]) if transcript_insights["common_phrases"] else "use engaging language"
        
        prompt = f"""Create {days_in_month} Instagram Reels for AI entrepreneurs ({month}).

Trends: {', '.join(trends[:3])}

TRANSCRIPT INSIGHTS (based on successful reels analysis):
- Average script length: ~{transcript_insights["avg_word_count"]} words
- Hook length: ~{transcript_insights["avg_hook_length"]} words
- Successful phrases: {common_phrases_text}

Format: {enhanced_format}

For the Transcript column, create engaging 25-30 second scripts following this structure:
- Hook (0-3s): {transcript_insights["avg_hook_length"]} words max - grab attention immediately
- Body (3-20s): Main value/insight - conversational tone
- CTA (20-30s): Clear call-to-action for engagement

Generate ALL {days_in_month} days (no shortcuts). Topics: AI tools, automation, scaling."""
    else:
        # Standard prompt without transcripts
        prompt = f"""Create {days_in_month} Instagram Reels for AI entrepreneurs ({month}).

Trends: {', '.join(trends[:3])}

Format: {base_format}

Generate ALL {days_in_month} days (no shortcuts). Topics: AI tools, automation, scaling."""

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
        
        # If we didn't get enough content, try to supplement it
        if len(lines_with_pipes) < days_in_month - 2:  # Allow minimal tolerance
            print(f"⚠️ Insufficient content: Expected {days_in_month} rows, got {len(lines_with_pipes)}")
            print("🔄 Attempting to generate missing days...")
            
            missing_days = days_in_month - len(lines_with_pipes)
            start_day = len(lines_with_pipes) + 1
            
            # Generate additional content for missing days with very conservative tokens
            supplement_prompt = f"""Generate EXACTLY {missing_days} more content entries starting from Day {start_day} to Day {days_in_month}.

Format: Day X | Title | Hook | Body | CTA | Format | Audio | Hashtags | Production | Optimization

Generate days {start_day} through {days_in_month}:"""
            
            try:
                supplement_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use faster model for supplements
                    messages=[{"role": "user", "content": supplement_prompt}],
                    temperature=0.7,
                    max_tokens=1500  # Very conservative for supplements
                )
                
                supplement_text = supplement_response.choices[0].message.content.strip()
                supplement_lines = [line for line in supplement_text.split('\n') if 'Day ' in line and '|' in line]
                
                if supplement_lines:
                    calendar_text += "\n" + "\n".join(supplement_lines)
                    lines_with_pipes = [line for line in calendar_text.split('\n') if '|' in line and 'Day ' in line]
                    print(f"✅ Supplemented content. Total rows now: {len(lines_with_pipes)}")
                
            except Exception as supplement_error:
                print(f"⚠️ Could not supplement content: {supplement_error}")
        
        return calendar_text
        
    except Exception as e:
        raise ValueError(f"❌ Error generating calendar: {str(e)}")
