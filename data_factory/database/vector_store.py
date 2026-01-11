"""
database/vector_store.py - ChromaDB Vector Storage Module

This module handles storing video transcript chunks as vectors in ChromaDB.
It uses sentence-transformers for embedding generation.

The database is stored at ../video_db so it can be accessed by:
1. This data factory (for writing)
2. The API server (for reading/searching)

Based on Paper F: Content-Based Filtering with Vector Search
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

# Database path - root level video_db folder (shared across project)
# Goes up from data_factory/database/ -> data_factory -> project root
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "video_db")
COLLECTION_NAME = "learning_videos"  # Generic name for all topics (not just DSA)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ============================================================================
# GLOBAL INITIALIZATION (Load once, reuse)
# ============================================================================

print(f"[Vector Store] Initializing ChromaDB at: {os.path.abspath(DATABASE_PATH)}")

# Initialize ChromaDB Persistent Client
chroma_client = chromadb.PersistentClient(path=DATABASE_PATH)

# Get or create the collection
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"description": "DSA video transcripts with embeddings"}
)

print(f"[Vector Store] Collection '{COLLECTION_NAME}' ready with {collection.count()} documents")

# Load embedding model once
print(f"[Vector Store] Loading embedding model: {EMBEDDING_MODEL}")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)
print(f"[Vector Store] Model loaded successfully!")


# ============================================================================
# STORAGE FUNCTIONS
# ============================================================================

def generate_chunk_id(video_id: str, chunk_index: int) -> str:
    """
    Generate a unique ID for a chunk.
    
    Format: video_id_chunk_index (e.g., "dQw4w9WgXcQ_0")
    
    Args:
        video_id: YouTube video ID
        chunk_index: Index of the chunk within the video
        
    Returns:
        Unique chunk ID string
    """
    return f"{video_id}_{chunk_index}"


def store_video_data(
    video_meta: Dict,
    chunks: List[Dict],
    difficulty: str,
    content_type: str,
    topic_tags: List[str],
    source: str = "Manual_Playlist",
    quality_tier: str = "Standard",
    granularity: str = "Specific"  # NEW: Specific vs Broad
) -> int:
    """
    Store video chunks in ChromaDB with embeddings.
    """
    if not chunks:
        print(f"⚠️ No chunks to store for {video_meta.get('title', 'Unknown')}")
        return 0
    
    video_id = video_meta.get("video_id", "unknown")
    video_title = video_meta.get("title", "Untitled")
    
    ids = []
    embeddings = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        # Generate unique ID
        chunk_id = generate_chunk_id(video_id, i)
        
        # Get text content
        text_content = chunk.get("text_content", "")
        
        if not text_content:
            continue
        
        # Generate embedding
        embedding = embedding_model.encode(text_content).tolist()
        
        # Build YouTube link with timestamp
        youtube_link = chunk.get("youtube_link", video_meta.get("youtube_link", ""))
        if not youtube_link and video_meta.get("youtube_link"):
            start_time = int(chunk.get("start_time", 0))
            youtube_link = f"{video_meta['youtube_link']}?t={start_time}"
        
        # Prepare metadata (Extended for Advanced Recommendations)
        metadata = {
            "video_id": video_id,
            "title": video_title,
            "youtube_link": youtube_link,
            "timestamp": chunk.get("timestamp_display", "0:00"),
            "start_seconds": chunk.get("start_time", 0),
            "end_seconds": chunk.get("end_time", 0),
            
            # --- METADATA FIELDS FOR FILTERING ---
            "difficulty": difficulty,
            "style": content_type,  # Mapped from 'style' tag
            "granularity": granularity,  # NEW: Specific vs Broad
            "quality_tier": quality_tier,
            "freshness": chunk.get("freshness_score", 0.5),
            # --------------------------------------
            
            "source": source,
            "channel": video_meta.get("channel", "Unknown"),
            "tags": ",".join(topic_tags),
            "chunk_index": i,
            "total_chunks": len(chunks),
            "description": text_content[:200] + "..." if len(text_content) > 200 else text_content
        }
        
        ids.append(chunk_id)
        embeddings.append(embedding)
        documents.append(text_content)
        metadatas.append(metadata)
    
    # Upsert to ChromaDB (update if exists, insert if new)
    if ids:
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"✅ Stored {len(ids)} chunks for: {video_title}")
    
    return len(ids)


def search_videos(
    query: str,
    n_results: int = 5,
    filter_difficulty: Optional[str] = None
) -> List[Dict]:
    """
    Search for relevant video chunks using semantic similarity.
    
    Args:
        query: Search query text
        n_results: Number of results to return
        filter_difficulty: Optional filter by difficulty level
        
    Returns:
        List of matching chunks with metadata
    """
    # Generate query embedding
    query_embedding = embedding_model.encode(query).tolist()
    
    # Build filter if specified
    where_filter = None
    if filter_difficulty:
        where_filter = {"difficulty": filter_difficulty}
    
    # Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    formatted_results = []
    if results and results.get("ids") and results["ids"][0]:
        for i in range(len(results["ids"][0])):
            result = {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i] if results.get("documents") else "",
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "distance": results["distances"][0][i] if results.get("distances") else 0
            }
            formatted_results.append(result)
    
    return formatted_results


def get_collection_stats() -> Dict:
    """
    Get statistics about the current collection.
    
    Returns:
        Dictionary with collection statistics
    """
    return {
        "collection_name": COLLECTION_NAME,
        "total_documents": collection.count(),
        "database_path": os.path.abspath(DATABASE_PATH)
    }


def clear_collection():
    """
    Clear all documents from the collection.
    Use with caution!
    """
    # Get all IDs
    all_ids = collection.get()["ids"]
    
    if all_ids:
        collection.delete(ids=all_ids)
        print(f"🗑️ Deleted {len(all_ids)} documents from collection")
    else:
        print("ℹ️ Collection is already empty")


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Vector Store - Test")
    print("=" * 60)
    
    stats = get_collection_stats()
    print(f"\nCollection: {stats['collection_name']}")
    print(f"Documents: {stats['total_documents']}")
    print(f"Path: {stats['database_path']}")
    
    # Test search
    if stats['total_documents'] > 0:
        print("\nTest search for 'binary search tree':")
        results = search_videos("binary search tree", n_results=3)
        for r in results:
            print(f"  - {r['metadata'].get('title', 'N/A')} ({r['distance']:.4f})")
