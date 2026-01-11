"""
seed_topics.py - Migration Script for Smart AI Hierarchy

This script populates the 'topics' collection with the new hierarchical structure.
It defines the relationship between Subjects, Modules, and Topics.

Usage: python backend/migrations/seed_topics.py
"""

import sys
import os

# Add parent directory to path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import topics_collection, is_db_connected

def seed_hierarchy():
    if not is_db_connected():
        print("Error: Could not connect to MongoDB.")
        return

    print("Checking for existing topics...")
    if topics_collection.count_documents({}) > 0:
        print("Topics already exist. Clearing collection to re-seed...")
        topics_collection.delete_many({})

    print("Seeding Topic Hierarchy...")

    # 1. ROOT SUBJECT
    root = {
        "_id": "dsa-root",
        "name": "Data Structures & Algorithms",
        "level": "Subject",
        "parent_id": None
    }
    topics_collection.insert_one(root)
    print(f"Created Root: {root['name']}")

    # 2. MODULES (Children of Root)
    modules = [
        {"_id": "mod-linear", "name": "Linear Data Structures", "level": "Module", "parent_id": "dsa-root"},
        {"_id": "mod-nonlinear", "name": "Non-Linear Data Structures", "level": "Module", "parent_id": "dsa-root"},
        {"_id": "mod-algos", "name": "Algorithms", "level": "Module", "parent_id": "dsa-root"}
    ]
    topics_collection.insert_many(modules)
    print(f"Created {len(modules)} Modules")

    # 3. TOPICS (Grandchildren - Where Quizzes Live)
    topics = [
        # Linear DS
        {"_id": "topic-arrays", "name": "Arrays", "level": "Topic", "parent_id": "mod-linear"},
        {"_id": "topic-linkedlists", "name": "Linked Lists", "level": "Topic", "parent_id": "mod-linear"},
        {"_id": "topic-stacks", "name": "Stack", "level": "Topic", "parent_id": "mod-linear"}, # "Stack" matches Question Tag
        {"_id": "topic-queues", "name": "Queue", "level": "Topic", "parent_id": "mod-linear"},
        
        # Non-Linear DS
        {"_id": "topic-trees", "name": "Trees", "level": "Topic", "parent_id": "mod-nonlinear"},
        {"_id": "topic-graphs", "name": "Graphs", "level": "Topic", "parent_id": "mod-nonlinear"},
        {"_id": "topic-heaps", "name": "Heaps", "level": "Topic", "parent_id": "mod-nonlinear"},

        # Algorithms
        {"_id": "topic-sorting", "name": "Sorting", "level": "Topic", "parent_id": "mod-algos"},
        {"_id": "topic-searching", "name": "Searching", "level": "Topic", "parent_id": "mod-algos"},
        {"_id": "topic-dp", "name": "Dynamic Programming", "level": "Topic", "parent_id": "mod-algos"}
    ]
    topics_collection.insert_many(topics)
    print(f"Created {len(topics)} Topics")

    print("\n✅ Migration Complete: Hierarchy Seeded Successfully.")

if __name__ == "__main__":
    seed_hierarchy()
