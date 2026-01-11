# Adaptive Learning Platform - Backend Architecture

## Overview
This backend powers the Adaptive Learning Platform, providing a robust API for user authentication, video learning, progress tracking, and interactive quizzes. It is built using **FastAPI** (Python) and **MongoDB**.

## Key Technologies
- **FastAPI**: High-performance web framework for building APIs with Python 3.11+.
- **MongoDB**: NoSQL database for flexible storage of user profiles, progress, and quizzes.
- **Google Gemini AI**: Generates personalized study notes from video titles.
- **Google OAuth 2.0**: Secure user authentication.
- **Pydantic**: Data validation and settings management using Python type hints.

## Architecture & Modules

The backend is organized into modular components within the `app` directory:

### 1. Main Entry Point (`main.py`)
- Initializes the FastAPI application.
- Configures **CORS** (Cross-Origin Resource Sharing) to allow the frontend to communicate with the backend.
- Registers the routers (auth, quiz, video, progress) to handle specific API endpoints.

### 2. Authentication (`app/auth.py`)
- Handles **Google OAuth 2.0** login flow.
- Verifies Google ID tokens and manages user sessions using **JWT (JSON Web Tokens)** stored in secure HTTP-only cookies.
- **Key Flow**: Login -> Google Consent -> Callback -> Token Verification -> JWT Creation -> Redirect to Dashboard.

### 3. Database Layer (`app/database.py`)
- Manages the connection to the **MongoDB** instance.
- Provides helper functions to interact with collections:
    - `users`: Stores user profiles.
    - `quizzes`: Stores quiz questions and topics.
    - `user_progress`: Tracks video watch history, quiz scores, and streaks.

### 4. Video Learning (`app/video.py`)
- Integrates with the **YouTube Data API** to search for educational videos.
- Uses **Google Gemini AI** to generate concise study notes based on video titles, enhancing the learning experience.

### 5. Progress Tracking (`app/progress.py`)
- Tracks user activity, including video watch percentage and quiz results.
- Calculates statistics for the dashboard:
    - **Weekly Streak**: Consecutive days of learning.
    - **Learning Progress**: Overall completion rate of watched videos.
    - **Quiz Performance**: Average, highest, and lowest scores.
- Implements a fallback mechanism (in-memory storage) if the database is temporarily unavailable.

### 6. Interactive Quizzes (`app/quiz.py`)
- Retrieves quiz topics and questions from the database (or a fallback JSON file).
- Evaluates user submissions, calculates scores, and identifies weak areas for improvement.

## Data Flow Example: Taking a Quiz
1. **Frontend** requests a quiz topic via `GET /quiz/{topic}`.
2. **Backend** (`quiz.py`) fetches questions from MongoDB.
3. **User** submits answers via `POST /quiz/submit`.
4. **Backend** calculates the score and identifies weak areas.
5. **Backend** (`progress.py`) saves the result to `user_progress` in MongoDB.
6. **Frontend** displays the result and updates the user's dashboard stats.

## Running the Backend
1. Ensure the virtual environment is active: `venv\Scripts\activate`
2. Run the server: `python main.py`
3. Access API documentation: `http://localhost:8000/docs`
