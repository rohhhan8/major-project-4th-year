# backend/app/transcript_pipeline.py
"""
Real-Time Transcript Pipeline

This module handles on-demand transcript processing for user-pasted YouTube URLs.
When a user pastes a YouTube link, this pipeline:
1. Fetches the transcript from YouTube
2. Chunks it into meaningful segments
3. Generates embeddings using sentence-transformers
4. Stores in ChromaDB for future use (caching)

This enables the platform to handle ANY YouTube video, not just pre-indexed ones.
"""

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import chromadb
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

print("[Transcript Pipeline] Initializing real-time transcript processor...")

router = APIRouter()

# Initialize YouTubeTranscriptApi instance (new API requires this)
yt_transcript_api = YouTubeTranscriptApi()

# Load embedding model
try:
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("[Transcript Pipeline] Embedding model loaded")
except Exception as e:
    print(f"[Transcript Pipeline] Warning: Could not load model: {e}")
    embedding_model = None

# Connect to ChromaDB
VIDEO_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "video_db")
chroma_client = chromadb.PersistentClient(path=VIDEO_DB_PATH)

try:
    video_collection = chroma_client.get_or_create_collection(name="learning_videos")
    print(f"[Transcript Pipeline] Connected to ChromaDB with {video_collection.count()} documents")
except Exception as e:
    print(f"[Transcript Pipeline] Error connecting to ChromaDB: {e}")
    video_collection = None

# YouTube API for video title
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube_client = None
try:
    if YOUTUBE_API_KEY:
        youtube_client = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
except Exception as e:
    print(f"[Transcript Pipeline] YouTube API client not available: {e}")


class ProcessVideoRequest(BaseModel):
    video_id: str


class ProcessVideoResponse(BaseModel):
    video_id: str
    title: str
    transcript_available: bool
    chunks_stored: int
    message: str


def get_video_title(video_id: str) -> str:
    """Fetch video title from YouTube API."""
    if not youtube_client:
        return f"Video {video_id}"
    
    try:
        response = youtube_client.videos().list(
            part="snippet",
            id=video_id
        ).execute()
        
        if response.get("items"):
            return response["items"][0]["snippet"]["title"]
    except Exception as e:
        print(f"[Transcript Pipeline] Could not fetch title: {e}")
    
    return f"Video {video_id}"


def fetch_youtube_transcript(video_id: str) -> Optional[str]:
    """
    Fetch transcript from YouTube using youtube-transcript-api.
    Returns full transcript text or None if unavailable.
    """
    try:
        # New API (v1.2+): Create instance and call fetch()
        transcript = yt_transcript_api.fetch(video_id)
        
        # Combine all transcript segments - transcript is iterable of FetchedTranscriptSnippet
        full_transcript = " ".join([snippet.text for snippet in transcript])
        
        print(f"[Transcript Pipeline] ✅ Fetched transcript: {len(full_transcript)} chars")
        return full_transcript
        
    except Exception as e:
        error_msg = str(e).lower()
        if "disabled" in error_msg:
            print(f"[Transcript Pipeline] ❌ Transcripts disabled for video: {video_id}")
        elif "not found" in error_msg or "no transcript" in error_msg:
            print(f"[Transcript Pipeline] ❌ No transcript found for video: {video_id}")
        else:
            print(f"[Transcript Pipeline] ❌ Error fetching transcript: {e}")
        return None


def chunk_transcript(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Split transcript into overlapping chunks for better semantic search.
    """
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)
        i += chunk_size - overlap
    
    return chunks


def check_video_exists(video_id: str) -> bool:
    """Check if video already exists in ChromaDB."""
    if not video_collection:
        return False
    
    try:
        results = video_collection.get(
            where={"video_id": video_id},
            limit=1
        )
        return len(results.get("ids", [])) > 0
    except Exception:
        return False


@router.post("/process", response_model=ProcessVideoResponse)
async def process_video(request: ProcessVideoRequest):
    """
    Process a YouTube video: fetch transcript, chunk, embed, and store in ChromaDB.
    This endpoint enables any pasted YouTube URL to work with the platform.
    """
    video_id = request.video_id
    
    print(f"\n[Transcript Pipeline] 🎬 Processing video: {video_id}")
    
    # Fetch video title first
    title = get_video_title(video_id)
    print(f"[Transcript Pipeline] 📝 Title: {title}")
    
    # Check if already processed
    if check_video_exists(video_id):
        print(f"[Transcript Pipeline] ✅ Video already in database")
        return ProcessVideoResponse(
            video_id=video_id,
            title=title,
            transcript_available=True,
            chunks_stored=0,
            message="Video already processed - transcript available"
        )
    
    # Fetch transcript from YouTube
    transcript = fetch_youtube_transcript(video_id)
    
    if not transcript:
        return ProcessVideoResponse(
            video_id=video_id,
            title=title,
            transcript_available=False,
            chunks_stored=0,
            message="No transcript available for this video"
        )
    
    # Check embedding model
    if not embedding_model or not video_collection:
        raise HTTPException(status_code=500, detail="ML models not initialized")
    
    # Chunk the transcript
    chunks = chunk_transcript(transcript)
    print(f"[Transcript Pipeline] 📦 Created {len(chunks)} chunks")
    
    # Generate embeddings and store in ChromaDB
    try:
        for i, chunk in enumerate(chunks):
            chunk_id = f"{video_id}_chunk_{i}"
            
            # Generate embedding
            embedding = embedding_model.encode(chunk).tolist()
            
            # Store in ChromaDB
            video_collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "video_id": video_id,
                    "title": title,
                    "chunk_index": i,
                    "source": "user_upload",
                    "difficulty": "general"
                }]
            )
        
        print(f"[Transcript Pipeline] ✅ Stored {len(chunks)} chunks in ChromaDB")
        
        return ProcessVideoResponse(
            video_id=video_id,
            title=title,
            transcript_available=True,
            chunks_stored=len(chunks),
            message=f"Successfully processed and stored {len(chunks)} transcript chunks"
        )
        
    except Exception as e:
        print(f"[Transcript Pipeline] ❌ Error storing chunks: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


@router.get("/check/{video_id}")
async def check_video_status(video_id: str):
    """
    Quick check if a video's transcript is already in the database.
    """
    exists = check_video_exists(video_id)
    title = get_video_title(video_id) if exists else None
    return {
        "video_id": video_id,
        "transcript_available": exists,
        "title": title
    }
