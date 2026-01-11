"""
quiz_engine.py - Online Quiz Analysis Engine

This module provides real-time analysis of student quiz performance.
It loads the pre-trained clustering model and classifies students
into "Learner Profiles" with appropriate search tags for recommendations.

What this does:
1. Takes a student's quiz score and time
2. Predicts which learner profile they belong to
3. Generates a tailored search query for video recommendations

Learner Profiles:
- "Struggling": Needs basic, step-by-step tutorials
- "Rushed": Needs quick summary/review content  
- "High Achiever": Can handle advanced concepts

Author: ML Engineering Team
Usage: Import and call analyze_student_performance(score, time, topic)
"""

import joblib
import numpy as np
from typing import Dict, Any, Optional
import os

# ============================================================================
# MODEL LOADING (Global Scope)
# ============================================================================

# Path to the saved model (Relative to this script)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "student_clustering_model.pkl")

# Load model once when module is imported
_model_package = None

def _load_model():
    """
    Load the trained clustering model from disk.
    This is called once and cached for efficiency.
    """
    global _model_package
    
    if _model_package is not None:
        return _model_package
    
    if not os.path.exists(MODEL_PATH):
        print(f"[Quiz Engine] WARNING: Model file not found at {MODEL_PATH}")
        print("[Quiz Engine] Please run train_model.py first to generate the model")
        return None
    
    try:
        _model_package = joblib.load(MODEL_PATH)
        print(f"[Quiz Engine] Model loaded successfully (v{_model_package.get('version', 'unknown')})")
        return _model_package
    except Exception as e:
        print(f"[Quiz Engine] Error loading model: {e}")
        return None


# Load on import
_load_model()


# ============================================================================
# SEARCH FILTERS (For Metadata-Filtered Recommendations)
# ============================================================================
# These map learner profiles to ChromaDB filter parameters
# Used by search_engine.find_best_video(query, difficulty=..., style=...)

SEARCH_FILTERS = {
    "Struggling": {
        "difficulty": "Beginner",
        "style": "Conceptual"  # Step-by-step theory first
    },
    "Rushed": {
        "difficulty": None,  # Any difficulty
        "style": "One_Shot"  # Aligns with Tagger V5 'One_Shot' category
    },
    "High Achiever": {
        "difficulty": "Advanced",
        "style": "Interview_Prep"  # Challenge them
    }
}

# ============================================================================
# SEARCH TAG TEMPLATES (Legacy Text-Based Search)
# ============================================================================

# Different search queries based on learner profile and topic
SEARCH_TEMPLATES = {
    "Struggling": {
        "default": "{topic} basic tutorial step by step for beginners",
        "Arrays": "Arrays basic tutorial step by step beginner friendly",
        "Linked Lists": "Linked Lists basics explained simply for beginners",
        "Sorting": "Sorting algorithms explained easy beginner tutorial",
        "Trees": "Binary trees basics simple explanation step by step",
        "Graphs": "Graph data structure basics beginner friendly tutorial",
        "Dynamic Programming": "Dynamic programming introduction easy examples"
    },
    "Rushed": {
        "default": "{topic} quick summary 5 minutes revision",
        "Arrays": "Arrays quick revision 5 minute summary",
        "Linked Lists": "Linked Lists quick recap short summary",
        "Sorting": "Sorting algorithms quick summary 5 minutes",
        "Trees": "Binary trees quick revision summary",
        "Graphs": "Graphs quick summary revision notes",
        "Dynamic Programming": "DP quick tricks and patterns summary"
    },
    "High Achiever": {
        "default": "{topic} advanced concepts techniques interview level",
        "Arrays": "Arrays advanced problems interview questions",
        "Linked Lists": "Linked Lists advanced techniques interview prep",
        "Sorting": "Advanced sorting algorithms time complexity analysis",
        "Trees": "Advanced tree problems interview questions",
        "Graphs": "Graph algorithms advanced problems interview",
        "Dynamic Programming": "DP advanced patterns optimization techniques"
    }
}


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_student_performance(
    score: float,
    time_taken: float,
    topic: str = "DSA",
    results: list = None,
    questions: list = None
) -> Dict[str, Any]:
    """
    Analyze a student's quiz performance and generate recommendations.
    
    Args:
        score: Student's quiz score (0-100)
        time_taken: Average time per question in seconds
        topic: The topic of the quiz
        results: List of {question_index, is_correct} dicts (Optional)
        questions: List of full question objects (Optional)
        
    Returns:
        Dictionary containing cluster_id, learner_profile, search_tag, 
        confidence, recommendation_type, feedback, and weak_tags.
    """
    
    # Load the model package
    model_package = _load_model()
    
    if model_package is None:
        # Fallback if model isn't loaded
        return _fallback_analysis(score, time_taken, topic)
    
    # Extract components
    model = model_package['model']
    scaler = model_package['scaler']
    labels_mapping = model_package['labels_mapping']
    
    # ----- Step 1: Prepare the input data -----
    # Create a feature array in the same format as training data
    student_data = np.array([[score, time_taken]])
    
    # Scale using the same scaler from training
    student_data_scaled = scaler.transform(student_data)
    
    # ----- Step 2: Predict the cluster -----
    cluster_id = model.predict(student_data_scaled)[0]
    
    # Get the learner profile label
    learner_profile = labels_mapping.get(cluster_id, "Unknown")
    
    # ----- Step 3: Calculate confidence -----
    # Confidence = how close to cluster center (inverse of distance)
    distances = model.transform(student_data_scaled)[0]  # Distance to each cluster
    min_distance = distances[cluster_id]
    # Normalize to 0-1 range (lower distance = higher confidence)
    confidence = max(0, 1 - (min_distance / 3))  # Rough normalization
    
    # ----- Step 4: Micro-Tag Analysis (NEW) -----
    # Analyze detailed weakness based on pillars (Theory vs Syntax)
    weak_tags = []
    if results: 
        micro_analysis = _analyze_micro_tags(results, questions)
        # Get tags where accuracy is below 60%
        weak_tags = [tag for tag, acc in micro_analysis.items() if acc < 60]
    
    # ----- Step 5: Gemini-Powered Diagnosis (NEW) -----
    from .ai_coach import generate_coaching_feedback, generate_smart_search_query
    
    # Generate Feedback
    feedback = generate_coaching_feedback(learner_profile, weak_tags, topic, score)
    
    # Generate Smart Query
    search_tag = generate_smart_search_query(learner_profile, topic, weak_tags)
    
    # ----- Step 6: Determine recommendation type -----
    recommendation_types = {
        "Struggling": "basic_tutorial",
        "Rushed": "quick_summary",
        "High Achiever": "advanced_content"
    }
    recommendation_type = recommendation_types.get(learner_profile, "general")
    
    # ----- Step 7: Get structured search filters -----
    search_filters = SEARCH_FILTERS.get(learner_profile, {"difficulty": None, "style": None})
    
    return {
        "cluster_id": int(cluster_id),
        "learner_profile": learner_profile,
        "search_tag": search_tag,
        "search_filters": search_filters,
        "confidence": round(confidence, 2),
        "recommendation_type": recommendation_type,
        "feedback": feedback,  # NEW: AI Coach Message
        "weak_tags": weak_tags, # NEW: Identified Weaknesses
        "input": {
            "score": score,
            "time_taken": time_taken,
            "topic": topic
        }
    }


def _analyze_micro_tags(results, questions):
    """
    Calculates accuracy percentage for each micro-tag (e.g., Theory: 80%, Syntax: 20%).
    """
    tag_stats = {} # { "Syntax": {correct: 2, total: 5} }
    
    for res in results:
        q_idx = res["question_index"]
        if q_idx >= len(questions): continue
        
        q = questions[q_idx]
        tags = q.get("micro_tags", ["General"])
        is_correct = res["is_correct"]
        
        for tag in tags:
            if tag not in tag_stats:
                tag_stats[tag] = {"correct": 0, "total": 0}
            tag_stats[tag]["total"] += 1
            if is_correct:
                tag_stats[tag]["correct"] += 1
                
    # Convert to average
    accuracies = {}
    for tag, stats in tag_stats.items():
        accuracies[tag] = round((stats["correct"] / stats["total"]) * 100, 1)
        
    return accuracies


def _generate_search_tag(learner_profile: str, topic: str) -> str:
    """
    Generate an appropriate search query based on learner profile and topic.
    
    Args:
        learner_profile: "Struggling", "Rushed", or "High Achiever"
        topic: The topic/concept (e.g., "Arrays")
        
    Returns:
        A search query string optimized for finding relevant videos
    """
    
    # Get the template dictionary for this profile
    templates = SEARCH_TEMPLATES.get(learner_profile, SEARCH_TEMPLATES["Struggling"])
    
    # Look for topic-specific template, otherwise use default
    if topic in templates:
        return templates[topic]
    else:
        # Use the default template with topic substitution
        default_template = templates.get("default", "{topic} tutorial")
        return default_template.format(topic=topic)


def _fallback_analysis(score: float, time_taken: float, topic: str) -> Dict[str, Any]:
    """
    Simple rule-based fallback if the ML model is not available.
    Uses basic thresholds to classify students.
    """
    
    print("[Quiz Engine] Using fallback rule-based analysis")
    
    # Simple rules
    if score >= 70:
        profile = "High Achiever"
    elif time_taken <= 30:
        profile = "Rushed"
    else:
        profile = "Struggling"
    
    search_tag = _generate_search_tag(profile, topic)
    search_filters = SEARCH_FILTERS.get(profile, {"difficulty": None, "style": None})
    
    return {
        "cluster_id": -1,  # -1 indicates fallback mode
        "learner_profile": profile,
        "search_tag": search_tag,
        "search_filters": search_filters,  # Structured filters for ChromaDB
        "confidence": 0.5,  # Lower confidence for fallback
        "recommendation_type": "general",
        "fallback_mode": True,
        "input": {
            "score": score,
            "time_taken": time_taken,
            "topic": topic
        }
    }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_all_profiles() -> list:
    """Return list of all possible learner profiles."""
    return ["Struggling", "Rushed", "High Achiever"]


def get_topics() -> list:
    """Return list of supported topics with specialized search templates."""
    return list(SEARCH_TEMPLATES["Struggling"].keys())


def is_model_loaded() -> bool:
    # Check if the ML model is loaded and ready.
    return _model_package is not None


# ============================================================================
# TEST / DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Quiz Engine - Demo")
    print("=" * 60)
    
    # Test cases representing different student types
    test_cases = [
        {"score": 35, "time": 95, "topic": "Arrays"},      # Struggling
        {"score": 85, "time": 50, "topic": "Sorting"},     # High Achiever
        {"score": 50, "time": 15, "topic": "Trees"},       # Rushed
        {"score": 42, "time": 80, "topic": "Graphs"},      # Struggling
        {"score": 92, "time": 45, "topic": "Dynamic Programming"},  # High Achiever
    ]
    
    print("\nAnalyzing test students:\n")
    
    for i, test in enumerate(test_cases, 1):
        result = analyze_student_performance(
            score=test["score"],
            time_taken=test["time"],
            topic=test["topic"]
        )
        
        print(f"Student {i}:")
        print(f"  Input: Score={test['score']}, Time={test['time']}s, Topic='{test['topic']}'")
        print(f"  Profile: {result['learner_profile']}")
        print(f"  Search Tag: \"{result['search_tag']}\"")
        print(f"  Confidence: {result['confidence']}")
        print()
