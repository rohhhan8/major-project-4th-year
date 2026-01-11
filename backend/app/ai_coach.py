"""
ai_coach.py - Gemini-Powered Learning Assistant

This module integrates Google's Gemini API to provide "Smart Diagnosis" and "Coaching".
It acts as the voice of the Smart Study Buddy.

Functions:
- generate_coaching_feedback: Generates personalized text advice.
- generate_smart_search_query: Generates an optimized search string for video retrieval.
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("[AI Coach] ✅ Gemini API configured successfully!")
else:
    print("[AI Coach] ⚠️ WARNING: GEMINI_API_KEY not found. AI Coach will use fallback mode.")
    model = None

def generate_coaching_feedback(learner_profile, weak_tags, topic, score):
    """
    Uses Gemini to generate a short, encouraging, and specific coaching tip.
    """
    print(f"\n{'='*60}")
    print(f"[AI Coach] 🧠 GENERATING FEEDBACK")
    print(f"  - Profile: {learner_profile}")
    print(f"  - Weak Tags: {weak_tags}")
    print(f"  - Topic: {topic}, Score: {score}%")
    
    if not model:
        fallback = "Great job taking the quiz! Keep focusing on your weak areas."
        print(f"  - Using FALLBACK (no API key): {fallback}")
        return fallback

    prompt = f"""
    Act as a friendly, expert coding tutor.
    User Context:
    - Topic: {topic}
    - Score: {score}%
    - Weakest Pillars: {', '.join(weak_tags) if weak_tags else 'None identified'}

    Task:
    Write a VERY CONCISE, actionable coaching tip (1-2 sentences MAX).
    - Be direct and encouraging.
    - Specific advice based on the weakest pillar:
      * Concept: "Visualize the core idea."
      * Implementation: "Practice syntax in an IDE."
      * Complexity: "Review Big-O analysis."
      * Debugging: "Trace code step-by-step."
      * Application: "Connect to real-world examples."
    
    Output example: "You have the logic down, but syntax is tripping you up. Spend 10 mins coding plain functions to build muscle memory."
    """
    
    try:
        response = model.generate_content(prompt)
        feedback = response.text.strip()
        print(f"  - ✅ Gemini Response: {feedback}")
        print(f"{'='*60}\n")
        return feedback
    except Exception as e:
        print(f"  - ❌ Error: {e}")
        return "Keep practicing! Consistency is key to mastering these concepts."

def generate_smart_search_query(learner_profile, topic, weak_tags):
    """
    Uses Gemini to create a highly optimized YouTube search query string.
    Maps 5-Pillar Weaknesses to specific video styles.
    """
    print(f"\n{'='*60}")
    print(f"[AI Coach] 🔍 GENERATING SMART SEARCH QUERY")
    print(f"  - Profile: {learner_profile}")
    print(f"  - Topic: {topic}")
    print(f"  - Weak Tags: {weak_tags}")
    
    if not model:
        fallback = f"{topic} tutorial {learner_profile}"
        print(f"  - Using FALLBACK: {fallback}")
        return fallback

    # Style Mapping based on Pillar
    style_preference = ""
    if "Concept" in weak_tags: style_preference = "Whiteboard animation logic visualization"
    elif "Implementation" in weak_tags: style_preference = "Live coding implementation tutorial python java"
    elif "Complexity" in weak_tags: style_preference = "Big-O time complexity analysis optimization"
    elif "Debugging" in weak_tags: style_preference = "Common mistakes debugging guide fix errors"
    elif "Application" in weak_tags: style_preference = "Real world application system design interview question"
    
    print(f"  - Style Preference: {style_preference or 'General'}")

    prompt = f"""
    Act as a Search Engine Optimization expert for Educational Videos.
    
    Context:
    - Topic: {topic}
    - User Profile: {learner_profile}
    - Weak Pillars: {', '.join(weak_tags) if weak_tags else 'General'}
    - Recommended Video Style: {style_preference or 'General tutorial'}

    Task:
    Generate a SINGLE, optimized YouTube search query string to find the perfect video.
    The query must be suitable for Vector Search embedding (keyword rich, semantic).
    
    Rules:
    - Combine the Topic + Style + Profile.
    - RETURN ONLY THE QUERY STRING. NO QUOTES.
    
    Example Output: "Stack data structure whiteboard animation logic visualization"
    """
    
    try:
        response = model.generate_content(prompt)
        query = response.text.strip().replace('"', '')
        print(f"  - ✅ Smart Query Generated: {query}")
        print(f"{'='*60}\n")
        return query
    except Exception as e:
        print(f"  - ❌ Error: {e}")
        # Fallback using style preference if AI fails
        return f"{topic} {style_preference}" if style_preference else f"{topic} tutorial"

def generate_study_notes(topic: str, video_title: str, transcript: str = None):
    """
    Generates comprehensive study notes using RAG + LLM.
    
    If transcript is provided (from ChromaDB), generates notes grounded in actual content.
    Otherwise, falls back to topic-based generation.
    
    Args:
        topic: The learning topic (e.g., "Binary Search")
        video_title: The video title for context
        transcript: Optional - The actual video transcript from ChromaDB
    
    Returns: 
        Markdown formatted string.
    """
    print(f"\n{'='*60}")
    print(f"[AI Coach] 📝 GENERATING NOTES")
    print(f"  - Topic: {topic}")
    print(f"  - Video: {video_title}")
    print(f"  - RAG Mode: {'ENABLED' if transcript else 'DISABLED (fallback)'}")
    
    if not model:
        return "# Error\nAI Coach not configured."

    # Build the prompt based on whether we have transcript context
    if transcript:
        # RAG-ENABLED: Ground notes in actual video content
        # With 30k token model, we can handle ~40000 chars (~10k words)
        max_transcript_chars = 40000
        truncated_transcript = transcript[:max_transcript_chars]
        if len(transcript) > max_transcript_chars:
            truncated_transcript += "\n\n[... transcript truncated for context limit ...]"
        
        prompt = f"""You are an expert note-taker converting a video lecture into detailed written notes.

=== VIDEO TRANSCRIPT ===
{truncated_transcript}
=== END TRANSCRIPT ===

Topic: {topic}
Video Title: {video_title}

TASK: Convert this transcript into well-structured study notes focusing ONLY on the educational content.

CRITICAL RULES:
1. SKIP ALL YOUTUBE INTRO FLUFF:
   - Skip greetings like "Hey guys", "Welcome back", "What's up everyone"
   - Skip channel promotions, subscribe reminders, sponsor mentions
   - Skip "today's agenda", "in this video we will cover"
   - Skip any personal stories or off-topic chat
   - START DIRECTLY from where the actual LEARNING content begins

2. Focus ONLY on educational material:
   - Concepts and explanations
   - Code examples and implementations
   - Technical definitions
   - Step-by-step tutorials
   - Problem-solving approaches

3. Use proper Markdown:
   - Use `##` for main topics, `###` for subtopics
   - Use `-` for bullet points (NOT *)
   - Use proper code blocks with language tags

4. Write comprehensive, detailed notes - capture all the technical content.

BEGIN YOUR NOTES (start directly with the first concept/topic):

# {topic}

"""
    else:
        # FALLBACK: Generate from topic name only
        prompt = f"""You are an expert note-taker creating comprehensive study notes.

Topic: {topic}
Video Title: {video_title}

TASK: Create detailed study notes on this topic following a natural, logical structure.

RULES:
1. Structure based on what makes sense for the topic - intro, main concepts, examples, etc.
2. Do NOT use a rigid template like "Key Concepts / Code / Application / Summary"
3. Use proper Markdown:
   - Use `##` for main sections, `###` for subsections
   - Use `-` for bullet points (NOT *)
   - Use proper code blocks with language tags
4. Include code examples where relevant.
5. Write in clean, readable prose. Use bullets for lists.
6. Organize logically - if the topic needs an introduction, add one. If it needs examples, add them.

BEGIN YOUR NOTES:

# {topic} - Study Notes

"""
    
    try:
        response = model.generate_content(prompt)
        notes = response.text
        print(f"  - ✅ Notes Generated ({len(notes)} chars)")
        print(f"{'='*60}\n")
        return notes
    except Exception as e:
        print(f"  - ❌ Error generating notes: {e}")
        return f"# Error\nFailed to generate notes: {str(e)}"
