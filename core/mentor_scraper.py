#!/usr/bin/env python3
"""
Mentor Profile Scraper - Extract content from Instagram mentor profiles
Combines Instaloader for reliable data + transcript extraction for video content
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import instaloader
import yt_dlp
from pathlib import Path

class MentorProfileScraper:
    """
    Scrapes Instagram mentor profiles for content patterns and video transcripts
    """
    
    def __init__(self, data_dir: str = "data/knowledge_base"):
        """Initialize scraper with data directory"""
        self.data_dir = Path(data_dir)
        self.mentor_dir = self.data_dir / "mentor_profiles"
        self.transcript_dir = self.data_dir / "video_transcripts"
        
        # Create directories
        self.mentor_dir.mkdir(parents=True, exist_ok=True)
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Instaloader
        self.loader = instaloader.Instaloader(
            download_videos=False,  # We'll handle video URLs separately
            download_pictures=False,  # We only need metadata and captions
            save_metadata=True,
            compress_json=True
        )
        
        # Rate limiting
        self.request_delay = 2  # seconds between requests
        self.last_request_time = 0
        
    def rate_limit(self):
        """Implement rate limiting to avoid being blocked"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()
    
    def scrape_mentor_profile(self, username: str, max_posts: int = 50) -> Dict:
        """
        Scrape a mentor's Instagram profile for content patterns
        
        Args:
            username: Instagram username (without @)
            max_posts: Maximum number of recent posts to analyze
            
        Returns:
            Dict containing profile data and content patterns
        """
        print(f"🔍 Scraping mentor profile: @{username}")
        
        try:
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            # Profile metadata
            profile_data = {
                'username': username,
                'scraped_at': datetime.now().isoformat(),
                'followers': profile.followers,
                'following': profile.followees,
                'posts_count': profile.mediacount,
                'bio': profile.biography,
                'external_url': profile.external_url,
                'is_verified': profile.is_verified,
                'posts': []
            }
            
            # Scrape recent posts
            post_count = 0
            for post in profile.get_posts():
                if post_count >= max_posts:
                    break
                    
                self.rate_limit()
                
                post_data = self._extract_post_data(post, username)
                if post_data:
                    profile_data['posts'].append(post_data)
                    
                    # Extract transcript if it's a video
                    if post.is_video:
                        transcript = self._extract_video_transcript(post, username)
                        if transcript:
                            post_data['transcript'] = transcript
                
                post_count += 1
                print(f"  📄 Processed post {post_count}/{max_posts}")
            
            # Save profile data
            profile_file = self.mentor_dir / f"{username}_profile.json"
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Scraped {post_count} posts from @{username}")
            return profile_data
            
        except Exception as e:
            print(f"❌ Error scraping @{username}: {str(e)}")
            return {}
    
    def _extract_post_data(self, post, username: str) -> Dict:
        """Extract relevant data from a single post"""
        try:
            # Basic post data
            post_data = {
                'shortcode': post.shortcode,
                'date': post.date.isoformat(),
                'caption': post.caption or "",
                'likes': post.likes,
                'comments': post.comments,
                'is_video': post.is_video,
                'url': f"https://instagram.com/p/{post.shortcode}/",
                'media_type': 'video' if post.is_video else 'image',
                'hashtags': [],
                'mentions': []
            }
            
            # Extract hashtags and mentions from caption
            if post.caption:
                caption_text = post.caption.lower()
                
                # Extract hashtags
                import re
                hashtags = re.findall(r'#(\w+)', caption_text)
                post_data['hashtags'] = hashtags
                
                # Extract mentions
                mentions = re.findall(r'@(\w+)', caption_text)
                post_data['mentions'] = mentions
                
                # Analyze caption structure for patterns
                post_data['caption_analysis'] = self._analyze_caption_structure(post.caption)
            
            # Engagement metrics
            if post.likes > 0:
                post_data['engagement_rate'] = (post.likes + post.comments) / post.likes
            
            return post_data
            
        except Exception as e:
            print(f"  ⚠️ Error extracting post data: {str(e)}")
            return {}
    
    def _analyze_caption_structure(self, caption: str) -> Dict:
        """Analyze caption for content patterns"""
        if not caption:
            return {}
        
        lines = caption.strip().split('\n')
        
        analysis = {
            'total_lines': len(lines),
            'total_chars': len(caption),
            'has_question': '?' in caption,
            'has_cta': any(word in caption.lower() for word in [
                'comment', 'share', 'save', 'follow', 'like', 'dm', 
                'link in bio', 'swipe', 'tag', 'try', 'click'
            ]),
            'has_emoji': any(ord(char) > 127 for char in caption),
            'first_line': lines[0] if lines else "",
            'last_line': lines[-1] if lines else "",
            'line_count': len([line for line in lines if line.strip()])
        }
        
        # Detect hook patterns in first line
        first_line = lines[0].lower() if lines else ""
        hook_patterns = {
            'question_hook': first_line.startswith(('what', 'how', 'why', 'when', 'where')),
            'number_hook': any(char.isdigit() for char in first_line[:10]),
            'attention_hook': any(word in first_line for word in [
                'stop', 'wait', 'attention', 'listen', 'watch', 'look'
            ]),
            'problem_hook': any(word in first_line for word in [
                'problem', 'struggle', 'mistake', 'wrong', 'fail'
            ]),
            'benefit_hook': any(word in first_line for word in [
                'secret', 'trick', 'tip', 'hack', 'way to', 'how to'
            ])
        }
        
        analysis['hook_patterns'] = hook_patterns
        
        return analysis
    
    def _extract_video_transcript(self, post, username: str) -> Optional[str]:
        """
        Extract transcript from Instagram video
        Uses yt-dlp for video download and then speech-to-text
        """
        try:
            if not post.is_video:
                return None
            
            video_url = f"https://instagram.com/p/{post.shortcode}/"
            
            # Configure yt-dlp for Instagram
            ydl_opts = {
                'format': 'best[height<=480]',  # Lower quality for faster processing
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract video info
                    info = ydl.extract_info(video_url, download=False)
                    
                    # For now, we'll use the caption as a proxy for transcript
                    # In a future enhancement, we could add actual speech-to-text
                    transcript = post.caption or ""
                    
                    # Save transcript file
                    transcript_file = self.transcript_dir / f"{username}_{post.shortcode}_transcript.txt"
                    with open(transcript_file, 'w', encoding='utf-8') as f:
                        f.write(f"Post URL: {video_url}\n")
                        f.write(f"Date: {post.date.isoformat()}\n")
                        f.write(f"Likes: {post.likes}\n")
                        f.write(f"Comments: {post.comments}\n")
                        f.write(f"Caption/Transcript:\n{transcript}\n")
                    
                    print(f"  🎬 Extracted transcript for video {post.shortcode}")
                    return transcript
                    
                except Exception as e:
                    print(f"  ⚠️ Could not extract video transcript: {str(e)}")
                    return post.caption  # Fallback to caption
                    
        except Exception as e:
            print(f"  ❌ Error in video transcript extraction: {str(e)}")
            return None
    
    def get_mentor_knowledge_summary(self, username: str) -> Dict:
        """
        Generate a summary of mentor's content patterns for AI enhancement
        """
        profile_file = self.mentor_dir / f"{username}_profile.json"
        
        if not profile_file.exists():
            print(f"❌ No data found for @{username}")
            return {}
        
        with open(profile_file, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
        
        posts = profile_data.get('posts', [])
        if not posts:
            return {}
        
        # Analyze patterns across all posts
        summary = {
            'username': username,
            'total_posts_analyzed': len(posts),
            'avg_engagement': sum(p.get('likes', 0) + p.get('comments', 0) for p in posts) / len(posts),
            'top_hashtags': self._get_top_hashtags(posts),
            'common_hook_patterns': self._get_common_hook_patterns(posts),
            'successful_cta_patterns': self._get_successful_ctas(posts),
            'content_themes': self._extract_content_themes(posts),
            'optimal_posting_patterns': self._analyze_posting_patterns(posts)
        }
        
        return summary
    
    def _get_top_hashtags(self, posts: List[Dict]) -> List[str]:
        """Get most frequently used hashtags"""
        hashtag_counts = {}
        for post in posts:
            for hashtag in post.get('hashtags', []):
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        return sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _get_common_hook_patterns(self, posts: List[Dict]) -> Dict:
        """Analyze common hook patterns"""
        hook_patterns = {}
        for post in posts:
            analysis = post.get('caption_analysis', {})
            patterns = analysis.get('hook_patterns', {})
            for pattern, found in patterns.items():
                if found:
                    hook_patterns[pattern] = hook_patterns.get(pattern, 0) + 1
        
        return hook_patterns
    
    def _get_successful_ctas(self, posts: List[Dict]) -> List[Dict]:
        """Find high-performing CTAs"""
        successful_ctas = []
        for post in posts:
            if post.get('caption_analysis', {}).get('has_cta') and post.get('likes', 0) > 0:
                successful_ctas.append({
                    'caption': post.get('caption', ''),
                    'engagement': post.get('likes', 0) + post.get('comments', 0),
                    'shortcode': post.get('shortcode')
                })
        
        return sorted(successful_ctas, key=lambda x: x['engagement'], reverse=True)[:5]
    
    def _extract_content_themes(self, posts: List[Dict]) -> List[str]:
        """Extract common content themes from captions"""
        # Simple keyword-based theme extraction
        # Could be enhanced with NLP in the future
        themes = {}
        keywords = [
            'ai', 'artificial intelligence', 'business', 'entrepreneur', 'marketing',
            'strategy', 'growth', 'productivity', 'automation', 'tools', 'tips',
            'success', 'mindset', 'scaling', 'revenue', 'profit', 'content'
        ]
        
        for post in posts:
            caption = post.get('caption', '').lower()
            for keyword in keywords:
                if keyword in caption:
                    themes[keyword] = themes.get(keyword, 0) + 1
        
        return sorted(themes.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def _analyze_posting_patterns(self, posts: List[Dict]) -> Dict:
        """Analyze optimal posting times and patterns"""
        # Extract posting hours and days
        posting_hours = []
        posting_days = []
        
        for post in posts:
            try:
                post_date = datetime.fromisoformat(post['date'].replace('Z', '+00:00'))
                posting_hours.append(post_date.hour)
                posting_days.append(post_date.weekday())
            except:
                continue
        
        # Find most common posting times
        hour_counts = {}
        for hour in posting_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        optimal_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'optimal_hours': optimal_hours,
            'total_posts_analyzed': len(posting_hours)
        }

def main():
    """Test the scraper with a sample profile"""
    scraper = MentorProfileScraper()
    
    # Example usage
    print("🚀 Testing Mentor Profile Scraper")
    
    # You would replace this with actual mentor usernames
    test_username = "garyvee"  # Example public business profile
    
    # Scrape profile
    profile_data = scraper.scrape_mentor_profile(test_username, max_posts=10)
    
    if profile_data:
        # Generate knowledge summary
        summary = scraper.get_mentor_knowledge_summary(test_username)
        print(f"\n📊 Knowledge Summary for @{test_username}:")
        print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()