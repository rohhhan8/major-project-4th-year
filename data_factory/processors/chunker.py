"""
processors/chunker.py - Transcript Chunking Module

This module splits long video transcripts into smaller, manageable chunks.
Each chunk represents approximately 5 minutes of content.

Chunking is essential for:
1. Better vector search (smaller, focused text segments)
2. Deep linking to specific parts of videos
3. Matching user queries to relevant video segments

Based on Paper F: Content-Based Filtering with Video Segmentation
"""

from typing import List, Dict, Optional


# ============================================================================
# CHUNKING CONFIGURATION
# ============================================================================

DEFAULT_CHUNK_SIZE_MINUTES = 5
MIN_CHUNK_TEXT_LENGTH = 50  # Minimum characters for a valid chunk


# ============================================================================
# CHUNKING FUNCTIONS
# ============================================================================

def chunk_transcript(
    transcript_list: List[Dict],
    chunk_size_minutes: int = DEFAULT_CHUNK_SIZE_MINUTES
) -> List[Dict]:
    """
    Split a transcript into time-based chunks.
    
    Each chunk represents approximately `chunk_size_minutes` of content.
    Chunks include start/end timestamps for deep linking.
    
    Args:
        transcript_list: List of transcript segments from YouTube API.
            Each segment has: {'text': str, 'start': float, 'duration': float}
        chunk_size_minutes: Target duration per chunk in minutes
        
    Returns:
        List of chunks, each containing:
        - start_time: Start timestamp in seconds
        - end_time: End timestamp in seconds
        - text_content: Combined text for the chunk
        - duration: Chunk duration in seconds
    """
    if not transcript_list:
        return []
    
    chunk_size_seconds = chunk_size_minutes * 60
    chunks = []
    
    current_chunk = {
        "start_time": transcript_list[0]["start"],
        "end_time": 0,
        "text_content": "",
        "segments": []
    }
    
    for segment in transcript_list:
        segment_text = segment["text"].strip()
        segment_start = segment["start"]
        segment_end = segment_start + segment.get("duration", 0)
        
        # Add segment to current chunk
        current_chunk["segments"].append(segment_text)
        current_chunk["end_time"] = segment_end
        
        # Check if chunk duration exceeds target
        chunk_duration = current_chunk["end_time"] - current_chunk["start_time"]
        
        if chunk_duration >= chunk_size_seconds:
            # Finalize current chunk
            current_chunk["text_content"] = " ".join(current_chunk["segments"])
            current_chunk["duration"] = chunk_duration
            del current_chunk["segments"]  # Remove temporary field
            
            # Only add if chunk has meaningful content
            if len(current_chunk["text_content"]) >= MIN_CHUNK_TEXT_LENGTH:
                chunks.append(current_chunk)
            
            # Start new chunk (next segment's start will be used)
            current_chunk = {
                "start_time": segment_end,
                "end_time": segment_end,
                "text_content": "",
                "segments": []
            }
    
    # Handle remaining segments
    if current_chunk["segments"]:
        current_chunk["text_content"] = " ".join(current_chunk["segments"])
        current_chunk["duration"] = current_chunk["end_time"] - current_chunk["start_time"]
        del current_chunk["segments"]
        
        if len(current_chunk["text_content"]) >= MIN_CHUNK_TEXT_LENGTH:
            chunks.append(current_chunk)
    
    return chunks


def chunk_transcript_by_sentences(
    transcript_list: List[Dict],
    sentences_per_chunk: int = 10
) -> List[Dict]:
    """
    Alternative chunking: Split by approximate sentence count.
    
    Useful when you want consistent text sizes rather than time-based splits.
    
    Args:
        transcript_list: YouTube transcript segments
        sentences_per_chunk: Target sentences per chunk
        
    Returns:
        List of chunks with text content and timestamps
    """
    if not transcript_list:
        return []
    
    # Combine all text
    full_text = " ".join([s["text"] for s in transcript_list])
    
    # Simple sentence splitting
    import re
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk_sentences = sentences[i:i + sentences_per_chunk]
        chunk_text = " ".join(chunk_sentences)
        
        if len(chunk_text) >= MIN_CHUNK_TEXT_LENGTH:
            # Estimate timestamps (rough approximation)
            progress = i / len(sentences)
            total_duration = transcript_list[-1]["start"] + transcript_list[-1].get("duration", 0)
            
            chunks.append({
                "start_time": progress * total_duration,
                "end_time": min((i + sentences_per_chunk) / len(sentences) * total_duration, total_duration),
                "text_content": chunk_text,
                "sentence_count": len(chunk_sentences)
            })
    
    return chunks


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to human-readable timestamp format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted string like "5:30" or "1:23:45"
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def get_youtube_timestamp_link(base_url: str, start_seconds: float) -> str:
    """
    Generate a YouTube link that starts at a specific timestamp.
    
    Args:
        base_url: Original YouTube video URL
        start_seconds: Start time in seconds
        
    Returns:
        URL with timestamp parameter (e.g., ?t=120)
    """
    start_int = int(start_seconds)
    
    # Handle different URL formats
    if "?" in base_url:
        return f"{base_url}&t={start_int}"
    else:
        return f"{base_url}?t={start_int}"


def get_chunk_summary(chunk: Dict) -> str:
    """
    Generate a brief summary/preview of a chunk.
    
    Useful for displaying search results.
    
    Args:
        chunk: Chunk dictionary with text_content
        
    Returns:
        First ~200 characters of the chunk
    """
    text = chunk.get("text_content", "")
    
    if len(text) <= 200:
        return text
    
    # Truncate at word boundary
    truncated = text[:200]
    last_space = truncated.rfind(" ")
    
    if last_space > 150:
        truncated = truncated[:last_space]
    
    return truncated + "..."


# ============================================================================
# CHUNK ENRICHMENT
# ============================================================================

def enrich_chunks_with_metadata(
    chunks: List[Dict],
    video_meta: Dict
) -> List[Dict]:
    """
    Add video metadata to each chunk for complete context.
    
    Args:
        chunks: List of transcript chunks
        video_meta: Video metadata dictionary
        
    Returns:
        Chunks with added metadata fields
    """
    enriched = []
    
    for i, chunk in enumerate(chunks):
        enriched_chunk = {
            **chunk,
            "video_id": video_meta.get("video_id"),
            "video_title": video_meta.get("title"),
            "youtube_link": get_youtube_timestamp_link(
                video_meta.get("youtube_link", ""),
                chunk["start_time"]
            ),
            "chunk_index": i,
            "total_chunks": len(chunks),
            "timestamp_display": format_timestamp(chunk["start_time"]),
            "channel": video_meta.get("channel")
        }
        enriched.append(enriched_chunk)
    
    return enriched
