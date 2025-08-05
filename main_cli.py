# === FILE: main_cli.py (Original CLI version) ===

from core.trend_retriever import get_trending_snippets
from core.calendar_generator import generate_calendar
from core.excel_exporter import export_to_excel
from core.cache_handler import get_cached_file, save_to_cache
from utils.helpers import normalize_month
import os
import sys

def main():
    """Main function to generate content calendar"""
    try:
        print("🚀 AI Content Calendar Generator (CLI)")
        print("=" * 50)
        
        # 1. Get and normalize input
        raw_month = input("Enter the month for content calendar (e.g., 'September 2025'): ").strip()
        
        if not raw_month:
            print("❌ No month provided. Exiting.")
            return
        
        normalized_month = normalize_month(raw_month)
        
        if normalized_month != raw_month:
            print(f"🛠️ Interpreting '{raw_month}' as '{normalized_month}'")
        
        month = normalized_month
        month_key = month.replace(" ", "_").lower()  # Used for filenames + cache keys
        
        print(f"📅 Generating calendar for: {month}")
        print(f"🔑 Cache key: {month_key}")

        # 2. Check cache
        print("\n🔍 Checking cache...")
        try:
            cached_url = get_cached_file(month_key)
            if cached_url:
                print(f"✅ Found cached calendar!")
                print(f"🌐 Supabase URL: {cached_url}")
                print(f"📁 Local file should be: data/output/calendar_{month_key}.xlsx")
                return
        except Exception as e:
            print(f"⚠️ Cache check failed: {str(e)}")
            print("🔄 Proceeding to generate new calendar...")

        # 3. Fetch trends with time awareness
        print("\n🔍 Fetching trending topics...")
        try:
            from core.trend_retriever import get_trend_age_warning
            
            # Show time context warning
            age_warning = get_trend_age_warning(month)
            print(f"   {age_warning}")
            
            snippets = get_trending_snippets(month)
            print(f"📊 Found {len(snippets)} trending topics")
            
            # Show sample trends for verification
            if snippets:
                print("📋 Sample trends:")
                for i, trend in enumerate(snippets[:3], 1):
                    preview = trend[:80] + "..." if len(trend) > 80 else trend
                    print(f"   {i}. {preview}")
                    
        except Exception as e:
            print(f"❌ Error fetching trends: {str(e)}")
            print("🔄 Using fallback trends...")
            snippets = [
                f"AI productivity tools for entrepreneurs {month}",
                f"Business scaling strategies {month}",
                f"Viral Instagram Reels formats {month}"
            ]

        # 4. Generate calendar
        print("\n🧠 Generating content calendar...")
        try:
            calendar_text = generate_calendar(snippets, month)
            
            # 5. Validate calendar output
            lines = calendar_text.splitlines()
            content_lines = [line for line in lines if "|" in line and "Date" not in line]
            
            if not calendar_text or len(content_lines) < 10:
                print(f"⚠️ Calendar seems short ({len(content_lines)} content rows). Continuing anyway...")
            else:
                print(f"✅ Generated calendar with {len(content_lines)} content rows")

            print("\n📄 Preview (first 3 lines):")
            preview_lines = [line for line in lines[:8] if line.strip()]
            for line in preview_lines[:3]:
                print(f"  {line}")
            
        except Exception as e:
            print(f"❌ Error generating calendar: {str(e)}")
            print("This might be due to OpenAI API issues. Please check your API key and try again.")
            return

        # 6. Export to Excel
        print("\n📤 Exporting to Excel...")
        output_path = f"data/output/calendar_{month_key}.xlsx"
        
        try:
            export_to_excel(calendar_text, output_path)
            
            # Verify file was created
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ Excel file created: {output_path} ({file_size:,} bytes)")
            else:
                print(f"❌ Excel file not found at: {output_path}")
                return
                
        except Exception as e:
            print(f"❌ Error exporting to Excel: {str(e)}")
            return

        # 7. Cache result in Supabase
        print("\n💾 Saving to Supabase cache...")
        try:
            save_to_cache(month_key, output_path)
            print("✅ Successfully cached in Supabase!")
        except Exception as e:
            print(f"⚠️ Caching failed: {str(e)}")
            print("📁 Local file is still available though!")

        print(f"\n🎉 COMPLETE! Your content calendar is ready:")
        print(f"📂 Local file: {output_path}")
        print(f"📅 Month: {month}")
        print(f"📊 Content rows: {len([line for line in calendar_text.splitlines() if '|' in line and 'Date' not in line])}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()