"""
update_questions_metadata.py - Metadata Backfill for Smart Diagnosis

This script updates existing questions with "Intelligence Fields":
1. topic_id: Links to the hierarchical 'topics' collection.
2. micro_tags: ["Theory", "Syntax", "Logic"]
3. ideal_time: Benchmark time for 'Rushed' analysis.
4. explanation: Immediate feedback text.

Usage: python backend/migrations/update_questions_metadata.py
"""

import sys
import os
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import questions_collection, topics_collection, is_db_connected

# Keyword mapping for Micro-Tags
MICRO_TAG_RULES = {
    "Syntax": ["syntax", "code", "keyword", "declare", "operator", "output"],
    "Theory": ["definition", "principle", "what is", "concept", "feature", "advantage"],
    "Logic": ["algorithm", "complexity", "worst case", "best case", "step", "process"]
}

# Time mapping by Difficulty (Benchmarks)
TIME_BENCHMARKS = {
    "Easy": 15,
    "Medium": 30,
    "Hard": 60
}

def determine_micro_tags(text):
    tags = set()
    text_lower = text.lower()
    
    for tag, keywords in MICRO_TAG_RULES.items():
        if any(k in text_lower for k in keywords):
            tags.add(tag)
            
    # Default if no keywords match
    if not tags:
        tags.add("Theory")
        
    return list(tags)

def get_topic_id(tag_list):
    """
    Finds the matching topic_id from the new hierarchy based on old tags.
    Example: ["Stack", "DS"] -> "topic-stacks"
    """
    # Map specifically known tags to IDs
    # This assumes the tags in DB match the names we seeded, roughly.
    # We normalized our IDs in seed_topics.py strictly (e.g. 'topic-arrays').
    
    for tag in tag_list:
        normalized = tag.lower().replace(" ", "")
        
        # Try to find a topic document that matches this tag name
        # We can try to look up by name or just use a known map
        
        known_map = {
            "stack": "topic-stacks",
            "queue": "topic-queues",
            "array": "topic-arrays",
            "linkedlist": "topic-linkedlists",
            "tree": "topic-trees",
            "graph": "topic-graphs",
            "heap": "topic-heaps",
            "sorting": "topic-sorting",
            "searching": "topic-searching",
            "dynamicprogramming": "topic-dp",
            "dp": "topic-dp"
        }
        
        if normalized in known_map:
            return known_map[normalized]
            
    return None

def update_metadata():
    if not is_db_connected():
        print("Error: Database not connected.")
        return

    print("Fetching all questions...")
    questions = list(questions_collection.find({}))
    print(f"Found {len(questions)} questions to update.")

    updated_count = 0
    
    for q in questions:
        # 1. Determine Micro-Tags
        text = q.get("question_text", "")
        micro_tags = determine_micro_tags(text)
        
        # 2. Determine Ideal Time
        difficulty = q.get("difficulty", "Medium")
        ideal_time = TIME_BENCHMARKS.get(difficulty, 30)
        
        # 3. Determine Topic ID
        current_tags = q.get("tags", [])
        topic_id = get_topic_id(current_tags)
        
        # 4. Generate Explanation (Placeholder for now)
        explanation = f"The correct answer is derived from {micro_tags[0]} principles of {current_tags[1] if len(current_tags)>1 else 'DSA'}."

        # Prepare Update
        update_fields = {
            "micro_tags": micro_tags,
            "ideal_time": ideal_time,
            "explanation": q.get("explanation", explanation) # Preserve if exists
        }
        
        if topic_id:
            update_fields["topic_id"] = topic_id
            
        # Execute Update
        questions_collection.update_one(
            {"_id": q["_id"]},
            {"$set": update_fields}
        )
        updated_count += 1
        
    print(f"✅ Successfully updated {updated_count} questions with Intelligence Fields.")

if __name__ == "__main__":
    update_metadata()
