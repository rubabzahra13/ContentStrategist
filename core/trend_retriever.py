# === FILE: core/trend_retriever.py ===
import requests
from utils.config import SERPER_API_KEY
import time
from datetime import datetime, timedelta
import re

def analyze_month_context(month_str):
    """
    Analyze the month context to determine search strategy
    Returns: (month_name, year, time_context, search_strategy)
    """
    try:
        # First normalize the month using helpers
        from utils.helpers import normalize_month
        normalized = normalize_month(month_str)
        
        parts = normalized.split()
        month_name = parts[0]
        year = int(parts[1]) if len(parts) > 1 else datetime.now().year
        
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        
        # Convert month name to number for comparison
        month_names = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        
        target_month = month_names.get(month_name, 1)
        target_date = datetime(year, target_month, 1)
        
        # Determine time context
        if year < current_year or (year == current_year and target_month < current_month):
            time_context = "PAST"
        elif year == current_year and target_month == current_month:
            time_context = "CURRENT"
        elif year > current_year or (year == current_year and target_month > current_month):
            time_context = "FUTURE"
        else:
            time_context = "CURRENT"
        
        # Determine search strategy based on context
        if time_context == "PAST":
            search_strategy = "historical_trends"
        elif time_context == "CURRENT":
            search_strategy = "real_time_trends"
        else:  # FUTURE
            search_strategy = "predictive_trends"
        
        return month_name, year, time_context, search_strategy
        
    except Exception as e:
        print(f"⚠️ Error analyzing month context: {e}")
        return "January", datetime.now().year, "CURRENT", "real_time_trends"

def get_trending_snippets(month):
    """
    Fetch time-aware trending snippets for content calendar generation
    Handles past, present, and future months intelligently
    """
    
    month_name, year, time_context, search_strategy = analyze_month_context(month)
    
    print(f"🕒 Time Context: {time_context} | Strategy: {search_strategy}")
    
    # Generate context-aware fallback content
    if time_context == "PAST":
        fallback_trends = [
            f"AI tools that dominated {month_name} {year} for entrepreneurs",
            f"Top business scaling strategies from {month_name} {year}",
            f"Instagram Reels formats that went viral in {month_name} {year}",
            f"Content automation trends from {month_name} {year}",
            f"Entrepreneurship lessons learned in {month_name} {year}"
        ]
    elif time_context == "FUTURE":
        fallback_trends = [
            f"Predicted AI tools for entrepreneurs in {month_name} {year}",
            f"Future business scaling trends expected in {month_name} {year}",
            f"Upcoming Instagram Reels formats for {month_name} {year}",
            f"AI automation predictions for {month_name} {year}",
            f"Forward-looking entrepreneurship strategies for {month_name} {year}"
        ]
    else:  # CURRENT
        fallback_trends = [
            f"Latest AI productivity tools trending now in {month_name} {year}",
            f"Current viral Instagram Reels formats for {month_name} {year}",
            f"Real-time business scaling strategies for {month_name} {year}",
            f"Today's hottest content automation tools",
            f"Live entrepreneurship trends in {month_name} {year}"
        ]
    
    if not SERPER_API_KEY:
        print("⚠️ No SERPER_API_KEY found, using context-aware fallback trends")
        return fallback_trends
    
    try:
        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": SERPER_API_KEY}
        
        # Context-aware search queries
        if search_strategy == "historical_trends":
            base_queries = [
                f"AI tools entrepreneurs used {month_name} {year}",
                f"business scaling strategies {month_name} {year} lessons",
                f"viral Instagram reels {month_name} {year} case studies",
                f"content marketing what worked {month_name} {year}",
                f"entrepreneurship trends {month_name} {year} review"
            ]
        elif search_strategy == "predictive_trends":
            base_queries = [
                f"AI tools predictions {month_name} {year} entrepreneurs",
                f"upcoming business trends {month_name} {year}",
                f"future Instagram reels formats {month_name} {year}",
                f"predicted content marketing {month_name} {year}",
                f"entrepreneurship forecast {month_name} {year}"
            ]
        else:  # real_time_trends
            base_queries = [
                f"trending AI tools entrepreneurs {month_name} {year}",
                f"viral Instagram reels business content {month_name} {year}",
                f"latest business scaling strategies {month_name} {year}",
                f"current content marketing trends {month_name} {year}",
                f"real-time AI automation tools {month_name} {year}"
            ]
        
        # Add recency modifiers based on context
        if time_context == "CURRENT":
            recency_terms = ["latest", "trending now", "this month", "current", "today"]
        elif time_context == "FUTURE":
            recency_terms = ["upcoming", "predicted", "forecast", "expected", "future"]
        else:  # PAST
            recency_terms = ["review", "case study", "lessons from", "what worked", "analysis"]
        
        # Enhanced queries with recency
        queries = []
        for i, base_query in enumerate(base_queries):
            if i < len(recency_terms):
                enhanced_query = f"{recency_terms[i]} {base_query}"
            else:
                enhanced_query = base_query
            queries.append(enhanced_query)
        
        all_snippets = []
        
        for query in queries:
            try:
                payload = {
                    "q": query,
                    "num": 3
                }
                
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                response.raise_for_status()
                
                results = response.json().get("organic", [])
                snippets = [item.get("snippet", "") for item in results if item.get("snippet")]
                all_snippets.extend(snippets)
                
                # Add small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ Error with query '{query}': {str(e)}")
                continue
        
        # Filter and clean snippets with time-awareness
        clean_snippets = []
        for snippet in all_snippets:
            if snippet and len(snippet.strip()) > 20:
                # Add context marker to snippet
                if time_context == "PAST":
                    contextual_snippet = f"[Historical Insight] {snippet.strip()}"
                elif time_context == "FUTURE":
                    contextual_snippet = f"[Future Prediction] {snippet.strip()}"
                else:
                    contextual_snippet = f"[Current Trend] {snippet.strip()}"
                
                clean_snippets.append(contextual_snippet)
        
        # Remove duplicates while preserving order
        unique_snippets = []
        seen = set()
        for snippet in clean_snippets:
            # Compare without context markers for deduplication
            core_snippet = snippet.split('] ', 1)[-1].lower()
            if core_snippet not in seen:
                seen.add(core_snippet)
                unique_snippets.append(snippet)
        
        # Validate trend freshness for current context
        if time_context == "CURRENT" and unique_snippets:
            fresh_snippets = validate_trend_freshness(unique_snippets, month_name, year)
            if fresh_snippets:
                unique_snippets = fresh_snippets
            else:
                print("⚠️ Trends appear stale, mixing with fallback content")
                unique_snippets.extend(fallback_trends[:3])
        
        # Return top 8 unique snippets or fallback
        if unique_snippets:
            print(f"✅ Retrieved {len(unique_snippets)} {time_context.lower()} trending snippets")
            return unique_snippets[:8]
        else:
            print(f"⚠️ No valid snippets found, using {time_context.lower()} fallback trends")
            return fallback_trends
            
    except Exception as e:
        print(f"❌ Error fetching trends: {str(e)}")
        print(f"🔄 Using {time_context.lower()} fallback trends instead")
        return fallback_trends

def validate_trend_freshness(snippets, month_name, year):
    """
    Validate if trends are fresh enough for current month
    Returns filtered snippets or None if all are stale
    """
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # If we're looking at current month/year, check for recent keywords
    if year == current_year:
        fresh_keywords = [
            "2024", "latest", "new", "trending", "current", "recent", 
            "this month", "today", "now", "breakthrough"
        ]
        
        fresh_snippets = []
        for snippet in snippets:
            snippet_lower = snippet.lower()
            if any(keyword in snippet_lower for keyword in fresh_keywords):
                fresh_snippets.append(snippet)
        
        if len(fresh_snippets) >= 3:
            return fresh_snippets
    
    return None  # Indicates trends might be stale

def get_trend_age_warning(month_str):
    """
    Provide warnings about trend age for user awareness
    """
    month_name, year, time_context, _ = analyze_month_context(month_str)
    current_year = datetime.now().year
    
    if time_context == "PAST":
        years_ago = current_year - year
        if years_ago > 1:
            return f"⚠️ WARNING: Trends are {years_ago} years old. Content may not reflect current market."
        elif years_ago == 1:
            return f"📅 NOTE: Using trends from {month_name} {year} (last year's data)."
        else:
            return f"📅 Using historical trends from {month_name} {year}."
    
    elif time_context == "FUTURE":
        years_ahead = year - current_year
        if years_ahead > 2:
            return f"🔮 NOTE: Very future-focused content for {month_name} {year}. Predictions may be speculative."
        else:
            return f"🔮 Using predictive trends for {month_name} {year}."
    
    else:  # CURRENT
        return f"🎯 Using real-time trends for {month_name} {year}."