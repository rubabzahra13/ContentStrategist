import os
from supabase import create_client
from dotenv import load_dotenv
from utils.helpers import normalize_month

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_excel_to_bucket(local_path, remote_name):
    # Step 1: Check if the file already exists in Supabase
    list_response = supabase.storage.from_(BUCKET_NAME).list()
    existing_files = [item['name'] for item in list_response]

    if remote_name in existing_files:
        try:
            supabase.storage.from_(BUCKET_NAME).remove([remote_name])
            print(f"♻️ Removed existing: {remote_name}")
        except Exception as e:
            print(f"⚠️ Could not remove existing file: {e}")
    else:
        print(f"🆕 No existing file found for: {remote_name}. Proceeding to upload.")

    # Step 2: Upload the file
    if not os.path.exists(local_path):
        print(f"❌ Local file not found: {local_path}")
        return None

    with open(local_path, "rb") as f:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=remote_name,
            file=f,
            file_options={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
        )

    public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(remote_name)
    print(f"✅ Uploaded: {remote_name}")
    print(f"🌐 Public URL: {public_url}")
    return public_url
