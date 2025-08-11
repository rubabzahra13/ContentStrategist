#!/usr/bin/env python3
"""
Special Dates and Holiday Content Handler
Automatically detects holidays and special events for targeted content creation
"""

from datetime import datetime, date
import calendar

# Special dates and holidays with content suggestions
SPECIAL_DATES = {
    # Major Holidays
    "01-01": {
        "name": "New Year's Day",
        "content_themes": ["New Year resolutions", "goal setting", "fresh starts", "business planning", "motivation"],
        "hook_suggestions": [
            "Why 92% of New Year's resolutions fail (and how to be in the 8%)",
            "The business goal that changed my entire 2025",
            "New Year, new revenue streams - here's my plan"
        ],
        "hashtags": ["#NewYear", "#Goals2025", "#NewYearMotivation", "#BusinessGoals", "#FreshStart"]
    },
    
    "02-14": {
        "name": "Valentine's Day", 
        "content_themes": ["relationship marketing", "customer love", "brand loyalty", "appreciation content"],
        "hook_suggestions": [
            "How to make your customers fall in love with your brand",
            "The Valentine's Day marketing strategy that tripled my sales",
            "Why treating customers like partners changes everything"
        ],
        "hashtags": ["#ValentinesDay", "#CustomerLove", "#BrandLoyalty", "#Appreciation", "#RelationshipMarketing"]
    },
    
    "03-17": {
        "name": "St. Patrick's Day",
        "content_themes": ["luck in business", "Irish entrepreneurship", "green marketing", "celebration content"],
        "hook_suggestions": [
            "The 'luck' that made me $100K (spoiler: it wasn't luck)",
            "Why successful entrepreneurs make their own luck",
            "Green isn't just a color - it's my business strategy"
        ],
        "hashtags": ["#StPatricksDay", "#BusinessLuck", "#GreenBusiness", "#Celebration", "#Irish"]
    },
    
    "07-04": {
        "name": "Independence Day",
        "content_themes": ["financial freedom", "business independence", "American entrepreneurship", "freedom content"],
        "hook_suggestions": [
            "How I gained financial independence in 2 years",
            "The business that gave me true freedom",
            "Why every entrepreneur needs to declare independence"
        ],
        "hashtags": ["#July4th", "#FinancialFreedom", "#Independence", "#Freedom", "#AmericanDream"]
    },
    
    "10-31": {
        "name": "Halloween",
        "content_themes": ["business fears", "scary truths", "transformation", "revealing content"],
        "hook_suggestions": [
            "The scariest business mistake I ever made",
            "3 business fears that are actually holding you back",
            "The Halloween transformation that saved my company"
        ],
        "hashtags": ["#Halloween", "#BusinessFears", "#Transformation", "#ScaryTruths", "#Spooky"]
    },
    
    "11-28": {  # Thanksgiving (4th Thursday of November - approximate)
        "name": "Thanksgiving",
        "content_themes": ["gratitude", "business wins", "customer appreciation", "reflection content"],
        "hook_suggestions": [
            "What I'm most grateful for in my business journey",
            "The customers who changed my life",
            "Why gratitude is the best business strategy"
        ],
        "hashtags": ["#Thanksgiving", "#Gratitude", "#Blessed", "#Reflection", "#CustomerAppreciation"]
    },
    
    "12-25": {
        "name": "Christmas",
        "content_themes": ["gift guides", "year-end reflection", "family business", "giving back", "holiday marketing"],
        "hook_suggestions": [
            "The Christmas gift that transformed my business",
            "How I built a million-dollar business by December 25th",
            "The best gift you can give your customers"
        ],
        "hashtags": ["#Christmas", "#HolidayMarketing", "#GiftGuide", "#YearEnd", "#GivingBack"]
    },
    
    "12-31": {
        "name": "New Year's Eve",
        "content_themes": ["year in review", "2025 predictions", "reflection", "planning ahead"],
        "hook_suggestions": [
            "My biggest business lesson from this year",
            "What I'm leaving behind in 2024",
            "2025 predictions that will change your business"
        ],
        "hashtags": ["#NewYearsEve", "#YearInReview", "#2025Predictions", "#Reflection", "#Planning"]
    },
    
    # Business/Marketing Special Days
    "11-29": {  # Black Friday (day after Thanksgiving)
        "name": "Black Friday",
        "content_themes": ["sales strategies", "deals", "marketing tactics", "customer behavior"],
        "hook_suggestions": [
            "The Black Friday strategy that made me $50K in one day",
            "Why I don't do Black Friday deals (and you shouldn't either)",
            "The psychology behind Black Friday buying"
        ],
        "hashtags": ["#BlackFriday", "#Sales", "#Marketing", "#Deals", "#Strategy"]
    },
    
    "12-02": {  # Cyber Monday (Monday after Thanksgiving)
        "name": "Cyber Monday", 
        "content_themes": ["online sales", "digital marketing", "e-commerce", "tech deals"],
        "hook_suggestions": [
            "The Cyber Monday hack that doubled my online sales",
            "Why Cyber Monday is better than Black Friday for entrepreneurs",
            "My secret Cyber Monday marketing playbook"
        ],
        "hashtags": ["#CyberMonday", "#OnlineSales", "#DigitalMarketing", "#Ecommerce", "#Tech"]
    }
}

# Monthly themes for when no specific date is found
MONTHLY_THEMES = {
    1: {
        "theme": "New Beginnings",
        "focus": ["goal setting", "planning", "fresh starts", "resolutions"],
        "trending": ["New Year goals", "planning 2025", "business resolutions"]
    },
    2: {
        "theme": "Growth & Love",
        "focus": ["relationship building", "customer love", "scaling", "partnerships"],
        "trending": ["Valentine marketing", "customer relationships", "love your audience"]
    },
    3: {
        "theme": "Spring Into Action",
        "focus": ["new projects", "spring cleaning", "fresh energy", "launches"],
        "trending": ["spring launches", "new beginnings", "fresh starts"]
    },
    4: {
        "theme": "Growth Season",
        "focus": ["expansion", "growth hacking", "optimization", "testing"],
        "trending": ["spring growth", "scaling up", "optimization"]
    },
    5: {
        "theme": "Momentum Building",
        "focus": ["acceleration", "Mother's Day appreciation", "community building"],
        "trending": ["building momentum", "community growth", "appreciation"]
    },
    6: {
        "theme": "Summer Strategy",
        "focus": ["summer campaigns", "Father's Day", "mid-year review", "vacation marketing"],
        "trending": ["summer strategy", "mid-year goals", "vacation planning"]
    },
    7: {
        "theme": "Independence & Freedom",
        "focus": ["financial freedom", "independence", "summer content", "freedom"],
        "trending": ["financial independence", "summer business", "freedom lifestyle"]
    },
    8: {
        "theme": "Back to Business",
        "focus": ["back to school", "refocus", "preparation", "systems"],
        "trending": ["back to school", "refocus", "business systems"]
    },
    9: {
        "theme": "Autumn Preparation",
        "focus": ["Q4 prep", "harvest season", "preparation", "planning"],
        "trending": ["Q4 preparation", "autumn planning", "harvest"]
    },
    10: {
        "theme": "Transformation",
        "focus": ["Halloween transformation", "scary truths", "change", "evolution"],
        "trending": ["business transformation", "Halloween marketing", "change"]
    },
    11: {
        "theme": "Gratitude & Giving",
        "focus": ["thanksgiving", "gratitude", "giving back", "appreciation"],
        "trending": ["gratitude business", "giving back", "appreciation"]
    },
    12: {
        "theme": "Reflection & Planning",
        "focus": ["year-end review", "holiday marketing", "planning 2025", "reflection"],
        "trending": ["year-end review", "holiday marketing", "2025 planning"]
    }
}

def get_special_date_content(month_str):
    """
    Get special date content for a given month
    Returns holiday-specific content suggestions
    """
    try:
        # Parse month and year
        month_parts = month_str.split()
        month_name = month_parts[0]
        year = int(month_parts[1]) if len(month_parts) > 1 else datetime.now().year
        
        # Convert month name to number
        month_names = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        month_num = month_names.get(month_name, 1)
        
        # Get days in month
        days_in_month = calendar.monthrange(year, month_num)[1]
        
        # Find special dates in this month
        special_dates_in_month = []
        
        for day in range(1, days_in_month + 1):
            date_key = f"{month_num:02d}-{day:02d}"
            if date_key in SPECIAL_DATES:
                special_dates_in_month.append({
                    "day": day,
                    "date_key": date_key,
                    "info": SPECIAL_DATES[date_key]
                })
        
        return {
            "month": month_name,
            "year": year,
            "month_num": month_num,
            "days_in_month": days_in_month,
            "special_dates": special_dates_in_month,
            "monthly_theme": MONTHLY_THEMES.get(month_num, {})
        }
        
    except Exception as e:
        print(f"Error getting special date content: {e}")
        return None

def get_special_date_prompt_section(month_str):
    """
    Generate special date section for AI prompt
    """
    date_info = get_special_date_content(month_str)
    
    if not date_info or not date_info["special_dates"]:
        # Return monthly theme if no specific dates
        monthly_theme = date_info["monthly_theme"] if date_info else {}
        if monthly_theme:
            return f"""
🎉 MONTHLY THEME FOR {month_str.upper()}:
Theme: {monthly_theme.get("theme", "General Business")}
Focus Areas: {", ".join(monthly_theme.get("focus", []))}
Trending Topics: {", ".join(monthly_theme.get("trending", []))}
"""
        return ""
    
    special_content = f"""
🎉 SPECIAL DATES & HOLIDAYS IN {month_str.upper()}:

"""
    
    for special_date in date_info["special_dates"]:
        day = special_date["day"]
        info = special_date["info"]
        
        special_content += f"""📅 DAY {day} - {info["name"]}:
Content Themes: {", ".join(info["content_themes"])}
Hook Ideas: 
{chr(10).join([f"• {hook}" for hook in info["hook_suggestions"][:2]])}
Hashtags: {", ".join(info["hashtags"][:3])}

"""
    
    # Add monthly theme
    monthly_theme = date_info["monthly_theme"]
    if monthly_theme:
        special_content += f"""🎯 OVERALL MONTHLY THEME:
{monthly_theme.get("theme", "")}: {", ".join(monthly_theme.get("focus", []))}

"""
    
    return special_content

if __name__ == "__main__":
    # Test the special dates
    print("🎉 Testing Special Dates System:")
    print(get_special_date_prompt_section("December 2025"))
    print("\n" + "="*50 + "\n")
    print(get_special_date_prompt_section("March 2025"))