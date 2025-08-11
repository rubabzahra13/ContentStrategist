# 🚀 Installation Guide - Enhanced AI Content Strategist

## 📋 Prerequisites

- Python 3.11+ 
- Git
- OpenAI API key

## 🔧 Installation Steps

### 1. Install Dependencies

```bash
# Install new requirements
pip install -r requirements.txt

# This will install:
# - instaloader (Instagram scraping)
# - yt-dlp (video processing)
# - All existing dependencies
```

### 2. Set Environment Variables

Add to your `.env` file or environment:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for enhanced features)
SERPER_API_KEY=your_serper_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_key_here
SUPABASE_BUCKET=your_bucket_name_here
SECRET_KEY=your_flask_secret_key_here
```

### 3. Create Knowledge Base Directories

```bash
# The app will create these automatically, but you can create them manually:
mkdir -p data/knowledge_base/mentor_profiles
mkdir -p data/knowledge_base/course_transcripts  
mkdir -p data/knowledge_base/video_transcripts
```

### 4. Test the Installation

```bash
# Test basic functionality
python manage_knowledge.py summary

# Should show empty knowledge base if successful
```

## 🧪 Quick Test

### Test Mentor Scraping:
```bash
# Add a test mentor (public business profile)
python manage_knowledge.py add-mentor garyvee --posts 10
```

### Test Course Transcript:
```bash
# Create a test transcript
echo "Welcome to AI Business Course. Today we'll learn about automation frameworks. The key is to start with one process and perfect it before moving to the next." > test_transcript.txt

# Add to knowledge base
python manage_knowledge.py add-transcript "Test Course" --file test_transcript.txt --instructor "Test" --topic "AI Business"
```

### Test Enhanced Calendar:
```bash
# Run the web app
python app.py

# Navigate to http://localhost:5000
# Try generating a calendar - it should now use enhanced AI prompts
```

## 🔧 Troubleshooting

### Issue: Import Errors
**Solution:** Install missing packages
```bash
pip install instaloader yt-dlp
```

### Issue: Instagram Scraping Fails
**Solutions:**
- Ensure target profile is public
- Check internet connection
- Start with fewer posts (--posts 5)
- Wait between requests if rate limited

### Issue: OpenAI API Errors
**Solutions:**
- Verify API key is correct
- Check OpenAI account has credits
- Ensure API key has necessary permissions

### Issue: Knowledge Base Errors
**Solutions:**
- Check file permissions for data/ directory
- Ensure sufficient disk space
- Verify JSON files aren't corrupted

## 📊 Verify Installation

Run this verification script:

```python
# Create verify_install.py
try:
    from core.knowledge_base import KnowledgeBase
    from core.mentor_scraper import MentorProfileScraper  
    from utils.transcript_processor import TranscriptProcessor
    from core.enhanced_calendar_generator import generate_enhanced_calendar
    
    print("✅ All modules imported successfully")
    
    # Test knowledge base
    kb = KnowledgeBase()
    summary = kb.get_knowledge_summary()
    print(f"✅ Knowledge base working: {summary['mentors']['count']} mentors, {summary['courses']['count']} courses")
    
    print("🎉 Installation successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Run: pip install -r requirements.txt")
except Exception as e:
    print(f"⚠️ Other error: {e}")
```

```bash
python verify_install.py
```

## 🎯 Next Steps

1. **Add Your First Mentor:**
   ```bash
   python manage_knowledge.py add-mentor [mentor_username] --posts 50
   ```

2. **Add Your Course Content:**
   ```bash
   python manage_knowledge.py add-transcript "Your Course Name" --file transcript.txt
   ```

3. **Generate Enhanced Calendar:**
   - Start web app: `python app.py`
   - Navigate to http://localhost:5000
   - Generate calendar and see the enhanced results!

4. **Explore Knowledge Base:**
   - Visit http://localhost:5000/knowledge
   - Manage mentors and transcripts via web interface

## 🔄 Regular Maintenance

### Weekly:
- Add new mentor content if they post frequently
- Update pattern analysis: `python manage_knowledge.py analyze`

### Monthly:  
- Add new course transcripts
- Review and update mentor list
- Clean up old cached data

### As Needed:
- Monitor calendar performance and adjust mentors accordingly
- Add seasonal or trending mentors
- Update course content with new materials

You're all set! Your AI Content Strategist now learns from the best and incorporates your expertise. 🚀