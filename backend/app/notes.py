# backend/app/notes.py
"""
Notes API Router
Generates comprehensive notes from COMPLETE video transcripts.
Features: Caching in MongoDB to avoid re-processing same videos.

NOTE: AI-generated notes are cached GLOBALLY by video_id (shared across all users).
This saves API calls - if notes exist for a video, any user can retrieve them.
User's personal handwritten notes are stored separately in user_notes.py.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .search_engine import get_video_transcript
from .note_generation_service import generate_comprehensive_notes
from .database import notes_collection, is_db_connected
from .auth import get_current_user

print("[Notes Module] ✅ Notes router loaded (Global Caching)")

router = APIRouter()

class NoteRequest(BaseModel):
    topic: str
    video_title: str
    video_id: Optional[str] = None
    force_regenerate: Optional[bool] = False

class NoteResponse(BaseModel):
    markdown: str
    rag_enabled: bool
    cached: bool
    metadata: Optional[dict] = None


# ============================================================================
# CACHING HELPERS - GLOBAL (by video_id only, shared across users)
# ============================================================================

def get_cached_notes(video_id: str) -> Optional[dict]:
    """
    Retrieve cached AI-generated notes from MongoDB.
    Notes are cached globally by video_id (same notes for all users).
    """
    if not is_db_connected():
        return None
    
    try:
        cached = notes_collection.find_one({"video_id": video_id})
        if cached:
            print(f"  - 📦 Cache HIT for video: {video_id}")
            return cached
        print(f"  - 🔍 Cache MISS for video: {video_id}")
        return None
    except Exception as e:
        print(f"  - ⚠️ Cache lookup error: {e}")
        return None


def save_notes_to_cache(video_id: str, topic: str, video_title: str, markdown: str, metadata: dict):
    """
    Save AI-generated notes to MongoDB (global cache by video_id).
    """
    if not is_db_connected():
        print(f"  - ⚠️ DB not connected, skipping cache save")
        return
    
    try:
        notes_collection.update_one(
            {"video_id": video_id},
            {
                "$set": {
                    "video_id": video_id,
                    "topic": topic,
                    "video_title": video_title,
                    "markdown": markdown,
                    "metadata": metadata,
                    "generated_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        print(f"  - 💾 Notes cached globally for video: {video_id}")
    except Exception as e:
        print(f"  - ⚠️ Cache save error: {e}")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/history")
async def get_notes_history(current_user: dict = Depends(get_current_user)):
    """
    Get list of all AI-generated notes (global).
    Returns unique notes per video_id (no duplicates).
    """
    print(f"\n[Notes API] 📚 GET /notes/history")
    
    if not is_db_connected():
        return {"notes": [], "message": "Database not connected"}
    
    try:
        # Get all cached notes, sorted by most recent
        cursor = notes_collection.find({}).sort("generated_at", -1).limit(100)
        
        # Deduplicate by video_id (keep first/most recent occurrence)
        seen_video_ids = set()
        notes_list = []
        
        for doc in cursor:
            vid = doc.get("video_id", "")
            if vid and vid not in seen_video_ids:
                seen_video_ids.add(vid)
                notes_list.append({
                    "video_id": vid,
                    "video_title": doc.get("video_title", "Untitled"),
                    "topic": doc.get("topic", ""),
                    "generated_at": str(doc.get("generated_at", "")),
                    "preview": doc.get("markdown", "")[:150] + "..." if doc.get("markdown") else ""
                })
        
        print(f"  - Found {len(notes_list)} unique notes")
        return {"notes": notes_list}
        
    except Exception as e:
        print(f"  - ❌ Error: {e}")
        return {"notes": [], "error": str(e)}


@router.get("/{video_id}")
async def get_note_by_video(video_id: str):
    """
    Get specific AI-generated note by video ID.
    No auth required - notes are public/global.
    """
    print(f"\n[Notes API] 📖 GET /notes/{video_id}")
    
    cached = get_cached_notes(video_id)
    if cached:
        return {
            "markdown": cached.get("markdown", ""),
            "video_title": cached.get("video_title", ""),
            "topic": cached.get("topic", ""),
            "generated_at": str(cached.get("generated_at", "")),
            "found": True
        }
    
    return {"found": False, "message": "Note not found"}


@router.post("/generate")
async def generate_notes(request: NoteRequest, current_user: dict = Depends(get_current_user)):
    """
    Generates study notes for a specific video.
    
    1. Check global cache first - if notes exist, return them
    2. If not cached (or force_regenerate), generate new notes
    3. Save to global cache before returning
    """
    print(f"\n[Notes API] 📝 POST /notes/generate")
    print(f"  - Topic: {request.topic}")
    print(f"  - Video ID: {request.video_id or 'None'}")
    print(f"  - Force Regenerate: {request.force_regenerate}")
    
    # If no video_id, we can't cache - use topic-only fallback
    if not request.video_id:
        print(f"  - ⚠️ No video_id provided, using topic-only mode")
        from .ai_coach import generate_study_notes
        notes = generate_study_notes(
            topic=request.topic,
            video_title=request.video_title,
            transcript=None
        )
        return {
            "markdown": notes,
            "rag_enabled": False,
            "cached": False,
            "metadata": {"mode": "topic_only"}
        }
    
    # ========================================
    # STEP 1: Check Global Cache (unless force_regenerate)
    # ========================================
    if not request.force_regenerate:
        cached = get_cached_notes(request.video_id)
        if cached:
            return {
                "markdown": cached.get("markdown", ""),
                "rag_enabled": True,
                "cached": True,
                "metadata": {
                    **cached.get("metadata", {}),
                    "generated_at": str(cached.get("generated_at", "")),
                    "source": "cache"
                }
            }
    
    # ========================================
    # STEP 2: Get Transcript from ChromaDB
    # ========================================
    transcript = get_video_transcript(request.video_id)
    
    if not transcript:
        print(f"  - ⚠️ No transcript found for video: {request.video_id}")
        from .ai_coach import generate_study_notes
        notes = generate_study_notes(
            topic=request.topic,
            video_title=request.video_title,
            transcript=None
        )
        return {
            "markdown": notes,
            "rag_enabled": False,
            "cached": False,
            "metadata": {"mode": "topic_only", "reason": "no_transcript_found"}
        }
    
    print(f"  - ✅ Full Transcript: {len(transcript)} chars")
    
    # ========================================
    # STEP 3: Generate Notes (Chunking & Stitching)
    # ========================================
    try:
        notes, metadata = generate_comprehensive_notes(
            topic=request.topic,
            video_title=request.video_title,
            transcript=transcript
        )
        
        # ========================================
        # STEP 4: Save to Global Cache
        # ========================================
        save_notes_to_cache(
            video_id=request.video_id,
            topic=request.topic,
            video_title=request.video_title,
            markdown=notes,
            metadata=metadata
        )
        
        return {
            "markdown": notes,
            "rag_enabled": True,
            "cached": False,
            "metadata": {**metadata, "source": "generated"}
        }
        
    except Exception as e:
        print(f"  - ❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
