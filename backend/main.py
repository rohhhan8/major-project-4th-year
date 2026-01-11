# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app import auth, quiz, video, progress, notes, user_notes, transcript_pipeline

# --- FastAPI Application Initialization ---
app = FastAPI(
    title="Adaptive Learning Platform API",
    description="Backend API for the Adaptive Learning Platform, powered by FastAPI.",
    version="1.0.0"
)

# --- CORS Configuration ---
# Allow all origins for local development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Specific origin required for credentials
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Router Registration ---
# Include routers from different modules to organize API endpoints
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
app.include_router(video.router, prefix="/video", tags=["Video"])
app.include_router(progress.router, prefix="/progress", tags=["Progress"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(user_notes.router, prefix="/user-notes", tags=["User Notes"])
app.include_router(transcript_pipeline.router, prefix="/transcript", tags=["Transcript Pipeline"])

# --- Root Endpoint ---
@app.get("/")
def read_root():
    """
    Root endpoint to verify that the API is running.
    """
    return {"message": "Welcome to the Adaptive Learning Platform API"}

# --- Application Entry Point ---
if __name__ == "__main__":
    # Run the application using Uvicorn server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
