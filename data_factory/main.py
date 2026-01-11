
"""
main.py - Offline Data Factory Orchestrator V3.1 (Production)

Features:
- MongoDB Atlas Integration (Dynamic Tasks)
- Priority Logic (Manual > Legacy > Auto)
- Playlist Expansion Support
- Robust Error Handling
- Write-Back to MongoDB

Author: Data Engineering Team
"""

import sys
import os
import time
import random
from dotenv import load_dotenv
from pymongo import MongoClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from extractors.youtube import get_video_metadata, get_transcript, extract_videos_from_playlist
from processors.tagger import determine_tags
from processors.chunker import chunk_transcript, enrich_chunks_with_metadata
from database.vector_store import store_video_data, get_collection_stats

# Load Environment Variables from Backend
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

MONGO_URI = os.getenv("MONGODB_URL")
DB_NAME = "major_project"
COLLECTION_NAME = "videos"

# ============================================================================
# MONGODB SETUP
# ============================================================================
try:
    if not MONGO_URI: raise Exception("MONGODB_URL missing")
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    videos_collection = db[COLLECTION_NAME]
    print(f"✅ Connected to MongoDB: {DB_NAME}.{COLLECTION_NAME}")
except Exception as e:
    print(f"❌ DB Connection Failed: {e}")
    videos_collection = None


# ============================================================================
# CORE PROCESSING LOGIC
# ============================================================================

def process_single_video(url: str, mongo_doc: dict = None) -> tuple:
    """
    Process a single video URL.
    Returns: (success, count, difficulty, style, engagement)
    """
    print(f"\n⚡ PROCESSING: {url}")
    
    try:
        # 1. Fetch Metadata
        print("   Step 1: Fetching Metadata...")
        meta = get_video_metadata(url)
        if not meta: raise ValueError("Metadata fetch failed")
        
        # 2. Fetch Transcript
        print("   Step 2: Fetching Transcript...")
        transcript = get_transcript(meta["video_id"])
        if not transcript: raise ValueError("Transcript fetch failed")
        
        # 3. Determine Tags (Priority Logic)
        print("   Step 3: Tagging (Priority Logic)...")
        
        # Extract Full Transcript for Scoring Engine
        transcript_text = " ".join([seg['text'] for seg in transcript])
        
        # Auto Tags (V5 Production Logic)
        auto_tags = determine_tags(
            title=meta["title"], 
            description=meta.get("description", ""),
            duration_seconds=meta["duration"], 
            views=meta.get("views", 0), 
            like_count=meta.get("likes", 0),
            full_transcript=transcript_text
        )
        
        mongo_doc = mongo_doc or {}
        
        # Merge Logic: Manual > Legacy (from old schema) > Auto
        manual_difficulty = mongo_doc.get("manual_difficulty") or mongo_doc.get("difficulty")
        final_difficulty = manual_difficulty or auto_tags["difficulty"]
        
        final_style = mongo_doc.get("manual_style") or auto_tags["style"]
        engagement = auto_tags["engagement"] # Always auto-calculated
        
        # Log decision
        diff_source = "MANUAL" if manual_difficulty else "AUTO"
        style_source = "MANUAL" if mongo_doc.get("manual_style") else "AUTO"
        
        print(f"      - Difficulty: {final_difficulty} ({diff_source})")
        print(f"      - Style: {final_style} ({style_source})")
        print(f"      - Engagement: {engagement}")

        # Topic Handling (Preserve Manual Topic if exists)
        topic_tags = []
        if mongo_doc.get("topic"):
            topic_tags.append(mongo_doc.get("topic"))
        
        # 4. Chunking
        print("   Step 4: Chunking...")
        chunks = chunk_transcript(transcript)
        # Enrich manual tags into chunks
        chunks = enrich_chunks_with_metadata(chunks, meta)
        
        # 5. Store Vector Data
        print("   Step 5: Storing Vectors...")
        count = store_video_data(
            video_meta=meta,
            chunks=chunks,
            difficulty=final_difficulty,
            content_type=final_style,
            topic_tags=topic_tags,
            source=mongo_doc.get("source", "Unknown"),
            quality_tier=engagement,
            granularity=auto_tags.get("granularity", "Specific")  # NEW: From tagger output
        )
        
        print(f"✅ SUCCESS: Saved {count} vectors for '{meta['title']}'")
        return True, count, final_difficulty, final_style, engagement
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        # Import traceback to print full error for debugging
        import traceback
        traceback.print_exc()
        return False, 0, None, None, None


def run_orchestrator():
    """
    Main loop: Polls MongoDB for pending tasks.
    """
    print("\n" + "="*60)
    print("🏭 DATA FACTORY ORCHESTRATOR V3.1 (Write-Back Enabled)")
    print("="*60)
    
    if videos_collection is None: return

    # Find pending or error tasks (Retry logic)
    # We want to process anything that is NOT 'done' and NOT 'processing'
    # Or specifically target 'pending' and 'error'
    query = {"status": {"$in": ["pending", "error"]}}
    pending_tasks = list(videos_collection.find(query).limit(200))
    
    print(f"📋 Found {len(pending_tasks)} pending tasks.")
    
    for task in pending_tasks:
        task_id = task["_id"]
        url = task["url"]
        source_type = task.get("source_type", "video") # 'video' or 'playlist'
        
        # Mark as processing
        videos_collection.update_one({"_id": task_id}, {"$set": {"status": "processing", "started_at": time.time()}})
        
        try:
            if source_type == "playlist":
                # Handle Playlist Expansion
                print(f("\n📂 EXPANDING PLAYLIST: {url}"))
                video_urls = extract_videos_from_playlist(url)
                
                # Insert new video tasks
                new_tasks = []
                for v_url in video_urls:
                    # Check if exists to avoid duplicates
                    if not videos_collection.find_one({"url": v_url}):
                        new_tasks.append({
                            "url": v_url,
                            "status": "pending",
                            "source_type": "video",
                            "source": f"Playlist_{task_id}",
                            "manual_difficulty": task.get("difficulty"), # Inherit legacy difficulty if exists
                            "topic": task.get("topic") # Inherit legacy topic
                        })
                
                if new_tasks:
                    videos_collection.insert_many(new_tasks)
                    print(f"      + Added {len(new_tasks)} videos from playlist.")
                    
                # Mark playlist task as done
                videos_collection.update_one({"_id": task_id}, {"$set": {"status": "done"}})
                
            else:
                # Handle Single Video
                success, count, diff, style, engage = process_single_video(url, task)
                
                if success:
                    # WRITE-BACK: Save calculated metadata to MongoDB
                    videos_collection.update_one({"_id": task_id}, {
                        "$set": {
                            "status": "done",
                            "processed_at": time.time(),
                            "final_difficulty": diff,
                            "final_style": style,
                            "final_engagement": engage, # Saved back to DB!
                            "video_metadata": { # Store full metadata for admin visibility
                                "difficulty": diff,
                                "style": style,
                                "engagement": engage
                            },
                            "vector_count": count
                        }
                    })
                else:
                     videos_collection.update_one({"_id": task_id}, {
                        "$set": {"status": "error", "processing_error": "Pipeline failure"}
                    })
                    
        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERROR: {error_msg}")
            
            # Smart Error Handling: Detect Permanent Failures
            # If video is gone forever, don't retry it.
            if "unavailable" in error_msg.lower() or "private video" in error_msg.lower() or "removed" in error_msg.lower():
                 print("   ↳ Marking as PERMANENTLY UNAVAILABLE")
                 videos_collection.update_one({"_id": task_id}, {
                    "$set": {"status": "unavailable", "error_log": error_msg}
                })
            elif "429" in error_msg:
                 print("   ↳ Rate limit detected! Keeping as error for later retry.")
                 # Maybe sleep deeper?
                 videos_collection.update_one({"_id": task_id}, {
                    "$set": {"status": "error", "error_log": "Rate Limit 429"}
                })
            else:
                 # Generic error, might be transient
                 videos_collection.update_one({"_id": task_id}, {
                    "$set": {"status": "error", "error_log": error_msg}
                })
            
        # -------------------------------------------------------------
        # RATE LIMIT PROTECTION: Much longer sleep to avoid 429 errors
        # YouTube rate limits are aggressive - need 60+ seconds between
        # -------------------------------------------------------------
        sleep_time = random.randint(5, 15)  # 1-2 minutes between videos
        print(f"💤 Sleeping for {sleep_time} seconds to avoid rate limiting...")
        time.sleep(sleep_time)

    # Final Stats
    stats = get_collection_stats()
    print(f"\n📊 Total Database Documents: {stats['total_documents']}")

if __name__ == "__main__":
    run_orchestrator()
