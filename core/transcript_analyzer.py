"""
Transcript Analysis Module
Analyzes successful Instagram Reel transcripts to extract patterns and insights
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import statistics

class TranscriptAnalyzer:
    def __init__(self):
        self.transcripts_path = Path("data/videos/transcripts")
        self.analysis_path = Path("data/videos/analysis")
        self.analysis_path.mkdir(parents=True, exist_ok=True)
        
        # Common Instagram Reel patterns
        self.hook_patterns = [
            r"^(if you|when you|stop|wait|here's|this is|you need|don't|never)",
            r"^(the secret|the truth|the problem|the reason)",
            r"^(3 things|5 ways|top \d+|biggest mistake)",
            r"(that changed everything|will blow your mind|everyone gets wrong)"
        ]
        
        self.engagement_phrases = [
            r"(comment below|drop a|tell me|what do you think|share this)",
            r"(follow for more|save this|like if you|agree with)",
            r"(which one|what's your|have you tried)"
        ]
    
    def load_all_transcripts(self) -> List[Dict]:
        """Load all transcript files"""
        transcripts = []
        
        for transcript_file in self.transcripts_path.glob("*_transcript.json"):
            try:
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    transcripts.append(data)
            except Exception as e:
                print(f"❌ Error loading {transcript_file}: {e}")
        
        return transcripts
    
    def analyze_structure(self, transcript_text: str) -> Dict:
        """Analyze the structure of a successful reel transcript"""
        words = transcript_text.split()
        sentences = re.split(r'[.!?]+', transcript_text)
        
        # Basic metrics
        analysis = {
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "avg_words_per_sentence": len(words) / max(len(sentences), 1),
            "character_count": len(transcript_text)
        }
        
        # Identify hook (first sentence/few words)
        first_sentence = sentences[0].strip() if sentences else ""
        analysis["hook"] = first_sentence
        analysis["hook_length"] = len(first_sentence.split())
        
        # Check for common hook patterns
        hook_score = 0
        for pattern in self.hook_patterns:
            if re.search(pattern, first_sentence.lower()):
                hook_score += 1
        analysis["hook_strength"] = hook_score
        
        # Check for engagement elements
        engagement_score = 0
        for pattern in self.engagement_phrases:
            if re.search(pattern, transcript_text.lower()):
                engagement_score += 1
        analysis["engagement_score"] = engagement_score
        
        # Identify call-to-action (usually last sentence)
        last_sentence = sentences[-1].strip() if sentences else ""
        analysis["cta"] = last_sentence
        
        # Check for numbers/lists
        number_mentions = len(re.findall(r'\b\d+\b', transcript_text))
        analysis["uses_numbers"] = number_mentions > 0
        analysis["number_count"] = number_mentions
        
        # Check for emotional words
        emotional_words = [
            "amazing", "incredible", "shocking", "secret", "mistake", 
            "wrong", "perfect", "terrible", "love", "hate", "fear"
        ]
        emotion_count = sum(1 for word in emotional_words if word in transcript_text.lower())
        analysis["emotional_intensity"] = emotion_count
        
        return analysis
    
    def extract_common_phrases(self, transcripts: List[Dict]) -> Dict:
        """Extract commonly used phrases across successful reels"""
        all_text = " ".join([t.get('transcript_text', '') for t in transcripts])
        
        # Extract 2-3 word phrases
        words = re.findall(r'\b\w+\b', all_text.lower())
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)]
        
        return {
            "common_bigrams": Counter(bigrams).most_common(20),
            "common_trigrams": Counter(trigrams).most_common(15)
        }
    
    def analyze_timing_patterns(self, transcripts: List[Dict]) -> Dict:
        """Analyze timing patterns from transcripts with word-level timestamps"""
        timing_analysis = {
            "avg_words_per_second": [],
            "hook_duration": [],
            "total_durations": []
        }
        
        for transcript in transcripts:
            if 'words' in transcript and transcript['words']:
                words = transcript['words']
                duration = transcript.get('duration', 0)
                
                if duration > 0:
                    wps = len(words) / duration
                    timing_analysis["avg_words_per_second"].append(wps)
                    timing_analysis["total_durations"].append(duration)
                
                # Analyze hook timing (first 3 seconds)
                hook_words = [w for w in words if w.get('start', 0) <= 3.0]
                if hook_words:
                    timing_analysis["hook_duration"].append(len(hook_words))
        
        # Calculate averages
        return {
            "avg_words_per_second": statistics.mean(timing_analysis["avg_words_per_second"]) if timing_analysis["avg_words_per_second"] else 0,
            "avg_hook_words": statistics.mean(timing_analysis["hook_duration"]) if timing_analysis["hook_duration"] else 0,
            "avg_total_duration": statistics.mean(timing_analysis["total_durations"]) if timing_analysis["total_durations"] else 0
        }
    
    def generate_insights(self) -> Dict:
        """Generate comprehensive insights from all transcripts"""
        transcripts = self.load_all_transcripts()
        
        if not transcripts:
            print("📁 No transcripts found for analysis")
            return {}
        
        print(f"🔍 Analyzing {len(transcripts)} transcripts...")
        
        # Analyze each transcript
        individual_analyses = []
        for transcript in transcripts:
            text = transcript.get('transcript_text', '')
            if text:
                analysis = self.analyze_structure(text)
                analysis['source_file'] = transcript.get('source_file', 'unknown')
                individual_analyses.append(analysis)
        
        # Generate aggregate insights
        insights = {
            "total_transcripts_analyzed": len(individual_analyses),
            "individual_analyses": individual_analyses,
            "patterns": self.extract_common_phrases(transcripts),
            "timing": self.analyze_timing_patterns(transcripts)
        }
        
        # Calculate averages
        if individual_analyses:
            insights["averages"] = {
                "word_count": statistics.mean([a["word_count"] for a in individual_analyses]),
                "sentence_count": statistics.mean([a["sentence_count"] for a in individual_analyses]),
                "hook_length": statistics.mean([a["hook_length"] for a in individual_analyses]),
                "engagement_score": statistics.mean([a["engagement_score"] for a in individual_analyses]),
                "emotional_intensity": statistics.mean([a["emotional_intensity"] for a in individual_analyses])
            }
        
        # Save insights
        self.save_insights(insights)
        
        return insights
    
    def save_insights(self, insights: Dict):
        """Save analysis insights to file"""
        output_path = self.analysis_path / "transcript_insights.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, ensure_ascii=False)
            print(f"✅ Insights saved to: {output_path}")
        except Exception as e:
            print(f"❌ Error saving insights: {e}")
    
    def generate_transcript_template(self, insights: Dict = None) -> str:
        """Generate a template for new reels based on analysis"""
        if not insights:
            insights = self.load_insights()
        
        if not insights:
            # Default template if no analysis available
            return self.get_default_template()
        
        avg = insights.get("averages", {})
        common_phrases = insights.get("patterns", {}).get("common_bigrams", [])
        
        template = f"""# Reel Transcript Template (Based on Analysis)

## Hook (0-3 seconds) - {int(avg.get('hook_length', 8))} words max
[Strong opening that stops scrolling - use numbers, curiosity, or emotion]
Example patterns:
- "If you [common problem]..."
- "Stop [doing this mistake]..."
- "Here's why [surprising fact]..."

## Body (3-20 seconds) - {int(avg.get('word_count', 50) * 0.7)} words
[Main content with value]
- Use {int(avg.get('sentence_count', 4))} clear sentences
- Include numbers or lists when possible
- Reference common successful phrases: {', '.join([p[0] for p in common_phrases[:5]])}

## CTA (20-30 seconds) - {int(avg.get('word_count', 50) * 0.2)} words  
[Clear call-to-action for engagement]
- Ask a question
- Request an action (comment, follow, save)
- Create urgency or FOMO

## Timing Notes:
- Speak at ~{insights.get('timing', {}).get('avg_words_per_second', 2.5):.1f} words per second
- Total duration: ~{insights.get('timing', {}).get('avg_total_duration', 25):.0f} seconds
- Hook should be punchy and immediate"""
        
        return template
    
    def get_default_template(self) -> str:
        """Default template when no analysis is available"""
        return """# Reel Transcript Template (Default)

## Hook (0-3 seconds) - 6-8 words max
[Strong opening that stops scrolling]
- Use curiosity, numbers, or emotion
- Examples: "If you don't know this...", "Stop doing this mistake", "3 secrets that..."

## Body (3-20 seconds) - 30-40 words
[Main valuable content]
- 3-4 clear sentences
- Include specific tips or insights
- Use "you" to make it personal

## CTA (20-30 seconds) - 8-12 words
[Engagement hook]
- Ask a question
- Request action (comment, follow, save)
- Examples: "Which one will you try first?", "Comment your biggest challenge"

## Timing Notes:
- Speak clearly at 2-3 words per second
- Total duration: 25-30 seconds
- Hook should grab attention immediately"""
    
    def load_insights(self) -> Dict:
        """Load previously saved insights"""
        insights_path = self.analysis_path / "transcript_insights.json"
        
        if not insights_path.exists():
            return {}
        
        try:
            with open(insights_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading insights: {e}")
            return {}

def analyze_transcripts():
    """Main function to analyze all transcripts"""
    analyzer = TranscriptAnalyzer()
    return analyzer.generate_insights()

if __name__ == "__main__":
    # Test the analysis functionality
    analyze_transcripts()