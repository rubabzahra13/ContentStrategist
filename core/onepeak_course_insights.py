#!/usr/bin/env python3
"""
One Peak Creative Course Insights
Extracted from 92+ lesson transcripts for AI Content Strategist
"""

# Core One Peak Creative Insights extracted from course transcripts
ONEPEAK_COURSE_INSIGHTS = {
    "course_overview": {
        "name": "Find Your Peak TikTok and Reels Creator Course",
        "instructors": ["One Peak Creative Team", "Glenn", "Kahn", "Megan"],
        "focus": "Short-form video content for TikTok, Instagram Reels, YouTube Shorts, Facebook",
        "core_principle": "Timeless storytelling principles that have worked since caveman era",
        "success_metric": "Watch time is gold - algorithms reward watch time above all else"
    },
    
    "viral_video_framework": {
        "core_requirements": [
            "Relatable content that resonates with audience",
            "Shareable content that people want to send to friends", 
            "Repeatable format that can be used consistently",
            "Maximum watch time through engagement",
            "Strong hook within first 5 seconds"
        ],
        
        "content_categories": [
            "Everyday life with dramatic hooks",
            "Educational/informational content",
            "Stranger interaction videos", 
            "Challenges with win/lose scenarios",
            "Skill showcasing with unique angles",
            "Skits and character-based content",
            "Audience-generated concepts"
        ]
    },
    
    "hook_strategies": {
        "principle": "You have 5 seconds to convince viewers to stay",
        "bad_examples": [
            "Hi everybody, I'm [name], and today we're making...",
            "Starting with vacation clips and music",
            "Assuming people know or care who you are"
        ],
        "good_examples": [
            "Apparently jackfruit can look and taste like pulled pork, so I'm going to try and trick my husband",
            "That escalated quickly",
            "The stakes have never been higher",
            "You won't believe what happened next"
        ],
        "hook_types": [
            "Curiosity gaps that create questions",
            "Surprising statements or facts",
            "Promise of revelation or outcome",
            "Relatable problem identification",
            "Controversy or bold claims"
        ]
    },
    
    "content_psychology": {
        "watch_time_tactics": [
            "Create conversation in comments through controversy",
            "Use relatability to build community feeling",
            "Add stakes and gamification elements",
            "Include win/lose scenarios",
            "Build to satisfying conclusions"
        ],
        
        "engagement_drivers": [
            "People's innate curiosity about strangers' reactions",
            "Satisfaction of watching perfected skills",
            "Desire to see who wins in challenges",
            "Connection through shared experiences",
            "Vicarious living through others' content"
        ]
    },
    
    "technical_execution": {
        "posting_checklist": [
            "Add appropriate background music",
            "Include text hooks and supporting text",
            "Add captions for accessibility",
            "Write strategic caption hooks (don't give away ending)",
            "Use 4-5 niche-specific hashtags (avoid generic like #FYP)",
            "Tag relevant brands/collaborators",
            "Choose intriguing cover photo with hook"
        ],
        
        "content_standards": [
            "Quality over quantity - don't post half-assed content",
            "Only post videos you believe in",
            "Better to miss posting than lower standards",
            "Algorithm judges video quality through views",
            "Don't blame algorithm - improve content quality"
        ]
    },
    
    "format_strategies": {
        "everyday_life": {
            "principle": "Find hooks in mundane activities",
            "example": "Turn cooking into 'tricking husband with fake meat'",
            "requirement": "Create interest and intrigue with well-crafted hook"
        },
        
        "educational": {
            "principle": "Provide knowledge with captivating hooks",
            "hook_style": "Show what they'll learn or why they need to know",
            "versatility": "Can be sprinkled into any niche content"
        },
        
        "stranger_interaction": {
            "principle": "Leverage curiosity about others' reactions",
            "authenticity_note": "Most viral videos are actually staged",
            "execution_tip": "Make staging look authentic through good acting"
        },
        
        "challenges": {
            "principle": "Add stakes and gamification to any niche",
            "examples": "Highest card changes diaper, make par for free lunch",
            "psychology": "People want to see who wins"
        }
    },
    
    "success_principles": {
        "persistence": [
            "Harry Potter rejected 12 times before publishing",
            "Van Gogh sold only 1 painting in lifetime, created 900+",
            "Walt Disney fired for 'lack of imagination'",
            "Stephen King rejected 60 times before first book sold 1M+ copies"
        ],
        
        "mindset": [
            "Success is going from failure to failure with enthusiasm",
            "You never fail if you never quit",
            "Algorithm is unbiased judge rating quality through views",
            "Don't chase trends - create timeless, memorable content"
        ],
        
        "growth_strategy": [
            "Post 3 videos per week minimum",
            "Focus on one consistent format",
            "Build audience that knows what to expect",
            "Use same audience across all content",
            "Quality and consistency over viral chasing"
        ]
    },
    
    "monetization_framework": {
        "brand_partnerships": {
            "approach": "Seamlessly incorporate sponsored content",
            "audience_retention": "Make sponsored videos audience still loves",
            "organic_tagging": "Tag brands in organic content for opportunities"
        },
        
        "success_stories": [
            "Jerry Carey: First video ever got 2.5M views, 100M+ total views in 8 months",
            "Steph: 350K followers, $15K/month affiliate sales",
            "Alex: $20K/month full-time creator",
            "Lewis: 1M+ views, 8K followers for client"
        ]
    },
    
    "content_creation_principles": {
        "timeless_storytelling": [
            "Based on principles that worked since caveman era",
            "Not quick hacks or trends",
            "Focus on impactful story structure",
            "Create authentic emotional connections"
        ],
        
        "platform_psychology": [
            "Platforms make money from time spent",
            "Algorithm rewards watch time above all metrics", 
            "Compete with $50K giveaways and extreme content",
            "Hook must be strong enough for any competition"
        ]
    }
}

def get_onepeak_insights_for_prompt():
    """
    Generate formatted insights for AI prompt integration
    """
    insights = ONEPEAK_COURSE_INSIGHTS
    
    return f"""
📚 ONE PEAK CREATIVE COURSE INSIGHTS:

🎯 VIRAL VIDEO FRAMEWORK:
✅ {' | '.join(insights['viral_video_framework']['core_requirements'])}

🎣 PROVEN HOOK STRATEGIES:
• {insights['hook_strategies']['principle']}
• Create curiosity gaps and questions
• Use surprising statements or bold claims
• Promise revelation or satisfying outcome

📊 CONTENT PSYCHOLOGY:
• Watch time is gold - algorithms reward time spent above all
• People want to see who wins in challenges
• Satisfy curiosity about strangers' reactions  
• Build community through shared relatable experiences

🎬 CONTENT CATEGORIES THAT WORK:
• Everyday life with dramatic hooks
• Educational content with captivating angles
• Challenge/competition formats with stakes
• Skill showcasing with unique twists

💡 SUCCESS PRINCIPLES:
• "{insights['success_principles']['mindset'][0]}"
• Quality over quantity - don't post half-assed content
• Algorithm judges quality through views - improve content, don't blame platform
• Create timeless, memorable content vs chasing trends

📝 TECHNICAL EXECUTION:
• Strategic caption hooks (don't give away ending)
• 4-5 niche-specific hashtags (avoid generic #FYP)
• Add text overlays and captions for clarity
• Choose intriguing cover photos
"""

def get_onepeak_hook_examples():
    """
    Get specific hook examples from One Peak Creative course
    """
    return [
        "Apparently jackfruit can look and taste like pulled pork, so I'm going to try and trick my husband",
        "That escalated quickly",
        "The stakes have never been higher", 
        "Full amount spent at the end",
        "You won't believe what happened next",
        "This person who pulls the highest card changes the next diaper",
        "I told him I'd buy lunch if he makes par on the next hole"
    ]

def get_onepeak_content_frameworks():
    """
    Get content creation frameworks from One Peak Creative
    """
    return [
        "Relatable + Shareable + Repeatable = Viral Formula",
        "Hook in first 5 seconds or instant scroll",
        "Find drama in mundane everyday activities", 
        "Add stakes and gamification to any niche",
        "Quality over quantity - algorithm judges through views",
        "Educational content with captivating curiosity gaps",
        "Stranger interactions (authentic or staged well)",
        "Challenge formats with clear win/lose scenarios"
    ]

if __name__ == "__main__":
    print("📚 One Peak Creative Course Insights Loaded")
    print(f"✅ {len(ONEPEAK_COURSE_INSIGHTS)} main categories")
    print(f"✅ Viral framework with {len(ONEPEAK_COURSE_INSIGHTS['viral_video_framework']['core_requirements'])} core requirements")
    print(f"✅ {len(get_onepeak_hook_examples())} proven hook examples")
    print(f"✅ {len(get_onepeak_content_frameworks())} content frameworks")