# Manual Transcript Collection Guide

## Method 1: YouTube Auto-Generated Transcripts (Recommended)

### For Hormozi & Vaibhav YouTube Videos:

1. **Find the Video**: Go to any Hormozi or Vaibhav YouTube video
2. **Open Transcript**: Click the "..." menu → "Show transcript"
3. **Copy Raw Text**: Select all transcript text and copy
4. **Clean Format**: Remove timestamps if needed

### Example Process:
```
1. Go to: https://youtube.com/@AlexHormozi
2. Pick a popular video (1M+ views)
3. Click "..." → "Show transcript"
4. Copy the entire transcript
5. Save as .txt file with format: "hormozi_video_title_YYYYMMDD.txt"
```

## Method 2: Instagram Reel Manual Transcription

### For Instagram Reels:
1. **Watch & Take Notes**: Play the reel and write down key points
2. **Focus on Hooks**: Capture the first 3-5 seconds exactly
3. **Get Main Message**: Write the core teaching/insight
4. **Capture CTA**: Note the call-to-action at the end

### Template Format:
```
CREATOR: Alex Hormozi
VIDEO_URL: https://instagram.com/p/[ID]
DATE: 2025-01-15
VIEWS: 2.3M
LIKES: 485K

HOOK: "Most entrepreneurs fail because they don't understand this one thing"

MAIN_CONTENT: 
[Key points and insights from the video]

CTA: "Comment below what's your biggest challenge"

HASHTAGS: #business #entrepreneur #scaling
```

## Method 3: Audio Transcription Tools

### Free Options:
- **Otter.ai**: 600 minutes/month free
- **Rev.com**: $1.25/minute (high accuracy)
- **Google Docs Voice Typing**: Completely free
- **Whisper by OpenAI**: Free if you run locally

### Process:
1. Screen record the video with audio
2. Upload to transcription service
3. Review and clean up the transcript
4. Format for our knowledge base

## Method 4: AI-Powered Video Analysis

### Using ChatGPT/Claude:
1. Describe the video content to AI
2. Ask for key insights extraction
3. Request hook and CTA identification
4. Get structured output

### Prompt Template:
```
"I watched a video by Alex Hormozi about [topic]. The main points were:
- [Point 1]
- [Point 2] 
- [Point 3]

Please format this as a structured transcript with:
1. Hook (opening line)
2. Key insights
3. Call to action
4. Success principles used
```

## Method 5: Community Sourced Content

### Where to Find:
- **Reddit**: r/entrepreneur, r/business
- **Twitter**: Quote tweets of their content
- **LinkedIn**: Their long-form posts
- **Podcasts**: Joe Rogan, BiggerPockets, etc.

## Adding Transcripts to Your System

### Option A: Direct Addition to Hardcoded Patterns
1. Edit `core/hardcoded_mentor_patterns.py`
2. Add new hooks, insights, and patterns
3. Restart the Flask app

### Option B: Create Transcript Files
1. Save transcripts in `data/transcripts/` folder
2. Use naming: `[creator]_[topic]_[date].txt`
3. I'll create a script to auto-import them

### Option C: RAG System Integration
1. Save as structured JSON files
2. Use the existing RAG pipeline
3. Automatically chunk and embed

## Recommended Workflow

### Week 1: YouTube Focus
- Collect 10 Hormozi YouTube transcripts
- Collect 10 Vaibhav YouTube transcripts
- Focus on most popular videos (1M+ views)

### Week 2: Instagram Reels
- Manually transcribe 20 top Hormozi reels
- Manually transcribe 20 top Vaibhav reels
- Use the template format above

### Week 3: Integration
- Add best insights to hardcoded patterns
- Create automated import system
- Test enhanced calendar generation

## Quality Guidelines

### What to Capture:
✅ Exact opening hooks (first 5 seconds)
✅ Core business insights and principles
✅ Specific strategies and frameworks
✅ Calls-to-action and engagement tactics
✅ Storytelling structures and examples

### What to Skip:
❌ Filler words and "um/uh"
❌ Irrelevant tangents
❌ Promotional content for courses
❌ Technical audio issues
❌ Comment responses in videos

## File Structure

```
data/
├── transcripts/
│   ├── hormozi/
│   │   ├── youtube/
│   │   │   ├── scaling_business_20250115.txt
│   │   │   └── offer_creation_20250110.txt
│   │   └── instagram/
│   │       ├── reel_business_tips_20250115.txt
│   │       └── reel_mindset_20250114.txt
│   └── vaibhav/
│       ├── youtube/
│       └── instagram/
└── processed/
    ├── hooks_extracted.json
    ├── insights_extracted.json
    └── patterns_identified.json
```

## Next Steps

1. **Choose Your Method**: Pick 1-2 methods that work best for you
2. **Start Small**: Begin with 5 transcripts per creator
3. **Test Integration**: See how it improves calendar quality
4. **Scale Up**: Add more content over time
5. **Automate**: Build tools to make the process easier

## Tools I Can Build for You

- **Transcript Formatter**: Converts raw text to structured format
- **Auto-Importer**: Reads transcript files and updates knowledge base
- **Quality Checker**: Validates transcript format and content
- **Pattern Extractor**: Identifies hooks, CTAs, and frameworks automatically