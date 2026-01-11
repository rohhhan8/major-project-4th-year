# backend/app/quiz.py
"""
Quiz API Endpoints (Two-Collection System)

Provides endpoints for:
- GET /quiz/topics: Hierarchical topic menu (Subjects -> Topics)
- GET /quiz/start/{topic_id}: 10 random questions for a topic
- POST /quiz/submit: Evaluate answers with Diagnosis Matrix

All operations are fully logged for debugging.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from .models import QuizSubmission, QuestionAnswer, DiagnosisPillar
from .database import (
    is_db_connected, 
    get_topics_hierarchy,
    get_random_questions_by_topic_id,
    get_topic_by_id,
    add_quiz_result, 
    quiz_attempts_collection,
    questions_collection
)
from .auth import get_current_user
from .search_engine import find_best_video
from .ai_coach import generate_coaching_feedback, generate_smart_search_query

print("[Quiz Module] ✅ Quiz router loaded and ready (Two-Collection System)")

router = APIRouter()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_question_for_frontend(question: dict) -> dict:
    """
    Formats a database question for frontend consumption.
    Removes correct_option_id to prevent cheating.
    """
    return {
        "id": str(question.get("_id", "")),
        "question_text": question.get("question_text", ""),
        "options": question.get("options", []),  # List of {id, text} objects
        "ideal_time_seconds": question.get("ideal_time_seconds", 30),
        "diagnosis_pillar": question.get("diagnosis_pillar", "Concept"),
        "difficulty": question.get("difficulty", "Medium"),
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.get("/topics")
async def get_quiz_topics(current_user: dict = Depends(get_current_user)):
    """
    Returns the hierarchical topic structure for building the quiz selection menu.
    Structure: { subjects: [{_id, name, icon, topics: [{_id, name, question_count}]}] }
    """
    print(f"\n{'='*60}")
    print(f"[Quiz API] 📂 GET /quiz/topics")
    print(f"  - User: {current_user.get('email')}")
    
    if not is_db_connected():
        print(f"  - ❌ Database not connected!")
        raise HTTPException(status_code=503, detail="Database not connected")
    
    hierarchy = await get_topics_hierarchy()
    
    if not hierarchy:
        print(f"  - ⚠️ No topics found in database")
        raise HTTPException(status_code=404, detail="No quiz topics found. Run migration script first.")
    
    total_topics = sum(len(s.get("topics", [])) for s in hierarchy)
    print(f"  - ✅ Returning {len(hierarchy)} subjects, {total_topics} topics")
    print(f"{'='*60}\n")
    
    return {"subjects": hierarchy}


@router.get("/start/{topic_id}")
async def start_quiz(topic_id: str, count: int = 10, current_user: dict = Depends(get_current_user)):
    """
    Starts a quiz by returning random questions for a specific topic.
    Uses MongoDB $sample for true randomization.
    """
    print(f"\n{'='*60}")
    print(f"[Quiz API] 🎮 GET /quiz/start/{topic_id}")
    print(f"  - Requested Questions: {count}")
    
    if not is_db_connected():
        print(f"  - ❌ Database not connected!")
        raise HTTPException(status_code=503, detail="Database not connected")
    
    # Verify topic exists
    topic = await get_topic_by_id(topic_id)
    if not topic:
        print(f"  - ❌ Topic not found: {topic_id}")
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")
    
    print(f"  - Topic Name: {topic.get('name')}")
    
    # Get random questions
    questions = await get_random_questions_by_topic_id(topic_id, count=count)
    
    if not questions:
        print(f"  - ❌ No questions found for topic")
        raise HTTPException(status_code=404, detail=f"No questions found for topic: {topic_id}")
    
    formatted_questions = [format_question_for_frontend(q) for q in questions]
    
    print(f"  - ✅ Returning {len(formatted_questions)} questions")
    print(f"{'='*60}\n")
    
    return {
        "topic_id": topic_id,
        "topic_name": topic.get("name"),
        "total_questions": len(formatted_questions),
        "questions": formatted_questions
    }


@router.post("/submit")
async def submit_quiz(submission: QuizSubmission, current_user: dict = Depends(get_current_user)):
    """
    Evaluates a quiz submission using the Diagnosis Matrix:
    1. Scores answers
    2. Compares user_time vs ideal_time
    3. Identifies weakest diagnosis_pillar
    4. Generates AI-powered recommendations
    """
    print(f"\n{'='*60}")
    print(f"[Quiz API] 📝 POST /quiz/submit")
    print(f"  - User: {current_user.get('email', 'Unknown')}")
    print(f"  - Topic ID: {submission.topic_id}")
    print(f"  - Answers Received: {len(submission.answers)}")
    print(f"  - Total Time: {submission.total_time_seconds}s")
    
    if not is_db_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    # Fetch the actual questions to get correct answers
    # Convert string IDs to ObjectId (MongoDB stores _id as ObjectId)
    from bson import ObjectId
    
    question_ids = [a.question_id for a in submission.answers]
    
    # Try to convert to ObjectId (for ObjectId-based _ids)
    object_ids = []
    for qid in question_ids:
        try:
            object_ids.append(ObjectId(qid))
        except:
            pass  # Skip invalid ObjectId strings
    
    # Query with both formats for compatibility
    questions_raw = list(questions_collection.find({
        "$or": [
            {"_id": {"$in": object_ids}},  # ObjectId format
            {"_id": {"$in": question_ids}}  # String format (just in case)
        ]
    }))
    questions_map = {str(q["_id"]): q for q in questions_raw}
    
    print(f"  - Questions Loaded: {len(questions_map)}")
    
    # =========================================================================
    # PHASE 1: SCORING & PILLAR TRACKING
    # =========================================================================
    print(f"\n[Diagnosis] 🧠 PHASE 1: SCORING")
    
    score = 0
    total_questions = len(submission.answers)
    
    # Track pillar statistics
    pillar_stats = {}
    for pillar in DiagnosisPillar:
        pillar_stats[pillar.value] = {"correct": 0, "total": 0, "rushed": 0, "time_ratio": []}
    
    failed_questions = []
    attempt_records = []
    user_id = current_user["id"]
    timestamp = datetime.now()
    
    for answer in submission.answers:
        question = questions_map.get(answer.question_id)
        if not question:
            print(f"  - ⚠️ Question {answer.question_id} not found, skipping")
            continue
        
        correct_option = question.get("correct_option_id")
        is_correct = answer.selected_option_id == correct_option
        
        pillar = question.get("diagnosis_pillar", "Concept")
        ideal_time = question.get("ideal_time_seconds", 30)
        time_ratio = answer.time_taken_seconds / ideal_time if ideal_time > 0 else 1
        
        # Dynamic init for unknown pillars (e.g. "Security")
        if pillar not in pillar_stats:
            pillar_stats[pillar] = {"correct": 0, "total": 0, "rushed": 0, "time_ratio": []}
            
        # Update pillar stats
        pillar_stats[pillar]["total"] += 1
        pillar_stats[pillar]["time_ratio"].append(time_ratio)
        
        if is_correct:
            score += 1
            pillar_stats[pillar]["correct"] += 1
        else:
            failed_questions.append(question)
        
        # Check if rushed (less than 30% of ideal time)
        if time_ratio < 0.3:
            pillar_stats[pillar]["rushed"] += 1
        
        # Record for persistent storage
        attempt_records.append({
            "user_id": user_id,
            "question_id": answer.question_id,
            "topic_id": submission.topic_id,
            "is_correct": is_correct,
            "time_taken_seconds": answer.time_taken_seconds,
            "ideal_time_seconds": ideal_time,
            "diagnosis_pillar": pillar,
            "timestamp": timestamp
        })
    
    percentage = (score / total_questions) * 100 if total_questions > 0 else 0
    print(f"  - Score: {score}/{total_questions} ({percentage:.1f}%)")
    
    # =========================================================================
    # PHASE 2: FIND WEAKEST PILLAR
    # =========================================================================
    print(f"\n[Diagnosis] 📊 PHASE 2: PILLAR ANALYSIS")
    
    pillar_breakdown = {}
    for pillar, stats in pillar_stats.items():
        if stats["total"] > 0:
            accuracy = (stats["correct"] / stats["total"]) * 100
            avg_time_ratio = sum(stats["time_ratio"]) / len(stats["time_ratio"])
            pillar_breakdown[pillar] = {
                "correct": stats["correct"],
                "total": stats["total"],
                "accuracy": round(accuracy, 1),
                "rushed_count": stats["rushed"],
                "avg_time_ratio": round(avg_time_ratio, 2)
            }
            print(f"  - {pillar}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%), Rushed: {stats['rushed']}")
    
    # Determine weakest pillar (lowest accuracy, higher total questions = more weight)
    weakest_pillar = "Concept"  # Default
    lowest_accuracy = 100
    for pillar, data in pillar_breakdown.items():
        if data["total"] >= 1 and data["accuracy"] < lowest_accuracy:
            lowest_accuracy = data["accuracy"]
            weakest_pillar = pillar
    
    print(f"  - ⚠️ Weakest Pillar: {weakest_pillar} ({lowest_accuracy:.1f}%)")
    
    # =========================================================================
    # PHASE 3: DETERMINE LEARNER PROFILE
    # =========================================================================
    print(f"\n[Diagnosis] 👤 PHASE 3: PROFILE CLASSIFICATION")
    
    avg_time_ratio = sum(
        sum(s["time_ratio"]) / len(s["time_ratio"]) 
        for s in pillar_stats.values() if s["time_ratio"]
    ) / max(1, len([s for s in pillar_stats.values() if s["time_ratio"]]))
    
    total_rushed = sum(s["rushed"] for s in pillar_stats.values())
    rushed_percentage = (total_rushed / total_questions) * 100 if total_questions > 0 else 0
    
    if percentage >= 70:
        learner_profile = "High Achiever"
    elif rushed_percentage > 40 or avg_time_ratio < 0.6:
        learner_profile = "Rushed"
    else:
        learner_profile = "Struggling"
    
    print(f"  - Avg Time Ratio: {avg_time_ratio:.2f}")
    print(f"  - Rushed Percentage: {rushed_percentage:.1f}%")
    print(f"  - Profile: {learner_profile}")
    
    # =========================================================================
    # PHASE 4: AI-POWERED RECOMMENDATIONS
    # =========================================================================
    print(f"\n[Diagnosis] 🤖 PHASE 4: AI RECOMMENDATIONS")
    
    # Get topic name for context
    topic = await get_topic_by_id(submission.topic_id)
    topic_name = topic.get("name", submission.topic_id) if topic else submission.topic_id
    
    # Collect UNIQUE search tags from failed questions
    failed_tags = []
    for q in failed_questions:
        failed_tags.extend(q.get("search_tags", []))
    unique_failed_tags = list(set(failed_tags))[:5]  # Limit to top 5 unique tags
    
    print(f"  - Failed Question Tags: {unique_failed_tags}")
    
    # Generate AI feedback
    feedback = generate_coaching_feedback(learner_profile, [weakest_pillar], topic_name, percentage)
    
    # Build SPECIFIC search query using failed tags
    # PRIORITY: Specific concepts first, then topic context
    # This ensures subtopic-level matching (e.g., "Arrays" not just "DSA")
    if unique_failed_tags:
        # Put specific concepts FIRST for better semantic matching
        # Format: "specific_concept in topic_context explanation"
        primary_concept = unique_failed_tags[0]  # Most important failed concept
        other_concepts = " ".join(unique_failed_tags[1:3]) if len(unique_failed_tags) > 1 else ""
        
        # Smart query: emphasize subtopic, not just main topic
        search_query = f"{primary_concept} {other_concepts} {topic_name} {weakest_pillar} tutorial explained step by step"
        print(f"  - Smart Query (subtopic-focused): {search_query}")
    else:
        # Fallback to AI-generated query if no tags
        search_query = generate_smart_search_query(learner_profile, topic_name, [weakest_pillar])
    
    # Find video recommendations
    print(f"[Quiz] 🔍 Searching for videos...")
    print(f"  - Query: {search_query}")
    recommendations = find_best_video(search_query)
    print(f"  - Found: {len(recommendations)} videos")
    
    # =========================================================================
    # PHASE 5: PERSIST DATA
    # =========================================================================
    print(f"\n[Diagnosis] 💾 PHASE 5: SAVING DATA")
    
    if attempt_records:
        quiz_attempts_collection.insert_many(attempt_records)
        print(f"  - Saved {len(attempt_records)} attempt records")
    
    primary_video_id = recommendations[0].get("video_id") if recommendations else None
    
    quiz_result_record = {
        "topic_id": submission.topic_id,
        "topic_name": topic_name,
        "score": score,
        "total_questions": total_questions,
        "percentage": round(percentage, 2),
        "passed": percentage >= 60,
        "total_time_seconds": submission.total_time_seconds,
        "learner_profile": learner_profile,
        "weakest_pillar": weakest_pillar,
        "recommended_video_id": primary_video_id,
        "submitted_at": timestamp
    }
    
    await add_quiz_result(user_id, quiz_result_record)
    print(f"  - Saved quiz summary")
    
    print(f"\n{'='*60}")
    print(f"[Quiz API] ✅ QUIZ SUBMISSION COMPLETE")
    print(f"{'='*60}\n")
    
    # =========================================================================
    # RESPONSE
    # =========================================================================
    return {
        "score": score,
        "total_questions": total_questions,
        "percentage": round(percentage, 2),
        "passed": percentage >= 60,
        
        "diagnosis": {
            "learner_profile": learner_profile,
            "weakest_pillar": weakest_pillar,
            "pillar_breakdown": pillar_breakdown,
            "feedback": feedback
        },
        
        "recommendations": recommendations,
        "search_query": search_query
    }


# ============================================================================
# LEGACY ENDPOINTS (Backward Compatibility)
# ============================================================================

@router.get("/legacy/{topic}")
async def get_quiz_by_topic_legacy(topic: str, limit: Optional[int] = 10):
    """
    [LEGACY] Retrieves quiz questions by topic name.
    Use /start/{topic_id} for new implementations.
    """
    from .database import get_questions_by_topic
    
    print(f"\n[Quiz API] ⚠️ LEGACY ENDPOINT: /quiz/legacy/{topic}")
    
    if not is_db_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    questions = await get_questions_by_topic(topic, limit=limit)
    
    if not questions:
        raise HTTPException(status_code=404, detail=f"No questions found for topic: '{topic}'")
    
    return {
        "topic": topic,
        "total_questions": len(questions),
        "questions": [format_question_for_frontend(q) for q in questions]
    }
