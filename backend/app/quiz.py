# backend/app/quiz.py
import json
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from .database import is_db_connected, get_all_quiz_topics_from_db, get_quiz_by_topic_from_db

router = APIRouter()

# --- Fallback: Load Quiz Data from JSON ---
def load_quiz_data_from_json():
    try:
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, '..', 'quizzes.json')
        with open(abs_file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- Pydantic Models ---
class Answer(BaseModel):
    question_index: int
    option_index: int

class QuizSubmission(BaseModel):
    topic: str
    answers: List[Answer]

# --- API Endpoints ---
@router.get("/topics")
async def get_quiz_topics():
    if is_db_connected():
        print("DB connected. Fetching topics from MongoDB.")
        topics = await get_all_quiz_topics_from_db()
    else:
        print("DB not connected. Fetching topics from JSON fallback.")
        quizzes = load_quiz_data_from_json()
        topics = [quiz["topic"] for quiz in quizzes]

    if not topics:
        raise HTTPException(status_code=404, detail="No quiz topics found.")
    return {"topics": topics}

@router.get("/{topic}")
async def get_quiz_by_topic(topic: str):
    quiz = None
    if is_db_connected():
        print(f"DB connected. Fetching quiz '{topic}' from MongoDB.")
        quiz = await get_quiz_by_topic_from_db(topic)
    else:
        print(f"DB not connected. Fetching quiz '{topic}' from JSON fallback.")
        quizzes = load_quiz_data_from_json()
        quiz = next((q for q in quizzes if q["topic"].lower() == topic.lower()), None)
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz topic not found.")
    
    questions_for_user = []
    for q in quiz["questions"]:
        options = [{"text": opt["text"]} for opt in q["options"]]
        questions_for_user.append({"question_text": q["question_text"], "options": options})
        
    return {"topic": quiz["topic"], "questions": questions_for_user}

@router.post("/submit")
async def submit_quiz(submission: QuizSubmission):
    # This endpoint primarily calculates results, so DB/JSON fetching is similar
    # We will enhance this later to save results to the DB
    topic = submission.topic
    quiz = None
    if is_db_connected():
        quiz = await get_quiz_by_topic_from_db(topic)
    else:
        quizzes = load_quiz_data_from_json()
        quiz = next((q for q in quizzes if q["topic"].lower() == topic.lower()), None)

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz topic not found.")

    score = 0
    total_questions = len(quiz["questions"])
    weak_areas = []

    for answer in submission.answers:
        q_index = answer.question_index
        opt_index = answer.option_index
        correct_option = quiz["questions"][q_index]["options"][opt_index]
        if correct_option.get("is_correct"): # Use .get() for safety
            score += 1
        else:
            weak_areas.append(quiz["questions"][q_index]["question_text"])

    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    
    # Here we would save the result to the progress DB
    # For now, we just return it
    return {
        "topic": topic,
        "score": score,
        "total_questions": total_questions,
        "percentage": round(percentage, 2),
        "weak_areas": weak_areas
    }
