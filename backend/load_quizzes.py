# backend/load_quizzes.py
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_DETAILS", "mongodb://localhost:27017")
DB_NAME = "adaptive_learning"
COLLECTION_NAME = "quizzes"

def load_quizzes_to_db():
    """Connects to MongoDB and loads quizzes from the JSON file."""
    try:
        client = MongoClient(MONGO_DETAILS)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # Construct the absolute path to the JSON file
        script_dir = os.path.dirname(__file__)  #<-- absolute dir the script is in
        abs_file_path = os.path.join(script_dir, 'quizzes.json')

        # Load the quiz data from the JSON file
        with open(abs_file_path, 'r') as f:
            quizzes_data = json.load(f)

        print("Starting to load quizzes into the database...")

        for quiz in quizzes_data:
            # Check if a quiz with the same topic already exists
            if collection.find_one({"topic": quiz["topic"]}):
                print(f"Quiz with topic '{quiz['topic']}' already exists. Skipping.")
            else:
                # Insert the new quiz
                collection.insert_one(quiz)
                print(f"Successfully inserted quiz with topic: '{quiz['topic']}'")

        print("Finished loading quizzes.")

    except FileNotFoundError:
        print("Error: quizzes.json not found. Make sure the file is in the 'backend' directory.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("Database connection closed.")

if __name__ == "__main__":
    load_quizzes_to_db()
