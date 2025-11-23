from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app import auth, quiz, video, progress

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
]

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])
app.include_router(video.router, prefix="/video", tags=["Video"])
app.include_router(progress.router, prefix="/progress", tags=["Progress"])

# CORS Middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Adaptive Learning Platform API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
