# 🛡️ AstraShield — AI Deepfake & Identity Fraud Detection

A full-stack web app that detects deepfakes, voice clones, and forged documents using AI.

---

## 📁 Project Structure

```
astrashield/
├── frontend/          ← Next.js website (what users see)
├── backend/           ← Python FastAPI server (the brain)
├── models/            ← AI model files and training scripts
├── docker/            ← Docker configuration
└── tests/             ← Test files
```

---

## 🚀 Quick Start (Step by Step)

### Step 1 — Install Node.js
Download from: https://nodejs.org  (choose "LTS" version)
After installing, restart your terminal and run: `node --version`

### Step 2 — Install Python packages
```bash
cd backend
pip install -r requirements.txt
```

### Step 3 — Install and start Redis (for background tasks)
**Windows:** Download Redis from https://github.com/tporadowski/redis/releases
**Mac:** `brew install redis && brew services start redis`
**Linux:** `sudo apt install redis-server && sudo service redis start`

### Step 4 — Start the Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 5 — Start the Celery Worker (background task processor)
Open a NEW terminal window:
```bash
cd backend
celery -A celery_app worker --loglevel=info
```

### Step 6 — Start the Frontend
Open ANOTHER new terminal window:
```bash
cd frontend
npm install
npm run dev
```

### Step 7 — Open your browser
Go to: http://localhost:3000

---

## 🔑 Environment Variables

Copy `.env.example` to `.env` in both `frontend/` and `backend/` and fill in your values.
