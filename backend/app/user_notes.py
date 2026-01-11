# backend/app/user_notes.py
"""
User Notes API Router
Handles saving/loading user's personal handwritten notes from the video canvas.
Stored separately from AI-generated notes.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from .database import database, is_db_connected
from .auth import get_current_user

print("[User Notes Module] ✅ User Notes router loaded")

router = APIRouter()

# Collection for user's personal notes
user_notes_collection = database["user_canvas_notes"]


class UserNoteRequest(BaseModel):
    video_id: str
    content: str  # HTML content from rich editor
    video_title: Optional[str] = None


class UserNoteResponse(BaseModel):
    video_id: str
    content: str
    video_title: Optional[str]
    updated_at: str


@router.post("/save")
async def save_user_notes(request: UserNoteRequest, current_user: dict = Depends(get_current_user)):
    """
    Save user's personal canvas notes for a video.
    Upserts - creates if doesn't exist, updates if exists.
    """
    user_id = current_user["id"]
    
    print(f"[User Notes] 💾 Saving notes for user: {user_id}, video: {request.video_id}")
    
    if not is_db_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        user_notes_collection.update_one(
            {"user_id": user_id, "video_id": request.video_id},
            {
                "$set": {
                    "user_id": user_id,
                    "video_id": request.video_id,
                    "video_title": request.video_title,
                    "content": request.content,
                    "updated_at": datetime.utcnow()
                },
                "$setOnInsert": {
                    "created_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return {"status": "success", "message": "Notes saved"}
        
    except Exception as e:
        print(f"[User Notes] ❌ Error saving: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{video_id}")
async def get_user_notes(video_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get user's personal notes for a specific video.
    """
    user_id = current_user["id"]
    
    print(f"[User Notes] 📖 Getting notes for user: {user_id}, video: {video_id}")
    
    if not is_db_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        notes = user_notes_collection.find_one(
            {"user_id": user_id, "video_id": video_id}
        )
        
        if not notes:
            return {"video_id": video_id, "content": "", "video_title": None, "updated_at": None}
        
        return {
            "video_id": notes.get("video_id"),
            "content": notes.get("content", ""),
            "video_title": notes.get("video_title"),
            "updated_at": str(notes.get("updated_at", ""))
        }
        
    except Exception as e:
        print(f"[User Notes] ❌ Error getting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/all")
async def get_all_user_notes(current_user: dict = Depends(get_current_user)):
    """
    Get all notes for the current user (for sidebar display).
    """
    user_id = current_user["id"]
    
    if not is_db_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        notes = list(user_notes_collection.find(
            {"user_id": user_id},
            {"_id": 0, "video_id": 1, "video_title": 1, "updated_at": 1}
        ).sort("updated_at", -1).limit(10))
        
        # Convert datetime to string
        for note in notes:
            if note.get("updated_at"):
                note["updated_at"] = str(note["updated_at"])
        
        return {"notes": notes}
        
    except Exception as e:
        print(f"[User Notes] ❌ Error listing: {e}")
        raise HTTPException(status_code=500, detail=str(e))
