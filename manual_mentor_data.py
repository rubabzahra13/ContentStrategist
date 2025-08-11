#!/usr/bin/env python3
"""
Manual Mentor Data Collection
Alternative to Apify - manually curate high-performing content
"""

# Manually curated high-performing content from Hormozi & Vaibhav
MANUAL_MENTOR_REELS = {
    "hormozi": [
        {
            "reel_url": "https://www.instagram.com/reel/hormozi_example1/",
            "video_url": "placeholder_video_url",
            "caption": "How I went from $0 to $100M without taking investor money...",
            "hashtags": ["#business", "#entrepreneur", "#nocode", "#scaling"],
            "view_count": 2500000,
            "like_count": 125000,
            "timestamp": "2025-01-15",
            "owner_username": "hormozi",
            "transcript": "Listen, everyone asks me how I scaled to $100M without investors. The secret isn't complicated. You need three things: a great offer, systemized delivery, and relentless execution. Most people fail because they try to do everything at once. Pick one thing, master it, then scale.",
            "hook": "How I went from $0 to $100M without taking investor money",
            "key_insights": ["Focus on one thing", "Master before scaling", "No investor money needed"]
        },
        {
            "reel_url": "https://www.instagram.com/reel/hormozi_example2/",
            "video_url": "placeholder_video_url",
            "caption": "The biggest mistake I see entrepreneurs make with their offers...",
            "hashtags": ["#offers", "#business", "#sales", "#value"],
            "view_count": 1800000,
            "like_count": 95000,
            "timestamp": "2025-01-10",
            "owner_username": "hormozi",
            "transcript": "The biggest mistake entrepreneurs make is creating offers that sound good to them, not their customers. Your offer should solve a painful problem your customer has right now. Make it so good they feel stupid saying no.",
            "hook": "The biggest mistake I see entrepreneurs make with their offers",
            "key_insights": ["Customer-focused offers", "Solve painful problems", "Make it irresistible"]
        },
        {
            "reel_url": "https://www.instagram.com/reel/hormozi_example3/",
            "video_url": "placeholder_video_url", 
            "caption": "Why most people fail at scaling their business (and how to fix it)...",
            "hashtags": ["#scaling", "#business", "#systems", "#growth"],
            "view_count": 2100000,
            "like_count": 110000,
            "timestamp": "2025-01-08",
            "owner_username": "hormozi",
            "transcript": "Most people fail at scaling because they try to do more things instead of doing the same things better. Scale your systems, not your complexity. Document everything, train your team, and measure what matters.",
            "hook": "Why most people fail at scaling their business",
            "key_insights": ["Scale systems not complexity", "Document everything", "Measure what matters"]
        }
    ],
    "vaibhavsisinty": [
        {
            "reel_url": "https://www.instagram.com/reel/vaibhav_example1/",
            "video_url": "placeholder_video_url",
            "caption": "The content strategy that got me 1M followers in 12 months...",
            "hashtags": ["#content", "#socialmedia", "#growth", "#strategy"],
            "view_count": 950000,
            "like_count": 48000,
            "timestamp": "2025-01-12",
            "owner_username": "vaibhavsisinty",
            "transcript": "Everyone asks about my content strategy. Here's the truth: I post value-first content every single day. No fluff, no filler. Every post teaches something actionable. Consistency beats perfection every time.",
            "hook": "The content strategy that got me 1M followers in 12 months",
            "key_insights": ["Value-first content", "Daily consistency", "Actionable teachings"]
        },
        {
            "reel_url": "https://www.instagram.com/reel/vaibhav_example2/",
            "video_url": "placeholder_video_url",
            "caption": "How to create viral hooks that actually convert...",
            "hashtags": ["#hooks", "#copywriting", "#viral", "#content"],
            "view_count": 1200000,
            "like_count": 67000,
            "timestamp": "2025-01-09",
            "owner_username": "vaibhavsisinty",
            "transcript": "Great hooks don't just get attention, they get the RIGHT attention. Start with a bold claim, create curiosity, and promise specific value. The best hooks make people feel like they'll miss out if they don't watch.",
            "hook": "How to create viral hooks that actually convert",
            "key_insights": ["Bold claims create interest", "Curiosity drives engagement", "Promise specific value"]
        },
        {
            "reel_url": "https://www.instagram.com/reel/vaibhav_example3/",
            "video_url": "placeholder_video_url",
            "caption": "The psychology behind why people buy (use this in your content)...",
            "hashtags": ["#psychology", "#sales", "#persuasion", "#business"],
            "view_count": 850000,
            "like_count": 42000,
            "timestamp": "2025-01-05",
            "owner_username": "vaibhavsisinty",
            "transcript": "People don't buy products, they buy better versions of themselves. Show them the transformation, not the features. Paint the picture of their life after using your solution. Sell the outcome, not the process.",
            "hook": "The psychology behind why people buy",
            "key_insights": ["Sell transformation", "Show the outcome", "Better version of themselves"]
        }
    ]
}

def get_manual_mentor_data():
    """Return manually curated mentor data"""
    all_reels = []
    for creator, reels in MANUAL_MENTOR_REELS.items():
        all_reels.extend(reels)
    return all_reels

def convert_to_pipeline_format():
    """Convert manual data to pipeline format"""
    from core.instagram_rag_pipeline import ReelData
    
    reels = []
    for creator, reel_list in MANUAL_MENTOR_REELS.items():
        for reel in reel_list:
            reel_data = ReelData(
                reel_url=reel["reel_url"],
                video_url=reel["video_url"],
                caption=reel["caption"],
                hashtags=reel["hashtags"],
                view_count=reel["view_count"],
                like_count=reel["like_count"],
                timestamp=reel["timestamp"],
                owner_username=reel["owner_username"]
            )
            reels.append(reel_data)
    
    return reels

if __name__ == "__main__":
    data = get_manual_mentor_data()
    print(f"📊 Manual mentor data loaded: {len(data)} reels")
    for creator, reels in MANUAL_MENTOR_REELS.items():
        print(f"  - {creator}: {len(reels)} reels")