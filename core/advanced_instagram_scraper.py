#!/usr/bin/env python3
"""
Advanced Instagram Scraper using instagrapi
Scrapes real-time data including hooks, scripts, captions from mentor profiles
"""

import json
import time
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

try:
    from instagrapi import Client
    from instagrapi.exceptions import LoginRequired, PrivateError, ClientError
    INSTAGRAPI_AVAILABLE = True
except ImportError:
    INSTAGRAPI_AVAILABLE = False
    print("⚠️ instagrapi not available. Install with: pip install instagrapi")

class AdvancedInstagramScraper:
    """
    Advanced Instagram scraper for mentor profiles using instagrapi
    """
    
    def __init__(self, data_dir: str = "data/instagram_data"):
        """Initialize the scraper"""
        if not INSTAGRAPI_AVAILABLE:
            raise ImportError("instagrapi library is required. Install with: pip install instagrapi")
        
        self.client = Client()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Session file for persistence
        self.session_file = self.data_dir / "session.json"
        
        # Rate limiting
        self.request_delay = 2  # seconds between requests
        self.max_retries = 3
        
    def login_anonymous(self) -> bool:
        """
        Try to access Instagram without login (public data only)
        """
        try:
            print("🔄 Attempting anonymous access to Instagram...")
            # Try to access public data without login
            # instagrapi can sometimes access public data without login
            return True
        except Exception as e:
            print(f"⚠️ Anonymous access failed: {e}")
            return False
    
    def login_with_credentials(self, username: str, password: str) -> bool:
        """
        Login with Instagram credentials (if available)
        """
        try:
            print(f"🔄 Logging in as {username}...")
            
            # Load previous session if exists
            if self.session_file.exists():
                print("📱 Loading previous session...")
                self.client.load_settings(str(self.session_file))
            
            # Login
            self.client.login(username, password)
            
            # Save session
            self.client.dump_settings(str(self.session_file))
            print("✅ Login successful!")
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def scrape_profile_public_data(self, username: str) -> Optional[Dict]:
        """
        Scrape public profile data without login
        """
        try:
            print(f"🔍 Scraping public data for @{username}...")
            
            # Get user info
            user_info = self.client.user_info_by_username(username)
            
            profile_data = {
                'username': username,
                'user_id': str(user_info.pk),
                'full_name': user_info.full_name,
                'bio': user_info.biography,
                'followers_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'media_count': user_info.media_count,
                'is_private': user_info.is_private,
                'scraped_at': datetime.now().isoformat(),
                'posts': []
            }
            
            if user_info.is_private:
                print(f"⚠️ @{username} is a private account. Limited data available.")
                return profile_data
            
            return profile_data
            
        except Exception as e:
            print(f"❌ Error scraping @{username}: {e}")
            return None
    
    def scrape_user_posts(self, username: str, max_posts: int = 50) -> List[Dict]:
        """
        Scrape recent posts from a user
        """
        posts = []
        
        try:
            print(f"📱 Scraping posts from @{username}...")
            
            # Get user ID
            user_info = self.client.user_info_by_username(username)
            user_id = user_info.pk
            
            # Get user posts
            medias = self.client.user_medias(user_id, amount=max_posts)
            
            for media in medias:
                try:
                    # Extract post data
                    post_data = {
                        'post_id': str(media.pk),
                        'shortcode': media.code,
                        'post_url': f"https://www.instagram.com/p/{media.code}/",
                        'caption': media.caption_text or '',
                        'media_type': str(media.media_type),
                        'like_count': media.like_count or 0,
                        'comment_count': media.comment_count or 0,
                        'taken_at': media.taken_at.isoformat() if media.taken_at else None,
                        'hashtags': [],
                        'mentions': [],
                        'is_video': media.media_type == 2,  # 2 is video
                        'video_url': None,
                        'image_url': media.thumbnail_url,
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # Extract hashtags and mentions from caption
                    if post_data['caption']:
                        # Extract hashtags
                        import re
                        hashtags = re.findall(r'#(\w+)', post_data['caption'])
                        post_data['hashtags'] = hashtags
                        
                        # Extract mentions
                        mentions = re.findall(r'@(\w+)', post_data['caption'])
                        post_data['mentions'] = mentions
                    
                    # Get video URL if it's a video/reel
                    if post_data['is_video']:
                        try:
                            post_data['video_url'] = media.video_url
                        except:
                            print(f"⚠️ Could not get video URL for {post_data['shortcode']}")
                    
                    posts.append(post_data)
                    
                    # Rate limiting
                    time.sleep(self.request_delay)
                    
                except Exception as e:
                    print(f"⚠️ Error processing post {media.code}: {e}")
                    continue
            
            print(f"✅ Scraped {len(posts)} posts from @{username}")
            return posts
            
        except Exception as e:
            print(f"❌ Error scraping posts from @{username}: {e}")
            return posts
    
    def extract_reel_scripts(self, posts: List[Dict]) -> List[Dict]:
        """
        Extract video scripts/spoken content from Reels
        Note: This would require video transcript extraction
        """
        reel_scripts = []
        
        for post in posts:
            if post.get('is_video') and post.get('video_url'):
                # For now, we'll use the caption as the "script"
                # In the future, you could integrate speech-to-text
                script_data = {
                    'post_id': post['post_id'],
                    'shortcode': post['shortcode'],
                    'script_text': post['caption'],  # Using caption as script
                    'estimated_duration': None,  # Could be extracted from video
                    'extracted_at': datetime.now().isoformat()
                }
                reel_scripts.append(script_data)
        
        return reel_scripts
    
    def scrape_mentor_profile(self, username: str, max_posts: int = 50, 
                            use_login: bool = False, login_username: str = None, 
                            login_password: str = None) -> Optional[Dict]:
        """
        Complete mentor profile scraping
        """
        try:
            # Setup client
            if use_login and login_username and login_password:
                if not self.login_with_credentials(login_username, login_password):
                    print("⚠️ Login failed, trying anonymous access...")
            
            # Scrape profile data
            profile_data = self.scrape_profile_public_data(username)
            if not profile_data:
                return None
            
            # Scrape posts
            posts = self.scrape_user_posts(username, max_posts)
            profile_data['posts'] = posts
            
            # Extract reel scripts
            reel_scripts = self.extract_reel_scripts(posts)
            profile_data['reel_scripts'] = reel_scripts
            
            # Save data
            output_file = self.data_dir / f"{username}_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved data to {output_file}")
            
            # Generate analytics
            analytics = self.analyze_content_patterns(profile_data)
            profile_data['content_analytics'] = analytics
            
            return profile_data
            
        except Exception as e:
            print(f"❌ Error scraping mentor profile @{username}: {e}")
            return None
    
    def analyze_content_patterns(self, profile_data: Dict) -> Dict:
        """
        Analyze content patterns from scraped data
        """
        posts = profile_data.get('posts', [])
        
        if not posts:
            return {}
        
        # Extract hooks (first line of captions)
        hooks = []
        for post in posts:
            caption = post.get('caption', '')
            if caption:
                first_line = caption.split('\n')[0].strip()
                if first_line and len(first_line) > 10:  # Meaningful hooks
                    hooks.append(first_line)
        
        # Extract hashtag patterns
        all_hashtags = []
        for post in posts:
            all_hashtags.extend(post.get('hashtags', []))
        
        # Count hashtag frequency
        hashtag_counts = {}
        for hashtag in all_hashtags:
            hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        # Sort by frequency
        top_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate engagement metrics
        total_likes = sum(post.get('like_count', 0) for post in posts)
        total_comments = sum(post.get('comment_count', 0) for post in posts)
        avg_likes = total_likes / len(posts) if posts else 0
        avg_comments = total_comments / len(posts) if posts else 0
        
        analytics = {
            'total_posts_analyzed': len(posts),
            'unique_hooks_found': len(hooks),
            'sample_hooks': hooks[:10],  # Top 10 hooks
            'top_hashtags': top_hashtags,
            'engagement_metrics': {
                'avg_likes_per_post': round(avg_likes, 2),
                'avg_comments_per_post': round(avg_comments, 2),
                'total_likes': total_likes,
                'total_comments': total_comments
            },
            'content_types': {
                'videos': len([p for p in posts if p.get('is_video')]),
                'photos': len([p for p in posts if not p.get('is_video')])
            },
            'analyzed_at': datetime.now().isoformat()
        }
        
        return analytics

def main():
    """Test the scraper"""
    if not INSTAGRAPI_AVAILABLE:
        print("❌ instagrapi not available. Please install with: pip install instagrapi")
        return
    
    scraper = AdvancedInstagramScraper()
    
    # Test with Alex Hormozi
    print("🎯 Testing scraper with Alex Hormozi...")
    hormozi_data = scraper.scrape_mentor_profile(
        username="hormozi",
        max_posts=20,
        use_login=False  # Try without login first
    )
    
    if hormozi_data:
        print(f"✅ Successfully scraped @hormozi:")
        print(f"   - Posts: {len(hormozi_data.get('posts', []))}")
        print(f"   - Hooks found: {hormozi_data.get('content_analytics', {}).get('unique_hooks_found', 0)}")
    
    # Test with Vaibhav Sisinty
    print("\n🎯 Testing scraper with Vaibhav Sisinty...")
    vaibhav_data = scraper.scrape_mentor_profile(
        username="vaibhavsisinty",
        max_posts=20,
        use_login=False
    )
    
    if vaibhav_data:
        print(f"✅ Successfully scraped @vaibhavsisinty:")
        print(f"   - Posts: {len(vaibhav_data.get('posts', []))}")
        print(f"   - Hooks found: {vaibhav_data.get('content_analytics', {}).get('unique_hooks_found', 0)}")

if __name__ == "__main__":
    main()