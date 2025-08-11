#!/usr/bin/env python3
"""
Knowledge Base Manager - Manages mentor content and course transcripts
Provides unified access to all knowledge sources for AI enhancement
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib

class KnowledgeBase:
    """
    Centralized knowledge base for mentor content and course transcripts
    """
    
    def __init__(self, data_dir: str = "data/knowledge_base"):
        """Initialize knowledge base"""
        self.data_dir = Path(data_dir)
        self.mentor_dir = self.data_dir / "mentor_profiles"
        self.course_dir = self.data_dir / "course_transcripts"
        self.transcript_dir = self.data_dir / "video_transcripts"
        self.patterns_file = self.data_dir / "patterns.json"
        
        # Create directories
        for directory in [self.mentor_dir, self.course_dir, self.transcript_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Load existing patterns
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load existing content patterns"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'mentor_patterns': {},
            'course_insights': {},
            'successful_hooks': [],
            'effective_ctas': [],
            'content_structures': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_patterns(self):
        """Save patterns to file"""
        self.patterns['last_updated'] = datetime.now().isoformat()
        with open(self.patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)
    
    def add_course_transcript(self, course_name: str, transcript_content: str, 
                            metadata: Optional[Dict] = None) -> bool:
        """
        Add course transcript to knowledge base
        
        Args:
            course_name: Name/identifier for the course
            transcript_content: Full transcript content
            metadata: Optional metadata (instructor, topic, duration, etc.)
            
        Returns:
            bool: Success status
        """
        try:
            # Create course directory
            course_path = self.course_dir / course_name
            course_path.mkdir(exist_ok=True)
            
            # Generate unique filename based on content hash
            content_hash = hashlib.md5(transcript_content.encode()).hexdigest()[:8]
            transcript_file = course_path / f"transcript_{content_hash}.txt"
            
            # Save transcript
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(f"Course: {course_name}\n")
                f.write(f"Added: {datetime.now().isoformat()}\n")
                if metadata:
                    f.write(f"Metadata: {json.dumps(metadata)}\n")
                f.write("-" * 50 + "\n")
                f.write(transcript_content)
            
            # Extract insights from transcript
            insights = self._extract_course_insights(transcript_content, course_name)
            
            # Update patterns
            if course_name not in self.patterns['course_insights']:
                self.patterns['course_insights'][course_name] = []
            
            self.patterns['course_insights'][course_name].append({
                'file': str(transcript_file),
                'insights': insights,
                'added_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            })
            
            self._save_patterns()
            
            print(f"✅ Added course transcript: {course_name}")
            print(f"📄 File: {transcript_file}")
            print(f"🧠 Extracted {len(insights.get('key_points', []))} key insights")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding course transcript: {str(e)}")
            return False
    
    def _extract_course_insights(self, transcript: str, course_name: str) -> Dict:
        """Extract actionable insights from course transcript"""
        insights = {
            'key_points': [],
            'strategies': [],
            'tools_mentioned': [],
            'action_items': [],
            'quotes': [],
            'frameworks': []
        }
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Keywords for different categories
        strategy_keywords = ['strategy', 'approach', 'method', 'technique', 'framework', 'system']
        tool_keywords = ['tool', 'software', 'platform', 'app', 'service', 'api']
        action_keywords = ['should', 'must', 'need to', 'have to', 'always', 'never', 'step']
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Extract strategies
            if any(keyword in sentence_lower for keyword in strategy_keywords):
                insights['strategies'].append(sentence.strip())
            
            # Extract tool mentions
            if any(keyword in sentence_lower for keyword in tool_keywords):
                insights['tools_mentioned'].append(sentence.strip())
            
            # Extract action items
            if any(keyword in sentence_lower for keyword in action_keywords):
                insights['action_items'].append(sentence.strip())
            
            # Extract powerful quotes (sentences with impact words)
            impact_words = ['secret', 'key', 'important', 'crucial', 'essential', 'critical']
            if any(word in sentence_lower for word in impact_words) and len(sentence) < 200:
                insights['quotes'].append(sentence.strip())
        
        # Extract numbered lists and frameworks
        framework_pattern = r'(\d+[\.\)]\s*[^.!?]*(?:[.!?]|$))'
        frameworks = re.findall(framework_pattern, transcript)
        insights['frameworks'] = [f.strip() for f in frameworks[:10]]  # Limit to top 10
        
        # Get key points (first sentences of paragraphs, topic sentences)
        paragraphs = transcript.split('\n\n')
        for para in paragraphs:
            if para.strip():
                first_sentence = para.strip().split('.')[0]
                if len(first_sentence) > 20 and len(first_sentence) < 150:
                    insights['key_points'].append(first_sentence + '.')
        
        # Limit all categories to prevent information overload
        for key in insights:
            if isinstance(insights[key], list):
                insights[key] = insights[key][:15]  # Limit to 15 items each
        
        return insights
    
    def get_mentor_knowledge(self, username: Optional[str] = None) -> Dict:
        """Get mentor knowledge for AI enhancement"""
        mentor_knowledge = {}
        
        if username:
            # Get specific mentor
            profile_file = self.mentor_dir / f"{username}_profile.json"
            if profile_file.exists():
                with open(profile_file, 'r', encoding='utf-8') as f:
                    mentor_knowledge[username] = json.load(f)
        else:
            # Get all mentors
            for profile_file in self.mentor_dir.glob("*_profile.json"):
                username = profile_file.stem.replace('_profile', '')
                with open(profile_file, 'r', encoding='utf-8') as f:
                    mentor_knowledge[username] = json.load(f)
        
        return mentor_knowledge
    
    def get_course_knowledge(self, course_name: Optional[str] = None) -> Dict:
        """Get course knowledge for AI enhancement"""
        if course_name and course_name in self.patterns['course_insights']:
            return {course_name: self.patterns['course_insights'][course_name]}
        
        return self.patterns['course_insights']
    
    def generate_enhanced_prompt(self, base_month: str, topic_focus: str = "AI and business") -> str:
        """
        Generate enhanced AI prompt using knowledge base
        
        Args:
            base_month: Month for calendar generation
            topic_focus: Focus area for content
            
        Returns:
            Enhanced prompt with mentor patterns and course insights
        """
        prompt_parts = []
        
        # Base prompt
        prompt_parts.append(f"""Create a strategic 30-day Instagram Reels content calendar for {base_month} 
focused on {topic_focus} for entrepreneurs.""")
        
        # Add mentor knowledge
        mentor_knowledge = self.get_mentor_knowledge()
        if mentor_knowledge:
            prompt_parts.append("\n🎯 MENTOR INSPIRATION:")
            prompt_parts.append("Use these proven content patterns from successful creators:")
            
            for username, data in list(mentor_knowledge.items())[:2]:  # Limit to 2 mentors
                posts = data.get('posts', [])
                if posts:
                    # Get top performing posts
                    top_posts = sorted(posts, key=lambda x: x.get('likes', 0), reverse=True)[:3]
                    
                    prompt_parts.append(f"\n@{username} patterns:")
                    for i, post in enumerate(top_posts, 1):
                        caption = post.get('caption', '')
                        if caption:
                            # Extract first line as hook example
                            first_line = caption.split('\n')[0]
                            if len(first_line) > 10:
                                prompt_parts.append(f"{i}. Hook style: \"{first_line[:100]}...\"")
                                
                                # Add engagement context
                                likes = post.get('likes', 0)
                                comments = post.get('comments', 0)
                                prompt_parts.append(f"   (Engagement: {likes:,} likes, {comments:,} comments)")
        
        # Add course insights
        course_knowledge = self.get_course_knowledge()
        if course_knowledge:
            prompt_parts.append("\n📚 COURSE INSIGHTS:")
            prompt_parts.append("Incorporate these proven strategies and frameworks:")
            
            all_strategies = []
            all_frameworks = []
            
            for course_name, course_data in course_knowledge.items():
                for entry in course_data:
                    insights = entry.get('insights', {})
                    all_strategies.extend(insights.get('strategies', []))
                    all_frameworks.extend(insights.get('frameworks', []))
            
            # Add top strategies
            if all_strategies:
                prompt_parts.append("\nProven strategies to include:")
                for strategy in all_strategies[:5]:  # Top 5 strategies
                    prompt_parts.append(f"• {strategy[:150]}...")
            
            # Add frameworks
            if all_frameworks:
                prompt_parts.append("\nFrameworks to reference:")
                for framework in all_frameworks[:3]:  # Top 3 frameworks
                    prompt_parts.append(f"• {framework[:150]}...")
        
        # Add successful patterns from knowledge base
        if self.patterns.get('successful_hooks'):
            prompt_parts.append("\n🎣 PROVEN HOOK PATTERNS:")
            for hook in self.patterns['successful_hooks'][:5]:
                prompt_parts.append(f"• {hook}")
        
        if self.patterns.get('effective_ctas'):
            prompt_parts.append("\n💬 EFFECTIVE CTAs:")
            for cta in self.patterns['effective_ctas'][:5]:
                prompt_parts.append(f"• {cta}")
        
        # Final instructions
        prompt_parts.append(f"""
📋 FORMAT REQUIREMENTS:
Generate {base_month} content calendar with these columns:
1. Day | 2. Reel Title | 3. Hook Script (0-2s) | 4. Body Breakdown (3-20s) | 
5. Close/CTA (20-30s) | 6. Format Style | 7. Audio Style | 8. Hashtag Strategy | 
9. Production Notes | 10. Optimization Tips

🎯 CONTENT GUIDELINES:
- Use mentor-inspired hooks that grab attention immediately
- Incorporate course insights and proven frameworks
- Mix educational, inspirational, and actionable content
- Ensure each post provides genuine value to entrepreneurs
- Use psychological triggers and engagement patterns that work
- Focus on {topic_focus} with practical applications""")
        
        return '\n'.join(prompt_parts)
    
    def analyze_mentor_patterns(self):
        """Analyze and update patterns from mentor data"""
        print("🔍 Analyzing mentor patterns...")
        
        mentor_knowledge = self.get_mentor_knowledge()
        
        # Reset patterns
        successful_hooks = []
        effective_ctas = []
        content_structures = []
        
        for username, data in mentor_knowledge.items():
            posts = data.get('posts', [])
            
            # Analyze high-performing posts
            high_performing = [p for p in posts if p.get('likes', 0) > 1000]  # Adjust threshold
            
            for post in high_performing:
                caption = post.get('caption', '')
                analysis = post.get('caption_analysis', {})
                
                if caption:
                    lines = caption.split('\n')
                    first_line = lines[0] if lines else ""
                    
                    # Extract successful hooks
                    if first_line and len(first_line) > 10:
                        successful_hooks.append({
                            'text': first_line,
                            'engagement': post.get('likes', 0) + post.get('comments', 0),
                            'username': username,
                            'patterns': analysis.get('hook_patterns', {})
                        })
                    
                    # Extract effective CTAs
                    if analysis.get('has_cta'):
                        last_line = lines[-1] if lines else ""
                        if last_line and any(word in last_line.lower() for word in ['comment', 'share', 'dm', 'save']):
                            effective_ctas.append({
                                'text': last_line,
                                'engagement': post.get('likes', 0) + post.get('comments', 0),
                                'username': username
                            })
                    
                    # Analyze content structure
                    content_structures.append({
                        'line_count': analysis.get('total_lines', 0),
                        'char_count': analysis.get('total_chars', 0),
                        'has_question': analysis.get('has_question', False),
                        'has_cta': analysis.get('has_cta', False),
                        'engagement': post.get('likes', 0) + post.get('comments', 0),
                        'username': username
                    })
        
        # Update patterns with top performers
        self.patterns['successful_hooks'] = [
            h['text'] for h in sorted(successful_hooks, key=lambda x: x['engagement'], reverse=True)[:15]
        ]
        
        self.patterns['effective_ctas'] = [
            c['text'] for c in sorted(effective_ctas, key=lambda x: x['engagement'], reverse=True)[:10]
        ]
        
        self.patterns['content_structures'] = content_structures
        
        self._save_patterns()
        
        print(f"✅ Updated patterns:")
        print(f"  • {len(self.patterns['successful_hooks'])} successful hooks")
        print(f"  • {len(self.patterns['effective_ctas'])} effective CTAs")
        print(f"  • {len(content_structures)} content structures analyzed")
    
    def get_knowledge_summary(self) -> Dict:
        """Get summary of all knowledge in the base"""
        mentor_knowledge = self.get_mentor_knowledge()
        course_knowledge = self.get_course_knowledge()
        
        summary = {
            'mentors': {
                'count': len(mentor_knowledge),
                'usernames': list(mentor_knowledge.keys()),
                'total_posts': sum(len(data.get('posts', [])) for data in mentor_knowledge.values())
            },
            'courses': {
                'count': len(course_knowledge),
                'names': list(course_knowledge.keys()),
                'total_transcripts': sum(len(transcripts) for transcripts in course_knowledge.values())
            },
            'patterns': {
                'successful_hooks': len(self.patterns.get('successful_hooks', [])),
                'effective_ctas': len(self.patterns.get('effective_ctas', [])),
                'last_updated': self.patterns.get('last_updated')
            }
        }
        
        return summary

def main():
    """Test the knowledge base"""
    kb = KnowledgeBase()
    
    print("🧠 Testing Knowledge Base")
    
    # Test adding course transcript
    sample_transcript = """
    The key to scaling an AI business is automation. You need to identify the top 3 processes 
    that eat up most of your time. Then, you systematically replace them with AI tools.
    
    Here's my proven framework:
    1. Audit your daily tasks
    2. Identify repetitive patterns
    3. Research AI solutions
    4. Implement and test
    5. Scale what works
    
    The secret is not trying to automate everything at once. Focus on one process, perfect it, 
    then move to the next. This approach has helped me scale from $10k to $100k monthly revenue.
    """
    
    kb.add_course_transcript(
        "AI_Business_Scaling", 
        sample_transcript,
        {"instructor": "Expert", "duration": "45min", "topic": "Business Automation"}
    )
    
    # Generate enhanced prompt
    enhanced_prompt = kb.generate_enhanced_prompt("January 2025", "AI automation for entrepreneurs")
    print(f"\n🎯 Enhanced Prompt Preview:")
    print(enhanced_prompt[:500] + "...")
    
    # Get summary
    summary = kb.get_knowledge_summary()
    print(f"\n📊 Knowledge Base Summary:")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()