# backend/app/progress.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from .auth import get_current_user 
from .database import (
    is_db_connected, 
    get_or_create_user_progress, 
    update_video_progress_in_db,
    update_quiz_result_in_db
)

router = APIRouter()

# --- Pydantic Models ---
class VideoProgressUpdate(BaseModel):
    video_id: str
    watch_percentage: float
    title: str
    category: str
    instructor: str

class QuizResult(BaseModel):
    topic: str
    score: int
    total_questions: int
    percentage: float

# --- In-memory Fallback Database ---
user_progress_fallback_db = {}

def get_or_create_user_fallback_progress(user_id: str):
    if user_id not in user_progress_fallback_db:
        user_progress_fallback_db[user_id] = {
            "user_id": user_id, "user_name": user_id.split('@')[0],
            "videos": {}, "quizzes": [], "streak": 0, "longest_streak": 0
        }
    return user_progress_fallback_db[user_id]

# --- API Endpoints ---
@router.post("/video")
async def update_video_progress(progress: VideoProgressUpdate, current_user: str = Depends(get_current_user)):
    progress_data = {
        "watch_percentage": progress.watch_percentage, "title": progress.title,
        "category": progress.category, "instructor": progress.instructor,
        "last_watched": "now"
    }
    if is_db_connected():
        await update_video_progress_in_db(current_user, progress.video_id, progress_data)
    else:
        user_data = get_or_create_user_fallback_progress(current_user)
        user_data["videos"][progress.video_id] = progress_data
    return {"status": "success", "message": "Progress updated."}

@router.post("/quiz")
async def save_quiz_result(result: QuizResult, current_user: str = Depends(get_current_user)):
    if is_db_connected():
        await update_quiz_result_in_db(current_user, result.dict())
    else:
        user_data = get_or_create_user_fallback_progress(current_user)
        user_data["quizzes"].append(result.dict())
    return {"status": "success", "message": "Quiz result saved."}

@router.get("/dashboard")
async def get_dashboard_data(current_user: str = Depends(get_current_user)):
    if is_db_connected():
        user_data = await get_or_create_user_progress(current_user)
    else:
        user_data = get_or_create_user_fallback_progress(current_user)
    
    quiz_scores = [q["percentage"] for q in user_data["quizzes"]]
    avg_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0
    highest_score = max(quiz_scores) if quiz_scores else 0
    lowest_score = min(quiz_scores) if quiz_scores else 0
    
    ongoing_videos = [
        {
            "title": v["title"], "category": v["category"], "instructor": v["instructor"],
            "progress": v["watch_percentage"], "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        }
        for video_id, v in user_data["videos"].items()
    ]
    
    video_progresses = [v["watch_percentage"] for v in user_data["videos"].values()]
    learning_progress = sum(video_progresses) / len(video_progresses) if video_progresses else 0

    return {
        "user_name": user_data["user_name"],
        "avg_quiz_score": {"avg": round(avg_score, 2), "highest": round(highest_score, 2), "lowest": round(lowest_score, 2), "change": -10},
        "weekly_streak": {"current": user_data["streak"], "longest": user_data["longest_streak"]},
        "learning_progress": round(learning_progress, 2),
        "ongoing_videos": ongoing_videos
    }
