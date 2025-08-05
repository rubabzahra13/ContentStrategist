# === FILE: core/cache_handler.py ===
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET")

# Initialize supabase client with error handling
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"⚠️ Failed to initialize Supabase client: {str(e)}")

def get_cached_file(month_key):
    """
    Check if a cached file exists for the given month_key with time-based validation
    Returns the public URL if found and fresh, None otherwise
    """
    if not supabase:
        print("⚠️ Supabase not initialized - skipping cache check")
        return None
        
    if not BUCKET_NAME:
        print("⚠️ No SUPABASE_BUCKET configured - skipping cache check")
        return None
    
    try:
        # expects month_key already normalized like "july_2025"
        response = supabase.table("content_calendar_cache").select("excel_url, created_at").eq("month_key", month_key).execute()
        data = response.data
        
        if data and len(data) > 0:
            url = data[0]["excel_url"]
            created_at = data[0].get("created_at")
            
            # Check cache freshness
            is_fresh, age_info = validate_cache_freshness(month_key, created_at)
            
            if is_fresh:
                print(f"🎯 Found fresh cached file for {month_key} ({age_info})")
                return url
            else:
                print(f"⏰ Cached file for {month_key} is stale ({age_info}) - will regenerate")
                return None
        else:
            print(f"📭 No cached file found for {month_key}")
            return None
            
    except Exception as e:
        print(f"❌ Error checking cache: {str(e)}")
        return None

def validate_cache_freshness(month_key, created_at):
    """
    Validate if cached content is still fresh based on month context
    Returns (is_fresh: bool, age_info: str)
    """
    from datetime import datetime, timedelta
    
    try:
        if not created_at:
            return False, "no timestamp"
        
        # Parse creation time
        if isinstance(created_at, str):
            # Handle different timestamp formats
            try:
                cache_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except:
                cache_time = datetime.fromisoformat(created_at.split('T')[0])
        else:
            cache_time = created_at
            
        now = datetime.now()
        age = now - cache_time.replace(tzinfo=None)
        
        # Extract year from month_key
        try:
            year = int(month_key.split('_')[-1])
            current_year = now.year
        except:
            year = current_year
        
        # Time-based freshness rules
        if year < current_year:
            # Past years: Cache valid for longer (30 days)
            max_age = timedelta(days=30)
            context = "historical"
        elif year > current_year:
            # Future years: Cache valid for longer (14 days)
            max_age = timedelta(days=14)
            context = "predictive"
        else:
            # Current year: Cache expires quickly (3 days)
            max_age = timedelta(days=3)
            context = "current"
        
        is_fresh = age <= max_age
        age_days = age.days
        
        if age_days == 0:
            age_info = f"created today ({context})"
        elif age_days == 1:
            age_info = f"1 day old ({context})"
        else:
            age_info = f"{age_days} days old ({context})"
        
        return is_fresh, age_info
        
    except Exception as e:
        return False, f"validation error: {e}"

def save_to_cache(month_key, local_file_path):
    """
    Upload file to Supabase storage and save metadata to database
    """
    if not supabase:
        raise ValueError("Supabase client not initialized. Check your environment variables.")
        
    if not BUCKET_NAME:
        raise ValueError("SUPABASE_BUCKET not configured. Check your environment variables.")
    
    if not os.path.exists(local_file_path):
        raise ValueError(f"Local file not found: {local_file_path}")
    
    try:
        # expects month_key already normalized like "july_2025"
        remote_file_name = f"calendar_{month_key}.xlsx"

        # Step 1: Delete old file if exists
        try:
            existing_files = supabase.storage.from_(BUCKET_NAME).list()
            file_names = [f['name'] for f in existing_files]
            
            if remote_file_name in file_names:
                supabase.storage.from_(BUCKET_NAME).remove([remote_file_name])
                print(f"🗑️ Removed existing file: {remote_file_name}")
        except Exception as e:
            print(f"⚠️ Could not remove existing file: {str(e)}")

        # Step 2: Upload new file
        print(f"⬆️ Uploading {remote_file_name}...")
        
        with open(local_file_path, "rb") as f:
            upload_response = supabase.storage.from_(BUCKET_NAME).upload(
                path=remote_file_name,
                file=f,
                file_options={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
            )
        
        # Step 3: Get public URL
        public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(remote_file_name)
        
        if not public_url:
            raise ValueError("Failed to get public URL for uploaded file")

        # Step 4: Save metadata in DB
        print(f"💾 Saving metadata to database...")
        
        from datetime import datetime
        
        db_response = supabase.table("content_calendar_cache").upsert({
            "month_key": month_key,
            "excel_url": public_url,
            "file_name": remote_file_name,
            "created_at": datetime.now().isoformat()
        }).execute()

        print(f"✅ Successfully cached calendar: {month_key}")
        print(f"🌐 Public URL: {public_url}")
        
        return public_url
        
    except Exception as e:
        print(f"❌ Error saving to cache: {str(e)}")
        raise ValueError(f"Failed to save file to Supabase: {str(e)}")
