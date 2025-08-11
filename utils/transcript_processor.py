#!/usr/bin/env python3
"""
Transcript Processor - Process and add course transcripts to knowledge base
Handles various transcript formats and extraction methods
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from core.knowledge_base import KnowledgeBase

class TranscriptProcessor:
    """
    Process and manage course transcripts for the knowledge base
    """
    
    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        """Initialize with knowledge base"""
        self.kb = knowledge_base or KnowledgeBase()
        self.supported_formats = ['.txt', '.srt', '.vtt', '.json']
    
    def process_transcript_file(self, file_path: str, course_name: str, 
                               metadata: Optional[Dict] = None) -> bool:
        """
        Process a transcript file and add to knowledge base
        
        Args:
            file_path: Path to transcript file
            course_name: Name for the course
            metadata: Optional metadata dict
            
        Returns:
            bool: Success status
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        if file_path.suffix.lower() not in self.supported_formats:
            print(f"❌ Unsupported format: {file_path.suffix}")
            print(f"Supported formats: {', '.join(self.supported_formats)}")
            return False
        
        try:
            # Read and process file based on format
            content = self._extract_content_from_file(file_path)
            
            if not content:
                print(f"❌ No content extracted from {file_path}")
                return False
            
            # Clean and process content
            processed_content = self._clean_transcript_content(content)
            
            # Add metadata from file if not provided
            if metadata is None:
                metadata = {
                    'source_file': str(file_path),
                    'file_size': file_path.stat().st_size,
                    'processed_at': datetime.now().isoformat()
                }
            else:
                metadata.update({
                    'source_file': str(file_path),
                    'processed_at': datetime.now().isoformat()
                })
            
            # Add to knowledge base
            success = self.kb.add_course_transcript(
                course_name=course_name,
                transcript_content=processed_content,
                metadata=metadata
            )
            
            if success:
                print(f"✅ Successfully processed transcript: {course_name}")
                print(f"📄 Content length: {len(processed_content)} characters")
                return True
            else:
                print(f"❌ Failed to add transcript to knowledge base")
                return False
                
        except Exception as e:
            print(f"❌ Error processing transcript: {str(e)}")
            return False
    
    def _extract_content_from_file(self, file_path: Path) -> str:
        """Extract content based on file format"""
        suffix = file_path.suffix.lower()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if suffix == '.txt':
                    return f.read()
                
                elif suffix == '.srt':
                    return self._extract_from_srt(f.read())
                
                elif suffix == '.vtt':
                    return self._extract_from_vtt(f.read())
                
                elif suffix == '.json':
                    return self._extract_from_json(f.read())
                
                else:
                    return f.read()  # Fallback to plain text
                    
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"❌ Encoding error: {str(e)}")
                return ""
    
    def _extract_from_srt(self, srt_content: str) -> str:
        """Extract text from SRT subtitle format"""
        # Remove subtitle numbers and timestamps
        lines = srt_content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines, numbers, and timestamp lines
            if (line and 
                not line.isdigit() and 
                '-->' not in line and
                not re.match(r'^\d{2}:\d{2}:\d{2}', line)):
                text_lines.append(line)
        
        return '\n'.join(text_lines)
    
    def _extract_from_vtt(self, vtt_content: str) -> str:
        """Extract text from VTT subtitle format"""
        lines = vtt_content.split('\n')
        text_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip VTT headers, cue identifiers, and timestamp lines
            if (line and 
                not line.startswith('WEBVTT') and
                not line.startswith('NOTE') and
                '-->' not in line and
                not re.match(r'^\d{2}:\d{2}:\d{2}', line) and
                not line.isdigit()):
                text_lines.append(line)
        
        return '\n'.join(text_lines)
    
    def _extract_from_json(self, json_content: str) -> str:
        """Extract text from JSON transcript format"""
        try:
            data = json.loads(json_content)
            
            # Common JSON transcript formats
            if isinstance(data, dict):
                # Format 1: {'transcript': 'text'}
                if 'transcript' in data:
                    return data['transcript']
                
                # Format 2: {'text': 'content'}
                if 'text' in data:
                    return data['text']
                
                # Format 3: {'segments': [{'text': '...'}]}
                if 'segments' in data:
                    segments = data['segments']
                    if isinstance(segments, list):
                        text_parts = []
                        for segment in segments:
                            if isinstance(segment, dict) and 'text' in segment:
                                text_parts.append(segment['text'])
                        return ' '.join(text_parts)
                
                # Format 4: {'words': [{'word': '...'}]}
                if 'words' in data:
                    words = data['words']
                    if isinstance(words, list):
                        word_parts = []
                        for word_obj in words:
                            if isinstance(word_obj, dict) and 'word' in word_obj:
                                word_parts.append(word_obj['word'])
                        return ' '.join(word_parts)
            
            # If it's a list of text items
            elif isinstance(data, list):
                text_parts = []
                for item in data:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict) and 'text' in item:
                        text_parts.append(item['text'])
                return ' '.join(text_parts)
            
            # Fallback: convert entire JSON to string
            return str(data)
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {str(e)}")
            return ""
    
    def _clean_transcript_content(self, content: str) -> str:
        """Clean and normalize transcript content"""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove common filler words if they appear excessively
        filler_words = ['um', 'uh', 'er', 'ah', 'like', 'you know']
        for filler in filler_words:
            # Remove if it appears more than 5 times per 1000 words
            word_count = len(content.split())
            filler_count = content.lower().count(f' {filler} ')
            if word_count > 0 and (filler_count / word_count) > 0.005:  # 0.5%
                content = re.sub(f' {filler} ', ' ', content, flags=re.IGNORECASE)
        
        # Clean up speaker labels (common in many transcripts)
        content = re.sub(r'Speaker \d+:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Interviewer:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'Host:', '', content, flags=re.IGNORECASE)
        
        # Remove timestamps if any remain
        content = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '', content)
        content = re.sub(r'\(\d{2}:\d{2}:\d{2}\)', '', content)
        
        # Clean up excessive punctuation
        content = re.sub(r'[.]{3,}', '...', content)
        content = re.sub(r'[!]{2,}', '!', content)
        content = re.sub(r'[?]{2,}', '?', content)
        
        # Final cleanup
        content = content.strip()
        
        return content
    
    def batch_process_directory(self, directory_path: str, course_name_prefix: str = "") -> Dict:
        """
        Process all transcript files in a directory
        
        Args:
            directory_path: Path to directory containing transcript files
            course_name_prefix: Prefix for course names
            
        Returns:
            Dict with processing results
        """
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return {'success': 0, 'failed': 0, 'files': []}
        
        results = {'success': 0, 'failed': 0, 'files': []}
        
        # Find all supported files
        transcript_files = []
        for suffix in self.supported_formats:
            transcript_files.extend(directory.glob(f"*{suffix}"))
        
        print(f"📁 Found {len(transcript_files)} transcript files in {directory_path}")
        
        for file_path in transcript_files:
            # Generate course name from filename
            course_name = course_name_prefix + file_path.stem
            course_name = re.sub(r'[^\w\s-]', '', course_name)  # Clean filename
            course_name = re.sub(r'\s+', '_', course_name)  # Replace spaces with underscores
            
            print(f"\n📄 Processing: {file_path.name}")
            
            metadata = {
                'filename': file_path.name,
                'directory': str(directory),
                'file_extension': file_path.suffix
            }
            
            success = self.process_transcript_file(str(file_path), course_name, metadata)
            
            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
            
            results['files'].append({
                'filename': file_path.name,
                'course_name': course_name,
                'success': success
            })
        
        print(f"\n📊 Batch processing complete:")
        print(f"  ✅ Successful: {results['success']}")
        print(f"  ❌ Failed: {results['failed']}")
        
        return results
    
    def add_transcript_from_text(self, course_name: str, transcript_text: str, 
                                metadata: Optional[Dict] = None) -> bool:
        """
        Add transcript directly from text string
        
        Args:
            course_name: Name for the course
            transcript_text: The transcript content
            metadata: Optional metadata
            
        Returns:
            bool: Success status
        """
        if not transcript_text or not transcript_text.strip():
            print("❌ Empty transcript text provided")
            return False
        
        # Clean the content
        processed_content = self._clean_transcript_content(transcript_text)
        
        # Add default metadata if none provided
        if metadata is None:
            metadata = {
                'source': 'direct_input',
                'added_at': datetime.now().isoformat(),
                'content_length': len(processed_content)
            }
        
        # Add to knowledge base
        return self.kb.add_course_transcript(course_name, processed_content, metadata)

def main():
    """Test the transcript processor"""
    print("📝 Testing Transcript Processor")
    
    processor = TranscriptProcessor()
    
    # Test with sample transcript text
    sample_transcript = """
    Welcome to AI Business Mastery Course, Module 1.
    
    In this lesson, we're going to cover the fundamentals of scaling your business with AI.
    
    The first principle is automation. You need to identify processes that take up most of your time.
    Here's my 5-step framework:
    
    1. Audit your daily workflow
    2. Identify repetitive tasks  
    3. Research AI solutions
    4. Implement one tool at a time
    5. Measure and optimize
    
    The key insight here is that successful entrepreneurs don't try to automate everything at once.
    They start with one process, perfect it, then scale to the next.
    
    This approach has helped me personally go from $10K to $100K monthly revenue in just 8 months.
    """
    
    # Test adding transcript from text
    success = processor.add_transcript_from_text(
        course_name="AI_Business_Mastery_Module_1",
        transcript_text=sample_transcript,
        metadata={
            "instructor": "AI Business Expert",
            "module": "Module 1",
            "duration": "25 minutes",
            "topic": "Business Automation Fundamentals"
        }
    )
    
    if success:
        print("✅ Successfully added sample transcript")
        
        # Test knowledge base integration
        kb = KnowledgeBase()
        summary = kb.get_knowledge_summary()
        print(f"\n📊 Knowledge Base Summary:")
        print(f"  Courses: {summary['courses']['count']}")
        print(f"  Course names: {summary['courses']['names']}")
    else:
        print("❌ Failed to add transcript")

if __name__ == "__main__":
    main()