# backend/app/models.py
"""
Data Models for the Smart Quiz & Diagnosis Engine

This module defines Pydantic models for:
- User Authentication
- Hierarchical Topics
- Questions with AI Metadata
- Quiz Submission & Analysis
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class TopicType(str, Enum):
    """Type of topic in the hierarchy"""
    SUBJECT = "SUBJECT"  # Top-level (e.g., "DSA", "React")
    TOPIC = "TOPIC"      # Sub-topic (e.g., "Stack", "Hooks")


class DiagnosisPillar(str, Enum):
    """5-Pillar Diagnosis System for weakness identification"""
    CONCEPT = "Concept"              # Understanding the 'What' and 'Why'
    IMPLEMENTATION = "Implementation" # Coding syntax and structure
    COMPLEXITY = "Complexity"        # Big-O, Time/Space analysis
    DEBUGGING = "Debugging"          # Error identification and fixing
    APPLICATION = "Application"      # Real-world use cases


# ============================================================================
# USER MODELS
# ============================================================================

class User(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    google_id: Optional[str] = None
    hashed_password: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


# ============================================================================
# TOPIC MODELS (Hierarchical Structure)
# ============================================================================

class Topic(BaseModel):
    """Schema for topics collection - folder structure"""
    id: str = Field(..., alias="_id")
    name: str
    type: TopicType
    parent_id: Optional[str] = None  # Links TOPIC to SUBJECT
    icon: Optional[str] = "📚"       # Emoji/icon for UI
    description: Optional[str] = None

    class Config:
        populate_by_name = True


# ============================================================================
# QUESTION MODELS (Quiz Content)
# ============================================================================

class QuestionOption(BaseModel):
    """Single option in a question"""
    id: str       # "A", "B", "C", "D"
    text: str     # Option text


class Question(BaseModel):
    """Schema for questions collection - quiz content with AI metadata"""
    id: str = Field(..., alias="_id")
    topic_id: str                              # FK to topics._id (MANDATORY)
    question_text: str
    options: List[QuestionOption]
    correct_option_id: str                     # "A", "B", etc.
    
    # AI Metadata (MANDATORY for diagnosis)
    ideal_time_seconds: int = Field(..., ge=5, le=300)  # Benchmark time
    diagnosis_pillar: DiagnosisPillar          # Which pillar this tests
    search_tags: List[str]                     # Keywords for vector search
    explanation: str                           # Instant feedback text
    
    # Optional metadata
    difficulty: Optional[str] = "Medium"       # Easy/Medium/Hard
    
    class Config:
        populate_by_name = True


# ============================================================================
# QUIZ SUBMISSION MODELS
# ============================================================================

class QuestionAnswer(BaseModel):
    """Single answer in a quiz submission"""
    question_id: str              # ID of the question
    selected_option_id: str       # User's selected option ("A", "B", etc.)
    time_taken_seconds: int       # Time spent on this question


class QuizSubmission(BaseModel):
    """Complete quiz submission from frontend"""
    topic_id: str                         # The topic being quizzed on
    answers: List[QuestionAnswer]         # List of answers with timing
    total_time_seconds: int               # Total quiz time


# ============================================================================
# DIAGNOSIS MODELS (Output)
# ============================================================================

class PillarBreakdown(BaseModel):
    """Statistics for a single diagnosis pillar"""
    correct: int
    total: int
    accuracy: float
    rushed_count: int    # How many answers were rushed (<50% ideal time)


class DiagnosisResult(BaseModel):
    """Complete diagnosis output"""
    score: int
    total_questions: int
    percentage: float
    
    weakest_pillar: DiagnosisPillar
    pillar_breakdown: dict  # {pillar_name: PillarBreakdown}
    
    learner_profile: str    # "Struggling", "Rushed", "High Achiever"
    search_query: str       # AI-generated search query
    feedback: str           # AI-generated coaching message
    recommendations: list   # List of video recommendations

