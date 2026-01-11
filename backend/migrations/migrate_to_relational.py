"""
migrate_to_relational.py - Migration Script for Two-Collection System

This script:
1. Creates the `topics` collection with hierarchical structure
2. Updates existing questions with new schema fields
3. Maps old `topic` field to new `topic_id` foreign key

Run this ONCE after updating the backend code.
"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random

load_dotenv()

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME", "major_project")

client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]

topics_collection = db["topics"]
questions_collection = db["questions"]

# ============================================================================
# TOPIC HIERARCHY DEFINITION
# ============================================================================

TOPICS_HIERARCHY = {
    "subject_dsa": {
        "name": "Data Structures & Algorithms",
        "icon": "🔢",
        "type": "SUBJECT",
        "topics": {
            "topic_arrays": {"name": "Arrays", "icon": "📊"},
            "topic_linked_list": {"name": "Linked List", "icon": "🔗"},
            "topic_stack": {"name": "Stack", "icon": "📚"},
            "topic_queue": {"name": "Queue", "icon": "🎫"},
            "topic_tree": {"name": "Trees", "icon": "🌳"},
            "topic_graph": {"name": "Graphs", "icon": "🕸️"},
            "topic_sorting": {"name": "Sorting", "icon": "📈"},
            "topic_searching": {"name": "Searching", "icon": "🔍"},
            "topic_dp": {"name": "Dynamic Programming", "icon": "🧩"},
            "topic_hashing": {"name": "Hashing", "icon": "#️⃣"},
        }
    },
    "subject_webdev": {
        "name": "Web Development",
        "icon": "🌐",
        "type": "SUBJECT",
        "topics": {
            "topic_html": {"name": "HTML", "icon": "📄"},
            "topic_css": {"name": "CSS", "icon": "🎨"},
            "topic_javascript": {"name": "JavaScript", "icon": "⚡"},
            "topic_react": {"name": "React", "icon": "⚛️"},
            "topic_nodejs": {"name": "Node.js", "icon": "🟢"},
        }
    },
    "subject_python": {
        "name": "Python Programming",
        "icon": "🐍",
        "type": "SUBJECT",
        "topics": {
            "topic_python_basics": {"name": "Python Basics", "icon": "📝"},
            "topic_oop": {"name": "OOP in Python", "icon": "🧱"},
            "topic_file_handling": {"name": "File Handling", "icon": "📁"},
        }
    }
}

# Mapping from old topic names to new topic_ids
TOPIC_NAME_TO_ID = {}

def seed_topics():
    """Creates the topic hierarchy in the database."""
    print("\n" + "="*60)
    print("PHASE 1: SEEDING TOPICS COLLECTION")
    print("="*60)
    
    # Clear existing topics
    topics_collection.delete_many({})
    print("  - Cleared existing topics")
    
    topic_docs = []
    
    for subject_id, subject_data in TOPICS_HIERARCHY.items():
        # Create subject document
        subject_doc = {
            "_id": subject_id,
            "name": subject_data["name"],
            "icon": subject_data["icon"],
            "type": "SUBJECT",
            "parent_id": None
        }
        topic_docs.append(subject_doc)
        
        # Create child topics
        for topic_id, topic_data in subject_data["topics"].items():
            topic_doc = {
                "_id": topic_id,
                "name": topic_data["name"],
                "icon": topic_data["icon"],
                "type": "TOPIC",
                "parent_id": subject_id
            }
            topic_docs.append(topic_doc)
            
            # Build mapping for migration
            TOPIC_NAME_TO_ID[topic_data["name"].lower()] = topic_id
            TOPIC_NAME_TO_ID[topic_data["name"]] = topic_id
    
    # Insert all topics
    topics_collection.insert_many(topic_docs)
    print(f"  - Inserted {len(topic_docs)} topics")
    
    # Add common aliases
    TOPIC_NAME_TO_ID["dsa"] = "topic_arrays"  # Default DSA to Arrays
    TOPIC_NAME_TO_ID["array"] = "topic_arrays"
    TOPIC_NAME_TO_ID["stacks"] = "topic_stack"
    TOPIC_NAME_TO_ID["queues"] = "topic_queue"
    TOPIC_NAME_TO_ID["linkedlist"] = "topic_linked_list"
    TOPIC_NAME_TO_ID["linked lists"] = "topic_linked_list"
    TOPIC_NAME_TO_ID["trees"] = "topic_tree"
    TOPIC_NAME_TO_ID["binary tree"] = "topic_tree"
    TOPIC_NAME_TO_ID["graphs"] = "topic_graph"
    TOPIC_NAME_TO_ID["dp"] = "topic_dp"
    
    print(f"  - Created {len(TOPIC_NAME_TO_ID)} topic aliases")


def migrate_questions():
    """Updates existing questions with new schema fields."""
    print("\n" + "="*60)
    print("PHASE 2: MIGRATING QUESTIONS")
    print("="*60)
    
    # Pillar keywords for classification
    PILLAR_KEYWORDS = {
        "Concept": ["what is", "define", "explain", "theory", "meaning", "purpose"],
        "Implementation": ["code", "implement", "write", "syntax", "function", "program"],
        "Complexity": ["time complexity", "space complexity", "big o", "efficiency", "optimize"],
        "Debugging": ["error", "bug", "fix", "wrong", "issue", "problem"],
        "Application": ["use case", "real world", "example", "application", "when to use", "scenario"]
    }
    
    questions = list(questions_collection.find({}))
    print(f"  - Found {len(questions)} existing questions")
    
    updated_count = 0
    
    for q in questions:
        updates = {}
        
        # 1. Assign topic_id from old 'topic' field
        old_topic = q.get("topic", "").lower()
        if old_topic in TOPIC_NAME_TO_ID:
            updates["topic_id"] = TOPIC_NAME_TO_ID[old_topic]
        else:
            # Try to match by tags
            for tag in q.get("tags", []):
                if tag.lower() in TOPIC_NAME_TO_ID:
                    updates["topic_id"] = TOPIC_NAME_TO_ID[tag.lower()]
                    break
            else:
                updates["topic_id"] = "topic_arrays"  # Default fallback
        
        # 2. Assign diagnosis_pillar based on question text
        question_text = q.get("question_text", "").lower()
        assigned_pillar = "Concept"  # Default
        
        for pillar, keywords in PILLAR_KEYWORDS.items():
            if any(kw in question_text for kw in keywords):
                assigned_pillar = pillar
                break
        
        updates["diagnosis_pillar"] = assigned_pillar
        
        # 3. Set ideal_time_seconds based on difficulty and pillar
        difficulty = q.get("difficulty", "Medium")
        base_time = {"Easy": 20, "Medium": 30, "Hard": 45}.get(difficulty, 30)
        pillar_modifier = {
            "Concept": 0,
            "Implementation": 10,
            "Complexity": 15,
            "Debugging": 10,
            "Application": 5
        }.get(assigned_pillar, 0)
        
        updates["ideal_time_seconds"] = base_time + pillar_modifier
        
        # 4. Generate search_tags from existing data
        search_tags = []
        search_tags.extend(q.get("tags", []))
        search_tags.append(q.get("topic", ""))
        search_tags.append(assigned_pillar.lower())
        updates["search_tags"] = list(set(filter(None, search_tags)))
        
        # 5. Add default explanation if missing
        if not q.get("explanation"):
            updates["explanation"] = f"Review this {assigned_pillar.lower()} question carefully."
        
        # 6. Convert options to new format if needed
        old_options = q.get("options", [])
        if old_options and isinstance(old_options[0], str):
            # Convert ["A", "B", "C", "D"] to [{id: "A", text: "A"}, ...]
            new_options = [{"id": chr(65+i), "text": opt} for i, opt in enumerate(old_options)]
            updates["options"] = new_options
            
            # Also update correct_option_id to use the ID format
            correct_answer = q.get("correct_answer", "")
            if correct_answer in old_options:
                idx = old_options.index(correct_answer)
                updates["correct_option_id"] = chr(65 + idx)
            else:
                updates["correct_option_id"] = "A"
        
        # Apply updates
        if updates:
            questions_collection.update_one(
                {"_id": q["_id"]},
                {"$set": updates}
            )
            updated_count += 1
    
    print(f"  - Updated {updated_count} questions")


def verify_migration():
    """Verifies the migration was successful."""
    print("\n" + "="*60)
    print("PHASE 3: VERIFICATION")
    print("="*60)
    
    # Check topics
    subjects = list(topics_collection.find({"type": "SUBJECT"}))
    topics = list(topics_collection.find({"type": "TOPIC"}))
    print(f"  - Subjects: {len(subjects)}")
    print(f"  - Topics: {len(topics)}")
    
    # Check questions with new fields
    questions_with_topic_id = questions_collection.count_documents({"topic_id": {"$exists": True}})
    questions_with_pillar = questions_collection.count_documents({"diagnosis_pillar": {"$exists": True}})
    
    print(f"  - Questions with topic_id: {questions_with_topic_id}")
    print(f"  - Questions with diagnosis_pillar: {questions_with_pillar}")
    
    # Sample pillar distribution
    pipeline = [
        {"$group": {"_id": "$diagnosis_pillar", "count": {"$sum": 1}}}
    ]
    pillar_dist = list(questions_collection.aggregate(pipeline))
    print(f"  - Pillar Distribution:")
    for p in pillar_dist:
        print(f"      - {p['_id']}: {p['count']}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TWO-COLLECTION MIGRATION SCRIPT")
    print("="*60)
    
    seed_topics()
    migrate_questions()
    verify_migration()
    
    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETE!")
    print("="*60 + "\n")
