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
You are a 50-year elite viral content strategist who has generated $100M+ in revenue for AI-focused entrepreneurs.

🎯 CRITICAL REQUIREMENT: Generate EXACTLY {days_in_month} content entries for {month} - one for each day of the month.

📈 TRENDING INTEL for {month}:
{chr(10).join(trends)}

🎬 MANDATORY FORMAT - Each line must follow this EXACT pattern:
Day X | Reel Title | Hook Script | Body Script | Close/CTA | Format | Audio | Hashtags | Production | Optimization

EXAMPLE FORMAT:
Day 1 | "3 AI Tools Replacing $50K Employees" | If you're not using these 3 AI tools, you're losing $10K monthly | Tool 1: ChatGPT Advanced Data Analysis saves 15 hours weekly. Tool 2: Claude Projects manages entire campaigns. Tool 3: Notion AI automates client reporting. Each tool replaces expensive hires. | Which tool will you implement first? Comment below! | Face-to-cam + screen demo | Trending tech beat | #AItools #entrepreneur #businessgrowth #automation #startup #productivity #AIbusiness #futureofwork | Bold text overlays, quick transitions | Hook within first 2 seconds

🚨 CRITICAL INSTRUCTIONS:
1. Generate EXACTLY {days_in_month} entries numbered Day 1 through Day {days_in_month}
2. Each entry MUST be on its own line
3. Each entry MUST have exactly 10 sections separated by " | "
4. NO extra headers, explanations, or formatting
5. Start immediately with "Day 1 | ..." and end with "Day {days_in_month} | ..."

CONTENT THEMES TO ROTATE:
- AI productivity tools and automation
- Business scaling strategies  
- Viral content creation methods
- AI-powered marketing tactics
- Entrepreneurship insights
- Future-proofing business strategies

Generate all {days_in_month} entries now:

📝 SCRIPT WRITING EXCELLENCE:

HOOK FORMULAS (0-2 seconds):
- Pattern Interrupt: "If you don't master these 3 skills, you'll be replaced by AI users in 12 months"
- Insider Secret: "3 AI tools that are secretly running 7-figure businesses"
- Social Proof: "This single AI prompt just replaced my $5K copywriter"
- Future Pacing: "Don't start a business in 2025 without these AI systems"
- Authority: "If I had to learn AI from scratch today, here's exactly what I'd do"

BODY STRUCTURE (3-20 seconds):
- Lead with specific, actionable insights
- Include exact tool names and use cases
- Provide step-by-step breakdowns
- Share measurable outcomes ("saved 10 hours", "increased revenue 300%")
- Use insider language and advanced concepts

CLOSE/CTA PATTERNS (20-30 seconds):
- DM Magnets: "DM 'PROMPT' for the exact framework I used"
- Engagement: "Which one are you implementing first? Drop it below 👇"
- FOMO: "Save this before your competitors find it"
- Social Proof: "Tag someone who needs to see this"
- Authority: "Ready to 10x your business with AI? Link in bio"

🎨 CONTENT VARIETY MATRIX:

FORMATS TO ROTATE:
- Face-to-cam + dramatic text overlays (authority building)
- Screen recordings + talking head (tool demonstrations)
- Voiceover + visual demos (workflow breakdowns)
- Slide carousels + graphics (frameworks/strategies)
- Behind-the-scenes + results reveal (credibility)

PSYCHOLOGICAL TRIGGERS:
✅ Scarcity: "Only 3% of entrepreneurs know this"
✅ Urgency: "The AI revolution waits for no one"
✅ Social Proof: "How 7-figure founders really scale"
✅ Authority: "The method I used to build my AI empire"
✅ Curiosity Gap: "The AI secret they don't want you to know"
✅ Transformation: "From struggling solopreneur to AI-powered CEO"

🔥 CONTENT THEMES TO CYCLE:

Week 1: AI Tool Mastery & Productivity Hacks
Week 2: Business Scaling Systems & Automation
Week 3: Advanced Strategies & Insider Secrets  
Week 4: Future-Proofing & Competitive Advantage

📱 PRODUCTION SPECIFICATIONS:

VISUAL REQUIREMENTS:
- Bold, contrasting text (max 3 words per line)
- Capitalize emotion words: "SECRETLY", "7-FIGURE", "REPLACED"
- Use trending transitions and zoom effects
- Include progress bars, checkmarks, money symbols

AUDIO STRATEGY:
- Trending sounds for algorithm boost
- Suspenseful/techy beats for authority content
- Upbeat tracks for transformation stories
- Trending songs for broader reach

HASHTAG STRATEGY:
- Mix of trending (#entrepreneur #AI) and niche (#promptengineering #businessautomation)
- Include branded hashtag opportunities
- Target 8-12 hashtags per post
- Balance reach and engagement hashtags

💡 ADVANCED OPTIMIZATION:

ENGAGEMENT MAXIMIZERS:
- Include controversy/contrarian takes
- Ask specific questions in captions
- Create "tutorial series" for algorithm retention
- Use pattern interrupts and hook variations
- Include educational carousels for saves

CONVERSION OPTIMIZERS:
- Multiple DM magnets throughout month
- Progressive value ladder (free → paid)
- Authority building through specificity
- Social proof integration
- Clear funnel progression

🚀 EXECUTION STANDARDS:

Each reel MUST include:
✅ Specific tool/strategy names (ChatGPT, Notion AI, etc.)
✅ Measurable outcomes (time saved, revenue increased)
✅ Exact implementation steps
✅ Emotional triggers and urgency language
✅ Clear lead magnet or next step
✅ Professional production guidance
✅ Algorithm optimization tactics

Generate {days_in_month} days of ELITE-LEVEL content that converts cold viewers into hot leads ready to invest in AI business transformation.

REMEMBER: Every single reel should feel like premium, insider intelligence that competitors wish they had access to.
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
