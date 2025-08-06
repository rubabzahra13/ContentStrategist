#!/usr/bin/env python3
"""
Quick test to verify the token limit fix and full month generation
"""
import os
import sys
sys.path.append('.')

from core.calendar_generator import generate_calendar, get_days_in_month
from core.excel_exporter import export_to_excel

def test_token_fix():
    """Test the fixed calendar generation with token limits"""
    print("🧪 Testing Token Limit Fix...")
    
    # Test different months
    test_months = ["March 2025", "February 2025", "August 2025"]
    
    for month in test_months:
        print(f"\n📅 Testing {month}...")
        
        # Check days calculation
        days = get_days_in_month(month)
        print(f"   Expected days: {days}")
        
        # Test with minimal trends to avoid token bloat
        test_trends = [
            "AI automation for entrepreneurs",
            "Business scaling with ChatGPT", 
            "Content creation workflows"
        ]
        
        try:
            # Generate calendar
            calendar_text = generate_calendar(test_trends, month)
            
            # Count actual content rows
            lines_with_pipes = [line for line in calendar_text.split('\n') 
                              if '|' in line and 'Date' not in line and 'Day' not in line]
            actual_rows = len(lines_with_pipes)
            
            print(f"   Generated rows: {actual_rows}")
            
            if actual_rows >= (days - 3):  # Allow some tolerance
                print(f"   ✅ SUCCESS: Generated enough content for {month}")
            else:
                print(f"   ⚠️ WARNING: Only {actual_rows} rows for {days}-day month")
            
            # Test Excel export
            test_filename = f"data/output/test_{month.replace(' ', '_').lower()}.xlsx"
            export_to_excel(calendar_text, test_filename)
            
            if os.path.exists(test_filename):
                size = os.path.getsize(test_filename)
                print(f"   📊 Excel file created: {size} bytes")
                # Clean up test file
                os.remove(test_filename)
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            if "token" in str(e).lower():
                print("   🚨 STILL HITTING TOKEN LIMIT!")
            return False
    
    print(f"\n🎉 Token fix test completed!")
    return True

if __name__ == "__main__":
    test_token_fix()