"""
database.py - Centralized MongoDB Connection & Collections

This module provides a single source of truth for all database operations.
All collections are defined here to prevent conflicts and ensure consistency.

Database: major_project (MongoDB Atlas)
Collections:
    - users: User accounts and authentication
    - questions: Quiz questions (migrated from quiz_app)
    - user_progress: Video progress, quiz scores, streaks
    - videos: Cached video metadata
    - notes: User-generated notes

Author: Backend Team
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# DATABASE CONNECTION
# ============================================================================

# Get connection string from environment (matches your .env file)
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "major_project")

# Validate connection string exists
if not MONGODB_URL:
    raise ValueError(
        "MONGODB_URL not found in environment variables! "
        "Please check your .env file."
    )

# Create MongoDB client with connection pooling
client = MongoClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000,  # 5 second timeout
    maxPoolSize=50,  # Connection pool
    retryWrites=True
)

# Get database reference
database = client[DATABASE_NAME]

# ============================================================================
# COLLECTIONS (Single Source of Truth)
# ============================================================================

# User Management
user_collection = database["users"]

# Quiz System (Legacy + Smart)
questions_collection = database["questions"]
topics_collection = database["topics"]       # [NEW] Hierarchical Topics
quiz_attempts_collection = database["quiz_attempts"] # [NEW] Granular History

# Progress Tracking
progress_collection = database["user_progress"]

# Video & Notes
videos_collection = database["videos"]
notes_collection = database["notes"]

# ============================================================================
# CONNECTION HELPERS
# ============================================================================

def is_db_connected() -> bool:
    """
    Checks if the MongoDB connection is active.
    Returns True if connected, False otherwise.
    """
    try:
        client.admin.command('ping')
        return True
    except Exception:
        return False


def get_db_info() -> dict:
    """
    Returns information about the current database connection.
    Useful for debugging and health checks.
    """
    return {
        "connected": is_db_connected(),
        "database": DATABASE_NAME,
        "collections": database.list_collection_names() if is_db_connected() else []
    }


# ============================================================================
# USER HELPERS
# ============================================================================

def user_helper(user) -> dict:
    """
    Converts a MongoDB user document to a clean dictionary.
    Removes internal MongoDB fields for API responses.
    """
    if not user:
        return None
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "full_name": user.get("full_name", ""),
        "google_id": user.get("google_id", ""),
        "created_at": user.get("created_at")
    }


async def get_user_by_email(email: str):
    """
    Retrieves a user from the database by their email address.
    Returns cleaned user data (no sensitive fields).
    """
    user = user_collection.find_one({"email": email})
    return user_helper(user) if user else None


async def get_user_by_email_raw(email: str):
    """
    Retrieves the RAW user document including hashed_password.
    Used for authentication only - do not expose to API.
    """
    return user_collection.find_one({"email": email})


async def get_user_by_google_id(google_id: str):
    """
    Retrieves a user from the database by their Google ID.
    """
    user = user_collection.find_one({"google_id": google_id})
    return user_helper(user) if user else None


async def create_user(user_data: dict):
    """
    Creates a new user in the database.
    """
    result = user_collection.insert_one(user_data)
    new_user = user_collection.find_one({"_id": result.inserted_id})
    return user_helper(new_user)


# ============================================================================
# QUIZ HELPERS (Two-Collection System)
# ============================================================================

async def get_topics_hierarchy():
    """
    Returns the full topic hierarchy for building the quiz menu.
    Structure: { subjects: [{_id, name, topics: [{_id, name}]}] }
    """
    print("\n[Database] 📂 FETCHING TOPIC HIERARCHY")
    
    # Get all subjects (type == SUBJECT)
    subjects = list(topics_collection.find({"type": "SUBJECT"}))
    print(f"  - Found {len(subjects)} subjects")
    
    hierarchy = []
    for subject in subjects:
        subject_data = {
            "_id": subject["_id"],
            "name": subject["name"],
            "icon": subject.get("icon", "📚"),
            "topics": []
        }
        
        # Get child topics
        child_topics = list(topics_collection.find({
            "type": "TOPIC",
            "parent_id": subject["_id"]
        }))
        
        for topic in child_topics:
            # Count questions for each topic
            question_count = questions_collection.count_documents({"topic_id": topic["_id"]})
            subject_data["topics"].append({
                "_id": topic["_id"],
                "name": topic["name"],
                "icon": topic.get("icon", "📄"),
                "question_count": question_count
            })
        
        print(f"  - {subject['name']}: {len(child_topics)} topics")
        hierarchy.append(subject_data)
    
    return hierarchy


async def get_random_questions_by_topic_id(topic_id: str, count: int = 10):
    """
    Gets random questions for a specific topic_id using MongoDB aggregation.
    This is the core function for quiz generation.
    """
    print(f"\n[Database] 🎲 FETCHING RANDOM QUESTIONS")
    print(f"  - Topic ID: {topic_id}")
    print(f"  - Requested Count: {count}")
    
    pipeline = [
        {"$match": {"topic_id": topic_id}},
        {"$sample": {"size": count}}
    ]
    
    questions = list(questions_collection.aggregate(pipeline))
    print(f"  - Retrieved: {len(questions)} questions")
    
    # Log question pillars for debugging
    pillars = [q.get("diagnosis_pillar", "Unknown") for q in questions]
    pillar_counts = {p: pillars.count(p) for p in set(pillars)}
    print(f"  - Pillar Distribution: {pillar_counts}")
    
    return questions


async def get_topic_by_id(topic_id: str):
    """
    Retrieves a single topic by its ID.
    """
    return topics_collection.find_one({"_id": topic_id})


async def get_all_quiz_topics():
    """
    [LEGACY] Retrieves all unique quiz topics from the questions collection.
    Kept for backward compatibility.
    """
    topics = questions_collection.distinct("topic")
    return topics


async def get_questions_by_topic(topic: str, limit: int = 10):
    """
    [LEGACY] Retrieves questions for a specific topic name (case-insensitive).
    Kept for backward compatibility.
    """
    import re
    cursor = questions_collection.find(
        {"topic": {"$regex": f"^{re.escape(topic)}$", "$options": "i"}}
    ).limit(limit)
    return list(cursor)


async def get_random_questions(topic: str, count: int = 5):
    """
    [LEGACY] Gets random questions for a topic name.
    Kept for backward compatibility.
    """
    pipeline = [
        {"$match": {"topic": topic}},
        {"$sample": {"size": count}}
    ]
    return list(questions_collection.aggregate(pipeline))


# ============================================================================
# PROGRESS HELPERS
# ============================================================================

async def get_or_create_user_progress(user_id: str):
    """
    Retrieves a user's progress document or creates a new one.
    """
    progress = progress_collection.find_one({"user_id": user_id})
    
    if not progress:
        # Create new progress document with default values
        new_progress = {
            "user_id": user_id,
            "videos": {},
            "quizzes": [],
            "streak": 0,
            "longest_streak": 0,
            "total_watch_time": 0,
            "total_quizzes_taken": 0
        }
        progress_collection.insert_one(new_progress)
        return new_progress
    
    return progress


async def update_video_progress(user_id: str, video_id: str, progress_data: dict):
    """
    Updates the progress for a specific video.
    """
    progress_collection.update_one(
        {"user_id": user_id},
        {"$set": {f"videos.{video_id}": progress_data}},
        upsert=True
    )


async def add_quiz_result(user_id: str, quiz_result: dict):
    """
    Appends a new quiz result to the user's progress.
    """
    progress_collection.update_one(
        {"user_id": user_id},
        {
            "$push": {"quizzes": quiz_result},
            "$inc": {"total_quizzes_taken": 1}
        },
        upsert=True
    )


async def update_streak(user_id: str, new_streak: int):
    """
    Updates the user's streak and longest streak.
    """
    progress = progress_collection.find_one({"user_id": user_id})
    longest = max(new_streak, progress.get("longest_streak", 0)) if progress else new_streak
    
    progress_collection.update_one(
        {"user_id": user_id},
        {"$set": {"streak": new_streak, "longest_streak": longest}},
        upsert=True
    )


# ============================================================================
# STARTUP CHECK
# ============================================================================

if __name__ == "__main__":
    # Quick connection test when running directly
    print(f"Database: {DATABASE_NAME}")
    print(f"Connected: {is_db_connected()}")
    print(f"Collections: {database.list_collection_names()}")
