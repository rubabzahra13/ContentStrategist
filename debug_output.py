#!/usr/bin/env python3
"""Debug what GPT is actually generating"""
import sys
sys.path.append('.')

from core.calendar_generator import generate_calendar

def debug_generation():
    month = "March 2025"
    trends = ["AI automation", "Business scaling", "Content creation"]
    
    print(f"🔍 Debugging GPT output for {month}...")
    
    try:
        result = generate_calendar(trends, month)
        print(f"\n📝 RAW GPT OUTPUT:\n{result}")
        print(f"\n📊 ANALYSIS:")
        
        lines = result.split('\n')
        for i, line in enumerate(lines):
            if '|' in line:
                print(f"   Line {i+1}: {line[:100]}...")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_generation()