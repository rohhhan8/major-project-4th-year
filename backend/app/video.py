# backend/app/video.py
import os
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# --- API Configuration ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error initializing APIs: {e}")
    # Handle the error appropriately, maybe raise an exception or set a flag
    youtube = None
    gemini_model = None

# --- Core Functions & API Endpoints ---
@router.get("/search")
async def search_videos(query: str):
    """Searches YouTube for videos based on a query."""
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

@router.get("/notes")
async def get_notes(video_id: str, title: str):
    """Generates notes for a video, trying transcript first, then Gemini."""
    if not gemini_model:
        raise HTTPException(status_code=500, detail="Gemini API not configured.")
    try:
        # 1. Try to get the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        transcript = " ".join([item['text'] for item in transcript_list])
        prompt = f"Summarize the following transcript from the video '{title}' into concise, helpful notes:\n\n{transcript}"
        response = gemini_model.generate_content(prompt)
        return {"notes": response.text}

    except Exception as e:
        print(f"Transcript not available for {video_id}. Using title-based generation. Error: {e}")
        # 2. If transcript fails, use Gemini with the video title
        try:
            prompt = f"Generate concise, helpful notes for a video titled '{title}'. Focus on the key concepts and learning points someone watching this video would need to know."
            response = gemini_model.generate_content(prompt)
            return {"notes": response.text}
        except Exception as gemini_e:
            raise HTTPException(status_code=500, detail=f"Gemini failed to generate notes: {gemini_e}")
