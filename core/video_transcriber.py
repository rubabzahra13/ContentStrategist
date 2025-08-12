"""
Video transcription module using OpenAI Whisper API
Transcribes Instagram Reels and other video content for analysis
"""

import os
import json
from pathlib import Path
from openai import OpenAI
from utils.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

class VideoTranscriber:
    def __init__(self):
        self.videos_path = Path("data/videos")
        self.raw_path = self.videos_path / "raw"
        self.transcripts_path = self.videos_path / "transcripts"
        
        # Ensure directories exist
        self.transcripts_path.mkdir(parents=True, exist_ok=True)
    
    def get_video_files(self):
        """Get list of video files in the raw folder"""
        supported_formats = {'.mp4', '.mov', '.avi', '.mp3', '.wav', '.m4a'}
        video_files = []
        
        if self.raw_path.exists():
            for file_path in self.raw_path.iterdir():
                if file_path.suffix.lower() in supported_formats:
                    video_files.append(file_path)
        
        return sorted(video_files)
    
    def transcribe_video(self, video_path, language="en"):
        """Transcribe a single video file using OpenAI Whisper"""
        try:
            print(f"🎙️ Transcribing: {video_path.name}")
            
            # Check file size (Whisper has 25MB limit)
            file_size = video_path.stat().st_size
            if file_size > 25 * 1024 * 1024:  # 25MB
                print(f"⚠️ File {video_path.name} is too large ({file_size/1024/1024:.1f}MB). Max size is 25MB.")
                return None
            
            # Transcribe using Whisper
            with open(video_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json",
                    timestamp_granularities=["word", "segment"]
                )
            
            return transcript
            
        except Exception as e:
            print(f"❌ Error transcribing {video_path.name}: {e}")
            return None
    
    def save_transcript(self, video_path, transcript_data):
        """Save transcript data to JSON file"""
        try:
            # Create output filename
            output_name = video_path.stem + "_transcript.json"
            output_path = self.transcripts_path / output_name
            
            # Prepare transcript data for saving
            transcript_info = {
                "source_file": video_path.name,
                "source_path": str(video_path),
                "transcript_text": transcript_data.text,
                "language": transcript_data.language,
                "duration": transcript_data.duration,
                "words": [
                    {
                        "word": word.word,
                        "start": word.start,
                        "end": word.end
                    } for word in transcript_data.words
                ] if hasattr(transcript_data, 'words') else [],
                "segments": [
                    {
                        "text": segment.text,
                        "start": segment.start,
                        "end": segment.end
                    } for segment in transcript_data.segments
                ] if hasattr(transcript_data, 'segments') else []
            }
            
            # Save to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript_info, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Transcript saved: {output_path.name}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving transcript: {e}")
            return None
    
    def transcribe_all_videos(self):
        """Transcribe all videos in the raw folder"""
        video_files = self.get_video_files()
        
        if not video_files:
            print("📁 No video files found in data/videos/raw/")
            return []
        
        print(f"🎥 Found {len(video_files)} video files to transcribe")
        
        transcribed_files = []
        
        for video_path in video_files:
            # Check if transcript already exists
            transcript_name = video_path.stem + "_transcript.json"
            transcript_path = self.transcripts_path / transcript_name
            
            if transcript_path.exists():
                print(f"⏭️ Transcript already exists: {transcript_name}")
                transcribed_files.append(transcript_path)
                continue
            
            # Transcribe the video
            transcript_data = self.transcribe_video(video_path)
            
            if transcript_data:
                saved_path = self.save_transcript(video_path, transcript_data)
                if saved_path:
                    transcribed_files.append(saved_path)
        
        print(f"✅ Transcription complete! Generated {len(transcribed_files)} transcripts")
        return transcribed_files
    
    def get_transcript_text(self, transcript_path):
        """Extract just the text from a transcript file"""
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('transcript_text', '')
        except Exception as e:
            print(f"❌ Error reading transcript {transcript_path}: {e}")
            return ""

def transcribe_videos():
    """Main function to transcribe all videos"""
    transcriber = VideoTranscriber()
    return transcriber.transcribe_all_videos()

if __name__ == "__main__":
    # Test the transcription functionality
    transcribe_videos()