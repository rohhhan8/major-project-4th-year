# 🎬 Quick Visual Guide - Running Your Project

## 🎯 TL;DR - 3 Steps to Run

```
Step 1: Run QUICKSTART script
Step 2: Open 2 terminals
Step 3: Run backend & frontend
```

---

## 📋 Step-by-Step Visual Guide

### STEP 1️⃣: Initial Setup (One Time Only)

#### On Windows:
**Pick ONE option:**

**Option A - PowerShell (Recommended):**
```
1. Right-click QUICKSTART.ps1
2. Click "Run with PowerShell"
3. Wait for setup to complete ✅
```

**Option B - Command Prompt:**
```
1. Open Command Prompt
2. Navigate to project folder
3. Run: QUICKSTART.bat
4. Wait for setup to complete ✅
```

**Option C - Manual (If scripts fail):**
```
1. Open Command Prompt
2. Run these commands:
   cd backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   python load_quizzes.py
   
3. Open another Command Prompt
4. Run:
   cd frontend
   npm install
```

---

### STEP 2️⃣: Configure MongoDB

#### Option A - Local MongoDB (Easy)
```
1. Download: https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB starts automatically ✅
4. In backend/.env, keep:
   MONGO_DETAILS=mongodb://localhost:27017
```

#### Option B - MongoDB Atlas Cloud (Recommended)
```
1. Go to: https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create free tier cluster
4. Get connection string
5. Update backend/.env:
   MONGO_DETAILS=mongodb+srv://USERNAME:PASSWORD@cluster.mongodb.net/adaptive_learning
```

---

### STEP 3️⃣: Running the Application (Daily)

#### Terminal Setup:
```
You need 2 terminal windows running simultaneously
```

#### Window 1 - Backend Server:
```
cd backend
venv\Scripts\activate  (Windows)
python main.py

Expected output:
✅ Uvicorn running on http://127.0.0.1:8000
✅ Quit the server with CONTROL-C
```

#### Window 2 - Frontend Server:
```
cd frontend
npm run dev

Expected output:
✅ Local: http://localhost:5173/
✅ Press q to quit
```

---

## ✅ Verification

### Everything Working? Check These:

| What | Where | Expected |
|------|-------|----------|
| Backend API Docs | http://localhost:8000/docs | 📖 Swagger UI page opens |
| Frontend App | http://localhost:5173 | 🏠 Landing page loads |
| Console Errors | Press F12 in browser | 🟢 No red errors |
| Backend Logs | Terminal 1 | 📊 Showing request logs |
| MongoDB | Run `mongosh` in new terminal | 🟢 Connected successfully |

---

## 🚀 File Locations You'll Need

```
YOUR PROJECT FOLDER
│
├── 📄 README.md ← Start here for overview!
├── 📄 PROJECT_INDEX.md ← Project structure
├── 📄 SETUP_INSTRUCTIONS.md ← Detailed steps
├── 📄 QUICKSTART.ps1 ← Run this (PowerShell)
├── 📄 QUICKSTART.bat ← Or this (Cmd)
│
├── 📁 backend/
│   ├── 🐍 main.py ← Backend runs this
│   ├── 📄 requirements.txt ← Python packages
│   ├── 📝 .env.example ← Copy & rename to .env
│   └── 📁 app/
│       ├── auth.py
│       ├── quiz.py
│       ├── video.py
│       └── progress.py
│
└── 📁 frontend/
    ├── 📄 package.json ← npm packages
    ├── 🚀 vite.config.js ← Frontend builder
    └── 📁 src/
        ├── App.jsx
        ├── main.jsx
        ├── pages/
        └── components/
```

---

## 🔥 Common First-Time Setup Issues

### ❌ "python: command not found"
```
👉 Solution: Install Python from https://www.python.org/
   Make sure to CHECK "Add Python to PATH" during installation!
```

### ❌ "npm: command not found"
```
👉 Solution: Install Node.js from https://nodejs.org/
   npm comes with Node.js automatically
```

### ❌ "MongoDB connection failed"
```
👉 Solution 1: Make sure MongoDB is running
   - Windows: Check Services for "MongoDB" service
   - Or run: mongod

👉 Solution 2: Check .env file has correct connection string
   - Open backend/.env
   - For local: mongodb://localhost:27017
   - For cloud: mongodb+srv://user:pass@cluster...
```

### ❌ "Port already in use"
```
👉 Solution: Change the port
   Backend: Edit backend/main.py line 29
            port=8001  (change 8000 to 8001)
   
   Frontend: npm run dev -- --port 5174
```

### ❌ "Quit the server with CONTROL-C" appears immediately
```
👉 Solution: Virtual environment not activated
   In backend terminal:
   1. Press Ctrl+C to stop
   2. Run: venv\Scripts\activate
   3. Run: python main.py
```

---

## 🎮 Testing the Setup

### Once Everything is Running:

#### Test 1: Backend API
```
1. Open http://localhost:8000/docs in browser
2. You should see Swagger UI with all endpoints
3. Try clicking "Try it out" on GET / endpoint
4. Click "Execute"
5. Should see: {"message": "Welcome to the Adaptive Learning Platform API"}
```

#### Test 2: Frontend App
```
1. Open http://localhost:5173 in browser
2. You should see the landing page
3. Try navigating to different pages
4. No errors should appear in browser console (F12)
```

#### Test 3: Database Connection
```
1. Open new terminal/command prompt
2. Run: mongosh
3. Then run: use adaptive_learning
4. Then run: show collections
5. Should see: quizzes, users, user_progress
```

---

## 📊 Dashboard After Login

Once logged in, you should see:
```
✅ Dashboard with:
   - Recent Activity
   - Learning Progress graph
   - Weekly Streak counter
   - Ongoing Videos
   - Upcoming Tasks
   - Average Quiz Score
   - Calendar view
```

---

## 🎯 First Quiz Test

```
1. Navigate to "Quiz Topics" or "Quizzes"
2. Select "Python Basics" topic
3. Take the quiz
4. Submit answers
5. See your score
6. Check dashboard - score should update!
```

---

## 💾 Stopping the Services

### Stop Backend (Terminal 1):
```
Press: Ctrl+C
Expected: 
KeyboardInterrupt
Shutting down...
```

### Stop Frontend (Terminal 2):
```
Press: Ctrl+C
Expected:
q to quit
```

### Restart
```
Just run the commands again in both terminals
```

---

## 🔄 Day-to-Day Usage

**After first setup, every day just:**

```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python main.py

# Terminal 2 - Frontend  
cd frontend
npm run dev

# Done! 🎉
# Visit http://localhost:5173
```

---

## 📝 Customization

### Add Quiz Topics
```
1. Edit: backend/quizzes.json
2. Add new topic and questions
3. Run: python load_quizzes.py
4. Refresh frontend
5. New topic appears!
```

### Change Default Ports
```
Backend: main.py, line 29
Frontend: vite.config.js or npm run dev -- --port 5174
```

### Update Styles
```
Tailwind CSS: frontend/src/components/ (already configured)
Custom CSS: frontend/src/index.css or App.css
```

---

## 🎓 Next After Getting Running

1. ✅ Get it running (you are here!)
2. 📖 Read the README.md
3. 🔍 Explore the API docs at http://localhost:8000/docs
4. 🎨 Customize the frontend components
5. ➕ Add more quiz content
6. 🚀 Deploy to production

---

## 📞 Quick Troubleshooting Checklist

- [ ] Python installed? `python --version`
- [ ] Node.js installed? `node --version`
- [ ] MongoDB running? `mongosh` works?
- [ ] .env file created? `backend/.env` exists?
- [ ] Backend starting? Terminal shows Uvicorn running?
- [ ] Frontend starting? Terminal shows Vite running?
- [ ] No red errors in browser console (F12)?
- [ ] Both terminals running simultaneously?

---

**You're all set! 🚀 Happy Learning!**

Questions? Check:
- README.md
- SETUP_INSTRUCTIONS.md
- PROJECT_INDEX.md
