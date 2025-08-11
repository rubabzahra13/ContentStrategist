#!/usr/bin/env python3
"""
Hardcoded Course Insights - Your course transcripts and key strategies
Now includes One Peak Creative course content from 92+ lesson transcripts
"""

# Import One Peak Creative insights
from .onepeak_course_insights import ONEPEAK_COURSE_INSIGHTS, get_onepeak_insights_for_prompt

# Combined course content - placeholders + real One Peak Creative content
COURSE_INSIGHTS = {
    
    # REAL COURSE CONTENT - One Peak Creative
    "onepeak_creative_viral_content": {
        "title": "Find Your Peak TikTok and Reels Creator Course",
        "instructors": ["One Peak Creative Team", "Glenn", "Kahn", "Megan"],
        "key_strategies": [
            "Watch time is gold - algorithms reward time spent above all else",
            "Hook viewers within first 5 seconds or they'll scroll away",
            "Create relatable, shareable, repeatable content formula",
            "Quality over quantity - don't post half-assed content",
            "Find drama and hooks in everyday mundane activities",
            "Add stakes and gamification to any content niche",
            "Use stranger interactions to leverage curiosity psychology",
            "Algorithm judges quality through views - improve content, don't blame platform"
        ],
        "viral_frameworks": [
            "Relatable + Shareable + Repeatable = Viral Formula",
            "5-Second Hook Rule: Capture attention or lose viewer",
            "Challenge Format: Add win/lose scenarios for engagement",
            "Educational Angle: Teach with captivating curiosity gaps",
            "Stranger Psychology: People love watching others' reactions",
            "Everyday Drama: Turn mundane into compelling content",
            "Stakes Addition: Gamify any niche for watch time"
        ],
        "hook_strategies": [
            "Create curiosity gaps that demand answers",
            "Use surprising statements or bold claims", 
            "Promise revelation or satisfying outcome",
            "Identify relatable problems immediately",
            "Avoid generic introductions like 'Hi, I'm [name]'",
            "Don't assume people know or care who you are",
            "Compete with extreme content - make hooks strong enough"
        ],
        "proven_hooks": [
            "Apparently jackfruit can look and taste like pulled pork, so I'm going to try and trick my husband",
            "That escalated quickly",
            "The stakes have never been higher",
            "Full amount spent at the end",
            "You won't believe what happened next",
            "Person who pulls highest card changes the next diaper",
            "I told him I'd buy lunch if he makes par on the next hole"
        ],
        "content_psychology": [
            "People want to see who wins in challenges",
            "Satisfy curiosity about strangers' reactions",
            "Build community through shared relatable experiences",
            "Create conversation through controversy and relatability",
            "Vicarious living through others' interesting content",
            "Satisfaction from watching perfected skills",
            "Innate curiosity about how things end"
        ],
        "success_principles": [
            "Success is going from failure to failure with enthusiasm",
            "You never fail if you never quit",
            "Harry Potter rejected 12 times before publishing",
            "Van Gogh sold only 1 painting, created 900+",
            "Walt Disney fired for 'lack of imagination'",
            "Stephen King rejected 60 times before 1M+ book sales",
            "Don't chase trends - create timeless, memorable content"
        ],
        "posting_strategy": [
            "Use 4-5 niche-specific hashtags (avoid generic #FYP)",
            "Write strategic caption hooks (don't give away ending)",
            "Add text overlays and captions for clarity",
            "Choose intriguing cover photos with hooks",
            "Tag relevant brands for partnership opportunities",
            "Post 3 videos per week minimum for growth",
            "Focus on one consistent format audience can expect"
        ]
    },
    "ai_business_automation": {
        "title": "AI Business Automation Masterclass",
        "instructor": "Your Name",
        "key_strategies": [
            "Start with one process and perfect it before moving to the next",
            "Use the 80/20 rule - automate the 20% that gives 80% results",
            "Always have a human review system for AI outputs",
            "Test automation in small batches before full deployment",
            "Focus on high-volume, repetitive tasks first"
        ],
        "frameworks": [
            "AIDA Framework: Audit → Identify → Deploy → Analyze",
            "3-Step Validation: Test → Measure → Scale",
            "Automation Priority Matrix: Impact vs Effort",
            "ROI Calculation: Time Saved × Hourly Rate - Tool Cost",
            "Quality Gates: 95% accuracy threshold before automation"
        ],
        "tools_mentioned": [
            "Zapier for workflow automation",
            "ChatGPT for content generation", 
            "Calendly for appointment scheduling",
            "Loom for video creation",
            "Notion for documentation"
        ],
        "powerful_quotes": [
            "Automation without strategy is just expensive procrastination",
            "The goal isn't to replace humans, it's to free them for higher-value work",
            "Every successful automation starts with a manual process that works",
            "Measure twice, automate once",
            "AI amplifies intelligence, not replaces it"
        ],
        "action_items": [
            "Audit your daily tasks and identify the top 3 most repetitive ones",
            "Research AI tools that can handle these specific tasks",
            "Start with one tool and master it before adding others",
            "Set up proper tracking to measure time and cost savings",
            "Create standard operating procedures for your automation workflows"
        ]
    },
    
    "scaling_with_ai": {
        "title": "Scaling Your Business with AI Tools",
        "instructor": "Your Name", 
        "key_strategies": [
            "Build systems, not just processes",
            "Use AI to enhance decision-making, not replace it",
            "Start with customer-facing automation for immediate ROI",
            "Create feedback loops to continuously improve AI outputs",
            "Train your team on AI tools to multiply effectiveness"
        ],
        "frameworks": [
            "SCALE Framework: Systems → Consistency → Automation → Leverage → Expansion",
            "AI Adoption Roadmap: Assess → Pilot → Implement → Optimize → Scale",
            "Value Creation Matrix: Customer Impact × Business Efficiency",
            "AI Ethics Checklist: Transparency, Fairness, Privacy, Accountability",
            "Performance Metrics: Speed, Accuracy, Cost, Satisfaction"
        ],
        "tools_mentioned": [
            "HubSpot for CRM automation",
            "Canva for design automation",
            "Buffer for social media scheduling",
            "Grammarly for writing assistance",
            "Salesforce Einstein for sales insights"
        ],
        "powerful_quotes": [
            "Scale is achieved when your systems work without you",
            "The best AI tool is the one your team actually uses",
            "Consistency beats perfection when scaling",
            "Your competitive advantage comes from how you combine tools, not the tools themselves",
            "AI doesn't scale your business, systems do"
        ],
        "action_items": [
            "Map your customer journey and identify automation opportunities",
            "Calculate the true cost of manual processes in your business",
            "Choose one AI tool and commit to using it for 30 days",
            "Document your successful automations for team replication",
            "Set monthly reviews to assess AI tool performance and ROI"
        ]
    }
}

def get_course_insights_for_prompt():
    """
    Generate course insights section for AI prompt
    Now includes real One Peak Creative viral content strategies
    """
    insights_text = []
    insights_text.append("📚 COURSE INSIGHTS FROM YOUR PROVEN STRATEGIES:")
    
    # Add One Peak Creative insights first (most important)
    onepeak_data = COURSE_INSIGHTS.get("onepeak_creative_viral_content")
    if onepeak_data:
        insights_text.append(f"\n🎓 {onepeak_data['title']} (REAL COURSE CONTENT):")
        
        # Viral frameworks 
        insights_text.append("🎯 VIRAL CONTENT FRAMEWORKS:")
        for framework in onepeak_data['viral_frameworks'][:4]:
            insights_text.append(f"• {framework}")
        
        # Hook strategies
        insights_text.append("🎣 PROVEN HOOK STRATEGIES:")
        for hook in onepeak_data['hook_strategies'][:3]:
            insights_text.append(f"• {hook}")
        
        # Success principles
        insights_text.append("💪 SUCCESS PRINCIPLES:")
        for principle in onepeak_data['success_principles'][:2]:
            insights_text.append(f"• {principle}")
    
    # Add other course content (placeholder courses)
    for course_key, course_data in COURSE_INSIGHTS.items():
        if course_key == "onepeak_creative_viral_content":
            continue  # Already added above
            
        insights_text.append(f"\n🎓 {course_data['title']}:")
        
        # Add key strategies
        insights_text.append("Key Strategies:")
        for strategy in course_data['key_strategies'][:2]:  # Reduced to make room for OnePeak
            insights_text.append(f"• {strategy}")
        
        # Add frameworks (if exists)
        if 'frameworks' in course_data:
            insights_text.append("Proven Frameworks:")
            for framework in course_data['frameworks'][:1]:  # Reduced to 1
                insights_text.append(f"• {framework}")
    
    return "\n".join(insights_text)

def get_actionable_strategies():
    """
    Get actionable strategies from all courses
    """
    all_strategies = []
    all_frameworks = []
    all_quotes = []
    
    for course_data in COURSE_INSIGHTS.values():
        all_strategies.extend(course_data['key_strategies'])
        all_frameworks.extend(course_data['frameworks'])
        all_quotes.extend(course_data['powerful_quotes'])
    
    return {
        "strategies": all_strategies,
        "frameworks": all_frameworks,
        "quotes": all_quotes
    }

def add_your_course_content(course_title, strategies, frameworks, quotes, tools=None):
    """
    Helper function to add your actual course content
    
    Usage:
    add_your_course_content(
        "Your Course Name",
        ["Strategy 1", "Strategy 2"],
        ["Framework 1", "Framework 2"], 
        ["Quote 1", "Quote 2"],
        ["Tool 1", "Tool 2"]
    )
    """
    course_key = course_title.lower().replace(" ", "_")
    
    COURSE_INSIGHTS[course_key] = {
        "title": course_title,
        "instructor": "Your Name",
        "key_strategies": strategies,
        "frameworks": frameworks, 
        "powerful_quotes": quotes,
        "tools_mentioned": tools or [],
        "action_items": []  # Can be populated later
    }
    
    print(f"✅ Added course content: {course_title}")
    return True

# Instructions for adding your actual content
INSTRUCTIONS = """
🚀 TO ADD YOUR ACTUAL COURSE CONTENT:

1. Replace the placeholder content in COURSE_INSIGHTS with your real course material
2. Use the add_your_course_content() function to easily add new courses
3. The AI will automatically use this content to enhance calendar generation

Example of what to include:
- Your best strategies and frameworks
- Powerful quotes from your courses  
- Tools you recommend
- Key action items for entrepreneurs

The more specific and actionable your content, the better the AI calendars will be!
"""

if __name__ == "__main__":
    print("📚 Course Insights Module")
    print("=" * 40)
    
    print("Available courses:")
    for course_key, course_data in COURSE_INSIGHTS.items():
        print(f"• {course_data['title']}")
    
    print(f"\nTotal strategies: {sum(len(c['key_strategies']) for c in COURSE_INSIGHTS.values())}")
    print(f"Total frameworks: {sum(len(c['frameworks']) for c in COURSE_INSIGHTS.values())}")
    print(f"Total quotes: {sum(len(c['powerful_quotes']) for c in COURSE_INSIGHTS.values())}")
    
    print("\n" + INSTRUCTIONS)