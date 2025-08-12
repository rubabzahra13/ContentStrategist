"""
Test video processing functionality
"""

import unittest
import os
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.video_transcriber import VideoTranscriber
from core.transcript_analyzer import TranscriptAnalyzer

class TestVideoProcessing(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.transcriber = VideoTranscriber()
        self.analyzer = TranscriptAnalyzer()
        
        # Ensure test directories exist
        self.transcriber.raw_path.mkdir(parents=True, exist_ok=True)
        self.transcriber.transcripts_path.mkdir(parents=True, exist_ok=True)
    
    def test_video_transcriber_initialization(self):
        """Test VideoTranscriber initializes correctly"""
        self.assertIsInstance(self.transcriber, VideoTranscriber)
        self.assertTrue(self.transcriber.videos_path.exists())
        self.assertTrue(self.transcriber.transcripts_path.exists())
    
    def test_get_video_files_empty(self):
        """Test getting video files when folder is empty"""
        video_files = self.transcriber.get_video_files()
        self.assertIsInstance(video_files, list)
        # Could be empty if no test videos
    
    def test_transcript_analyzer_initialization(self):
        """Test TranscriptAnalyzer initializes correctly"""
        self.assertIsInstance(self.analyzer, TranscriptAnalyzer)
        self.assertTrue(self.analyzer.transcripts_path.exists())
        self.assertTrue(self.analyzer.analysis_path.exists())
    
    def test_default_template_generation(self):
        """Test generating default transcript template"""
        template = self.analyzer.get_default_template()
        self.assertIsInstance(template, str)
        self.assertIn("Hook", template)
        self.assertIn("Body", template)
        self.assertIn("CTA", template)
    
    def test_analyze_structure_basic(self):
        """Test basic transcript structure analysis"""
        sample_text = "If you don't know this secret, you're missing out. Here's the truth about AI tools. They can automate 80% of your content creation. Comment below which tool you'll try first!"
        
        analysis = self.analyzer.analyze_structure(sample_text)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("word_count", analysis)
        self.assertIn("hook", analysis)
        self.assertIn("cta", analysis)
        self.assertGreater(analysis["word_count"], 0)
    
    def test_insights_generation_empty(self):
        """Test insights generation with no transcripts"""
        insights = self.analyzer.generate_insights()
        
        # Should handle empty gracefully
        self.assertIsInstance(insights, dict)
    
    def test_common_phrase_extraction(self):
        """Test extraction of common phrases"""
        sample_transcripts = [
            {"transcript_text": "If you don't know this secret about AI tools"},
            {"transcript_text": "Here's the secret to scaling your business with AI tools"},
            {"transcript_text": "The secret weapon every entrepreneur needs"}
        ]
        
        phrases = self.analyzer.extract_common_phrases(sample_transcripts)
        
        self.assertIsInstance(phrases, dict)
        self.assertIn("common_bigrams", phrases)
        self.assertIn("common_trigrams", phrases)
    
    def test_load_insights_nonexistent(self):
        """Test loading insights when file doesn't exist"""
        insights = self.analyzer.load_insights()
        self.assertIsInstance(insights, dict)
        # Should return empty dict if no insights file exists

if __name__ == '__main__':
    print("🧪 Testing Video Processing Functionality")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2)