# 🎓 Adaptive Learning Platform

A full-stack web application designed to provide personalized learning experiences with video content, interactive quizzes, and progress tracking.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Project Structure](#project-structure)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Features](#features)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

This adaptive learning platform helps users:
- 📚 Learn through structured video content
- 📝 Test knowledge with interactive quizzes
- 📊 Track learning progress and streaks
- 🎯 Adapt learning based on quiz performance
- 👤 Authenticate securely with Google OAuth

---

## 🛠 Tech Stack

### Frontend
- **React 19** - UI library
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **React Router DOM** - Client-side routing
- **Axios** - HTTP client
- **React YouTube** - YouTube video integration

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database
- **Google OAuth** - Social authentication
- **PyJWT** - JWT token management
- **Uvicorn** - ASGI server

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** → [Download](https://www.python.org/)
- **Node.js 18+** → [Download](https://nodejs.org/)
- **MongoDB** (Local or Atlas) → [Setup Guide](#database-setup)

### Automatic Setup (Windows)

**Option 1: PowerShell**
```powershell
.\QUICKSTART.ps1
```

**Option 2: Command Prompt**
```cmd
QUICKSTART.bat
```

These scripts will:
✅ Check Python and Node.js installation
✅ Create Python virtual environment
✅ Install all dependencies
✅ Configure environment files
✅ Load initial quiz data

---

## 📖 Detailed Setup

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install fastapi uvicorn pymongo python-jose cryptography email-validator google-auth-oauthlib google-auth python-dotenv
```

#### 4. Configure Environment
Copy `.env.example` to `.env` and update:
```bash
cp .env.example .env
```

Edit `.env`:
```env
# Local MongoDB
MONGO_DETAILS=mongodb://localhost:27017

# Or MongoDB Atlas (Cloud)
# MONGO_DETAILS=mongodb+srv://user:password@cluster.mongodb.net/adaptive_learning

# JWT Secret (generate a secure key)
SECRET_KEY=your-random-secret-key-here-min-32-chars
```

#### 5. Load Quiz Data
```bash
python load_quizzes.py
```

#### 6. Start Backend Server
```bash
python main.py
```

✅ Backend running at: `http://localhost:8000`
📚 API Documentation: `http://localhost:8000/docs`

---

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Start Development Server
```bash
npm run dev
```

✅ Frontend running at: `http://localhost:5173` (or `5174`)

---

## 🏃 Running the Application

### Method 1: Two Separate Terminals (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Method 2: Concurrent Execution

**Windows (PowerShell):**
```powershell
# In root directory
$backend = Start-Process -FilePath python -ArgumentList "backend/main.py" -PassThru
$frontend = Start-Process -FilePath npm -ArgumentList "-C frontend run dev" -PassThru
```

**macOS/Linux:**
```bash
cd backend && source venv/bin/activate && python main.py &
cd frontend && npm run dev &
```

---

## 📊 Project Structure

```
adaptive-learning-platform/
│
├── backend/
│   ├── app/
│   │   ├── auth.py           # Google OAuth, JWT authentication
│   │   ├── database.py       # MongoDB connection & helpers
│   │   ├── models.py         # Pydantic data models
│   │   ├── quiz.py           # Quiz endpoints
│   │   ├── video.py          # Video endpoints
│   │   └── progress.py       # Progress tracking endpoints
│   │
│   ├── main.py               # FastAPI application entry point
│   ├── quizzes.json          # Quiz questions & answers
│   ├── load_quizzes.py       # Script to populate DB
│   ├── requirements.txt      # Python dependencies
│   ├── .env.example          # Environment template
│   └── .gitignore
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/    # Dashboard components
│   │   │   │   ├── AvgQuizScore.jsx
│   │   │   │   ├── Calendar.jsx
│   │   │   │   ├── LearningProgress.jsx
│   │   │   │   ├── OngoingVideos.jsx
│   │   │   │   ├── RecentActivity.jsx
│   │   │   │   ├── UpcomingTasks.jsx
│   │   │   │   └── WeeklyStreak.jsx
│   │   │   └── (other components)
│   │   │
│   │   ├── pages/            # Route pages
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── LandingPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── NotesPage.jsx
│   │   │   ├── QuizPage.jsx
│   │   │   ├── QuizTopicsPage.jsx
│   │   │   ├── VideoPlayerPage.jsx
│   │   │   └── VideoResultsPage.jsx
│   │   │
│   │   ├── App.jsx           # Main app component
│   │   ├── App.css
│   │   ├── AuthContext.jsx   # Auth state management
│   │   ├── main.jsx          # React entry point
│   │   ├── index.css
│   │   └── assets/
│   │
│   ├── public/               # Static assets
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── eslint.config.js
│
├── SETUP_INSTRUCTIONS.md     # Detailed setup guide
├── QUICKSTART.bat            # Windows batch setup script
├── QUICKSTART.ps1            # PowerShell setup script
└── README.md                 # This file
```

---

## 🌐 Database Setup

### Option 1: Local MongoDB

**Windows:**
1. Download from: https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB starts automatically as a service

**macOS (Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongod
```

**Verify Connection:**
```bash
mongosh
# or
mongo
```

### Option 2: MongoDB Atlas (Cloud - Recommended)

1. Go to: https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create a free tier cluster
4. Get connection string
5. Update `.env`:
   ```env
   MONGO_DETAILS=mongodb+srv://username:password@cluster.mongodb.net/adaptive_learning?retryWrites=true&w=majority
   ```

---

## 📚 API Documentation

Once backend is running, view interactive API docs:

**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `GET /auth/login` - Initiate Google OAuth login
- `GET /auth/callback` - OAuth callback

#### Quizzes
- `GET /quiz/topics` - Get all quiz topics
- `GET /quiz/{topic}` - Get quiz by topic
- `POST /quiz/submit` - Submit quiz answers

#### Videos
- `GET /video/list` - Get all videos
- `POST /video/progress` - Update video progress

#### Progress
- `GET /progress/{user_id}` - Get user progress
- `GET /progress/streak/{user_id}` - Get user streak

---

## ✨ Features

- ✅ **Google OAuth Authentication** - Secure login
- ✅ **Interactive Quizzes** - Multiple choice questions
- ✅ **Video Learning** - YouTube video integration
- ✅ **Progress Tracking** - Track completed quizzes & videos
- ✅ **Streaks** - Motivating daily streaks
- ✅ **Dashboard** - Visual learning analytics
- ✅ **Responsive Design** - Works on desktop & mobile
- ✅ **CORS Enabled** - Frontend-backend communication

---

## 🐛 Troubleshooting

### Backend Issues

**❌ "Address already in use" on port 8000**
```bash
# Change port in main.py:
# Change: uvicorn.run(..., port=8000)
# To: uvicorn.run(..., port=8001)
```

**❌ "ModuleNotFoundError" for imports**
```bash
# Ensure virtual environment is activated and dependencies installed
pip install -r requirements.txt
```

**❌ MongoDB connection error**
```bash
# Verify MongoDB is running:
mongosh
# Or check .env has correct connection string
```

**❌ "client_secret.json" not found**
```
This is expected if OAuth isn't configured.
The application will still run without OAuth login.
```

### Frontend Issues

**❌ "Port 5173 already in use"**
```bash
npm run dev -- --port 5174
```

**❌ CORS errors in console**
```
- Ensure backend is running
- Check backend CORS middleware allows localhost:5173
```

**❌ "npm: command not found"**
```bash
# Reinstall Node.js from: https://nodejs.org/
```

### General

**❌ Changes not appearing**
```bash
# Frontend: Hard refresh (Ctrl+Shift+R)
# Backend: Server auto-reloads with Uvicorn
```

**❌ Database shows old data**
```bash
# Clear quiz collection and reload:
# In mongosh:
# db.quizzes.deleteMany({})
# Then run: python load_quizzes.py
```

---

## 📦 Build for Production

### Backend Deployment
```bash
# Remove reload for production
# In main.py, change: uvicorn.run(..., reload=False)
# Deploy to: Heroku, Railway, Render, or AWS
```

### Frontend Build
```bash
cd frontend
npm run build
# Creates optimized build in: frontend/dist/
# Deploy to: Vercel, Netlify, or static hosting
```

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Commit changes: `git commit -m 'Add amazing feature'`
3. Push to branch: `git push origin feature/amazing-feature`
4. Open Pull Request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 💡 Need Help?

- 📖 Check [SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)
- 📚 Read [API Documentation](#api-documentation)
- 🐛 Check [Troubleshooting](#troubleshooting) section
- 🌐 Visit [MongoDB Docs](https://docs.mongodb.com/)
- ⚡ Visit [FastAPI Docs](https://fastapi.tiangolo.com/)
- ⚛️ Visit [React Docs](https://react.dev/)

---

**Happy Learning! 🚀**
