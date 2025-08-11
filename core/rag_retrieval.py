#!/usr/bin/env python3
"""
RAG Retrieval System for Instagram Content
Provides hybrid retrieval with vector similarity + keyword search
"""

import sqlite3
import json
import numpy as np
from typing import Dict, List, Optional, Any
import requests
import os
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RetrievedContent:
    """Retrieved content from RAG system"""
    text: str
    hook: Optional[str]
    caption: str
    hashtags: List[str]
    views: int
    likes: int
    posted_at: str
    creator_handle: str
    reel_id: int
    reel_url: str
    relevance_score: float

class RAGRetriever:
    """
    RAG retrieval system for Instagram mentor content
    """
    
    def __init__(self, db_path: str = "data/instagram_rag.db"):
        """Initialize retriever"""
        self.db_path = db_path
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
    
    def retrieve(self, query: str, creators: Optional[List[str]] = None, 
                limit: int = 8, min_similarity: float = 0.7) -> List[RetrievedContent]:
        """
        Retrieve relevant content using hybrid search
        
        Args:
            query: Search query
            creators: Optional list of creator handles to filter by
            limit: Maximum number of results
            min_similarity: Minimum similarity threshold
        
        Returns:
            List of retrieved content items
        """
        try:
            # Create query embedding
            query_embedding = self._create_query_embedding(query)
            if not query_embedding:
                logger.warning("Failed to create query embedding, using keyword search only")
                return self._keyword_search(query, creators, limit)
            
            # Perform hybrid retrieval
            return self._hybrid_search(query, query_embedding, creators, limit, min_similarity)
            
        except Exception as e:
            logger.error(f"Error in retrieval: {e}")
            return []
    
    def _create_query_embedding(self, query: str) -> Optional[List[float]]:
        """Create embedding for query using OpenAI"""
        if not self.openai_api_key:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "text-embedding-3-large",
                "input": query
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                json=data,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            return result["data"][0]["embedding"]
            
        except Exception as e:
            logger.warning(f"Error creating query embedding: {e}")
            return None
    
    def _hybrid_search(self, query: str, query_embedding: List[float], 
                      creators: Optional[List[str]], limit: int, 
                      min_similarity: float) -> List[RetrievedContent]:
        """
        Hybrid search combining vector similarity and keyword matching
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Build query with filters
                where_conditions = ["r.is_trending = TRUE"]
                params = []
                
                if creators:
                    placeholders = ",".join("?" * len(creators))
                    where_conditions.append(f"c.handle IN ({placeholders})")
                    params.extend(creators)
                
                where_clause = " AND ".join(where_conditions)
                
                # Get all relevant chunks with metadata
                query_sql = f"""
                    SELECT 
                        rc.chunk_text,
                        rc.embedding,
                        r.hook,
                        r.caption,
                        r.hashtags,
                        r.view_count,
                        r.like_count,
                        r.posted_at,
                        c.handle,
                        r.id,
                        r.reel_url
                    FROM rag_chunks rc
                    JOIN reels r ON rc.reel_id = r.id
                    JOIN creators c ON r.creator_id = c.id
                    WHERE {where_clause}
                """
                
                cursor = conn.execute(query_sql, params)
                results = cursor.fetchall()
                
                # Calculate similarities and score
                scored_results = []
                query_words = set(query.lower().split())
                
                for row in results:
                    (chunk_text, embedding_blob, hook, caption, hashtags_json, 
                     view_count, like_count, posted_at, creator_handle, reel_id, reel_url) = row
                    
                    # Vector similarity
                    try:
                        stored_embedding = json.loads(embedding_blob.decode())
                        vector_similarity = self._cosine_similarity(query_embedding, stored_embedding)
                    except:
                        vector_similarity = 0.0
                    
                    # Keyword similarity
                    content_words = set((chunk_text + " " + (caption or "")).lower().split())
                    keyword_overlap = len(query_words.intersection(content_words)) / len(query_words)
                    
                    # Combined score (70% vector, 30% keyword)
                    combined_score = 0.7 * vector_similarity + 0.3 * keyword_overlap
                    
                    if combined_score >= min_similarity:
                        hashtags = json.loads(hashtags_json) if hashtags_json else []
                        
                        scored_results.append(RetrievedContent(
                            text=chunk_text,
                            hook=hook,
                            caption=caption or "",
                            hashtags=hashtags,
                            views=view_count or 0,
                            likes=like_count or 0,
                            posted_at=posted_at or "",
                            creator_handle=creator_handle,
                            reel_id=reel_id,
                            reel_url=reel_url,
                            relevance_score=combined_score
                        ))
                
                # Sort by relevance and return top results
                scored_results.sort(key=lambda x: x.relevance_score, reverse=True)
                return scored_results[:limit]
                
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def _keyword_search(self, query: str, creators: Optional[List[str]], 
                       limit: int) -> List[RetrievedContent]:
        """
        Fallback keyword-based search
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Build query with filters
                where_conditions = ["r.is_trending = TRUE"]
                params = []
                
                if creators:
                    placeholders = ",".join("?" * len(creators))
                    where_conditions.append(f"c.handle IN ({placeholders})")
                    params.extend(creators)
                
                # Add keyword search
                query_words = query.lower().split()
                keyword_conditions = []
                for word in query_words:
                    keyword_conditions.append("(LOWER(rc.chunk_text) LIKE ? OR LOWER(r.caption) LIKE ?)")
                    params.extend([f"%{word}%", f"%{word}%"])
                
                if keyword_conditions:
                    where_conditions.append(f"({' OR '.join(keyword_conditions)})")
                
                where_clause = " AND ".join(where_conditions)
                
                query_sql = f"""
                    SELECT 
                        rc.chunk_text,
                        r.hook,
                        r.caption,
                        r.hashtags,
                        r.view_count,
                        r.like_count,
                        r.posted_at,
                        c.handle,
                        r.id,
                        r.reel_url
                    FROM rag_chunks rc
                    JOIN reels r ON rc.reel_id = r.id
                    JOIN creators c ON r.creator_id = c.id
                    WHERE {where_clause}
                    ORDER BY r.view_count DESC, r.like_count DESC
                    LIMIT ?
                """
                
                params.append(limit)
                cursor = conn.execute(query_sql, params)
                results = cursor.fetchall()
                
                retrieved_content = []
                for row in results:
                    (chunk_text, hook, caption, hashtags_json, view_count, 
                     like_count, posted_at, creator_handle, reel_id, reel_url) = row
                    
                    hashtags = json.loads(hashtags_json) if hashtags_json else []
                    
                    retrieved_content.append(RetrievedContent(
                        text=chunk_text,
                        hook=hook,
                        caption=caption or "",
                        hashtags=hashtags,
                        views=view_count or 0,
                        likes=like_count or 0,
                        posted_at=posted_at or "",
                        creator_handle=creator_handle,
                        reel_id=reel_id,
                        reel_url=reel_url,
                        relevance_score=0.5  # Default for keyword search
                    ))
                
                return retrieved_content
                
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return dot_product / (norm_a * norm_b)
            
        except Exception as e:
            logger.warning(f"Error calculating cosine similarity: {e}")
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                stats = {}
                
                # Total reels
                cursor = conn.execute("SELECT COUNT(*) FROM reels")
                stats["total_reels"] = cursor.fetchone()[0]
                
                # Trending reels
                cursor = conn.execute("SELECT COUNT(*) FROM reels WHERE is_trending = TRUE")
                stats["trending_reels"] = cursor.fetchone()[0]
                
                # Total chunks
                cursor = conn.execute("SELECT COUNT(*) FROM rag_chunks")
                stats["total_chunks"] = cursor.fetchone()[0]
                
                # Reels by creator
                cursor = conn.execute("""
                    SELECT c.handle, COUNT(r.id) as reel_count
                    FROM creators c
                    LEFT JOIN reels r ON c.id = r.creator_id
                    GROUP BY c.handle
                """)
                stats["reels_by_creator"] = dict(cursor.fetchall())
                
                # Latest reel date
                cursor = conn.execute("SELECT MAX(posted_at) FROM reels")
                latest_date = cursor.fetchone()[0]
                stats["latest_reel_date"] = latest_date
                
                return stats
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}

def main():
    """Test the retrieval system"""
    retriever = RAGRetriever()
    
    # Test queries
    test_queries = [
        "offer creation",
        "audience growth", 
        "scaling business",
        "content strategy"
    ]
    
    print("🔍 Testing RAG Retrieval System")
    print("=" * 50)
    
    # Get stats first
    stats = retriever.get_stats()
    print(f"📊 System Stats:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Test retrieval
    for query in test_queries:
        print(f"🎯 Query: '{query}'")
        results = retriever.retrieve(query, limit=3)
        
        if results:
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. @{result.creator_handle} (score: {result.relevance_score:.3f})")
                print(f"      Hook: {result.hook[:60]}..." if result.hook else "      No hook")
                print(f"      Views: {result.views:,}, Likes: {result.likes:,}")
        else:
            print("   No results found")
        print()

if __name__ == "__main__":
    main()