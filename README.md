# 🛡️ AstraShield — AI Deepfake & Identity Fraud Detection

An AI-powered cybersecurity platform that detects deepfakes, voice clones, and forged identity documents.

## 🌐 Live Demo
- **Website:** https://astrashield-rho.vercel.app
- **API Docs:** https://astrashield.onrender.com/docs



## 🔍 What It Does
- Detects AI-generated deepfake images
- Detects voice cloning and synthetic audio
- Detects forged identity documents
- Analyzes metadata for AI generation signatures
- Produces a Fraud Risk Score (0-100)

## 🛠️ Tech Stack
- **Frontend:** Next.js 14, Tailwind CSS
- **Backend:** Python FastAPI, Celery
- **AI Models:** EfficientNet-B4, ResNet-18
- **Databases:** MongoDB Atlas, PostgreSQL
- **Queue:** Redis (Upstash)
- **Deployment:** Vercel + Render

## 📁 Project Structure
```
astrashield/
├── frontend/     → Next.js dashboard
├── backend/      → FastAPI + Celery
├── models/       → AI model training scripts
├── scripts/      → Setup and demo scripts
└── docker/       → Docker configuration
```

## 🚀 Run Locally
1. Clone the repo
2. Install Docker Desktop
3. Run `docker compose up postgres mongo redis minio -d`
4. Run `cd backend && pip install -r requirements.txt`
5. Run `cd backend && uvicorn main:app --reload --port 8000`
6. Run `cd frontend && npm install && npm run dev`
7. Open https://astrashield-rho.vercel.app

## 👨‍💻 Developer
Rohan Kumar — Engineering Student
GitHub: https://github.com/Rohankumar2201
```
