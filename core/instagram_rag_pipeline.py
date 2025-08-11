#!/usr/bin/env python3
"""
Instagram Reels → RAG Pipeline
One-time ingestion pipeline for Hormozi + Vaibhav content using specified APIs
"""

import requests
import json
import time
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import hashlib
import re
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ReelData:
    """Data structure for Instagram Reel"""
    reel_url: str
    video_url: str
    caption: str
    hashtags: List[str]
    view_count: int
    like_count: int
    timestamp: str
    owner_username: str
    is_trending: bool = False
    transcript: Optional[str] = None
    hook: Optional[str] = None

class InstagramRAGPipeline:
    """
    One-time Instagram Reels → RAG pipeline using specified APIs
    """
    
    def __init__(self, db_path: str = "data/instagram_rag.db"):
        """Initialize the pipeline"""
        self.db_path = db_path
        self.data_dir = Path("data/instagram_rag")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # API configuration
        self.apify_token = os.getenv('APIFY_TOKEN')
        self.assemblyai_token = os.getenv('ASSEMBLYAI_TOKEN')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Pipeline parameters - REGULATED TO PREVENT OVERSAMPLING
        self.target_creators = ["hormozi", "vaibhavsisinty"]
        self.fetch_per_creator = 120  # Still fetch 120 for selection pool
        self.trending_keep_per_creator = 5  # REGULATED: Only keep top 5 per creator
        
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        logger.info("Initializing database...")
        
        with sqlite3.connect(self.db_path) as conn:
            # Creators table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS creators (
                    id INTEGER PRIMARY KEY,
                    handle TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    follower_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Reels table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reels (
                    id INTEGER PRIMARY KEY,
                    reel_url TEXT UNIQUE NOT NULL,
                    video_url TEXT,
                    caption TEXT,
                    hashtags TEXT,  -- JSON array
                    view_count INTEGER DEFAULT 0,
                    like_count INTEGER DEFAULT 0,
                    posted_at TIMESTAMP,
                    creator_id INTEGER,
                    is_trending BOOLEAN DEFAULT FALSE,
                    hook TEXT,
                    transcript TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES creators (id)
                )
            """)
            
            # RAG chunks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rag_chunks (
                    id INTEGER PRIMARY KEY,
                    reel_id INTEGER,
                    chunk_text TEXT NOT NULL,
                    chunk_index INTEGER,
                    embedding BLOB,  -- Serialized embedding vector
                    token_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (reel_id) REFERENCES reels (id)
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reels_trending ON reels (is_trending)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reels_creator ON reels (creator_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_reel ON rag_chunks (reel_id)")
            
            conn.commit()
        
        logger.info("Database initialized successfully")
    
    def step1_scrape_reels(self) -> List[ReelData]:
        """
        Step 1: Get Instagram Reels data (Apify primary, manual fallback)
        """
        # Use Apify first since we have paid subscription
        logger.info("Step 1: Scraping Instagram Reels with Apify...")
        
        if not self.apify_token:
            logger.error("APIFY_TOKEN not found in environment")
            return []
        
        # Use main Instagram scraper with paid subscription
        actor_id = "apify/instagram-scraper"  # Main Instagram scraper
        
        # Start the scraping run - Note: Apify uses ~ instead of / in URLs
        actor_id_url = actor_id.replace("/", "~")
        start_url = f"https://api.apify.com/v2/acts/{actor_id_url}/runs"
        
        input_data = {
            "directUrls": [f"https://www.instagram.com/{creator}/" for creator in self.target_creators],
            "resultsLimit": 120  # Total limit across all profiles
        }
        
        headers = {"Content-Type": "application/json"}
        params = {"token": self.apify_token}
        
        try:
            # Start run
            logger.info(f"Starting Apify run for creators: {self.target_creators}")
            start_response = requests.post(start_url, json=input_data, headers=headers, params=params)
            start_response.raise_for_status()
            
            run_data = start_response.json()
            run_id = run_data["data"]["id"]
            dataset_id = run_data["data"]["defaultDatasetId"]
            
            logger.info(f"Run started with ID: {run_id}")
            
            # Poll run status
            status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
            
            while True:
                status_response = requests.get(status_url, params=params)
                status_response.raise_for_status()
                
                status_data = status_response.json()
                status = status_data["data"]["status"]
                
                logger.info(f"Run status: {status}")
                
                if status == "SUCCEEDED":
                    break
                elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
                    logger.error(f"Run failed with status: {status}")
                    return []
                
                time.sleep(10)  # Wait 10 seconds before checking again
            
            # Fetch dataset
            dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
            dataset_params = {**params, "clean": "true", "format": "json"}
            
            dataset_response = requests.get(dataset_url, params=dataset_params)
            dataset_response.raise_for_status()
            
            raw_data = dataset_response.json()
            logger.info(f"Fetched {len(raw_data)} items from dataset")
            
            # Convert to ReelData objects
            reels = []
            for item in raw_data:
                try:
                    reel = self._parse_apify_reel(item)
                    if reel:
                        reels.append(reel)
                except Exception as e:
                    logger.warning(f"Error parsing reel item: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(reels)} reels")
            return reels
            
        except Exception as e:
            logger.error(f"Error in Apify scraping: {e}")
            
            # Fallback to manual data if Apify fails
            try:
                from manual_mentor_data import convert_to_pipeline_format
                logger.info("🔄 Falling back to manual mentor data")
                manual_reels = convert_to_pipeline_format()
                if manual_reels:
                    logger.info(f"✅ Loaded {len(manual_reels)} reels from manual data fallback")
                    return manual_reels
            except Exception as manual_error:
                logger.warning(f"Manual data fallback also failed: {manual_error}")
            
            return []
    
    def _parse_apify_reel(self, item: Dict) -> Optional[ReelData]:
        """Parse Apify response item into ReelData"""
        try:
            # Map fields (adjust based on actual Apify response structure)
            reel_url = item.get("url") or item.get("reelUrl") or item.get("postUrl")
            video_url = item.get("videoUrl") or item.get("video", {}).get("url")
            caption = item.get("caption", "")
            hashtags = item.get("hashtags", [])
            view_count = item.get("videoViewCount") or item.get("viewCount", 0)
            like_count = item.get("likeCount", 0)
            timestamp = item.get("timestamp") or item.get("takenAt")
            owner_username = item.get("ownerUsername") or item.get("username")
            
            if not reel_url or not video_url:
                return None
            
            return ReelData(
                reel_url=reel_url,
                video_url=video_url,
                caption=caption,
                hashtags=hashtags if isinstance(hashtags, list) else [],
                view_count=int(view_count) if view_count else 0,
                like_count=int(like_count) if like_count else 0,
                timestamp=timestamp,
                owner_username=owner_username
            )
            
        except Exception as e:
            logger.warning(f"Error parsing reel item: {e}")
            return None
    
    def step2_rank_trending(self, reels: List[ReelData]) -> List[ReelData]:
        """
        Step 2: Rank and select top trending reels
        """
        logger.info("Step 2: Ranking trending reels...")
        
        # Group by creator
        creator_reels = {}
        for reel in reels:
            creator = reel.owner_username
            if creator not in creator_reels:
                creator_reels[creator] = []
            creator_reels[creator].append(reel)
        
        trending_reels = []
        
        for creator, creator_reel_list in creator_reels.items():
            # Sort by views (fallback to likes)
            sorted_reels = sorted(
                creator_reel_list, 
                key=lambda r: (r.view_count or 0, r.like_count or 0), 
                reverse=True
            )
            
            # Take top N per creator
            top_reels = sorted_reels[:self.trending_keep_per_creator]
            
            # Mark as trending
            for reel in top_reels:
                reel.is_trending = True
            
            trending_reels.extend(top_reels)
            logger.info(f"Selected {len(top_reels)} trending reels for @{creator}")
        
        logger.info(f"Total trending reels selected: {len(trending_reels)}")
        return trending_reels
    
    def step3_transcribe_reels(self, reels: List[ReelData]) -> List[ReelData]:
        """
        Step 3: Auto-transcribe using AssemblyAI
        """
        logger.info("Step 3: Transcribing reels with AssemblyAI...")
        
        if not self.assemblyai_token:
            logger.error("ASSEMBLYAI_TOKEN not found in environment")
            return reels
        
        headers = {
            "authorization": self.assemblyai_token,
            "content-type": "application/json"
        }
        
        for i, reel in enumerate(reels):
            try:
                logger.info(f"Transcribing reel {i+1}/{len(reels)}: {reel.reel_url}")
                
                # Create transcription job
                transcript_data = {"audio_url": reel.video_url}
                
                create_response = requests.post(
                    "https://api.assemblyai.com/v2/transcript",
                    json=transcript_data,
                    headers=headers
                )
                create_response.raise_for_status()
                
                transcript_job = create_response.json()
                transcript_id = transcript_job["id"]
                
                logger.info(f"Created transcription job: {transcript_id}")
                
                # Poll for completion
                while True:
                    status_response = requests.get(
                        f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                        headers=headers
                    )
                    status_response.raise_for_status()
                    
                    status_data = status_response.json()
                    status = status_data["status"]
                    
                    if status == "completed":
                        reel.transcript = status_data.get("text", "")
                        logger.info(f"Transcription completed for reel {i+1}")
                        break
                    elif status == "error":
                        logger.warning(f"Transcription failed for reel {i+1}: {status_data.get('error')}")
                        reel.transcript = None
                        break
                    
                    time.sleep(5)  # Wait 5 seconds before checking again
                
                # Extract hook
                reel.hook = self._extract_hook(reel.caption, reel.transcript)
                
            except Exception as e:
                logger.warning(f"Error transcribing reel {i+1}: {e}")
                # Try fallback method
                reel.transcript = self._fallback_transcribe(reel.video_url)
                reel.hook = self._extract_hook(reel.caption, reel.transcript)
        
        logger.info("Transcription step completed")
        return reels
    
    def _fallback_transcribe(self, video_url: str) -> Optional[str]:
        """
        Fallback transcription using yt-dlp + OpenAI Whisper
        """
        try:
            logger.info("Attempting fallback transcription...")
            
            # Download video with yt-dlp
            temp_dir = self.data_dir / "temp"
            temp_dir.mkdir(exist_ok=True)
            
            # Generate unique filename
            video_hash = hashlib.md5(video_url.encode()).hexdigest()[:8]
            audio_file = temp_dir / f"audio_{video_hash}.mp3"
            
            # Use yt-dlp to extract audio
            cmd = [
                "yt-dlp",
                "--extract-audio",
                "--audio-format", "mp3",
                "--output", str(audio_file),
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning(f"yt-dlp failed: {result.stderr}")
                return None
            
            # Transcribe with OpenAI
            if self.openai_api_key and audio_file.exists():
                headers = {"Authorization": f"Bearer {self.openai_api_key}"}
                
                with open(audio_file, "rb") as f:
                    files = {"file": f}
                    data = {"model": "whisper-1"}
                    
                    response = requests.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers=headers,
                        files=files,
                        data=data
                    )
                    
                    if response.status_code == 200:
                        transcript_data = response.json()
                        transcript = transcript_data.get("text", "")
                        
                        # Clean up temp file
                        audio_file.unlink(missing_ok=True)
                        
                        return transcript
            
            # Clean up temp file
            audio_file.unlink(missing_ok=True)
            
        except Exception as e:
            logger.warning(f"Fallback transcription failed: {e}")
        
        return None
    
    def _extract_hook(self, caption: str, transcript: Optional[str]) -> Optional[str]:
        """
        Extract hook from caption or transcript
        """
        # Try caption first
        if caption:
            # Method 1: First punchy sentence ≤140 chars
            sentences = re.split(r'[.!?]+', caption)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) <= 140 and len(sentence) > 10:
                    return sentence
            
            # Method 2: First 2 short lines
            lines = caption.split('\n')
            short_lines = [line.strip() for line in lines[:2] if len(line.strip()) < 100]
            if short_lines:
                return ' '.join(short_lines)
            
            # Method 3: First sentence
            if sentences:
                first_sentence = sentences[0].strip()
                if len(first_sentence) > 10:
                    return first_sentence[:140]
        
        # Try transcript if no good hook from caption
        if transcript:
            sentences = re.split(r'[.!?]+', transcript)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) <= 140 and len(sentence) > 10:
                    return sentence
        
        return None
    
    def step4_store_normalize(self, reels: List[ReelData]) -> None:
        """
        Step 4: Normalize and store in database
        """
        logger.info("Step 4: Storing reels in database...")
        
        with sqlite3.connect(self.db_path) as conn:
            # Store creators
            for creator in self.target_creators:
                conn.execute(
                    "INSERT OR IGNORE INTO creators (handle) VALUES (?)",
                    (creator,)
                )
            
            # Get creator IDs
            creator_ids = {}
            for creator in self.target_creators:
                cursor = conn.execute(
                    "SELECT id FROM creators WHERE handle = ?",
                    (creator,)
                )
                result = cursor.fetchone()
                if result:
                    creator_ids[creator] = result[0]
            
            # Store reels (with deduplication)
            stored_count = 0
            for reel in reels:
                creator_id = creator_ids.get(reel.owner_username)
                if not creator_id:
                    continue
                
                try:
                    conn.execute("""
                        INSERT OR REPLACE INTO reels (
                            reel_url, video_url, caption, hashtags, view_count, 
                            like_count, posted_at, creator_id, is_trending, 
                            hook, transcript
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        reel.reel_url,
                        reel.video_url,
                        reel.caption,
                        json.dumps(reel.hashtags),
                        reel.view_count,
                        reel.like_count,
                        reel.timestamp,
                        creator_id,
                        reel.is_trending,
                        reel.hook,
                        reel.transcript
                    ))
                    stored_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error storing reel {reel.reel_url}: {e}")
            
            conn.commit()
            logger.info(f"Stored {stored_count} reels in database")
    
    def step5_chunk_and_embed(self) -> None:
        """
        Step 5: Chunk content and create embeddings for RAG
        """
        logger.info("Step 5: Chunking and creating embeddings...")
        
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            # Get reels that need embedding
            cursor = conn.execute("""
                SELECT id, caption, transcript, hook 
                FROM reels 
                WHERE is_trending = TRUE 
                AND id NOT IN (SELECT DISTINCT reel_id FROM rag_chunks)
            """)
            
            reels_to_process = cursor.fetchall()
            logger.info(f"Processing {len(reels_to_process)} reels for embedding")
            
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            for reel_id, caption, transcript, hook in reels_to_process:
                try:
                    # Combine content for chunking
                    content_parts = []
                    if hook:
                        content_parts.append(f"Hook: {hook}")
                    if caption:
                        content_parts.append(f"Caption: {caption}")
                    if transcript:
                        content_parts.append(f"Transcript: {transcript}")
                    
                    full_content = "\n\n".join(content_parts)
                    
                    # Simple sentence-aware chunking (~700-900 tokens)
                    chunks = self._chunk_content(full_content)
                    
                    for chunk_index, chunk_text in enumerate(chunks):
                        # Create embedding
                        embedding_data = {
                            "model": "text-embedding-3-large",
                            "input": chunk_text
                        }
                        
                        response = requests.post(
                            "https://api.openai.com/v1/embeddings",
                            json=embedding_data,
                            headers=headers
                        )
                        response.raise_for_status()
                        
                        embedding_result = response.json()
                        embedding_vector = embedding_result["data"][0]["embedding"]
                        
                        # Serialize embedding
                        embedding_blob = json.dumps(embedding_vector).encode()
                        
                        # Store chunk and embedding
                        conn.execute("""
                            INSERT INTO rag_chunks (
                                reel_id, chunk_text, chunk_index, embedding, token_count
                            ) VALUES (?, ?, ?, ?, ?)
                        """, (
                            reel_id,
                            chunk_text,
                            chunk_index,
                            embedding_blob,
                            len(chunk_text.split())  # Rough token count
                        ))
                        
                        time.sleep(0.1)  # Rate limiting
                
                except Exception as e:
                    logger.warning(f"Error embedding reel {reel_id}: {e}")
            
            conn.commit()
            logger.info("Embedding step completed")
    
    def _chunk_content(self, content: str, target_tokens: int = 800) -> List[str]:
        """
        Sentence-aware chunking for ~700-900 tokens
        """
        sentences = re.split(r'(?<=[.!?])\s+', content)
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(sentence.split())
            
            if current_tokens + sentence_tokens > target_tokens and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_tokens = sentence_tokens
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def step6_create_retrieval_endpoint(self) -> None:
        """
        Step 6: This will be implemented in the Flask app
        The retrieval logic will be added to app.py
        """
        logger.info("Step 6: Retrieval endpoint will be implemented in Flask app")
        # This is handled in the Flask integration
        pass
    
    def run_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete pipeline
        """
        logger.info("🚀 Starting Instagram Reels → RAG Pipeline")
        start_time = datetime.now()
        
        results = {
            "start_time": start_time.isoformat(),
            "steps_completed": [],
            "errors": [],
            "final_stats": {}
        }
        
        try:
            # Step 1: Scrape reels
            reels = self.step1_scrape_reels()
            results["steps_completed"].append("scrape_reels")
            results["scraped_count"] = len(reels)
            
            if not reels:
                logger.warning("No reels scraped, stopping pipeline")
                return results
            
            # Step 2: Rank trending
            trending_reels = self.step2_rank_trending(reels)
            results["steps_completed"].append("rank_trending")
            results["trending_count"] = len(trending_reels)
            
            # Step 3: Transcribe
            transcribed_reels = self.step3_transcribe_reels(trending_reels)
            results["steps_completed"].append("transcribe_reels")
            
            # Step 4: Store
            self.step4_store_normalize(transcribed_reels)
            results["steps_completed"].append("store_normalize")
            
            # Step 5: Chunk and embed
            self.step5_chunk_and_embed()
            results["steps_completed"].append("chunk_and_embed")
            
            # Get final stats
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM reels WHERE is_trending = TRUE")
                trending_stored = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM rag_chunks")
                chunks_created = cursor.fetchone()[0]
                
                results["final_stats"] = {
                    "trending_reels_stored": trending_stored,
                    "rag_chunks_created": chunks_created
                }
            
            end_time = datetime.now()
            results["end_time"] = end_time.isoformat()
            results["duration_minutes"] = (end_time - start_time).total_seconds() / 60
            
            logger.info("🎉 Pipeline completed successfully!")
            logger.info(f"Final stats: {results['final_stats']}")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results["errors"].append(str(e))
        
        return results

def main():
    """Run the pipeline"""
    # Check environment variables
    required_env = ["APIFY_TOKEN", "ASSEMBLYAI_TOKEN", "OPENAI_API_KEY"]
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        logger.error(f"Missing required environment variables: {missing_env}")
        logger.info("Please set these in your .env file or environment")
        return
    
    # Run pipeline
    pipeline = InstagramRAGPipeline()
    results = pipeline.run_pipeline()
    
    # Save results
    results_file = pipeline.data_dir / "pipeline_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {results_file}")

if __name__ == "__main__":
    main()