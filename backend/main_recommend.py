"""
main_recommend.py - Online Recommendation Engine (API Layer)

This module provides the REST API endpoints for the video recommendation system.
It exposes the Content-Based Filtering engine via FastAPI.

Endpoints:
    GET /recommend?topic=<string> - Get video recommendation for a weak topic
    GET /health - Check system health status

Based on Paper F: Hybrid Recommendation System for Adaptive E-Learning.

Author: ML Engineering Team
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

# Import our search engine module
from app.search_engine import find_best_video, health_check

# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Video Recommendation Engine",
    description="""
    Online Recommendation Engine for Adaptive E-Learning Platform.
    
    This API provides video recommendations based on a user's weak topics using
    Content-Based Filtering with semantic search over pre-indexed video transcripts.
    
    **Architecture:**
    - Offline Factory: ChromaDB populated with video transcript vectors (handled by data team)
    - Online Engine: This API - queries the database in read-only mode
    
    **Paper Reference:** Hybrid Recommendation System (Paper F)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "service": "Video Recommendation Engine",
        "version": "1.0.0",
        "description": "Content-Based Filtering for Adaptive E-Learning",
        "endpoints": {
            "recommend": "/recommend?topic=<your_topic>",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/recommend")
async def recommend_video(
    topic: str = Query(..., min_length=2, max_length=200, description="The weak topic or concept"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (Beginner, Intermediate, Advanced)"),
    style: Optional[str] = Query(None, description="Filter by style (Conceptual, Practical, Quick_Summary, etc.)"),
    granularity: Optional[str] = Query(None, description="Filter by granularity (Specific, Broad)")
):
    """
    Get a video recommendation with optional metadata filters.
    """
    
    # Clean and normalize
    clean_topic = topic.strip()
    
    if not clean_topic:
        return {"status": "error", "message": "Topic cannot be empty"}
    
    # Call search engine with filters
    results = find_best_video(clean_topic, difficulty=difficulty, style=style, granularity=granularity)
    
    if results:
        return {
            "status": "success",
            "count": len(results),
            "data": results,
            "query": clean_topic,
            "filters": {"difficulty": difficulty, "style": style, "granularity": granularity}
        }
    else:
        # No matching video found
        return {
            "status": "error",
            "message": f"No relevant video found for topic: '{clean_topic}'. Try rephrasing your query.",
            "query": clean_topic,
            "suggestions": [
                "Try using more specific keywords",
                "Check for spelling errors",
                "Use common DSA terminology"
            ]
        }


@app.get("/health")
async def health_status():
    """
    Check the health status of the recommendation engine.
    
    Returns status of:
    - Embedding model (sentence-transformers)
    - ChromaDB connection
    - Video collection availability
    - Document count in the database
    
    Use this endpoint to verify the system is ready to serve requests.
    """
    
    status = health_check()
    
    is_healthy = all([
        status.get("model_loaded"),
        status.get("database_connected"),
        status.get("collection_available")
    ])
    
    return {
        "status": "healthy" if is_healthy else "degraded",
        "components": status,
        "ready": is_healthy
    }


# ============================================================================
# STANDALONE SERVER (for development/testing)
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Starting Video Recommendation Engine")
    print("=" * 60)
    print("API Docs: http://localhost:8001/docs")
    print("Health Check: http://localhost:8001/health")
    print("Example: http://localhost:8001/recommend?topic=binary+search")
    print("=" * 60)
    
    uvicorn.run(
        "main_recommend:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
