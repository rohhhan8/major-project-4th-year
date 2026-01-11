from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from .auth import get_current_user 
from .database import (
    is_db_connected, 
    get_or_create_user_progress, 
    update_video_progress,
    add_quiz_result
)

print("[Progress Module] ✅ Progress router loaded and ready")

router = APIRouter()

# --- Pydantic Models ---
class VideoProgressUpdate(BaseModel):
    video_id: str
    watch_percentage: float
    title: Optional[str] = "Unknown Title"
    category: Optional[str] = "General"
    instructor: Optional[str] = "Unknown"

class QuizResult(BaseModel):
    topic: str
    score: int
    total_questions: int
    percentage: float

# --- In-memory Fallback Database ---
# Used when MongoDB is not connected (e.g., during initial setup or dev without DB)
user_progress_fallback_db = {}

def get_or_create_user_fallback_progress(user_id: str):
    """
    Retrieves or creates user progress from the in-memory fallback database.
    """
    if user_id not in user_progress_fallback_db:
        # Generate a safe display name
        display_name = user_id.split('@')[0] if isinstance(user_id, str) and '@' in user_id else "Guest"
        
        user_progress_fallback_db[user_id] = {
            "user_id": user_id, 
            "user_name": display_name,
            "videos": {}, 
            "quizzes": [], 
            "streak": 0, 
            "longest_streak": 0
        }
    return user_progress_fallback_db[user_id]

# --- API Endpoints ---
@router.post("/video")
async def save_video_progress_endpoint(progress: VideoProgressUpdate, current_user: dict = Depends(get_current_user)):
    """
    Updates the user's progress for a specific video.
    Tracks watch percentage and last watched timestamp.
    """
    user_id = current_user["id"]
    
    progress_data = {
        "watch_percentage": progress.watch_percentage, 
        "title": progress.title,
        "category": progress.category, 
        "instructor": progress.instructor,
        "last_watched": "now"
    }
    
    if is_db_connected():
        await update_video_progress(user_id, progress.video_id, progress_data)
    else:
        user_data = get_or_create_user_fallback_progress(user_id)
        user_data["videos"][progress.video_id] = progress_data
        
    return {"status": "success", "message": "Progress updated."}

@router.post("/quiz")
async def save_quiz_result(result: QuizResult, current_user: dict = Depends(get_current_user)):
    """
    Saves the result of a completed quiz to the user's profile.
    """
    user_id = current_user["id"]
    
    if is_db_connected():
        await add_quiz_result(user_id, result.dict())
    else:
        user_data = get_or_create_user_fallback_progress(user_id)
        user_data["quizzes"].append(result.dict())
        
    return {"status": "success", "message": "Quiz result saved."}

@router.get("/dashboard")
async def get_dashboard_data(current_user: dict = Depends(get_current_user)):
    """
    Aggregates data for the user's dashboard.
    Calculates average scores, streaks, and learning progress.
    """
    user_id = current_user["id"]
    user_name = current_user.get("full_name", current_user.get("email", "Learner"))
    
    print(f"\n[Progress] 📊 DASHBOARD REQUEST")
    print(f"  - User: {user_name} ({user_id[:8]}...)")

    if is_db_connected():
        user_data = await get_or_create_user_progress(user_id)
    else:
        user_data = get_or_create_user_fallback_progress(user_id)
    
    # Calculate quiz statistics
    quiz_scores = [q["percentage"] for q in user_data["quizzes"]]
    avg_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
    highest_score = max(quiz_scores) if quiz_scores else 0
    lowest_score = min(quiz_scores) if quiz_scores else 0
    
    print(f"  - Quizzes Taken: {len(quiz_scores)}, Avg Score: {avg_score:.1f}%")
    
    # Format ongoing videos list
    ongoing_videos = [
        {
            "video_id": k,  # CRITICAL: Include video_id for navigation
            "title": v.get("title", f"Video {k}"), 
            "category": v.get("category", "General"), 
            "instructor": v.get("instructor", "Unknown"),
            "progress": v.get("watch_percentage", 0), 
            "thumbnail": f"https://i.ytimg.com/vi/{k}/hqdefault.jpg"
        }
        for k, v in user_data["videos"].items()
    ]
    
    # Calculate overall learning progress based on video completion
    video_progresses = [v.get("watch_percentage", 0) for v in user_data["videos"].values()]
    learning_progress = sum(video_progresses) / len(video_progresses) if video_progresses else 0

    return {
        "user_name": user_name,
        "avg_quiz_score": {
            "avg": round(avg_score, 2), 
            "highest": round(highest_score, 2), 
            "lowest": round(lowest_score, 2), 
            "change": -10 
        },
        "weekly_streak": {
            "current": user_data.get("streak", 0), 
            "longest": user_data.get("longest_streak", 0)
        },
        "learning_progress": round(learning_progress, 2),
        "ongoing_videos": ongoing_videos
    }
