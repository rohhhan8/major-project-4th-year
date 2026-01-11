"""
extractors/youtube.py - YouTube Data Extraction Module

This module handles all YouTube-related data extraction:
- Fetching video metadata (title, duration, thumbnail)
- Downloading transcripts with timestamps

Uses yt-dlp for BOTH metadata and transcripts (most reliable method).
"""

import yt_dlp
import requests
import re
import os
import time
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET

# ============================================================================
# YT-DLP CONFIGURATION
# ============================================================================

# MANUAL COOKIE STRATEGY
# Since automated methods are failing, we use a manually exported cookie file.
# The user must export cookies to 'data_factory/cookies.txt'

COOKIE_FILE = os.path.join(os.path.dirname(__file__), "..", "cookies.txt")


def load_cookies_for_requests() -> dict:
    """
    Load cookies from Netscape format cookie file for use with requests library.
    Returns a dict suitable for requests.get(cookies=...)
    """
    cookies = {}
    try:
        if os.path.exists(COOKIE_FILE):
            with open(COOKIE_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        # Netscape format: domain, flag, path, secure, expiration, name, value
                        name = parts[5]
                        value = parts[6]
                        cookies[name] = value
    except Exception as e:
        print(f"⚠️ Could not load cookies: {e}")
    return cookies


# Mimic a real Chrome browser on Windows
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
}

YDL_OPTS_META = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'skip_download': True,
    'cookiefile': COOKIE_FILE,
    'sleep_interval': 15,          # Increased for safety
    'http_headers': HEADERS,       # Send real browser headers
    'force_ipv4': True,            # IPv6 ranges are often blocked
}

YDL_OPTS_TRANSCRIPT = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['en'],
    'subtitlesformat': 'json3',
    'cookiefile': COOKIE_FILE,
    'sleep_interval': 15,
    'http_headers': HEADERS,
    'force_ipv4': True,
}


# ============================================================================
# VIDEO ID EXTRACTION
# ============================================================================

def extract_video_id(url: str) -> Optional[str]:
    """
    Extract the video ID from various YouTube URL formats.
    """
    patterns = [
        r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be/)([0-9A-Za-z_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    # If standard extraction fails, try using yt-dlp info
    # (Only if the input is a full URL not just an ID)
    if "http" in url:
        return None
        
    return url if len(url) == 11 else None


# ============================================================================
# METADATA EXTRACTION
# ============================================================================

def get_video_metadata(video_url: str) -> Optional[Dict]:
    """
    Fetch metadata for a YouTube video using yt-dlp.
    """
    try:
        with yt_dlp.YoutubeDL(YDL_OPTS_META) as ydl:
            # Extract video info without downloading
            info = ydl.extract_info(video_url, download=False)
            
            if info is None:
                print(f"⚠️ Could not extract info for {video_url}")
                return None
            
            video_id = info.get('id', '')
            
            metadata = {
                "video_id": video_id,
                "title": info.get('title', 'Unknown Title'),
                "duration": info.get('duration', 0),
                "thumbnail_url": info.get('thumbnail', ''),
                "channel": info.get('uploader', info.get('channel', 'Unknown')),
                "youtube_link": f"https://www.youtube.com/watch?v={video_id}",
                "views": info.get('view_count', 0),
                "publish_date": info.get('upload_date', None),
                "description": info.get('description', '')[:500]
            }
            
            return metadata
        
    except Exception as e:
        print(f"⚠️ Error fetching metadata for {video_url}: {e}")
        return None


# ============================================================================
# TRANSCRIPT EXTRACTION (Via yt-dlp)
# ============================================================================

def parse_json3_transcript(json3_data: dict) -> List[Dict]:
    """
    Parse generic JSON3 format from YouTube.
    """
    segments = []
    
    events = json3_data.get('events', [])
    for event in events:
        # Some events are just metadata/positioning
        if 'segs' not in event:
            continue
            
        start_ms = event.get('tStartMs', 0)
        duration_ms = event.get('dDurationMs', 0)
        
        text_parts = []
        for seg in event['segs']:
            if 'utf8' in seg:
                text_parts.append(seg['utf8'])
        
        text = "".join(text_parts).strip()
        
        # Skip empty segments or newlines
        if not text or text == "\n":
            continue
            
        segments.append({
            'text': text,
            'start': start_ms / 1000.0,
            'duration': duration_ms / 1000.0
        })
        
    return segments

def get_transcript(video_id: str) -> Optional[List[Dict]]:
    """
    Fetch transcript using yt-dlp with cookies (STRICT).
    
    No retries - if it fails, move to next video immediately.
    Uses yt-dlp's direct subtitle download with cookies.
    """
    import tempfile
    import json
    import glob
    import shutil
    
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    temp_dir = None
    
    try:
        # Verify cookies file exists
        if not os.path.exists(COOKIE_FILE):
            print(f"⚠️ CRITICAL: cookies.txt not found at {COOKIE_FILE}")
            return None
        
        # Create temp directory for subtitle download
        temp_dir = tempfile.mkdtemp(prefix="yt_transcript_")
        output_template = os.path.join(temp_dir, "%(id)s")
        
        # Configure yt-dlp to download subtitles to temp directory
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'en-US', 'en-GB'],
            'subtitlesformat': 'json3',
            'cookiefile': COOKIE_FILE,
            'http_headers': HEADERS,
            'force_ipv4': True,
            'outtmpl': output_template,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            
            if not info:
                print(f"⚠️ Could not extract video info for {video_id}")
                return None
        
        # Find the downloaded subtitle file
        subtitle_files = glob.glob(os.path.join(temp_dir, "*.json3"))
        if not subtitle_files:
            subtitle_files = glob.glob(os.path.join(temp_dir, "*.json*"))
        
        if not subtitle_files:
            print(f"⚠️ No subtitle file downloaded for {video_id}")
            return None
        
        # Read and parse the subtitle file
        with open(subtitle_files[0], 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        segments = parse_json3_transcript(json_data)
        
        if segments:
            print(f"   ✅ Transcript fetched: {len(segments)} segments")
            return segments
        
        return None
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if "429" in error_msg:
            print(f"⚠️ Rate limited (429) - skipping {video_id}")
        elif "video unavailable" in error_msg or "private" in error_msg:
            print(f"⚠️ Video unavailable: {video_id}")
        elif "sign in" in error_msg:
            print(f"⚠️ Needs auth - update cookies.txt")
        else:
            print(f"⚠️ yt-dlp error: {e}")
        return None
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None
        
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


def get_full_transcript_text(video_id: str) -> Optional[str]:
    """
    Get the full transcript as a single string.
    """
    transcript = get_transcript(video_id)
    if transcript is None:
        return None
    
    return " ".join([segment['text'] for segment in transcript])


# ============================================================================
# PLAYLIST EXTRACTION
# ============================================================================

def extract_videos_from_playlist(playlist_url: str) -> List[str]:
    """
    Extract all video URLs from a YouTube playlist using yt-dlp.
    
    Args:
        playlist_url: YouTube playlist URL
        
    Returns:
        List of unique video URLs
    """
    playlist_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'ignoreerrors': True,
    }
    
    try:
        print(f"📋 Extracting videos from playlist: {playlist_url}...")
        with yt_dlp.YoutubeDL(playlist_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            
            if not info:
                print("⚠️ Playlist extraction failed or empty.")
                return []
            
            entries = info.get('entries', [])
            video_urls = []
            
            for entry in entries:
                if entry and entry.get('id'):
                    video_urls.append(f"https://www.youtube.com/watch?v={entry['id']}")
            
            # Remove duplicates
            unique_urls = list(set(video_urls))
            print(f"✅ Found {len(unique_urls)} unique videos in playlist.")
            return unique_urls
            
    except Exception as e:
        print(f"⚠️ Error extracting playlist: {e}")
        return []
