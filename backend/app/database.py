# backend/app/database.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")
client = MongoClient(MONGO_DETAILS, serverSelectionTimeoutMS=2000) # Faster timeout
database = client.adaptive_learning

user_collection = database.get_collection("users")
quiz_collection = database.get_collection("quizzes")
progress_collection = database.get_collection("user_progress")

# --- DB Connection Check ---
def is_db_connected():
    try:
        client.admin.command('ismaster')
        return True
    except Exception:
        return False

# --- User Helpers ---
def user_helper(user) -> dict:
    return { "id": str(user["_id"]), "email": user["email"], "full_name": user.get("full_name"), "google_id": user["google_id"] }

async def get_user_by_email(email: str):
    user = user_collection.find_one({"email": email})
    if user: return user_helper(user)
    return None

async def create_user(user_data: dict):
    user = user_collection.insert_one(user_data)
    new_user = user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)

# --- Quiz Helpers ---
async def get_all_quiz_topics_from_db():
    cursor = quiz_collection.find({}, {"topic": 1, "_id": 0})
    return [doc["topic"] for doc in cursor]

async def get_quiz_by_topic_from_db(topic: str):
    return quiz_collection.find_one({"topic": topic})

# --- Progress Helpers ---
async def get_or_create_user_progress(user_id: str):
    progress = progress_collection.find_one({"user_id": user_id})
    if not progress:
        # Create a new progress document for the user
        new_progress = {
            "user_id": user_id,
            "user_name": user_id.split('@')[0],
            "videos": {},
            "quizzes": [],
            "streak": 0,
            "longest_streak": 0
        }
        progress_collection.insert_one(new_progress)
        return new_progress
    return progress

async def update_video_progress_in_db(user_id: str, video_id: str, progress_data: dict):
    # Use $set to update a specific field in the videos object
    progress_collection.update_one(
        {"user_id": user_id},
        {"$set": {f"videos.{video_id}": progress_data}}
    )

async def update_quiz_result_in_db(user_id: str, quiz_result: dict):
    # Use $push to add a new quiz result to the array
    progress_collection.update_one(
        {"user_id": user_id},
        {"$push": {"quizzes": quiz_result}}
    )
