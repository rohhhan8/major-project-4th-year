# Thinkly - Architecture & Technical Deep Dive

A comprehensive analysis of the Adaptive Learning Platform codebase, including system architecture, data flows, key algorithms, and project novelty.

---

## System Architecture Overview

```mermaid
flowchart TB
    subgraph Client["🌐 React Frontend (Port 5173)"]
        LP[Landing Page]
        DASH[Dashboard]
        QUIZ[Quiz Module]
        VIDEO[Video Player]
        NOTES[Notes Viewer]
    end

    subgraph Backend["⚙️ FastAPI Backend"]
        subgraph MainAPI["Main API (Port 8000)"]
            AUTH["/auth - Google OAuth"]
            QUIZ_API["/quiz - Quiz Engine"]
            VIDEO_API["/video - Video Metadata"]
            PROGRESS["/progress - User Tracking"]
            NOTES_API["/notes - AI Notes Generation"]
        end
        
        subgraph RecommendAPI["Recommendation API (Port 8001)"]
            RECOMMEND["/recommend - Semantic Search"]
            HEALTH["/health - System Status"]
        end
    end

    subgraph ML["🧠 Machine Learning Components"]
        KMEANS["K-Means Clustering\n(Learner Profiling)"]
        EMBEDDINGS["SentenceTransformer\n(all-MiniLM-L6-v2)"]
    end

    subgraph Storage["💾 Data Storage"]
        FIREBASE[(Firebase/Firestore\nUser Data)]
        CHROMA[(ChromaDB\nVideo Vectors)]
    end

    subgraph External["☁️ External Services"]
        GOOGLE[Google OAuth 2.0]
        GEMINI[Gemini AI API]
        YOUTUBE[YouTube API]
    end

    Client <--> MainAPI
    Client <--> RecommendAPI
    AUTH --> GOOGLE
    NOTES_API --> GEMINI
    VIDEO_API --> YOUTUBE
    QUIZ_API --> KMEANS
    RECOMMEND --> EMBEDDINGS
    RECOMMEND --> CHROMA
    AUTH --> FIREBASE
    PROGRESS --> FIREBASE
```

---

## Data Flow Diagrams

### 1. Quiz → Analysis → Recommendation Flow

```mermaid
sequenceDiagram
    participant U as Student
    participant F as Frontend
    participant Q as Quiz API
    participant ML as Quiz Engine
    participant R as Recommend API
    participant DB as ChromaDB

    U->>F: Start Quiz
    F->>Q: GET /quiz/start/{topic}
    Q-->>F: Questions + Metadata
    
    U->>F: Submit Answers
    F->>Q: POST /quiz/submit
    Q->>ML: analyze_student_performance()
    
    Note over ML: K-Means Clustering<br/>Score + Time → Learner Profile
    
    ML-->>Q: {profile, weak_tags, search_tag}
    Q-->>F: Analysis Results
    
    F->>R: GET /recommend?topic={weak_tag}
    R->>DB: Semantic Search (Embedding)
    DB-->>R: Top Video Matches
    R-->>F: Recommended Videos
    F-->>U: Show Results + Recommendations
```

### 2. AI Notes Generation Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant N as Notes API
    participant T as Transcript Service
    participant G as Gemini AI
    participant C as Cache (Firestore)

    U->>F: Click "Generate AI Notes"
    F->>N: GET /notes/ai?video_id={id}
    
    N->>C: Check Cache (video_id)
    alt Notes Cached
        C-->>N: Cached Notes
        N-->>F: Return Cached
    else Not Cached
        N->>T: Fetch Transcript
        T-->>N: Full Transcript
        
        Note over N: Chunking Strategy<br/>Split into 25K char segments
        
        loop For Each Chunk
            N->>G: Generate Notes (chunk)
            G-->>N: Chunk Notes
        end
        
        Note over N: Stitching<br/>Combine all chunks
        
        N->>C: Cache Complete Notes
        N-->>F: Return Notes
    end
    
    F-->>U: Display Markdown Notes
```

---

## Key Algorithms & Technical Novelty

### 1. 🎯 K-Means Learner Profiling (Unsupervised ML)

**Location:** `backend/app/train_model.py` + `backend/app/quiz_engine.py`

**Algorithm:**
```python
# Feature Vector: [normalized_score, normalized_time]
# Clusters into 3 profiles:
#   - "Struggling" (low score, high time)
#   - "Rushed" (low score, low time)  
#   - "High Achiever" (high score, moderate time)
```

**Novelty:**
- Combines **score** AND **time-per-question** to detect nuanced learner states
- A student with 50% score who took 5 seconds/question (rushed) gets different content than one who took 60 seconds/question (struggling with concepts)
- Profile-specific search tags are generated to find appropriate difficulty videos

---

### 2. 🔍 Semantic Search with ChromaDB (Content-Based Filtering)

**Location:** `backend/app/search_engine.py`

**Algorithm:**
```python
# 1. Embed user query using SentenceTransformer
query_embedding = model.encode("binary search time complexity")

# 2. Query ChromaDB for nearest neighbors
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={"difficulty": "Beginner"}  # Optional metadata filter
)
```

**Novelty:**
- Videos are pre-indexed by transcript chunks (offline factory)
- Supports **metadata filtering** (difficulty, style, granularity)
- Fallback logic when no exact matches found
- Returns specific timestamp ranges within videos, not just video IDs

---

### 3. 📝 Divide-and-Conquer Notes Generation (LLM Chunking)

**Location:** `backend/app/note_generation_service.py`

**Architecture:**
```mermaid
flowchart LR
    T[Full Transcript<br/>100K+ chars] --> C1[Chunk 1<br/>25K chars]
    T --> C2[Chunk 2<br/>25K chars]
    T --> C3[Chunk 3<br/>25K chars]
    T --> CN[Chunk N...]
    
    C1 --> G1[Gemini API]
    C2 --> G2[Gemini API]
    C3 --> G3[Gemini API]
    CN --> GN[Gemini API]
    
    G1 --> S[Stitcher]
    G2 --> S
    G3 --> S
    GN --> S
    
    S --> M[Master Notes<br/>Markdown]
```

**Novelty:**
- Handles **multi-hour lecture videos** that exceed LLM context limits
- **Overlapping chunks** (500 char overlap) prevent mid-sentence breaks
- Smart break-point detection (finds sentence endings)
- Rate limiting built-in for API quotas
- College-level prompt engineering for high-quality study notes

---

### 4. 🏷️ Micro-Tag Analysis (Question-Level Insights)

**Location:** `backend/app/quiz_engine.py` (lines 225-251)

```python
def _analyze_micro_tags(results, questions):
    """
    Calculates accuracy percentage for each micro-tag.
    Example output: {"Theory": 80%, "Syntax": 20%, "Time Complexity": 60%}
    """
```

**Novelty:**
- Goes beyond topic-level analysis to **sub-topic granularity**
- Questions are tagged with micro-concepts (e.g., "pointer manipulation", "edge cases")
- Generates targeted recommendations for specific weak areas

---

## Component Architecture

```mermaid
graph TB
    subgraph Frontend
        A[App.jsx<br/>Router] --> B[AuthContext<br/>Global Auth State]
        A --> C[MainLayout<br/>Navbar + Outlet]
        
        C --> D[DashboardPage]
        C --> E[QuizPage]
        C --> F[VideoPlayerPage]
        C --> G[NotesPage]
        
        D --> H[OngoingVideos]
        D --> I[Stats Cards]
        E --> J[QuizCard]
        F --> K[NotesCanvas]
    end

    subgraph Backend
        L[main.py<br/>FastAPI App] --> M[auth.py<br/>Google OAuth]
        L --> N[quiz.py<br/>Quiz Router]
        L --> O[video.py<br/>Video Metadata]
        L --> P[notes.py<br/>AI Notes]
        L --> Q[progress.py<br/>User Progress]
        
        N --> R[quiz_engine.py<br/>ML Analysis]
        P --> S[note_generation_service.py<br/>Gemini Integration]
        
        T[main_recommend.py<br/>Separate Server] --> U[search_engine.py<br/>ChromaDB + Embeddings]
    end

    subgraph DataLayer
        V[(Firestore<br/>Users, Progress, Notes)]
        W[(ChromaDB<br/>Video Vectors)]
        X[student_clustering_model.pkl<br/>K-Means Model]
    end

    M --> V
    Q --> V
    P --> V
    U --> W
    R --> X
```

---

## Database Schema

```mermaid
erDiagram
    USERS {
        string uid PK
        string email
        string name
        timestamp created_at
    }
    
    VIDEO_PROGRESS {
        string user_id FK
        string video_id PK
        float watch_percentage
        string title
        timestamp last_watched
    }
    
    AI_NOTES {
        string video_id PK
        text markdown_content
        json metadata
        timestamp generated_at
    }
    
    USER_NOTES {
        string id PK
        string user_id FK
        string video_id FK
        text content
        timestamp updated_at
    }
    
    QUIZ_RESULTS {
        string id PK
        string user_id FK
        string topic
        float score
        float time_taken
        json question_results
        timestamp completed_at
    }

    USERS ||--o{ VIDEO_PROGRESS : tracks
    USERS ||--o{ USER_NOTES : creates
    USERS ||--o{ QUIZ_RESULTS : completes
```

---

## Project Uniqueness & Innovation

| Feature | Traditional LMS | Thinkly's Approach |
|---------|----------------|-------------------|
| **Learning Analysis** | Basic pass/fail | ML clustering with time + score behavioral analysis |
| **Recommendations** | Manual playlists | Semantic search over transcript embeddings |
| **Note Generation** | None | LLM-powered with chunking for any video length |
| **Personalization** | One-size-fits-all | Profile-specific content (Struggling vs Rushed vs Achiever) |
| **Video Integration** | External links | In-app player with progress tracking + transcript sync |

### Technical Differentiators:

1. **Hybrid ML Pipeline**: Combines unsupervised clustering (K-Means) with semantic retrieval (embeddings)
2. **Scalable LLM Integration**: Chunking strategy handles videos of any length without token limit issues
3. **Real-time Adaptation**: Quiz results immediately influence video recommendations
4. **Offline + Online Architecture**: Pre-computed embeddings (offline factory) + real-time queries

---

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, TailwindCSS, Framer Motion |
| Backend | FastAPI, Python 3.11, Uvicorn |
| ML/AI | scikit-learn (K-Means), SentenceTransformers, Google Gemini |
| Vector DB | ChromaDB (persistent mode) |
| Auth | Google OAuth 2.0, Firebase Auth |
| Storage | Firebase Firestore |
| External | YouTube Data API, YouTube Transcript API |
