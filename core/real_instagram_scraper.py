#!/usr/bin/env python3
"""
Real Instagram Scraper - Working 2025 Methods
Extracts actual hooks, captions, and video scripts from Instagram profiles
Uses GraphQL API method that doesn't require login
"""

import requests
import json
import time
import re
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

class RealInstagramScraper:
    """
    Real Instagram scraper using GraphQL API (no login required)
    """
    
    def __init__(self, data_dir: str = "data/real_instagram_data"):
        """Initialize the scraper"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers that work for GraphQL method
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "X-IG-App-ID": "936619743392459",  # This is a known working app ID
            "Content-Type": "application/x-www-form-urlencoded",
            "X-FB-LSD": "AVqbxe3J_YA",
            "X-ASBD-ID": "129477",
            "Sec-Fetch-Site": "same-origin"
        }
        
        # Rate limiting
        self.request_delay = 3  # seconds between requests
        self.max_retries = 3
        
    def get_user_id_from_username(self, username: str) -> Optional[str]:
        """
        Get Instagram user ID from username using web profile info
        """
        try:
            print(f"🔍 Getting user ID for @{username}...")
            
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            headers = {
                "User-Agent": self.headers["User-Agent"],
                "X-IG-App-ID": self.headers["X-IG-App-ID"]
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {}).get('user', {})
                user_id = user_data.get('id')
                
                if user_id:
                    print(f"✅ Found user ID: {user_id}")
                    return user_id
                else:
                    print(f"⚠️ User ID not found in response")
                    return None
            else:
                print(f"❌ Failed to get user info: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting user ID: {e}")
            return None
    
    def get_posts_from_profile(self, username: str, max_posts: int = 50) -> List[Dict]:
        """
        Get posts from Instagram profile using GraphQL API
        """
        posts = []
        
        try:
            print(f"📱 Scraping posts from @{username} using GraphQL...")
            
            # First, get some basic profile info
            user_id = self.get_user_id_from_username(username)
            if not user_id:
                print(f"❌ Could not get user ID for @{username}")
                return posts
            
            # Use GraphQL to get posts
            variables = {
                "id": user_id,
                "first": min(max_posts, 50)  # Instagram limits to 50 per request
            }
            
            graphql_url = "https://www.instagram.com/api/graphql"
            params = {
                "variables": json.dumps(variables),
                "doc_id": "17888483320059182",  # This is the query ID for user media
                "lsd": "AVqbxe3J_YA"
            }
            
            response = requests.post(graphql_url, headers=self.headers, data=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract posts from response
                user_data = data.get('data', {}).get('user', {})
                media_edges = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])
                
                print(f"📊 Found {len(media_edges)} posts")
                
                for edge in media_edges:
                    post_node = edge.get('node', {})
                    
                    try:
                        # Extract post data
                        post_data = {
                            'post_id': post_node.get('id'),
                            'shortcode': post_node.get('shortcode'),
                            'post_url': f"https://www.instagram.com/p/{post_node.get('shortcode')}/",
                            'display_url': post_node.get('display_url'),
                            'is_video': post_node.get('is_video', False),
                            'video_url': post_node.get('video_url'),
                            'like_count': post_node.get('edge_liked_by', {}).get('count', 0),
                            'comment_count': post_node.get('edge_media_to_comment', {}).get('count', 0),
                            'taken_at_timestamp': post_node.get('taken_at_timestamp'),
                            'caption': '',
                            'hashtags': [],
                            'mentions': [],
                            'scraped_at': datetime.now().isoformat()
                        }
                        
                        # Extract caption
                        caption_edges = post_node.get('edge_media_to_caption', {}).get('edges', [])
                        if caption_edges:
                            caption_text = caption_edges[0].get('node', {}).get('text', '')
                            post_data['caption'] = caption_text
                            
                            # Extract hashtags and mentions
                            if caption_text:
                                hashtags = re.findall(r'#(\w+)', caption_text)
                                mentions = re.findall(r'@(\w+)', caption_text)
                                post_data['hashtags'] = hashtags
                                post_data['mentions'] = mentions
                        
                        posts.append(post_data)
                        
                    except Exception as e:
                        print(f"⚠️ Error processing post: {e}")
                        continue
                
                print(f"✅ Successfully scraped {len(posts)} posts from @{username}")
                
            else:
                print(f"❌ GraphQL request failed: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error scraping posts: {e}")
        
        # Rate limiting
        time.sleep(self.request_delay)
        
        return posts
    
    def extract_hooks_and_scripts(self, posts: List[Dict]) -> Dict:
        """
        Extract hooks and video scripts from posts
        """
        hooks = []
        video_scripts = []
        engagement_data = []
        
        for post in posts:
            caption = post.get('caption', '')
            
            if caption:
                # Extract hook (first meaningful line)
                lines = caption.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 15 and not line.startswith('#') and not line.startswith('@'):
                        hooks.append({
                            'hook_text': line,
                            'post_url': post.get('post_url'),
                            'likes': post.get('like_count', 0),
                            'comments': post.get('comment_count', 0),
                            'is_video': post.get('is_video', False)
                        })
                        break
                
                # If it's a video, consider the caption as the "script"
                if post.get('is_video'):
                    video_scripts.append({
                        'script_text': caption,
                        'post_url': post.get('post_url'),
                        'likes': post.get('like_count', 0),
                        'comments': post.get('comment_count', 0),
                        'video_url': post.get('video_url')
                    })
                
                # Collect engagement data
                engagement_data.append({
                    'likes': post.get('like_count', 0),
                    'comments': post.get('comment_count', 0),
                    'caption_length': len(caption),
                    'hashtag_count': len(post.get('hashtags', [])),
                    'is_video': post.get('is_video', False)
                })
        
        return {
            'hooks': hooks,
            'video_scripts': video_scripts,
            'engagement_data': engagement_data
        }
    
    def analyze_content_patterns(self, username: str, posts: List[Dict]) -> Dict:
        """
        Analyze content patterns to extract mentor insights
        """
        extracted_data = self.extract_hooks_and_scripts(posts)
        
        # Analyze hooks
        hooks = extracted_data['hooks']
        top_hooks = sorted(hooks, key=lambda x: x['likes'] + x['comments'], reverse=True)[:10]
        
        # Analyze video scripts
        video_scripts = extracted_data['video_scripts']
        top_video_scripts = sorted(video_scripts, key=lambda x: x['likes'] + x['comments'], reverse=True)[:5]
        
        # Analyze engagement patterns
        engagement_data = extracted_data['engagement_data']
        if engagement_data:
            avg_likes = sum(e['likes'] for e in engagement_data) / len(engagement_data)
            avg_comments = sum(e['comments'] for e in engagement_data) / len(engagement_data)
            video_posts = [e for e in engagement_data if e['is_video']]
            photo_posts = [e for e in engagement_data if not e['is_video']]
            
            avg_video_engagement = sum(e['likes'] + e['comments'] for e in video_posts) / len(video_posts) if video_posts else 0
            avg_photo_engagement = sum(e['likes'] + e['comments'] for e in photo_posts) / len(photo_posts) if photo_posts else 0
        else:
            avg_likes = avg_comments = avg_video_engagement = avg_photo_engagement = 0
        
        # Extract hashtag patterns
        all_hashtags = []
        for post in posts:
            all_hashtags.extend(post.get('hashtags', []))
        
        hashtag_frequency = {}
        for hashtag in all_hashtags:
            hashtag_frequency[hashtag] = hashtag_frequency.get(hashtag, 0) + 1
        
        top_hashtags = sorted(hashtag_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Content type analysis
        total_posts = len(posts)
        video_count = len([p for p in posts if p.get('is_video')])
        photo_count = total_posts - video_count
        
        analysis = {
            'username': username,
            'total_posts_analyzed': total_posts,
            'content_breakdown': {
                'videos': video_count,
                'photos': photo_count,
                'video_percentage': round((video_count / total_posts * 100), 2) if total_posts > 0 else 0
            },
            'top_performing_hooks': [
                {
                    'hook': hook['hook_text'],
                    'engagement': hook['likes'] + hook['comments'],
                    'post_url': hook['post_url']
                } for hook in top_hooks
            ],
            'top_video_scripts': [
                {
                    'script_preview': script['script_text'][:100] + '...' if len(script['script_text']) > 100 else script['script_text'],
                    'engagement': script['likes'] + script['comments'],
                    'post_url': script['post_url']
                } for script in top_video_scripts
            ],
            'engagement_metrics': {
                'avg_likes_per_post': round(avg_likes, 2),
                'avg_comments_per_post': round(avg_comments, 2),
                'avg_video_engagement': round(avg_video_engagement, 2),
                'avg_photo_engagement': round(avg_photo_engagement, 2)
            },
            'hashtag_patterns': top_hashtags,
            'analyzed_at': datetime.now().isoformat()
        }
        
        return analysis
    
    def scrape_mentor_profile(self, username: str, max_posts: int = 50) -> Optional[Dict]:
        """
        Complete mentor profile scraping with real Instagram data
        """
        try:
            print(f"🎯 Starting real scrape of @{username}...")
            
            # Get posts
            posts = self.get_posts_from_profile(username, max_posts)
            
            if not posts:
                print(f"❌ No posts found for @{username}")
                return None
            
            # Analyze patterns
            analysis = self.analyze_content_patterns(username, posts)
            
            # Combine data
            mentor_data = {
                'username': username,
                'scraped_at': datetime.now().isoformat(),
                'posts': posts,
                'content_analysis': analysis,
                'scraping_method': 'GraphQL API (no login required)',
                'success': True
            }
            
            # Save to file
            output_file = self.data_dir / f"{username}_real_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(mentor_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved real data to {output_file}")
            print(f"✅ Successfully scraped {len(posts)} posts with real hooks and scripts!")
            
            return mentor_data
            
        except Exception as e:
            print(f"❌ Error scraping @{username}: {e}")
            return None

def main():
    """Test the real scraper"""
    scraper = RealInstagramScraper()
    
    print("🚀 Testing Real Instagram Scraper...")
    print("=" * 60)
    
    # Test with Alex Hormozi
    print("🎯 Testing with Alex Hormozi...")
    hormozi_data = scraper.scrape_mentor_profile("hormozi", max_posts=20)
    
    if hormozi_data:
        analysis = hormozi_data['content_analysis']
        print(f"📊 Alex Hormozi Results:")
        print(f"   - Posts analyzed: {analysis['total_posts_analyzed']}")
        print(f"   - Videos: {analysis['content_breakdown']['videos']}")
        print(f"   - Photos: {analysis['content_breakdown']['photos']}")
        print(f"   - Top hook: {analysis['top_performing_hooks'][0]['hook'][:50]}..." if analysis['top_performing_hooks'] else "   - No hooks found")
    
    time.sleep(5)  # Rate limiting between requests
    
    # Test with Vaibhav Sisinty
    print("\n🎯 Testing with Vaibhav Sisinty...")
    vaibhav_data = scraper.scrape_mentor_profile("vaibhavsisinty", max_posts=20)
    
    if vaibhav_data:
        analysis = vaibhav_data['content_analysis']
        print(f"📊 Vaibhav Sisinty Results:")
        print(f"   - Posts analyzed: {analysis['total_posts_analyzed']}")
        print(f"   - Videos: {analysis['content_breakdown']['videos']}")
        print(f"   - Photos: {analysis['content_breakdown']['photos']}")
        print(f"   - Top hook: {analysis['top_performing_hooks'][0]['hook'][:50]}..." if analysis['top_performing_hooks'] else "   - No hooks found")
    
    print("\n🎉 Real scraping complete! Check the data/ folder for detailed results.")

if __name__ == "__main__":
    main()