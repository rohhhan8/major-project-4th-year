"""
update_metadata_5pillars.py - Diagnosis V2 Migration

Updates questions to use the 5-Pillar Diagnosis System:
1. Concept (Definition, Theory) -> Rec: Whiteboard
2. Implementation (Syntax, How-to) -> Rec: Live Coding
3. Complexity (Big-O, Performance) -> Rec: Analysis
4. Debugging (Fix, Error) -> Rec: Debugging Guide
5. Application (Use Case, Real-world) -> Rec: System Design

Usage: python backend/migrations/update_metadata_5pillars.py
"""

import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import questions_collection, is_db_connected

PILLAR_KEYWORDS = {
    "Complexity": ["complexity", "big-o", "time", "space", "efficiency", "worst case", "best case", "o(1)", "o(n)"],
    "Implementation": ["syntax", "code", "declare", "initialize", "method", "function", "class", "import"],
    "Debugging": ["error", "fail", "bug", "output", "wrong", "fix", "missing", "exception"],
    "Application": ["use case", "real world", "application", "scenario", "design", "system", "undo", "browser"],
    "Concept": ["definition", "what is", "principle", "difference", "explain", "theoretical", "type of"]
}

def determine_pillars_and_time(text, difficulty):
    text_lower = text.lower()
    
    # 1. Determine Pillar
    assigned_pillar = "Concept" # Default
    
    # Check keywords (Priority: Complexity > Debugging > Application > Implementation > Concept)
    # We use this order because "Concept" keywords might appear in others (e.g. "Explain the error").
    
    if any(k in text_lower for k in PILLAR_KEYWORDS["Complexity"]):
        assigned_pillar = "Complexity"
    elif any(k in text_lower for k in PILLAR_KEYWORDS["Debugging"]):
        assigned_pillar = "Debugging"
    elif any(k in text_lower for k in PILLAR_KEYWORDS["Application"]):
        assigned_pillar = "Application"
    elif any(k in text_lower for k in PILLAR_KEYWORDS["Implementation"]):
        assigned_pillar = "Implementation"
    
    # 2. Determine Ideal Time (Refined)
    # Concepts are fast. Complexity/Application take thought. Debugging takes longest.
    base_time = 30
    if difficulty == "Easy": base_time = 15
    if difficulty == "Hard": base_time = 45
    
    time_modifiers = {
        "Concept": 0.8,      # Fast recall
        "Implementation": 1.0, # Standard
        "Complexity": 1.2,   # Needs calculation
        "Application": 1.2,  # Needs thought
        "Debugging": 1.5     # Needs tracing
    }
    
    ideal_time = int(base_time * time_modifiers[assigned_pillar])
    
    return [assigned_pillar], ideal_time

def update_pillars():
    if not is_db_connected():
        print("Error: Database not connected.")
        return

    print("Fetching questions...")
    questions = list(questions_collection.find({}))
    
    count = 0
    headers = {"Concept": 0, "Implementation": 0, "Complexity": 0, "Debugging": 0, "Application": 0}
    
    for q in questions:
        text = q.get("question_text", "")
        difficulty = q.get("difficulty", "Medium")
        
        updated_tags, ideal_time = determine_pillars_and_time(text, difficulty)
        
        # Update DB
        questions_collection.update_one(
            {"_id": q["_id"]},
            {"$set": {
                "micro_tags": updated_tags,
                "ideal_time": ideal_time
            }}
        )
        
        headers[updated_tags[0]] += 1
        count += 1
        
    print(f"✅ Updated {count} questions with 5-Pillar Metadata.")
    print("Distribution:", headers)

if __name__ == "__main__":
    update_pillars()
