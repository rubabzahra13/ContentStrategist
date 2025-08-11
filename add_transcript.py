#!/usr/bin/env python3
"""
Manual Transcript Addition Tool
Easily add mentor transcripts to your knowledge base
"""

import os
import json
from datetime import datetime
from typing import Dict, List

def add_transcript_to_hardcoded_patterns(creator: str, transcript_data: Dict):
    """
    Add transcript insights to hardcoded patterns file
    """
    patterns_file = "core/hardcoded_mentor_patterns.py"
    
    # Read current file
    with open(patterns_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract insights from transcript
    hook = transcript_data.get('hook', '')
    insights = transcript_data.get('insights', [])
    cta = transcript_data.get('cta', '')
    
    print(f"Adding transcript for {creator}:")
    print(f"Hook: {hook}")
    print(f"Insights: {len(insights)} items")
    print(f"CTA: {cta}")
    
    # TODO: Actually modify the patterns file
    # For now, just print what would be added
    print(f"\n✅ Would add to {creator.upper()}_PATTERNS in {patterns_file}")

def create_transcript_from_input():
    """
    Interactive transcript creation
    """
    print("🎯 Manual Transcript Addition Tool")
    print("=" * 50)
    
    # Get basic info
    creator = input("Creator (hormozi/vaibhav): ").lower().strip()
    if creator not in ['hormozi', 'vaibhav']:
        print("❌ Creator must be 'hormozi' or 'vaibhav'")
        return
    
    video_url = input("Video URL (optional): ").strip()
    topic = input("Video topic/title: ").strip()
    
    print(f"\n📝 Adding transcript for {creator} - {topic}")
    print("Enter the content (press Enter twice when done):")
    
    # Get transcript content
    lines = []
    while True:
        line = input()
        if line == "" and len(lines) > 0 and lines[-1] == "":
            break
        lines.append(line)
    
    raw_transcript = "\n".join(lines[:-1])  # Remove last empty line
    
    # Extract key components
    print("\n🎯 Now let's extract key components:")
    
    hook = input("Opening hook (first compelling line): ").strip()
    if not hook:
        # Try to extract first sentence
        first_sentence = raw_transcript.split('.')[0] if '.' in raw_transcript else raw_transcript[:100]
        hook = first_sentence.strip()
        print(f"Auto-extracted hook: {hook}")
    
    print("\nKey insights (one per line, press Enter twice when done):")
    insights = []
    while True:
        insight = input()
        if insight == "":
            break
        insights.append(insight.strip())
    
    cta = input("Call-to-action (if any): ").strip()
    
    # Create structured transcript
    transcript_data = {
        'creator': creator,
        'topic': topic,
        'url': video_url,
        'date_added': datetime.now().isoformat(),
        'hook': hook,
        'insights': insights,
        'cta': cta,
        'raw_transcript': raw_transcript
    }
    
    # Save to file
    os.makedirs('data/transcripts', exist_ok=True)
    filename = f"data/transcripts/{creator}_{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Transcript saved to: {filename}")
    
    # Ask if user wants to add to hardcoded patterns
    add_to_patterns = input("\nAdd to hardcoded patterns now? (y/n): ").lower().strip()
    if add_to_patterns == 'y':
        add_transcript_to_hardcoded_patterns(creator, transcript_data)
    
    return transcript_data

def quick_add_youtube_transcript():
    """
    Quick way to add a YouTube transcript
    """
    print("🎬 Quick YouTube Transcript Addition")
    print("=" * 40)
    
    creator = input("Creator (hormozi/vaibhav): ").lower().strip()
    video_url = input("YouTube URL: ").strip()
    
    print("\nPaste the YouTube auto-generated transcript below:")
    print("(Copy from YouTube's 'Show transcript' feature)")
    print("Press Enter twice when done:")
    
    lines = []
    while True:
        line = input()
        if line == "" and len(lines) > 0 and lines[-1] == "":
            break
        lines.append(line)
    
    raw_transcript = "\n".join(lines[:-1])
    
    # Clean up timestamps if present
    cleaned_transcript = ""
    for line in raw_transcript.split('\n'):
        # Remove timestamps like "0:00" or "10:25"
        if ':' in line and line.split(':')[0].isdigit():
            continue
        cleaned_transcript += line + " "
    
    print(f"\n📊 Cleaned transcript: {len(cleaned_transcript)} characters")
    print("First 200 chars:", cleaned_transcript[:200] + "...")
    
    # Auto-extract hook (first compelling sentence)
    sentences = cleaned_transcript.split('.')
    hook = sentences[0].strip() if sentences else ""
    
    # Save quick version
    transcript_data = {
        'creator': creator,
        'url': video_url,
        'date_added': datetime.now().isoformat(),
        'hook': hook,
        'raw_transcript': cleaned_transcript.strip(),
        'source': 'youtube_auto_transcript'
    }
    
    filename = f"data/transcripts/{creator}_youtube_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    os.makedirs('data/transcripts', exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(transcript_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Quick transcript saved to: {filename}")
    print(f"🎯 Extracted hook: {hook}")
    
    return transcript_data

def batch_import_transcripts():
    """
    Import multiple transcript files at once
    """
    print("📁 Batch Transcript Import")
    print("=" * 30)
    
    transcript_dir = "data/transcripts"
    if not os.path.exists(transcript_dir):
        print(f"❌ Directory {transcript_dir} not found")
        return
    
    json_files = [f for f in os.listdir(transcript_dir) if f.endswith('.json')]
    
    if not json_files:
        print("❌ No JSON transcript files found")
        return
    
    print(f"Found {len(json_files)} transcript files:")
    for i, file in enumerate(json_files, 1):
        print(f"{i}. {file}")
    
    # TODO: Process each file and update hardcoded patterns
    print("\n🔄 Batch import feature coming soon!")
    print("For now, use individual transcript addition.")

if __name__ == "__main__":
    print("🎥 Instagram Mentor Transcript Tool")
    print("=" * 50)
    print("1. Add detailed transcript")
    print("2. Quick YouTube transcript")
    print("3. Batch import")
    print("4. Exit")
    
    choice = input("\nChoose option (1-4): ").strip()
    
    if choice == "1":
        create_transcript_from_input()
    elif choice == "2":
        quick_add_youtube_transcript()
    elif choice == "3":
        batch_import_transcripts()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")