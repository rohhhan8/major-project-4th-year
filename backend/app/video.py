# backend/app/video.py
import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from googleapiclient.discovery import build
from dotenv import load_dotenv
from .search_engine import get_video_transcript

load_dotenv()

router = APIRouter()

# --- API Configuration ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Third-Party APIs
try:
    genai.configure(api_key=GEMINI_API_KEY)
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-flash')
except Exception as e:
    print(f"Error initializing APIs: {e}")
    # Set to None to handle gracefully in endpoints
    youtube = None
    gemini_model = None

# --- Core Functions & API Endpoints ---
@router.get("/search")
async def search_videos(query: str):
    """
    Searches YouTube for videos based on a search query.
    Returns a list of videos with IDs, titles, and thumbnails.
    """
    if not youtube:
        raise HTTPException(status_code=500, detail="YouTube API not configured.")
    
    try:
        request = youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=9
        )
        response = request.execute()
        
        videos = []
        for item in response.get("items", []):
            videos.append({
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
            })
        return {"videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching YouTube: {e}")


@router.get("/transcript/{video_id}")
async def get_transcript(video_id: str):
    """
    Retrieves the stored transcript for a video from ChromaDB.
    Used by the video player page to display transcript alongside the video.
    """
    print(f"[Video API] 📜 GET /video/transcript/{video_id}")
    
    try:
        transcript = get_video_transcript(video_id)
        
        if not transcript:
            return {"transcript": "Transcript not available for this video.", "available": False}
        
        return {"transcript": transcript, "available": True, "length": len(transcript)}
        
    except Exception as e:
        print(f"[Video API] ❌ Error getting transcript: {e}")
        return {"transcript": "Error loading transcript.", "available": False}


@router.get("/notes")
async def get_notes(video_id: str, title: str):
    """
    Generates study notes for a specific video using the Gemini AI model.
    Uses the video title to prompt the AI for key concepts and learning points.
    """
    if not gemini_model:
        raise HTTPException(status_code=500, detail="Gemini API not configured.")
    
    try:
        prompt = f"Generate concise, helpful notes for a video titled '{title}'. Focus on the key concepts and learning points someone watching this video would need to know."
        response = gemini_model.generate_content(prompt)
        return {"notes": response.text}
    except Exception as gemini_e:
        raise HTTPException(status_code=500, detail=f"Gemini failed to generate notes: {gemini_e}")

