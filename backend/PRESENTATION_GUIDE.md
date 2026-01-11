# Backend Presentation Guide for Exhibition

Use this guide to explain how your project's backend works during your presentation. It breaks down the technical code into easy-to-understand concepts.

---

## 1. The Big Picture (The "Brain" of the Operation)
**Concept:** The backend is the hidden "brain" that powers the website. It handles data, security, and intelligence (AI).
**Tech Stack:** Built with **Python (FastAPI)** for speed and **MongoDB** for flexible data storage.

---

## 2. Code Walkthrough - "Who does what?"

Explain your code files like they are departments in a company:

### `main.py` - The Receptionist (Entry Point)
*   **What it does:** This is the front door of the backend. When the frontend (website) asks for something, `main.py` decides which department handles it.
*   **Key Code:**
    *   `app = FastAPI()`: Starts the application.
    *   `app.include_router(...)`: Connects the different departments (Auth, Video, Quiz, Progress).
    *   `CORSMiddleware`: Allows your frontend website to talk to this backend safely.

### `app/auth.py` - The Security Guard (Authentication)
*   **What it does:** Checks user ID cards. It ensures only real users can log in and saves their session.
*   **Key Code:**
    *   `verify_oauth2_token(...)`: Asks Google, "Is this user really who they say they are?"
    *   `create_access_token(...)`: Creates a digital "wristband" (JWT) for the user so they stay logged in as they browse.
    *   **Clock Skew Fix:** Mention you added a "10-second tolerance" to handle time differences between servers—a smart reliability fix!

### `app/video.py` - The Smart Researcher (AI & Content)
*   **What it does:** Finds videos and uses AI to write notes for them.
*   **Key Code:**
    *   `search_videos(...)`: Uses the **YouTube API** to find relevant educational videos.
    *   `get_notes(...)`: This is the "Magic" part. It sends the video title to **Google Gemini AI** and asks it to "Generate concise, helpful notes."
    *   *Exhibition Tip:* Show this file to demonstrate you are using cutting-edge Generative AI.

### `app/quiz.py` - The Examiner (Testing)
*   **What it does:** Hand out test papers and grades them.
*   **Key Code:**
    *   `get_quiz_by_topic(...)`: Fetches questions from the database.
    *   `submit_quiz(...)`: Checks the user's answers, calculates the percentage score, and identifies "weak areas" where the user needs to study more.

### `app/progress.py` - The Analyst (Stats & Dashboard)
*   **What it does:** Tracks everything the user does to build their dashboard.
*   **Key Code:**
    *   `update_video_progress(...)`: Remembers how much of a video you watched.
    *   `get_dashboard_data(...)`: Calculates your "Weekly Streak", "Average Score", and "Learning Progress" so the user sees their growth.

### `app/database.py` - The Vault (Storage)
*   **What it does:** Safely stores all the data.
*   **Key Code:**
    *   `MongoClient(...)`: Connects to the database.
    *   `user_collection`, `quiz_collection`: Specific drawers in the vault for different types of data.

---

## 3. The "Wow" Factor Flow
If a judge asks **"How does the AI part work?"**, explain this flow:

1.  **User** clicks a video on the frontend.
2.  **Backend (`video.py`)** sees the video title.
3.  **Backend** sends a prompt to **Google Gemini**: *"Generate notes for [Title]..."*
4.  **Gemini** returns the summary.
5.  **Backend** sends it back to the user instantly.

---

## 4. Why is this backend "Good"?
*   **Modular:** Everything is in its own file (clean code).
*   **Secure:** Uses industry-standard OAuth2 and JWT.
*   **Scalable:** Built on FastAPI (very fast) and MongoDB (handles lots of data).
*   **Intelligent:** Integrates Generative AI, not just static data.
