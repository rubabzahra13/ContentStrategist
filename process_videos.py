#!/usr/bin/env python3
"""
Video Processing Script
Process videos manually added to data/videos/raw/ folder
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.video_transcriber import VideoTranscriber
from core.transcript_analyzer import TranscriptAnalyzer

def main():
    """Main function to process all videos and generate insights"""
    print("🎬 VIDEO PROCESSING PIPELINE")
    print("=" * 50)
    
    # Step 1: Check for videos
    transcriber = VideoTranscriber()
    video_files = transcriber.get_video_files()
    
    if not video_files:
        print("📁 No video files found in data/videos/raw/")
        print("💡 Add your Instagram Reels videos to data/videos/raw/ and run this script again")
        return
    
    print(f"🎥 Found {len(video_files)} video files:")
    for video in video_files:
        print(f"   • {video.name}")
    
    # Step 2: Transcribe videos
    print(f"\n🎙️ TRANSCRIBING VIDEOS")
    print("-" * 30)
    transcribed_files = transcriber.transcribe_all_videos()
    
    if not transcribed_files:
        print("❌ No transcripts were generated")
        return
    
    print(f"✅ Generated {len(transcribed_files)} transcripts")
    
    # Step 3: Analyze transcripts
    print(f"\n🔍 ANALYZING TRANSCRIPTS")
    print("-" * 30)
    analyzer = TranscriptAnalyzer()
    insights = analyzer.generate_insights()
    
    if not insights:
        print("❌ No insights were generated")
        return
    
    # Step 4: Display results
    print(f"\n📊 ANALYSIS RESULTS")
    print("=" * 50)
    
    if insights.get("total_transcripts_analyzed", 0) > 0:
        avg = insights.get("averages", {})
        print(f"📈 Videos Analyzed: {insights['total_transcripts_analyzed']}")
        print(f"📝 Average Word Count: {avg.get('word_count', 0):.1f} words")
        print(f"🎯 Average Hook Length: {avg.get('hook_length', 0):.1f} words")
        print(f"💬 Engagement Score: {avg.get('engagement_score', 0):.1f}/5")
        print(f"🔥 Emotional Intensity: {avg.get('emotional_intensity', 0):.1f}")
        
        # Show timing info if available
        timing = insights.get("timing", {})
        if timing.get("avg_total_duration", 0) > 0:
            print(f"⏱️ Average Duration: {timing['avg_total_duration']:.1f} seconds")
            print(f"🗣️ Speaking Rate: {timing['avg_words_per_second']:.1f} words/second")
        
        # Show common phrases
        patterns = insights.get("patterns", {})
        bigrams = patterns.get("common_bigrams", [])
        if bigrams:
            print(f"\n🔥 TOP SUCCESSFUL PHRASES:")
            for i, (phrase, count) in enumerate(bigrams[:10], 1):
                print(f"   {i:2d}. \"{phrase}\" (used {count} times)")
        
        print(f"\n📋 TRANSCRIPT TEMPLATE")
        print("-" * 30)
        template = analyzer.generate_transcript_template(insights)
        print(template)
        
    print(f"\n🎉 PROCESSING COMPLETE!")
    print("✅ Your content calendars will now include improved transcripts based on these patterns")
    print("🚀 Run the calendar generator to see the enhanced content!")

if __name__ == "__main__":
    main()