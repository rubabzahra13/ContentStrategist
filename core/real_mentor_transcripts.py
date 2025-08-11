# === FILE: core/real_mentor_transcripts.py ===
"""
Real mentor transcripts from actual Instagram content
This replaces the need for live scraping with curated high-value content
"""

HORMOZI_REAL_TRANSCRIPTS = [
    {
        "hook": "I have $35 million in my bank account",
        "transcript": "I have $35 million in my bank account. That's it. I mean, it's funny because if you start with I have $10,000 in my bank account, I have $1,000 in my bank account. I have $3,000 in my bank account. What should I do to get rich? It's actually an irrelevant stat for what you should do next. Because at that level of money, that money is not going to get you rich. The only thing that will get you rich is increasing your active income so that that's not the amount of money you're playing with. And so the only thing you do with that money is increase your ability to generate more money. It's active income, not passive income. That's where you should be focused on.",
        "key_insights": ["Focus on active income, not passive income", "Money amount doesn't matter at low levels", "Invest in income generation ability"],
        "content_type": "Money Strategy",
        "engagement_pattern": "Direct revelation + contrarian insight"
    },
    {
        "hook": "If you want to close more sales, say less",
        "transcript": "If you want to close more sales, say less. So when we take on a portfolio company, one of the first things we look at is the sales script and not what we can add, but what can we remove? You can typically, dramatically, improve the close rate of a team by simply taking a script that's like this and cutting it to this. Makes for easier training, faster onboarding, and clearer communication in the prospect.",
        "key_insights": ["Less talking = more sales", "Remove content from scripts", "Simplicity improves close rates"],
        "content_type": "Sales Strategy",
        "engagement_pattern": "Contrarian statement + proof + practical application"
    },
    {
        "hook": "The greatest skill you can develop is the ability to stay in a great mood",
        "transcript": "The greatest skill you can develop is the ability to stay in a great mood in the absence of things to be in a great mood about. And if you can be in a bad mood for no reason, you might as well be in a good mood for no reason.",
        "key_insights": ["Mood control is the ultimate skill", "Don't depend on external circumstances", "Choose your emotional state"],
        "content_type": "Mindset",
        "engagement_pattern": "Philosophical insight + logical conclusion"
    },
    {
        "hook": "I've got three boxes here",
        "transcript": "I've got three boxes here. One of them contains a thousand dollars, one of them contains ten thousand dollars, and one of them contains a hundred thousand dollars. And you three are the Avengers of Entrepreneurship on the Internet. So you're gonna tell me what you would do with that amount of money to build a scalable business. So do I get to give the money? Is that how this works? Yeah, yeah, yeah. Okay, so there's two paths to make money quickly if you don't have any. And the first path is go find the best entrepreneur and go work for them. Learn as much as you can. Totally agree. Like Kim Kardashian was Harris Hilton's assistant, and she learned the playbook of being famous, and then she took it to a new level. And then the second way is high risk, but highest reward. Go do it yourself.",
        "key_insights": ["Two paths to wealth: learn from the best or go solo", "Work for successful people first", "Kim Kardashian learned from Paris Hilton"],
        "content_type": "Business Strategy",
        "engagement_pattern": "Interactive setup + practical frameworks"
    }
]

VAIBHAV_REAL_TRANSCRIPTS = [
    {
        "hook": "Sam Altman killed millions of jobs with one insane update",
        "transcript": "Sam Altman killed millions of jobs with one insane update. He released GPT-5 today and literally made it free for all. Here are the 12 insane features of GPT-5 that you should try. Number 4 is my personal favorite. Let's get into it. Number 12 Smart Reasoning Mode. GPT-5 now roots your prompt through the best model based on complexity. If it's a simple ask, you get an answer instantly. If it's more complex, it slows down and thinks harder and then answers. No more picking the right model for right task bullshit.",
        "key_insights": ["GPT-5 has smart reasoning mode", "Auto-selects best model", "Eliminates model selection complexity"],
        "content_type": "AI Tools",
        "engagement_pattern": "Dramatic hook + numbered list + personal favorite"
    },
    {
        "hook": "Most people won't hear about these tools till 2026",
        "transcript": "If you go to this website, you could build almost anything without programming skills. I asked it to create a food delivery app and it instantly created one. And that's only the two number seven on the list. Welcome to week five of Hidden AI Tools of the Week. Want to move quicker? Just hold down right here to watch it at 2x speed. Let's jump into this number 10, Rici Mini. Looks like a toy. Functions like Ironman's Jarvis. Train it with Python and it becomes your robotic desk assistant. Open source. Meaning no limits. Most people won't hear about these tools till 2026. You're getting them six months early. Now let's get right back. These aren't just cool new tools. They're competitive weapons. And you just got access before the rest of the world.",
        "key_insights": ["No-code app building", "6-month early access advantage", "Tools are competitive weapons"],
        "content_type": "AI Discovery",
        "engagement_pattern": "Exclusive access + competitive advantage + urgency"
    },
    {
        "hook": "Sundar Pichai just knocked out Sam Altman in one single day",
        "transcript": "Sundar pichai just knocked out Sam Altman in one single day. We have announced over a dozen models and research breakthroughs. He released these 13 crazy AI updates in Google IO. Number 10 will blow your mind. You can see the change here. Let's get into this. One, try on AI for shopping. You upload your photo. Google shows how clothes will look on your body. Folds, shape, everything. Like it, click once, it buys it for you. Two, new AI search tab. Google now has a special AI tab. You can ask longer questions, follow up like a chat, and it remembers your topic.",
        "key_insights": ["Google IO had 13 major AI updates", "Try-on AI for shopping", "AI search with memory"],
        "content_type": "Tech Competition",
        "engagement_pattern": "Competition narrative + numbered reveals + mind-blowing promise"
    }
]

COMBINED_REAL_PATTERNS = {
    "hormozi_style_indicators": [
        "Direct money statements",
        "Contrarian business advice", 
        "Portfolio company examples",
        "Cut-through-the-BS approach",
        "Specific dollar amounts",
        "Focus on fundamentals"
    ],
    
    "vaibhav_style_indicators": [
        "AI tool reveals",
        "Tech industry drama",
        "Numbered lists and rankings",
        "Early access exclusivity",
        "Competitive advantage angles",
        "Tool comparisons and reviews"
    ],
    
    "universal_high_value_patterns": [
        "Specific numbers and data points",
        "Contrarian insights that challenge conventional wisdom",
        "Personal examples with real outcomes",
        "Actionable frameworks and strategies",
        "Industry insider knowledge",
        "Competitive intelligence"
    ]
}

def get_random_real_transcript(mentor="both"):
    """Get a random real transcript for content inspiration"""
    import random
    
    if mentor == "hormozi":
        return random.choice(HORMOZI_REAL_TRANSCRIPTS)
    elif mentor == "vaibhav":
        return random.choice(VAIBHAV_REAL_TRANSCRIPTS)
    else:
        all_transcripts = HORMOZI_REAL_TRANSCRIPTS + VAIBHAV_REAL_TRANSCRIPTS
        return random.choice(all_transcripts)

def get_real_content_for_prompt():
    """Get formatted real content for AI prompt enhancement"""
    hormozi_sample = get_random_real_transcript("hormozi")
    vaibhav_sample = get_random_real_transcript("vaibhav")
    
    return f"""
📱 REAL MENTOR CONTENT EXAMPLES:

🔥 HORMOZI STYLE (Direct Business):
Hook: "{hormozi_sample['hook']}"
Full Content: "{hormozi_sample['transcript'][:200]}..."
Key Insights: {', '.join(hormozi_sample['key_insights'])}

🚀 VAIBHAV STYLE (AI/Tech):
Hook: "{vaibhav_sample['hook']}"
Full Content: "{vaibhav_sample['transcript'][:200]}..."
Key Insights: {', '.join(vaibhav_sample['key_insights'])}

💡 CONTENT PATTERNS TO EMULATE:
• Use specific numbers and dollar amounts
• Lead with contrarian or surprising statements
• Provide immediate actionable value
• Include insider knowledge and examples
• Create urgency through exclusivity or timing
"""

if __name__ == "__main__":
    # Test the module
    print("Real Mentor Transcripts Module")
    print("=" * 40)
    print(f"Hormozi transcripts: {len(HORMOZI_REAL_TRANSCRIPTS)}")
    print(f"Vaibhav transcripts: {len(VAIBHAV_REAL_TRANSCRIPTS)}")
    print("\nSample content:")
    print(get_real_content_for_prompt())