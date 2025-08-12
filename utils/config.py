import os
from dotenv import load_dotenv

# Try to load .env file, but don't fail if it doesn't exist or has issues
try:
    load_dotenv()
except:
    print("⚠️ Warning: Could not load .env file, using environment variables")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")