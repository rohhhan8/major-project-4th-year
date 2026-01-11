# backend/app/note_generation_service.py
"""
NoteGenerationService - Robust Long-Video Notes Generator

Architecture: Chunking & Stitching (Divide and Conquer)
- Input: Full video transcript (potentially hours long)
- Chunking: Split into ~25,000 char overlapping segments
- Loop: Send each chunk to Gemini with verbose prompt
- Stitching: Append all outputs into master markdown

Author: AI Engineering Team
"""

import time
import google.generativeai as genai
from typing import List, Tuple, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("[NoteGenerationService] ✅ Gemini configured")
else:
    model = None
    print("[NoteGenerationService] ⚠️ GEMINI_API_KEY not found")


class NoteGenerationService:
    """
    Generates comprehensive academic notes from long video transcripts
    using a Divide-and-Conquer chunking strategy.
    """
    
    # Configuration
    CHUNK_SIZE = 25000  # ~15 minutes of video content
    CHUNK_OVERLAP = 500  # Overlap to maintain context continuity
    RATE_LIMIT_DELAY = 1.5  # Seconds between API calls
    
    def __init__(self, topic: str, video_title: str):
        self.topic = topic
        self.video_title = video_title
        self.chunks: List[str] = []
        self.master_notes: str = ""
        self.failed_chunks: List[int] = []
        
    def chunk_transcript(self, transcript: str) -> List[str]:
        """
        Split transcript into overlapping chunks of ~25,000 characters.
        
        Why overlapping? To prevent cutting off mid-sentence/concept.
        """
        chunks = []
        start = 0
        transcript_length = len(transcript)
        
        while start < transcript_length:
            end = start + self.CHUNK_SIZE
            
            # Find a good break point (end of sentence) if possible
            if end < transcript_length:
                # Look for sentence ending within last 500 chars of chunk
                break_point = transcript.rfind('. ', end - 500, end)
                if break_point != -1:
                    end = break_point + 1
            
            chunk = transcript[start:end]
            chunks.append(chunk.strip())
            
            # Move start with overlap
            start = end - self.CHUNK_OVERLAP
        
        self.chunks = chunks
        print(f"[NoteGenerationService] 📦 Split transcript into {len(chunks)} chunks")
        return chunks
    
    def _build_chunk_prompt(self, chunk_text: str, chunk_index: int, total_chunks: int) -> str:
        """
        Build prompt for college-level study notes from transcript.
        """
        return f"""You are a senior Computer Science student creating STUDY NOTES from a lecture recording.

=== LECTURE TRANSCRIPT (Part {chunk_index + 1}/{total_chunks}) ===
{chunk_text}
=== END TRANSCRIPT ===

YOUR TASK: Transform this lecture transcript into PROPER STUDY NOTES that a student would use to revise.

FORMAT RULES:
1. For each topic/concept mentioned, write:
   - **Topic Name** as a heading (## or ###)
   - A clear 1-2 sentence DEFINITION/EXPLANATION
   - Key points as bullets

2. If code is discussed:
   - Write the actual code in a proper code block
   - Add a brief explanation of what it does

3. If examples are given:
   - Include them with clear context

4. DO NOT:
   - Copy transcript word-for-word
   - Include filler words, "um", "like", YouTuber commentary
   - Write long paragraphs - use bullets for clarity

5. WRITE LIKE COLLEGE NOTES:
   - Clean, organized, easy to scan
   - Definitions should be concise and accurate
   - Each concept should be understandable on its own

EXAMPLE FORMAT:
## Arrays
A data structure that stores elements of the same type in contiguous memory locations.

- Fixed size (declared at creation)
- O(1) access time using index
- Memory efficient for sequential data

```python
arr = [1, 2, 3, 4, 5]
print(arr[0])  # Output: 1
```

NOW WRITE YOUR NOTES:"""

    def _generate_chunk_notes(self, chunk_text: str, chunk_index: int, total_chunks: int) -> Optional[str]:
        """
        Send a single chunk to Gemini and get detailed notes.
        Includes error handling and rate limiting.
        """
        if not model:
            return f"<!-- Error: Gemini not configured for chunk {chunk_index + 1} -->"
        
        prompt = self._build_chunk_prompt(chunk_text, chunk_index, total_chunks)
        
        try:
            response = model.generate_content(prompt)
            notes = response.text
            print(f"  ✅ Chunk {chunk_index + 1}/{total_chunks}: Generated {len(notes)} chars")
            return notes
            
        except Exception as e:
            error_msg = f"<!-- Error processing chunk {chunk_index + 1}: {str(e)} -->"
            print(f"  ❌ Chunk {chunk_index + 1}/{total_chunks}: FAILED - {str(e)}")
            self.failed_chunks.append(chunk_index + 1)
            return error_msg
    
    def generate_full_notes(self, transcript: str) -> Tuple[str, dict]:
        """
        Main entry point: Generate complete notes from full transcript.
        
        Returns:
            Tuple of (master_notes_markdown, metadata_dict)
        """
        print(f"\n{'='*60}")
        print(f"[NoteGenerationService] 📝 STARTING FULL NOTES GENERATION")
        print(f"  - Topic: {self.topic}")
        print(f"  - Transcript Length: {len(transcript)} chars")
        
        # Step 1: Chunk the transcript
        chunks = self.chunk_transcript(transcript)
        total_chunks = len(chunks)
        
        if total_chunks == 0:
            return "# Error\nNo transcript content provided.", {"error": "empty_transcript"}
        
        # Start with clean notes (no metadata header)
        self.master_notes = ""
        
        # Step 3: Loop through chunks with rate limiting
        print(f"\n[NoteGenerationService] 🔄 Processing {total_chunks} chunks...")
        
        for i, chunk in enumerate(chunks):
            # Generate notes for this chunk
            chunk_notes = self._generate_chunk_notes(chunk, i, total_chunks)
            
            # Append notes directly (no section dividers for cleaner output)
            if chunk_notes and "[No educational content" not in chunk_notes:
                self.master_notes += chunk_notes + "\n\n"
            
            # Rate limiting (skip on last chunk)
            if i < total_chunks - 1:
                time.sleep(self.RATE_LIMIT_DELAY)
        
        print(f"\n[NoteGenerationService] ✅ COMPLETE")
        print(f"  - Total Output: {len(self.master_notes)} chars")
        print(f"  - Failed Chunks: {len(self.failed_chunks)}")
        print(f"{'='*60}\n")
        
        # Return notes and metadata
        metadata = {
            "total_chunks": total_chunks,
            "failed_chunks": self.failed_chunks,
            "output_length": len(self.master_notes),
            "input_length": len(transcript)
        }
        
        return self.master_notes, metadata


# Convenience function for API usage
def generate_comprehensive_notes(topic: str, video_title: str, transcript: str) -> Tuple[str, dict]:
    """
    Convenience wrapper for the NoteGenerationService.
    """
    service = NoteGenerationService(topic, video_title)
    return service.generate_full_notes(transcript)
