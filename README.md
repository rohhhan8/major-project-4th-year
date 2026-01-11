# 🧠 Thinkly - AI-Powered Adaptive Learning Platform

> **An intelligent educational platform that analyzes your learning patterns and recommends personalized video content using Machine Learning and RAG (Retrieval-Augmented Generation).**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18-61DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4)

---

## 📌 Project Overview

Thinkly is a research-backed adaptive learning platform that goes beyond traditional LMS systems by using **unsupervised machine learning** and **semantic search** to understand each student's unique learning patterns and recommend the most relevant educational content.

### **Core Innovation**

| Traditional LMS | Thinkly's Approach |
|----------------|-------------------|
| Basic pass/fail grading | **ML clustering analyzing score + response time** |
| Manual playlists | **Semantic search over video transcript embeddings** |
| No note-taking help | **LLM-powered notes with RAG chunking strategy** |
| One-size-fits-all | **Profile-specific content (Struggling vs Rushed vs Achiever)** |

---

## 🔬 Novel Research Contributions

### **1. K-Means Learner Profiling (Unsupervised ML)**

**What's New:** Unlike traditional quiz systems that only look at scores, we use a **2D feature space (Score × Time)** to detect nuanced learning behaviors.

| Cluster | Score | Time | Behavior |
|---------|-------|------|----------|
| **Struggling** | Low (20-55%) | High (60-120s) | Trying but needs basics |
| **Rushed** | Variable (30-70%) | Low (10-35s) | Too fast, missing concepts |
| **High Achiever** | High (70-100%) | Moderate (30-70s) | Ready for advanced content |

**Technical Details:**
- **Algorithm:** scikit-learn K-Means with `n_clusters=3`  
- **Dataset:** **5,000 synthetic student records** (40% Struggling, 35% Achievers, 25% Rushed)
- **Features:** StandardScaler normalized score and time-per-question
- **Model File:** `student_clustering_model.pkl` (~3KB)

**Profile Classification Formula:**
```python
if percentage >= 70:
    profile = "High Achiever"
elif rushed_percentage > 40 or avg_time_ratio < 0.6:
    profile = "Rushed"
else:
    profile = "Struggling"
```

---

### **2. 5-Pillar Micro-Diagnosis System (Novel)**

**What's New:** Goes beyond topic-level analysis to **sub-topic weakness identification** using a 5-pillar framework.

| Pillar | Tests | Recommended Content |
|--------|-------|---------------------|
| **Concept** | Definition, Theory, "What is" | Whiteboard Animations |
| **Implementation** | Syntax, Code Structure | Live Coding Tutorials |
| **Complexity** | Big-O, Time/Space Analysis | Analysis Deep-Dives |
| **Debugging** | Error Fixing, Edge Cases | Debugging Guides |
| **Application** | Real-world Use Cases | System Design Videos |

**How It Works:**
1. Each MCQ question is tagged with a **diagnosis_pillar**
2. After quiz, we calculate **accuracy per pillar**
3. **Weakest pillar** drives video recommendations
4. Questions have **ideal_time** based on pillar (Debugging = 1.5x base time)

**Rushed Detection Formula:**
```python
time_ratio = user_time / ideal_time
is_rushed = time_ratio < 0.3  # Less than 30% of ideal time
```

---

### **3. RAG-Based Video Recommendation (Semantic Search)**

**What's New:** We use **sentence embeddings** to find videos by meaning, not keywords.

**Architecture:**
```
User Query → SentenceTransformer → ChromaDB → Top-N Videos
              (all-MiniLM-L6-v2)    (Vector DB)
```

**Technical Details:**
- **Embedding Model:** `all-MiniLM-L6-v2` (384 dimensions)
- **Vector Database:** ChromaDB (persistent mode)
- **Relevance Formula:** `100 × exp(-distance × 0.5)` for percentage scoring
- **Fallback Logic:** Relaxes filters when strict search yields no results
- **Video Database:** Pre-indexed YouTube transcript chunks

---

### **3. LLM-Powered Notes Generation with Chunking Strategy**

**What's New:** Handles **multi-hour lecture videos** that exceed LLM token limits using a divide-and-conquer approach.

**Pipeline:**
```
Full Transcript → [25K char chunks with 500 char overlap] → Gemini API → Stitch → Master Notes
```

**Technical Details:**
- **LLM:** Google Gemini 2.5 Flash
- **Chunk Size:** ~25,000 characters (~15 mins of content)
- **Overlap:** 500 characters for context continuity
- **Smart Break Points:** Finds sentence endings to avoid mid-thought cuts
- **Rate Limiting:** 1.5s delay between API calls

---

### **4. Gemini AI Coach (Smart Diagnosis)**

**What's New:** Uses LLM to generate **personalized coaching tips** and **optimized search queries** based on weak areas.

**Features:**
- Analyzes micro-tags (Concept, Implementation, Complexity, Debugging, Application)
- Maps weakness to video style (whiteboard animations for concepts, live coding for implementation)
- Generates natural language coaching feedback

---

### **5. Automatic Video Tagging Engine (Data Factory)**

**What's New:** A **weighted scoring system** that analyzes title, intro, and full transcript to auto-classify videos.

**Tagging Categories:**
| Tag Type | Options |
|----------|---------|
| **Difficulty** | Beginner, Intermediate, Advanced |
| **Style** | One_Shot, Course, Practical, Interview_Prep, Conceptual, Advice |
| **Granularity** | Specific, Broad |
| **Engagement** | Popular, Standard, Hidden_Gem |

**Scoring Weights:**
- Title match: **+10 points**
- Intro (first 500 chars): **+5 points**  
- Body frequency: **+1 point per occurrence**

---

## 📊 Datasets & Models

| Resource | Details |
|----------|---------|
| **MCQ Question Bank** | **2,700+** questions across DSA, Python, Web Dev with 5-pillar tags |
| **Synthetic Student Data** | **5,000** records with score (0-100) and time_per_question (10-120s) |
| **Video Transcript Chunks** | **2,520** embeddings in ChromaDB (384 dimensions each) |
| **K-Means Model** | 3 clusters, StandardScaler, saved as `.pkl` |
| **Sentence Transformer** | `all-MiniLM-L6-v2` from Hugging Face |

> 📄 **Research Foundation:** See [`Personalized_Adaptive_Learning_IEEE_Paper.pdf`](./Personalized_Adaptive_Learning_IEEE_Paper.pdf) for the academic basis of this system.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                  │
│  Landing • Dashboard • Quiz • Video Player • Notes Viewer  │
└──────────────────────────┬──────────────────────────────────┘
                           │
       ┌───────────────────┴───────────────────┐
       │                                       │
       ▼                                       ▼
┌──────────────────┐                 ┌──────────────────────┐
│  Main API :8000  │                 │ Recommend API :8001   │
│  ─────────────   │                 │ ──────────────────    │
│  • /auth         │                 │ • /recommend          │
│  • /quiz         │                 │ • /health             │
│  • /video        │                 │                       │
│  • /notes        │                 │ Semantic Search with  │
│  • /progress     │                 │ ChromaDB + Embeddings │
└────────┬─────────┘                 └───────────┬───────────┘
         │                                       │
         ▼                                       ▼
┌──────────────────────────────────────────────────────────────┐
│                     MACHINE LEARNING LAYER                    │
│  K-Means Clustering │ SentenceTransformer │ Gemini 2.5 Flash │
└──────────────────────────────────────────────────────────────┘
         │                       │                    │
         ▼                       ▼                    ▼
   ┌──────────┐           ┌──────────┐         ┌──────────┐
   │ Firebase │           │ ChromaDB │         │ Gemini   │
   │ Firestore│           │ (Vectors)│         │ API      │
   └──────────┘           └──────────┘         └──────────┘
```

> 📐 **Detailed architecture diagrams available in** [`ARCHITECTURE_DIAGRAMS.md`](./ARCHITECTURE_DIAGRAMS.md)

---

## 📁 Project Structure

```
thinkly/
├── backend/              # FastAPI Python Backend
│   ├── app/              # Core application modules
│   │   ├── quiz_engine.py       # K-Means inference engine
│   │   ├── train_model.py       # Model training pipeline
│   │   ├── search_engine.py     # ChromaDB semantic search
│   │   ├── ai_coach.py          # Gemini AI integration
│   │   └── note_generation_service.py  # Chunking strategy
│   └── main.py           # FastAPI app entry point
│
├── frontend/             # React + Vite Frontend
│   └── src/
│       ├── pages/        # Route components
│       └── components/   # Reusable UI components
│
├── data_factory/         # Offline Video Processing Pipeline
│   ├── extractors/       # YouTube transcript extraction
│   ├── processors/       # Tagger & Chunker logic
│   └── database/         # ChromaDB vector storage
│
└── video_db/             # ChromaDB persistent storage (included)
```

---

## 🚀 Getting Started

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- API Keys: Google OAuth, Gemini API, YouTube Data API

### **1. Clone & Install**

```bash
# Clone the repository
git clone https://github.com/Learnwisely/major-project.git
cd major-project

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### **2. Configure Environment**

Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MONGODB_URL=your_mongodb_connection_string
```

### **3. Run the Application**

```bash
# Terminal 1: Backend API
cd backend
python main.py  # Runs on http://localhost:8000

# Terminal 2: Recommendation Engine (Optional)
python main_recommend.py  # Runs on http://localhost:8001

# Terminal 3: Frontend
cd frontend
npm run dev  # Runs on http://localhost:5173
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React 18, Vite, TailwindCSS, Framer Motion |
| **Backend** | FastAPI, Python 3.11, Uvicorn |
| **Vector DB** | ChromaDB (persistent mode) |
| **Auth** | Google OAuth 2.0, Firebase Auth |
| **Storage** | Firebase Firestore, MongoDB Atlas |
| **External APIs** | YouTube Data API, YouTube Transcript API |

---

## 🤖 Machine Learning & AI Stack

### **Core ML Libraries**

| Library | Version | Purpose |
|---------|---------|---------|
| **scikit-learn** | Latest | K-Means clustering, StandardScaler normalization |
| **NumPy** | Latest | Numerical computations, array operations |
| **Pandas** | Latest | DataFrame operations, data preprocessing |
| **Joblib** | Latest | Model serialization/deserialization (.pkl) |

### **NLP & Embeddings**

| Library | Model | Purpose |
|---------|-------|---------|
| **SentenceTransformers** | `all-MiniLM-L6-v2` | 384-dim semantic embeddings |
| **ChromaDB** | Persistent Client | Vector storage & similarity search |
| **PyTorch** | Backend | Powers SentenceTransformers inference |
| **Transformers (HuggingFace)** | Backend | Pre-trained language model weights |

### **Generative AI**

| Service | Model | Purpose |
|---------|-------|---------|
| **Google Gemini API** | `gemini-2.5-flash` | AI coaching, notes generation, smart queries |
| **google-generativeai** | v0.8.5 | Python SDK for Gemini |

### **Data Pipeline**

| Library | Purpose |
|---------|---------|
| **youtube-transcript-api** | Extract video transcripts |
| **pytube / yt-dlp** | Video metadata extraction |
| **tqdm** | Progress bars for batch processing |
| **PyMongo** | MongoDB Atlas connection |

---

## 📈 Key Algorithms Summary

| Algorithm | Purpose | Location |
|-----------|---------|----------|
| **K-Means Clustering** | Learner profile classification | `quiz_engine.py` |
| **Semantic Search** | Content-based video recommendation | `search_engine.py` |
| **Divide & Conquer Chunking** | Long video notes generation | `note_generation_service.py` |
| **Weighted Scoring Tagger** | Automatic video classification | `tagger.py` |
| **Exponential Decay Relevance** | Similarity percentage calculation | `search_engine.py` |
| **5-Pillar Diagnosis** | Micro-weakness identification | `quiz.py` |

---

## 📚 Documentation

- [`ARCHITECTURE_DIAGRAMS.md`](./ARCHITECTURE_DIAGRAMS.md) - Detailed system diagrams with Mermaid
- [`EXAM_PROJECT_WRITEUP.md`](./EXAM_PROJECT_WRITEUP.md) - Academic project documentation
- [`backend/README.md`](./backend/README.md) - Backend API documentation

---

## 👨‍💻 Authors

Built as a Major Project for B.Tech Computer Science.

---

## 📄 License

This project is for educational purposes.
