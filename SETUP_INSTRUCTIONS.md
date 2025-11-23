# Adaptive Learning Platform - Setup Instructions

## Project Overview
This is a full-stack adaptive learning platform with a **React + Vite** frontend and a **FastAPI** backend with MongoDB for data persistence.

### Stack
- **Frontend**: React 19, Vite, Tailwind CSS, React Router
- **Backend**: FastAPI, MongoDB, Google OAuth
- **Database**: MongoDB (local or cloud)

---

## Prerequisites

### Install Requirements
1. **Node.js & npm** - Download from https://nodejs.org/ (includes npm)
2. **Python 3.8+** - Download from https://www.python.org/
3. **MongoDB** - Either:
   - **Local**: Download from https://www.mongodb.com/try/download/community
   - **Cloud**: MongoDB Atlas (free tier: https://www.mongodb.com/cloud/atlas)

---

## Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd backend
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install fastapi uvicorn pymongo python-multipart python-jose cryptography email-validator google-auth-oauthlib google-auth-httplib2 google-auth python-dotenv
```

### Step 4: Create `.env` File
Create a `.env` file in the `backend/` directory:
```env
# MongoDB Connection
MONGO_DETAILS=mongodb://localhost:27017
# Or for MongoDB Atlas:
# MONGO_DETAILS=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/adaptive_learning

# JWT Configuration
SECRET_KEY=your-secret-key-here

# Google OAuth (Optional - for login feature)
# Download client_secret.json from Google Cloud Console
# GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### Step 5: Load Initial Quiz Data
```bash
python load_quizzes.py
```

### Step 6: Run Backend Server
```bash
python main.py
```
Backend will start at: **http://localhost:8000**
API docs available at: **http://localhost:8000/docs**

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Create `.env` File (Optional)
Create a `.env.local` file in the `frontend/` directory:
```env
VITE_API_URL=http://localhost:8000
```

### Step 4: Run Development Server
```bash
npm run dev
```
Frontend will start at: **http://localhost:5173** or **http://localhost:5174**

---

## Running Both Services Together

### Option 1: Separate Terminals (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Option 2: Concurrent in One Terminal
From the root directory:
```bash
# Windows
start cmd /k "cd backend && venv\Scripts\activate && python main.py"
start cmd /k "cd frontend && npm run dev"

# macOS/Linux
(cd backend && source venv/bin/activate && python main.py) &
(cd frontend && npm run dev) &
```

---

## Database Setup

### Using Local MongoDB

1. **Install MongoDB Community Edition**
2. **Start MongoDB Service:**
   ```bash
   # Windows - if installed as service
   # Already running, or start manually:
   "C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe"
   
   # macOS (via Homebrew)
   brew services start mongodb-community
   
   # Linux (via apt)
   sudo systemctl start mongod
   ```

3. **Verify Connection:**
   ```bash
   mongosh
   # or
   mongo
   ```

### Using MongoDB Atlas (Cloud)

1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string: `mongodb+srv://<user>:<password>@<cluster>.mongodb.net/<dbname>`
4. Update `.env` in backend with this connection string

---

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── auth.py          # Google OAuth & JWT authentication
│   │   ├── database.py      # MongoDB helpers
│   │   ├── models.py        # Pydantic models
│   │   ├── quiz.py          # Quiz endpoints
│   │   ├── video.py         # Video endpoints
│   │   └── progress.py      # User progress tracking
│   ├── main.py              # FastAPI app entry point
│   ├── quizzes.json         # Quiz data
│   └── load_quizzes.py      # Script to load quiz data to DB
│
└── frontend/
    ├── src/
    │   ├── App.jsx          # Main app component
    │   ├── AuthContext.jsx  # Auth state management
    │   ├── main.jsx         # Entry point
    │   ├── pages/           # Route pages
    │   └── components/      # Reusable components
    ├── package.json         # Dependencies
    ├── vite.config.js       # Vite configuration
    └── tailwind.config.js   # Tailwind CSS config
```

---

## Common Commands

### Backend
- Start server: `python main.py`
- API docs: Visit `http://localhost:8000/docs`
- Deactivate venv: `deactivate`

### Frontend
- Dev mode: `npm run dev`
- Build for production: `npm build`
- Preview production build: `npm run preview`
- Lint code: `npm run lint`

---

## Troubleshooting

### Backend Won't Start
- **Port 8000 in use?** Change in `main.py`: `uvicorn.run(..., port=8001)`
- **MongoDB connection error?** Ensure MongoDB is running or `.env` has correct connection string
- **Module not found?** Ensure venv is activated and dependencies installed: `pip install -r requirements.txt`

### Frontend Won't Start
- **Port 5173 in use?** Try `npm run dev -- --port 5174`
- **API connection error?** Ensure backend is running and CORS is enabled
- **Dependencies missing?** Run `npm install` again

### Database Issues
- **Can't connect to MongoDB?** Check if MongoDB service is running
- **Quiz data missing?** Run `python load_quizzes.py` from backend directory
- **Collections not created?** First request to endpoints will auto-create them

---

## Next Steps

1. Configure Google OAuth (optional) for social login
2. Customize quiz topics in `quizzes.json`
3. Add more video content to the platform
4. Deploy backend to Heroku/Railway/Render
5. Deploy frontend to Vercel/Netlify

---

## Support

For issues, check:
- Backend logs in terminal running FastAPI
- Browser console (F12) for frontend errors
- MongoDB logs if database connection fails
