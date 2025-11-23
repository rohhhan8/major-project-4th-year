# ✅ First Time Setup Checklist

Use this checklist to ensure everything is set up correctly!

---

## 📋 Pre-Setup Requirements

- [ ] **Python 3.8+** installed
  - Check: Open terminal, run `python --version`
  - If not: Download from https://www.python.org/

- [ ] **Node.js & npm** installed
  - Check: Open terminal, run `node --version` and `npm --version`
  - If not: Download from https://nodejs.org/

- [ ] **MongoDB** ready (local or cloud)
  - Option 1 (Local): https://www.mongodb.com/try/download/community
  - Option 2 (Cloud): https://www.mongodb.com/cloud/atlas

- [ ] **Git** installed (optional but recommended)
  - Check: `git --version`

---

## 🚀 Automated Setup

### Choose ONE method:

#### Method 1: PowerShell (Recommended for Windows)
```powershell
# 1. Open PowerShell in project folder
# 2. Run:
.\QUICKSTART.ps1
# 3. Wait for completion ✅
```

#### Method 2: Command Prompt (Windows)
```cmd
# 1. Open Command Prompt in project folder
# 2. Run:
QUICKSTART.bat
# 3. Wait for completion ✅
```

#### Method 3: Manual Setup (All systems)
- [ ] Follow SETUP_INSTRUCTIONS.md step by step

---

## 🔧 Configuration

### Backend Configuration
- [ ] Copy `backend/.env.example` → `backend/.env`
- [ ] Edit `backend/.env`:
  - [ ] Add MongoDB connection string
  - [ ] Verify `SECRET_KEY` is set

### Frontend Configuration (Optional)
- [ ] `.env` file not needed for local development
- [ ] Default API URL: `http://localhost:8000`

### Database Configuration
- [ ] MongoDB is running
- [ ] Connection string is correct in `.env`
- [ ] Can connect via `mongosh` (if local)

---

## 📦 Dependency Installation

### Backend Dependencies
- [ ] Virtual environment created: `backend/venv/`
- [ ] Virtual environment activated
- [ ] `requirements.txt` installed successfully
  - Check: `pip list` should show all packages

### Frontend Dependencies
- [ ] `npm install` completed in `frontend/` folder
- [ ] `node_modules/` folder created
- [ ] No `npm ERR!` messages

### Quiz Data
- [ ] `python load_quizzes.py` ran successfully
- [ ] Quiz data loaded in MongoDB

---

## 🏃 First Run

### Terminal 1: Backend Server

```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python main.py
```

- [ ] No errors in terminal
- [ ] See message: `Uvicorn running on http://127.0.0.1:8000`
- [ ] Ready to accept requests

### Terminal 2: Frontend Server

```bash
cd frontend
npm run dev
```

- [ ] No errors in terminal
- [ ] See message: `Local: http://localhost:5173/`
- [ ] Frontend is compiling/ready

---

## ✨ Verification

### API Documentation
- [ ] Open: http://localhost:8000/docs
- [ ] See: Swagger UI with all endpoints
- [ ] Try: Click "GET /" and execute
- [ ] Result: See welcome message

### Frontend Application
- [ ] Open: http://localhost:5173
- [ ] See: Landing page loads
- [ ] No errors in browser console (F12)
- [ ] Can navigate between pages

### Database Connection
- [ ] Open new terminal
- [ ] Run: `mongosh`
- [ ] Run: `use adaptive_learning`
- [ ] Run: `show collections`
- [ ] See: quizzes, users, user_progress

---

## 🧪 Functional Tests

### Authentication
- [ ] Landing page loads
- [ ] Can see login button
- [ ] OAuth redirect works (if configured)

### Quiz Functionality
- [ ] Navigate to "Quiz Topics" or "Quizzes"
- [ ] See "Python Basics" topic
- [ ] Click to open quiz
- [ ] See quiz questions
- [ ] Can select answers
- [ ] Submit button works
- [ ] See score/results

### Dashboard
- [ ] After taking quiz, dashboard updates
- [ ] See progress chart
- [ ] See recent activity
- [ ] See streak counter

### Video Section
- [ ] Can navigate to video section
- [ ] Videos load (if data available)

---

## 🐛 Troubleshooting Checklist

### Backend Won't Start

- [ ] Python path correct?
  - Run: `which python` (macOS/Linux) or `where python` (Windows)

- [ ] Virtual environment activated?
  - Look for `(venv)` prefix in terminal

- [ ] Dependencies installed?
  - Run: `pip list | grep fastapi`

- [ ] MongoDB running?
  - Try: `mongosh` in new terminal

- [ ] Port 8000 available?
  - Check: No other service on port 8000

### Frontend Won't Start

- [ ] npm installed?
  - Run: `npm --version`

- [ ] Dependencies installed?
  - Check: `frontend/node_modules/` exists

- [ ] Port 5173 available?
  - Use: `npm run dev -- --port 5174`

- [ ] Browser issue?
  - Try different browser
  - Clear cache (Ctrl+Shift+Del)

### API Calls Failing

- [ ] Backend running?
  - Check: http://localhost:8000 works

- [ ] CORS enabled?
  - Check: Backend has CORS middleware

- [ ] API response correct?
  - Check: http://localhost:8000/docs

### Database Issues

- [ ] MongoDB running?
  - Windows: Check Services for "MongoDB"
  - macOS: `brew services list`

- [ ] Connection string correct?
  - Check: `.env` file for `MONGO_DETAILS`

- [ ] Quiz data loaded?
  - Run: `python load_quizzes.py` again

---

## 📱 Cross-Browser Testing

- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if on macOS)
- [ ] Edge

---

## 📚 Documentation Review

- [ ] Read: README.md
- [ ] Understand: QUICK_START_VISUAL_GUIDE.md
- [ ] Reference: PROJECT_INDEX.md
- [ ] Setup details: SETUP_INSTRUCTIONS.md

---

## ✅ Final Verification

Run through this final checklist:

- [ ] Backend terminal shows "Uvicorn running"
- [ ] Frontend terminal shows "Local: http://localhost:5173/"
- [ ] http://localhost:5173 shows landing page
- [ ] http://localhost:8000/docs shows API docs
- [ ] No red errors in browser console (F12)
- [ ] Can navigate to all pages
- [ ] Quiz page loads questions
- [ ] Dashboard shows after quiz

---

## 🎉 Success!

If all checkboxes are checked, your project is:
✅ Properly set up
✅ Running correctly
✅ Ready for development
✅ Database connected
✅ Frontend & Backend communicating

---

## 📝 Next Steps After Setup

1. **Explore the code:**
   - [ ] Read `backend/main.py`
   - [ ] Read `frontend/src/App.jsx`
   - [ ] Understand app structure

2. **Customize the app:**
   - [ ] Change styles in Tailwind
   - [ ] Add new quiz topics
   - [ ] Modify dashboard components

3. **Add features:**
   - [ ] New endpoints in backend
   - [ ] New pages in frontend
   - [ ] New functionality

4. **Deploy (later):**
   - [ ] Build frontend: `npm run build`
   - [ ] Deploy to Vercel/Netlify
   - [ ] Deploy backend to Heroku/Railway

---

## 🆘 Need Help?

1. **Check documentation:**
   - README.md
   - SETUP_INSTRUCTIONS.md
   - QUICK_START_VISUAL_GUIDE.md

2. **Check browser console:**
   - F12 → Console tab → Look for errors

3. **Check terminal output:**
   - Backend terminal → Look for error messages
   - Frontend terminal → Look for compilation errors

4. **Restart services:**
   - Stop (Ctrl+C in both terminals)
   - Run again from scratch

5. **Google error messages:**
   - Copy exact error into Google
   - Usually finds the solution

---

## 🎯 Common Tasks Checklist

### Daily Development
- [ ] Activate backend venv
- [ ] Run `python main.py`
- [ ] Run `npm run dev`
- [ ] Develop and test

### Before Committing Code
- [ ] Run linter: `npm run lint` (frontend)
- [ ] Test manually
- [ ] Check for console errors

### Updating Dependencies
- [ ] Backend: `pip install -r requirements.txt`
- [ ] Frontend: `npm install`

### Deploying to Production
- [ ] Update `.env` for production
- [ ] Build frontend: `npm run build`
- [ ] Configure backend deployment
- [ ] Test thoroughly

---

## 📊 Status Indicators

### Everything Good ✅
```
Terminal 1: "Uvicorn running on http://127.0.0.1:8000"
Terminal 2: "Local: http://localhost:5173"
Browser: Page loads, no console errors
```

### Backend Issue 🔴
```
Terminal 1: Shows error or no "Uvicorn running" message
Check: Python, venv, MongoDB, port 8000
```

### Frontend Issue 🔴
```
Terminal 2: Shows error or "Failed to compile"
Check: npm, node_modules, port 5173
```

### Database Issue 🔴
```
mongosh shows "MongoServerSelectionError"
Check: MongoDB running, connection string in .env
```

---

**You're all set! Happy coding! 🚀**
