"""
processors/tagger.py - Human-Level Smart Tagging Module V5 (Final Production)

Features:
- Frequency-Based Scoring Engine (Title vs Intro vs Body)
- Full Transcript Analysis
- Robust "Style" Detection logic
- Existing Diff/Usage logic preserved
"""

from typing import Dict, List

# ============================================================================
# KEYWORDS & CONFIG
# ============================================================================

# Comprehensive Keyword Dictionary
KEYWORDS = {
    "One_Shot": ["crash course", "in one video", "summary of", "cheat sheet", "entire topic", "fast track", "recap", "one shot"],
    "Course": ["full course", "zero to hero", "curriculum", "bootcamp", "complete series", "all lectures", "from scratch", "playlist covers"],
    "Practical": ["code", "implementation", "hands-on", "build", "project", "demo", "typing", "function", "terminal", "tutorial"],
    "Interview_Prep": ["leetcode", "solution", "problem", "complexity", "google", "amazon", "interview", "approach", "optimizing"],
    "Conceptual": ["theory", "concept", "under the hood", "architecture", "diagram", "whiteboard", "why it works", "visualize"],
    "Advice": ["roadmap", "mistakes", "salary", "jobs", "resume", "career", "guide to", "resources"]
}

DIFFICULTY_KEYWORDS = {
    "Beginner": ["intro", "introduction", "basic", "basics", "beginner", "beginners", "what is", "101", "getting started", "foundation"],
    "Advanced": ["advanced", "internal", "architecture", "under the hood", "optimization", "system design", "master", "expert", "complex", "low level", "scaling"]
}

# ============================================================================
# LOGIC FUNCTIONS
# ============================================================================

def determine_style_with_scoring(title: str, full_transcript: str, duration: int) -> tuple:
    """
    Determine Style using a Weighted Scoring System.
    Returns: (Style, Granularity)
    """
    # Initialize scores
    scores = {k: 0 for k in KEYWORDS}
    
    title_lower = title.lower()
    transcript_lower = full_transcript.lower()
    intro_lower = transcript_lower[:500] # First 500 chars
    
    # 1. Title Matches (+10 Points) - High Confidence
    for style, words in KEYWORDS.items():
        for w in words:
            if w in title_lower:
                scores[style] += 10
                
    # 2. Intro Matches (+5 Points) - Speaker Intent
    for style, words in KEYWORDS.items():
        for w in words:
            if w in intro_lower:
                scores[style] += 5
                
    # 3. Body Matches (+1 Point) - Content Frequency
    # We limit this to avoid performace hit on huge strings, or just count
    for style, words in KEYWORDS.items():
        for w in words:
            # Count occurrences in the full text
            count = transcript_lower.count(w)
            scores[style] += count * 1

    # Find the winner
    best_style = max(scores, key=scores.get)
    max_score = scores[best_style]
    
    # Debug print could go here, but we return values
    
    # Fallback if no clear winner (Score 0)
    if max_score == 0:
        if duration < 300: return "Quick_Summary", "Specific"
        if duration > 3600: return "Course", "Broad"
        return "Conceptual", "Specific" # Default
        
    # Granularity mapping based on Style
    granularity = "Specific"
    if best_style in ["Course", "Advice"]:
        granularity = "Broad"
        
    return best_style, granularity


def determine_difficulty(title: str, description: str) -> str:
    """
    Determine Difficulty by scanning Title then Description.
    """
    title_lower = title.lower()
    desc_lower = description.lower()
    
    # Step A: Title Scan
    for word in DIFFICULTY_KEYWORDS["Beginner"]:
        if word in title_lower: return "Beginner"
    for word in DIFFICULTY_KEYWORDS["Advanced"]:
        if word in title_lower: return "Advanced"
        
    # Step B: Description Scan (Fallback)
    for word in DIFFICULTY_KEYWORDS["Beginner"]:
        if word in desc_lower: return "Beginner"
    for word in DIFFICULTY_KEYWORDS["Advanced"]:
        if word in desc_lower: return "Advanced"
        
    # Default
    return "Intermediate"


def determine_engagement(views: int, likes: int) -> str:
    """
    Determine Engagement Quality (Hidden Gem vs Popular).
    """
    if views == 0: return "Unknown"
    
    # Popularity Check
    if views > 500_000:
        return "Popular"
        
    # Hidden Gem Check
    like_ratio = likes / views if views > 0 else 0
    if views < 50_000 and like_ratio > 0.04:
        return "Hidden_Gem"
        
    return "Standard"


# ============================================================================
# MAIN ACCESS POINT
# ============================================================================

def determine_tags(title: str, description: str, duration_seconds: int, views: int, like_count: int, full_transcript: str = "") -> Dict[str, str]:
    """
    Generate Final Production Smart Tags.
    
    Args:
        title: Video title
        description: Video description
        duration_seconds: Length
        views: View count
        like_count: Like count
        full_transcript: Complete transcript text
    """
    
    style, granularity = determine_style_with_scoring(title, full_transcript, duration_seconds)
    difficulty = determine_difficulty(title, description)
    engagement = determine_engagement(views, like_count)
    
    return {
        "difficulty": difficulty,
        "style": style,
        "granularity": granularity,
        "engagement": engagement
    }
