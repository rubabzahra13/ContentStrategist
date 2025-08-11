#!/usr/bin/env python3
"""
Enhanced Calendar Generator - Uses mentor knowledge and course insights
Replaces the basic calendar_generator.py with knowledge-enhanced AI prompting
"""

from openai import OpenAI
from utils.config import OPENAI_API_KEY
try:
    from core.knowledge_base import KnowledgeBase
except ImportError:
    KnowledgeBase = None

from core.hardcoded_mentor_patterns import (
    ALL_MENTOR_PATTERNS, 
    get_mentor_inspired_hook,
    get_mentor_inspired_cta,
    get_content_framework,
    get_mentor_insights_summary
)
from core.hardcoded_course_insights import (
    get_course_insights_for_prompt,
    get_actionable_strategies
)
from core.special_dates import get_special_date_prompt_section
from core.real_mentor_transcripts import get_real_content_for_prompt
from typing import List, Dict

def get_rag_content_for_trends(trends: List[str]) -> List[Dict]:
    """
    Get real Instagram content from RAG system based on trends
    Includes token management to prevent prompt overflow
    """
    try:
        from core.rag_retrieval import RAGRetriever
        
        retriever = RAGRetriever()
        all_content = []
        
        # Query for each trend with specific creators - REGULATED TO 5 VIDEOS PER CREATOR
        creators = ['hormozi', 'vaibhavsisinty']
        
        # Get exactly 5 videos per creator (10 total) to prevent oversampling
        hormozi_content = retriever.retrieve("business scaling entrepreneur", creators=['hormozi'], limit=5)
        vaibhav_content = retriever.retrieve("AI tools growth hacking", creators=['vaibhavsisinty'], limit=5)
        
        all_content = hormozi_content + vaibhav_content
        
        # Deduplicate by reel_id
        seen_ids = set()
        unique_content = []
        for content in all_content:
            if content.reel_id not in seen_ids:
                unique_content.append(content)
                seen_ids.add(content.reel_id)
        
        # Token management: Limit content to prevent prompt overflow
        try:
            import tiktoken
            enc = tiktoken.encoding_for_model("gpt-4-turbo-preview")
            
            # Estimate tokens for content pieces
            token_budget = 1000  # Max tokens for RAG content in prompt
            current_tokens = 0
            filtered_content = []
            
            for content in unique_content[:10]:  # Start with max 10 pieces
                # Estimate tokens for this content piece
                content_text = f"{getattr(content, 'caption', '')} {getattr(content, 'transcript', '')}"
                content_tokens = len(enc.encode(content_text))
                
                if current_tokens + content_tokens <= token_budget:
                    filtered_content.append(content)
                    current_tokens += content_tokens
                else:
                    break  # Stop adding content to stay within budget
            
            print(f"🎯 Retrieved {len(filtered_content)} real Instagram content pieces from RAG (5 per creator, {current_tokens} tokens)")
            return filtered_content
            
        except Exception as token_error:
            print(f"⚠️ Token calculation failed, using first 5 pieces: {token_error}")
            return unique_content[:5]  # Conservative fallback
        
    except Exception as e:
        print(f"⚠️ Could not retrieve RAG content: {e}")
        return []
import calendar
import re
import json
from datetime import datetime

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

def generate_mentor_enhanced_prompt(month, trends, days_in_month, real_content=None):
    """
    Generate AI prompt enhanced with hardcoded mentor patterns + real Instagram content
    """
    
    # Get mentor patterns
    alex_patterns = ALL_MENTOR_PATTERNS["alex_hormozi"]
    vaibhav_patterns = ALL_MENTOR_PATTERNS["vaibhav_sisinty"]
    combined_patterns = ALL_MENTOR_PATTERNS["combined"]
    
    # Sample successful hooks from mentors
    sample_hooks = alex_patterns["successful_hooks"][:3] + vaibhav_patterns["successful_hooks"][:3]
    
    # Sample proven CTAs
    sample_ctas = alex_patterns["proven_ctas"][:3] + vaibhav_patterns["proven_ctas"][:3]
    
    # Sample frameworks
    sample_frameworks = alex_patterns["content_frameworks"][:2] + vaibhav_patterns["content_frameworks"][:2]
    
    # Generate real content section if available
    real_content_section = ""
    if real_content:
        real_content_section = f"""

🎬 REAL INSTAGRAM CONTENT FROM MENTORS (Use for Inspiration):

"""
        for i, content in enumerate(real_content[:5], 1):  # Show top 5
            script_preview = getattr(content, 'text', 'Script not available')[:100] + "..."
            real_content_section += f"""Example {i} - @{content.creator_handle} ({content.views:,} views, {content.likes:,} likes):
Hook: "{content.hook}"
Caption: "{content.caption[:150]}..."
Script Sample: "{script_preview}"
Hashtags: {', '.join(content.hashtags[:5])}
---
"""
    
    enhanced_prompt = f"""🚨 CRITICAL INSTRUCTIONS - MUST FOLLOW:
1. Generate EXACTLY {days_in_month} complete rows (Day 1 through Day {days_in_month})
2. EVERY row MUST have ALL 11 columns filled out completely  
3. Hooks MUST be exactly 1 sentence with specific numbers
4. Scripts MUST include specific dollar amounts, percentages, or data points
5. DO NOT stop generating until ALL {days_in_month} days are complete

Create a strategic {days_in_month}-day Instagram Reels content calendar for {month} focused on AI and business scaling for entrepreneurs.

🎯 MENTOR INSPIRATION - Learn from these proven patterns:

{get_real_content_for_prompt()}

📱 ALEX HORMOZI STYLE (7M+ followers, $100M+ entrepreneur):
Bio: "{alex_patterns['bio']}"
Content Style: {alex_patterns['content_style']}

Successful Hook Examples:
• "{sample_hooks[0]}"
• "{sample_hooks[1]}" 
• "{sample_hooks[2]}"

📱 VAIBHAV SISINTY STYLE (300K+ followers, Growth expert):
Bio: "{vaibhav_patterns['bio']}"
Content Style: {vaibhav_patterns['content_style']}

Successful Hook Examples:
• "{sample_hooks[3]}"
• "{sample_hooks[4]}"
• "{sample_hooks[5]}"

🎣 PROVEN HOOK PATTERNS TO USE:
{chr(10).join([f"• {hook}" for hook in combined_patterns["universal_hooks"][:5]])}

💬 HIGH-ENGAGEMENT CTA PATTERNS:
{chr(10).join([f"• {cta}" for cta in sample_ctas])}

📋 PROVEN CONTENT FRAMEWORKS:
{chr(10).join([f"• {framework}" for framework in sample_frameworks])}

{get_course_insights_for_prompt()}{real_content_section}

🔥 CURRENT TRENDS TO INTEGRATE:
{', '.join(trends[:5])}

{get_special_date_prompt_section(month)}

🎯 VALUE DELIVERY PRINCIPLES (from mentors):
• Give away your best strategies for free
• Use real data and specific examples  
• Share failures as much as successes
• Focus on practical, actionable advice
• Build trust through transparency
• Stay authentic and relatable

📋 SPECIFIC REQUIREMENTS:
- Generate ALL {days_in_month} days for {month}
- Use mentor-inspired hooks but adapt to AI/business scaling niche
- Each post must provide genuine entrepreneurial value
- Mix Alex's direct business approach with Vaibhav's growth hacking style
- Include specific tools, strategies, and frameworks
- Make each post scroll-stopping and highly engaging
- Use psychological triggers from successful posts

🎉 CRITICAL: SPECIAL DATES & HOLIDAY CONTENT:
- For any holidays or special dates mentioned above (Christmas, New Year, etc.), create themed content that ties business/AI concepts to the celebration
- Use the provided holiday hook suggestions and content themes
- Example: Day 25 (Christmas) should include Christmas-themed business content with holiday hashtags
- Make holiday content authentic and valuable, not just promotional
- Incorporate holiday emotions and themes into business lessons

🎬 SCRIPT/TRANSCRIPT COLUMN REQUIREMENTS:
- Write the EXACT words you would say in the reel (like Hormozi/Vaibhav style)
- Include natural speech patterns, pauses, emphasis 
- Use conversational tone that builds trust and authority
- Include specific examples, numbers, and case studies
- Make it sound authentic and engaging when spoken aloud
- Length: 30-60 seconds of natural speaking (150-300 words)

📝 REAL MENTOR SCRIPT EXAMPLES:
HORMOZI MONEY: "I have $35 million in my bank account. That's it. But here's what's crazy - if you have $10,000 or even $1,000, that money won't make you rich. The only thing that will get you rich is increasing your active income. Focus on active income, not passive income."

HORMOZI SALES: "If you want to close more sales, say less. When we take on portfolio companies, first thing we do is look at the sales script - not what to add, but what to remove. You can dramatically improve close rates by cutting scripts in half."

VAIBHAV AI TOOLS: "Sam Altman killed millions of jobs with one insane update. He released GPT-5 today and literally made it free for all. Here are the 12 insane features of GPT-5 that you should try. Number 4 is my personal favorite."

VAIBHAV INSIDER: "Most people won't hear about these tools till 2026. You're getting them six months early. These aren't just cool new tools. They're competitive weapons. And you just got access before the rest of the world."

🎯 INSTAGRAM CONTENT STRUCTURE - CRITICAL UNDERSTANDING:

📱 HOOK (Cover Text): 2-4 catchy words/phrases that appear on reel cover
- Examples: "$35M SECRET", "92% FAIL", "AI KILLED JOBS", "SALES HACK"
- NOT full sentences - just attention-grabbing text overlay

📝 CAPTION (Under Post): The description text users see below the reel
- 1-3 sentences explaining value proposition
- Include relevant hashtags
- Call-to-action for engagement

🎬 SCRIPT/TRANSCRIPT: Exact words spoken in the video (30-60 seconds)
- Natural speaking patterns with pauses
- Specific numbers, case studies, frameworks
- Authentic mentor voice (Hormozi/Vaibhav style)

📊 CORRECT OUTPUT FORMAT:
Day X | "Reel Title" | Hook Cover Text | Instagram Caption | Full Speaking Script | Video Style | Audio Type | Hashtags | Production Notes | Engagement Strategy

⚠️ CRITICAL: Generate ALL {days_in_month} days - do not stop early or cut off the calendar

💎 PREMIUM CONTENT REQUIREMENTS ($5M STANDARD):

🔥 HOOK COVER TEXT Examples:
- Hormozi Style: "$35M BANK", "SALES SECRET", "SCALE HACK", "RICH MINDSET"
- Vaibhav Style: "AI KILLED JOBS", "GPT-5 DROP", "TECH BOMB", "TOOL LEAK"

📱 INSTAGRAM CAPTION Examples:
- "The one thing that separates $1M entrepreneurs from everyone else... (it's not what you think) 💰 #BusinessScaling #Entrepreneur"
- "Most people won't discover this AI tool until 2026. You're getting early access 🚀 #AITools #TechAdvantage"

🎬 SPEAKING SCRIPT Requirements:
- Start with hook: "Listen, I have $35 million in my bank account, but here's what's crazy..."
- Include specific data: "I analyzed 10,000 successful businesses and found..."
- Use frameworks: "There are three ways to scale: first... second... third..."
- End with value: "Try this strategy and watch what happens to your revenue."

🎯 CONTENT MUST INCLUDE:
- Specific dollar amounts or percentages
- Contrarian insights that challenge common beliefs
- Personal case studies or examples
- Actionable frameworks viewers can implement
- Authentic speaking voice (not corporate speak)

📊 CRITICAL: USE EXACTLY THIS PIPE-SEPARATED FORMAT (NO MARKDOWN, NO BULLETS):

Day 1 | "AI Revolution" | "AI KILLED JOBS" | "The one AI tool that's replacing entire teams... and why you need it 🤖 #AIRevolution #TechDisruption" | "Listen, Sam Altman just dropped something that's going to change everything. GPT-5 is here and it's literally free. I've been testing it for 48 hours and here's what I found..." | Educational Reel | Trending Audio | #AI #GPT5 #TechNews | Film talking head with graphics | Ask: "Which AI tool shocked you most?"

GENERATE EXACTLY {days_in_month} ROWS IN THIS EXACT PIPE FORMAT - NO OTHER FORMATTING:"""
    
    return enhanced_prompt

def generate_enhanced_calendar(trends, month, knowledge_base=None):
    """
    Generate content calendar enhanced with hardcoded mentor knowledge + RAG retrieval
    
    Args:
        trends: Trending topics list
        month: Month string (e.g., "January 2025")
        knowledge_base: Optional KnowledgeBase instance (fallback to hardcoded patterns)
        
    Returns:
        Enhanced calendar text with mentor-inspired content + real Instagram data
    """
    
    if not trends:
        trends = ["AI tools for entrepreneurs", "business scaling strategies", "viral content formats"]
    
    # Get correct number of days for the month
    days_in_month = get_days_in_month(month)
    print(f"📅 Requesting {days_in_month} days of enhanced content for {month}")
    
    # Use GPT-4 Turbo with dynamic token management
    model = "gpt-4-turbo-preview"
    
    # Calculate optimal max_tokens based on prompt size to prevent token limit issues
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model(model)
        
        # Get preliminary prompt to estimate tokens
        preliminary_prompt = generate_mentor_enhanced_prompt(month, trends, days_in_month, [])
        base_tokens = len(enc.encode(preliminary_prompt))
        
        # Add buffer for real content and safety margin
        estimated_total_tokens = base_tokens + 500  # Buffer for real content
        
        # GPT-4-turbo context limit is 128k, leave room for response
        context_limit = 128000
        safety_margin = 2000  # Safety buffer
        
        available_tokens = context_limit - estimated_total_tokens - safety_margin
        
        # Dynamic max_tokens based on available space and content needs
        # GPT-4-turbo-preview has a max_tokens limit of 4096
        model_max_tokens = 4096
        
        if days_in_month > 25:
            max_tokens = min(available_tokens, model_max_tokens, 4000)  # Large months
        elif days_in_month > 20:
            max_tokens = min(available_tokens, model_max_tokens, 3500)  # Medium months
        else:
            max_tokens = min(available_tokens, model_max_tokens, 3000)  # Small months
            
        # Ensure minimum viable tokens but respect model limits
        max_tokens = max(min(max_tokens, model_max_tokens), 2000)
        
        print(f"🎯 Token Management: {estimated_total_tokens:,} input + {max_tokens:,} output = {estimated_total_tokens + max_tokens:,} total")
        
    except Exception as e:
        print(f"⚠️ Token calculation failed, using safe defaults: {e}")
        # Fallback to safe defaults
        if days_in_month > 20:
            max_tokens = 3500
        else:
            max_tokens = 2500
    
    # Get real Instagram content via RAG retrieval
    real_instagram_content = get_rag_content_for_trends(trends)
    
    # Generate enhanced prompt using hardcoded mentor patterns + real content
    enhanced_prompt = generate_mentor_enhanced_prompt(month, trends, days_in_month, real_instagram_content)

    try:
        print("🧠 Generating enhanced calendar with knowledge base...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert viral content strategist with 15+ years experience creating Instagram content for entrepreneurs. You combine proven mentor strategies with cutting-edge AI business insights to create highly engaging, value-driven content calendars."
                },
                {
                    "role": "user", 
                    "content": enhanced_prompt
                }
            ],
            temperature=0.8,  # Slightly higher for more creative content
            max_tokens=max_tokens
        )

        calendar_text = response.choices[0].message.content.strip()

        # Validate response has content and proper format
        if not calendar_text:
            raise ValueError("❌ OpenAI returned empty response")
            
        # Check if it has the expected format
        lines_with_pipes = [line for line in calendar_text.split('\n') if '|' in line and 'Day ' in line]
        
        print(f"📊 Generated {len(lines_with_pipes)} enhanced content rows for {days_in_month}-day month")
        
        # Check if we need to supplement content
        if len(lines_with_pipes) < days_in_month:
            if len(lines_with_pipes) >= 8:  # Good main generation
                print(f"✅ Main generation successful: {len(lines_with_pipes)} days")
                print(f"🔄 Supplementing remaining {days_in_month - len(lines_with_pipes)} days...")
            else:
                print(f"⚠️ Limited main generation: {len(lines_with_pipes)} days")
                print(f"🔄 Attempting to generate {days_in_month - len(lines_with_pipes)} missing days...")
            
            missing_days = days_in_month - len(lines_with_pipes)
            start_day = len(lines_with_pipes) + 1
            
            # Get successful patterns for supplementation from hardcoded mentors
            sample_hooks = get_mentor_inspired_hook() 
            
            supplement_context = f"Use mentor-inspired patterns like: \"{sample_hooks[:80]}...\""
            
            # Generate additional content for missing days with enhanced context
            supplement_prompt = f"""Generate EXACTLY {missing_days} more Instagram Reels content entries for entrepreneurs, starting from Day {start_day} to Day {days_in_month}.

{supplement_context}

🎯 PREMIUM INSTAGRAM CONTENT STRUCTURE ($5M STANDARD):

📱 HOOK COVER TEXT: 2-4 catchy words (Examples: "$35M SECRET", "AI KILLED JOBS")
📝 INSTAGRAM CAPTION: 1-3 sentences with value proposition and hashtags
🎬 SPEAKING SCRIPT: 30-60 seconds of authentic mentor-style content with specific numbers

💎 SCRIPT EXAMPLES:
HORMOZI: "Listen, I have $35 million in my bank account. But here's what's crazy - if you have $1,000 or $10,000, that money won't make you rich. The only thing that will get you rich is increasing your active income. Focus on active income, not passive income."

VAIBHAV: "Sam Altman just killed millions of jobs with one insane update. He released GPT-5 today and literally made it free for all. Here are the 12 insane features you need to know. Number 4 is my personal favorite."

CRITICAL: USE EXACTLY THIS PIPE-SEPARATED FORMAT (NO MARKDOWN):

Day {start_day} | "Business Growth" | "SCALE SECRET" | "The growth hack 99% of entrepreneurs miss... here's how to 10x your revenue 💰 #BusinessGrowth #Scaling" | "Most entrepreneurs fail because they focus on the wrong metrics. I've analyzed over 1,000 successful businesses and found they all do this one thing differently..." | Educational Reel | Trending Audio | #Business #Growth | Film with data graphics | Ask: "What's your biggest scaling challenge?"

GENERATE EXACTLY {missing_days} ROWS FROM DAY {start_day} TO DAY {days_in_month} IN THIS EXACT FORMAT:"""
            
            try:
                # Dynamic token management for supplements
                try:
                    import tiktoken
                    enc = tiktoken.encoding_for_model("gpt-3.5-turbo")
                    supplement_tokens = len(enc.encode(supplement_prompt))
                    
                    # GPT-3.5-turbo context limit is 16k, max_tokens limit is 4096
                    available_supplement_tokens = min(16000 - supplement_tokens - 1000, 4096)  # Safety margin + model limit
                    supplement_max_tokens = min(available_supplement_tokens, missing_days * 120)  # ~120 tokens per day
                    supplement_max_tokens = max(supplement_max_tokens, 1000)  # Minimum viable
                    
                    print(f"🔧 Supplement Token Management: {supplement_tokens:,} input + {supplement_max_tokens:,} output")
                except:
                    supplement_max_tokens = 3000  # Safe fallback
                
                supplement_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use faster model for supplements
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert content strategist creating Instagram content for entrepreneurs."
                        },
                        {
                            "role": "user", 
                            "content": supplement_prompt
                        }
                    ],
                    temperature=0.8,
                    max_tokens=supplement_max_tokens  # Dynamic token management
                )
                
                supplement_text = supplement_response.choices[0].message.content.strip()
                supplement_lines = [line for line in supplement_text.split('\n') if 'Day ' in line and '|' in line]
                
                if supplement_lines:
                    calendar_text += "\n" + "\n".join(supplement_lines)
                    lines_with_pipes = [line for line in calendar_text.split('\n') if '|' in line and 'Day ' in line]
                    print(f"✅ Supplemented content. Total rows now: {len(lines_with_pipes)}")
                
            except Exception as supplement_error:
                print(f"⚠️ Could not supplement content: {supplement_error}")
        
        # Add enhanced knowledge footer for reference
        mentor_insights = get_mentor_insights_summary()
        
        rag_content_count = len(real_instagram_content) if real_instagram_content else 0
        
        footer = f"""

🧠 ENHANCED KNOWLEDGE SOURCES:
• Alex Hormozi (@hormozi): {ALL_MENTOR_PATTERNS['alex_hormozi']['bio']} - 7M+ followers
• Vaibhav Sisinty (@vaibhavsisinty): {ALL_MENTOR_PATTERNS['vaibhav_sisinty']['bio']} - 300K+ followers
• Hardcoded patterns: {len(ALL_MENTOR_PATTERNS['combined']['universal_hooks'])} proven hooks, {len(ALL_MENTOR_PATTERNS['combined']['high_engagement_ctas'])} effective CTAs
• Real Instagram content: {rag_content_count} actual posts from mentor feeds
• Success principles: Value-first content, authentic storytelling, data-driven execution

Generated with battle-tested mentor strategies + real Instagram RAG retrieval system."""
        
        calendar_text += footer
        
        print("✅ Enhanced calendar generated with mentor knowledge and course insights!")
        return calendar_text
        
    except Exception as e:
        print(f"❌ Error generating enhanced calendar: {str(e)}")
        # Fallback to basic generation
        print("🔄 Falling back to basic calendar generation...")
        return generate_basic_fallback_calendar(trends, month, days_in_month)

def generate_basic_fallback_calendar(trends, month, days_in_month):
    """Fallback calendar generation if enhanced version fails"""
    try:
        basic_prompt = f"""Create {days_in_month} Instagram Reels for AI entrepreneurs ({month}).

Trends: {', '.join(trends[:3])}

Format: Day X | "Title" | Hook | Body | CTA | Format | Audio | Hashtags | Production | Optimization

Generate ALL {days_in_month} days (no shortcuts). Topics: AI tools, automation, scaling."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": basic_prompt}],
            temperature=0.7,
            max_tokens=2500
        )

        return response.choices[0].message.content.strip()
        
    except Exception as e:
        raise ValueError(f"❌ Both enhanced and fallback calendar generation failed: {str(e)}")

# Backward compatibility function
def generate_calendar(trends, month):
    """
    Backward compatibility wrapper for existing codebase
    This maintains the same interface as the original calendar_generator.py
    """
    return generate_enhanced_calendar(trends, month)

def main():
    """Test the enhanced calendar generator"""
    print("🧠 Testing Enhanced Calendar Generator")
    
    # Initialize knowledge base
    kb = KnowledgeBase()
    
    # Test with sample data
    test_trends = [
        "AI automation tools trending in January 2025",
        "Instagram Reels business strategies",
        "Entrepreneurship AI productivity hacks"
    ]
    
    test_month = "January 2025"
    
    print(f"🎯 Generating enhanced calendar for {test_month}")
    
    # Generate calendar
    calendar_result = generate_enhanced_calendar(test_trends, test_month, kb)
    
    if calendar_result:
        # Show preview
        lines = calendar_result.split('\n')
        calendar_lines = [line for line in lines if '|' in line and 'Day ' in line]
        
        print(f"\n📊 Generated {len(calendar_lines)} content entries")
        print("\n📝 Preview (first 3 entries):")
        for line in calendar_lines[:3]:
            print(f"  {line}")
        
        print(f"\n💾 Full calendar length: {len(calendar_result)} characters")
    else:
        print("❌ Failed to generate calendar")

if __name__ == "__main__":
    main()