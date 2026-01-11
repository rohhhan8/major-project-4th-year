"""
search_engine.py - Online Recommendation Engine (Logic Layer)

This module implements the Content-Based Filtering logic for video recommendations.
Based on Paper F: Hybrid Recommendation System for Adaptive E-Learning.

The engine performs semantic search over pre-indexed video transcripts stored in ChromaDB.
It uses sentence embeddings to find the most relevant video segment for a user's weak topic.

Architecture Notes:
- Offline Factory (separate team): Populates ChromaDB with video transcript vectors
- Online Engine (this module): Queries the database in read-only mode

Author: ML Engineering Team
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import Optional, Dict, Any

# ============================================================================
# MODEL INITIALIZATION (Global Scope)
# ============================================================================
# Load the sentence transformer model once at module import time.
# This avoids expensive model reloading on every API request.
# Model: all-MiniLM-L6-v2 - A lightweight but effective model for semantic search
# Dimensions: 384, Max Sequence Length: 256 tokens

print("[Search Engine] Loading sentence transformer model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("[Search Engine] Model loaded successfully!")

# ============================================================================
# DATABASE INITIALIZATION (Read-Only Mode)
# ============================================================================
# Connect to the persistent ChromaDB instance.
# IMPORTANT: This is strictly READ-ONLY. The Offline Factory team handles data ingestion.
# Path is relative to backend/app/, goes up to project root

import os
VIDEO_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "video_db")

print(f"[Search Engine] Connecting to ChromaDB at: {os.path.abspath(VIDEO_DB_PATH)}")
chroma_client = chromadb.PersistentClient(path=VIDEO_DB_PATH)

# Get the pre-existing collection containing video embeddings
# The collection was created and populated by the Offline Factory team
try:
    video_collection = chroma_client.get_collection(name="learning_videos")
    print(f"[Search Engine] Connected to 'learning_videos' collection with {video_collection.count()} documents")
except Exception as e:
    print(f"[Search Engine] WARNING: Could not connect to collection: {e}")
    video_collection = None


def get_video_transcript(video_id: str) -> Optional[str]:
    """
    Retrieves stored transcript chunks for a specific video from ChromaDB.
    Used for RAG-based notes generation.
    
    Args:
        video_id: The YouTube video ID (e.g., 'dQw4w9WgXcQ')
    
    Returns:
        Concatenated transcript text or None if not found.
    """
    if video_collection is None:
        print("[Search Engine] Error: Video collection not available for transcript retrieval")
        return None
    
    try:
        # Query by video_id metadata filter
        results = video_collection.get(
            where={"video_id": video_id},
            include=["documents", "metadatas"]
        )
        
        if not results or not results.get("documents"):
            print(f"[Search Engine] No transcript found for video_id: {video_id}")
            return None
        
        # Concatenate all transcript chunks for this video
        transcript_chunks = results["documents"]
        full_transcript = "\n\n".join(transcript_chunks)
        
        print(f"[Search Engine] Retrieved {len(transcript_chunks)} chunks for video: {video_id}")
        return full_transcript
        
    except Exception as e:
        print(f"[Search Engine] Error retrieving transcript: {e}")
        return None


def find_best_video(
    query_text: str,
    difficulty: Optional[str] = None,
    style: Optional[str] = None,
    granularity: Optional[str] = None  # NEW: Specific vs Broad filter
) -> Optional[Dict[str, Any]]:
    """
    Find the most relevant video segment for a given topic/query with optional filters.
    """
    
    # Validate collection availability
    if video_collection is None:
        print("[Search Engine] Error: Video collection not available")
        return None
    
    # Check if collection has any documents
    if video_collection.count() == 0:
        print("[Search Engine] Warning: Collection is empty")
        return None
    
    try:
        # Step 1: Generate embedding for the query text
        query_embedding = embedding_model.encode(query_text).tolist()
        
        # Step 2: Build Filter Query
        where_filter = {}
        if difficulty:
            where_filter["difficulty"] = difficulty
        if style:
            where_filter["style"] = style
        if granularity:
            where_filter["granularity"] = granularity
            
        # Handle empty filter (ChromaDB expects None if empty)
        final_where = where_filter if where_filter else None
        
        # Step 3: Perform semantic search
        results = video_collection.query(
            query_embeddings=[query_embedding],
            n_results=9, # Return Top 9 matches for grid layout
            where=final_where,
            include=["documents", "metadatas", "distances"]
        )
        
        # Step 4: Validate results
        if not results or not results.get('ids') or len(results['ids'][0]) == 0:
            print(f"[Search Engine] No results found for query: '{query_text}' with filters {final_where}")
            return []
        
        # Step 5: Extract and format matches
        recommendations = []
        
        for i in range(len(results['ids'][0])):
            video_id = results['ids'][0][i]
            metadata = results['metadatas'][0][i]
            document = results['documents'][0][i]
            distance = results['distances'][0][i] if results.get('distances') else 1.0
            
            similarity_score = 1 - distance
            print(f"[Search Engine] Match {i+1}: {video_id} (Score: {similarity_score:.4f})")
            
            recommendations.append({
                "title": metadata.get("title", "Recommended Video"),
                "video_id": video_id,
                "description": metadata.get("description", document[:100] + "..."),
                "youtube_link": metadata.get("youtube_link", metadata.get("url", "")),
                "timestamp": metadata.get("timestamp", "0:00"),
                "source": metadata.get("source", "Unknown"),
                "difficulty": metadata.get("difficulty", "Unknown"),
                "style": metadata.get("style", "Unknown"),
                "score": round(similarity_score, 4)
            })
        
        return recommendations
        
    except Exception as e:
        print(f"[Search Engine] Error during search: {e}")
        return []

def find_best_video(
    query_text: str,
    difficulty: Optional[str] = None,
    style: Optional[str] = None,
    granularity: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Find the most relevant video segment with fallback logic.
    """
    # 1. Try with FULL FILTERS
    result = _execute_search(query_text, difficulty, style, granularity)
    if result:
        return result
    
    # 2. Log failure and try FALLBACK (Relaxed filters)
    print(f"[Search Engine] Strict search failed for '{query_text}'. Retrying without filters...")
    result = _execute_search(query_text, filter_difficulty=None, filter_style=None, filter_granularity=None)
    
    if result:
        # Add note to top result
        result[0]["note"] = "Showing best available match (exact filters not found)"
        return result
        
    return []

def _execute_search(query, filter_difficulty=None, filter_style=None, filter_granularity=None):
    """
    Internal helper to execute the actual ChromaDB query.
    Fetches many results to ensure we get unique videos after deduplication.
    """
    if video_collection is None: return []
    
    try:
        query_embedding = embedding_model.encode(query).tolist()
        
        where_filter = {}
        if filter_difficulty: where_filter["difficulty"] = filter_difficulty
        if filter_style: where_filter["style"] = filter_style
        if filter_granularity: where_filter["granularity"] = filter_granularity
        
        # Fetch many results to ensure enough unique videos after dedup
        results = video_collection.query(
            query_embeddings=[query_embedding],
            n_results=50,  # Fetch many chunks, will deduplicate
            where=where_filter if where_filter else None,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results['ids'] or len(results['ids'][0]) == 0:
            return []
            
        return _format_and_deduplicate_results(results)
    except Exception as e:
        print(f"[Search Engine] _execute_search error: {e}")
        return []

def _format_and_deduplicate_results(results):
    """
    Format ChromaDB results with:
    1. Proper relevance scoring (normalized 0-100%)
    2. Deduplication by video_id (keep best match per video)
    3. Sorted by relevance descending
    4. Include thumbnail URL
    """
    import math
    
    # First pass: collect all results
    all_results = []
    
    for i in range(len(results['ids'][0])):
        chunk_id = results['ids'][0][i]
        metadata = results['metadatas'][0][i]
        document = results['documents'][0][i]
        distance = results['distances'][0][i] if results.get('distances') else 1.0
        
        # Get actual video_id from metadata (not chunk_id)
        video_id = metadata.get("video_id", chunk_id.split("_chunk_")[0] if "_chunk_" in chunk_id else chunk_id)
        
        # Better relevance formula using exponential decay
        # L2 distance 0 -> 100%, distance 0.5 -> 77%, distance 1.0 -> 60%, distance 1.5 -> 47%
        # More generous scoring that reflects actual semantic similarity
        relevance_percent = 100 * math.exp(-distance * 0.5)
        
        all_results.append({
            "video_id": video_id,
            "title": metadata.get("title", "Recommended Video"),
            "description": document[:200] + "..." if len(document) > 200 else document,
            "difficulty": metadata.get("difficulty", "General"),
            "style": metadata.get("style", "General"),
            "timestamp": metadata.get("timestamp", ""),
            "youtube_link": metadata.get("youtube_link", f"https://www.youtube.com/watch?v={video_id}"),
            "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            "relevance_percent": round(relevance_percent, 1),
            "score": round(relevance_percent / 100, 4),
            "distance": round(distance, 4)
        })
    
    # Deduplicate: keep only the best match per video_id
    seen_videos = {}
    for result in all_results:
        vid = result["video_id"]
        if vid not in seen_videos or result["relevance_percent"] > seen_videos[vid]["relevance_percent"]:
            seen_videos[vid] = result
    
    # Convert to list and sort by relevance descending
    unique_results = list(seen_videos.values())
    unique_results.sort(key=lambda x: x['relevance_percent'], reverse=True)
    
    # Log results
    print(f"[Search Engine] Found {len(unique_results)} unique videos from {len(all_results)} chunks")
    for i, rec in enumerate(unique_results[:5]):
        print(f"  - #{i+1}: {rec['relevance_percent']:.1f}% - {rec['title'][:40]}...")
    
    return unique_results





def health_check() -> Dict[str, Any]:
    """
    Perform a health check on the search engine components.
    
    Returns:
        Dictionary with status of each component
    """
    return {
        "model_loaded": embedding_model is not None,
        "database_connected": chroma_client is not None,
        "collection_available": video_collection is not None,
        "document_count": video_collection.count() if video_collection else 0
    }
