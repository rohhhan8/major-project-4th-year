# 📑 Project Index - Adaptive Learning Platform

## 🎯 Quick Reference

### Important Files to Know
| File | Purpose | Location |
|------|---------|----------|
| `README.md` | Complete project overview & setup guide | Root |
| `SETUP_INSTRUCTIONS.md` | Detailed step-by-step setup | Root |
| `QUICKSTART.ps1` | Automated setup script (PowerShell) | Root |
| `QUICKSTART.bat` | Automated setup script (Batch) | Root |
| `backend/requirements.txt` | Python dependencies | Backend |
| `backend/.env.example` | Environment variables template | Backend |
| `backend/main.py` | FastAPI application entry point | Backend |
| `frontend/package.json` | Node.js dependencies | Frontend |

---

## 🚀 Getting Started (5 Minutes)

### Option A: Automated Setup (Easiest)
**Windows PowerShell:**
```powershell
.\QUICKSTART.ps1
```

**Windows Command Prompt:**
```cmd
QUICKSTART.bat
```

### Option B: Manual Setup

**1. Backend Setup:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env  # Configure MongoDB
python load_quizzes.py
python main.py
```

**2. Frontend Setup (New Terminal):**
```bash
cd frontend
npm install
npm run dev
```

---

## 📂 Project Structure Summary

```
📁 Project Root
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── auth.py (Google OAuth & JWT)
│   │   ├── database.py (MongoDB helpers)
│   │   ├── models.py (Data models)
│   │   ├── quiz.py (Quiz endpoints)
│   │   ├── video.py (Video endpoints)
│   │   └── progress.py (Progress tracking)
│   ├── main.py ⭐ Start here (Backend entry point)
│   ├── quizzes.json (Quiz data)
│   ├── load_quizzes.py (Initialize quiz data)
│   ├── requirements.txt (Dependencies)
│   └── .env.example (Config template)
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 pages/ (Route pages)
│   │   ├── 📁 components/ (UI components)
│   │   ├── App.jsx (Main component)
│   │   ├── AuthContext.jsx (Auth state)
│   │   └── main.jsx (Entry point)
│   ├── package.json (Dependencies)
│   ├── vite.config.js (Vite config)
│   └── tailwind.config.js (Tailwind config)
│
├── README.md ⭐ Read this first!
├── SETUP_INSTRUCTIONS.md (Detailed guide)
├── QUICKSTART.ps1 (Auto setup)
├── QUICKSTART.bat (Auto setup)
└── PROJECT_INDEX.md (This file)
```

---

## 🎯 What Each Component Does

### Backend (`/backend`)
- **FastAPI Server** running on `http://localhost:8000`
- **MongoDB** database for storing users, quizzes, and progress
- **Google OAuth** for authentication
- **RESTful API** endpoints for frontend communication
- Interactive API docs at: `http://localhost:8000/docs`

### Frontend (`/frontend`)
- **React App** running on `http://localhost:5173`
- **Dashboard** showing learning progress
- **Quiz Pages** for testing knowledge
- **Video Player** for learning content
- **Authentication** with Google OAuth

### Database (`MongoDB`)
- Stores user accounts and progress
- Stores quiz content and responses
- Tracks learning streaks and achievements

---

## 🔌 Key Endpoints (When Backend Running)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `http://localhost:8000/docs` | GET | API documentation |
| `http://localhost:5173` | - | Frontend app |
| `/auth/login` | GET | Google OAuth login |
| `/quiz/topics` | GET | Get all quiz topics |
| `/quiz/{topic}` | GET | Get specific quiz |
| `/quiz/submit` | POST | Submit quiz answers |
| `/video/list` | GET | Get all videos |
| `/progress/{user_id}` | GET | Get user progress |

---

## ⚙️ Configuration Files

### Backend Configuration

**`.env` (Backend)**
```env
MONGO_DETAILS=mongodb://localhost:27017
SECRET_KEY=your-secret-key
```

**`requirements.txt`**
Lists all Python packages needed

### Frontend Configuration

**`package.json`**
Lists all Node.js packages and scripts

**`vite.config.js`**
Vite bundler configuration

**`tailwind.config.js`**
Tailwind CSS styling configuration

---

## 🐍 Python Virtual Environment Commands

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Deactivate
deactivate

# Install dependencies
pip install -r requirements.txt

# Add new package
pip install package_name

# Save packages to requirements.txt
pip freeze > requirements.txt
```

---

## 📦 Node.js/npm Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Install new package
npm install package_name
```

---

## 🗄️ MongoDB Commands

```bash
# Start MongoDB (if not running as service)
mongod

# Connect to MongoDB
mongosh
# or
mongo

# List databases
show dbs

# Use a database
use adaptive_learning

# List collections
show collections

# View all documents in collection
db.quizzes.find()

# Count documents
db.quizzes.countDocuments()

# Clear collection
db.quizzes.deleteMany({})
```

---

## 🚨 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Backend won't start | Ensure MongoDB is running, check `.env` |
| Port already in use | Change port in `main.py` or `npm run dev -- --port 5174` |
| Can't find Python | Install Python from https://www.python.org/ |
| Can't find npm | Install Node.js from https://nodejs.org/ |
| API calls fail | Ensure backend is running and CORS is enabled |
| Quiz data missing | Run `python load_quizzes.py` |

---

## 📚 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **MongoDB**: https://docs.mongodb.com/
- **React**: https://react.dev/
- **Vite**: https://vitejs.dev/
- **Tailwind CSS**: https://tailwindcss.com/

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Backend running: `http://localhost:8000` ✓
- [ ] API docs visible: `http://localhost:8000/docs` ✓
- [ ] Frontend running: `http://localhost:5173` ✓
- [ ] Can view landing page ✓
- [ ] Can navigate to quiz topics ✓
- [ ] Can view quizzes ✓
- [ ] No console errors (F12) ✓
- [ ] No backend terminal errors ✓

---

## 🎓 Next Steps

1. ✅ Run the quick start script
2. ✅ Verify both frontend and backend are running
3. ✅ Explore the dashboard
4. ✅ Take a quiz
5. 📖 Read backend/app files to understand the architecture
6. 🎨 Customize frontend components
7. ➕ Add more quiz topics to `quizzes.json`

---

## 📞 Need Help?

1. **Check README.md** - Main documentation
2. **Check SETUP_INSTRUCTIONS.md** - Detailed setup steps
3. **Check terminal errors** - Most issues show up here
4. **Check browser console** (F12) - Frontend errors
5. **Check .env file** - Verify MongoDB connection string

---

**Happy Learning! 🚀**
