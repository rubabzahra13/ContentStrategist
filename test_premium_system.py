#!/usr/bin/env python3
"""
Test the $5M Premium Instagram Content System
"""

from core.enhanced_calendar_generator import generate_enhanced_calendar

def test_premium_system():
    print('🎯 TESTING COMPLETE $5M PREMIUM SYSTEM')
    print('=' * 60)

    try:
        # Test December for Christmas content
        result = generate_enhanced_calendar(['AI automation', 'business scaling'], 'December 2025')
        
        lines = result.split('\n')
        day_lines = [line for line in lines if 'Day ' in line and '|' in line]
        
        print(f'✅ Generated {len(day_lines)} days of premium content')
        
        if day_lines:
            # Show new premium format
            sample = day_lines[0]
            parts = sample.split('|')
            
            print(f'\n📱 PREMIUM INSTAGRAM FORMAT ({len(parts)} columns):')
            if len(parts) >= 5:
                print(f'Day: {parts[0].strip()}')
                print(f'Title: {parts[1].strip()}')
                print(f'Hook Cover: "{parts[2].strip()}"')
                print(f'Caption: {parts[3].strip()[:80]}...')
                print(f'Script: {parts[4].strip()[:120]}...')
            
            # Check Christmas content (Day 25)
            christmas_day = None
            for line in day_lines:
                if 'Day 25' in line:
                    christmas_day = line
                    break
            
            if christmas_day:
                print(f'\n🎄 CHRISTMAS DAY CONTENT:')
                xmas_parts = christmas_day.split('|')
                if len(xmas_parts) >= 3:
                    print(f'Hook Cover: "{xmas_parts[2].strip()}"')
                    if len(xmas_parts) > 3:
                        print(f'Caption: {xmas_parts[3].strip()[:100]}...')
            
            print(f'\n🎉 SUCCESS! Premium {len(day_lines)}-day calendar generated!')
            print('\n📊 CONTENT QUALITY CHECK:')
            
            # Quality analysis
            hook_quality = 0
            script_quality = 0
            
            for line in day_lines[:5]:  # Check first 5 days
                parts = line.split('|')
                if len(parts) >= 3:
                    hook = parts[2].strip()
                    if len(hook.split()) <= 4 and any(char.isupper() for char in hook):
                        hook_quality += 1
                
                if len(parts) >= 5:
                    script = parts[4].strip()
                    if any(word in script.lower() for word in ['$', 'million', 'thousand', '%']) and len(script) > 100:
                        script_quality += 1
            
            print(f'Hook Quality: {hook_quality}/5 (catchy, short covers)')
            print(f'Script Quality: {script_quality}/5 (specific numbers, detailed)')
            
            if hook_quality >= 4 and script_quality >= 4:
                print('🏆 PREMIUM QUALITY ACHIEVED!')
            else:
                print('⚠️ Quality needs improvement')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_premium_system()