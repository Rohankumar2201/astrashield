# 🛡️ AstraShield

<div align="center">

<img src="https://img.shields.io/badge/STATUS-LIVE-brightgreen?style=for-the-badge&labelColor=0a0a0f" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0f" />
<img src="https://img.shields.io/badge/Next.js-14-ffffff?style=for-the-badge&logo=next.js&logoColor=white&labelColor=0a0a0f" />
<img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white&labelColor=0a0a0f" />
<img src="https://img.shields.io/badge/PyTorch-2.1-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white&labelColor=0a0a0f" />
<img src="https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge&labelColor=0a0a0f" />

<br/><br/>

### AI-Powered Deepfake and Identity Fraud Detection System

*Detects fake images, cloned voices, and forged documents using deep learning and classical forensics — delivering a single Fraud Risk Score from 0 to 100.*

<br/>

**[Live Demo](https://astrashield-rho.vercel.app)** &nbsp;•&nbsp;
**[API](https://astrashield.onrender.com)** &nbsp;•&nbsp;
**[API Docs](https://astrashield.onrender.com/docs)**

<br/>

> Built for **IIT Bombay Hack and Break 2024** — Cybersecurity + Generative AI Track

</div>

---

## Table of Contents

- [The Problem](#the-problem)
- [What AstraShield Does](#what-astrashield-does)
- [Live Demo](#live-demo)
- [How Detection Works](#how-detection-works)
- [Fraud Risk Score](#fraud-risk-score)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [Use Cases](#use-cases)
- [Roadmap](#roadmap)
- [Author](#author)

---

## The Problem

Generative AI has created an asymmetric threat in cybersecurity:

| Threat | Real-World Impact |
|--------|------------------|
| CEO Voice Cloning | A UK energy company lost $243,000 in a single call (2019) |
| AI-Generated Identities | Synthetic faces bypass KYC checks at banks at industrial scale |
| Deepfake Videos | Political deepfakes manipulate elections across multiple countries |
| Forged Documents | AI-edited Aadhaar and passport scans sold on dark web marketplaces |

**Creating deepfakes takes minutes. Detecting them has been fragmented, expensive, and inaccessible — until now.**

---

## What AstraShield Does

Upload any image, audio clip, or identity document and AstraShield runs it through a multi-layer AI forensic pipeline:

```
Upload File
      ↓
4 Detection Modules Run In Parallel
      ↓
Weighted Ensemble Scoring Engine
      ↓
Fraud Risk Score (0 to 100) + Full Forensic Report
```

| Module | Input | What It Detects |
|--------|-------|----------------|
| Image Deepfake | JPEG, PNG, WEBP | GAN artifacts, blending boundaries, texture anomalies |
| Voice Clone | MP3, WAV, M4A | Vocoder harmonics, unnatural pitch, TTS artifacts |
| Document Forgery | PDF | Copy-paste artifacts, font inconsistencies, noise patterns |
| Metadata Forensics | Any file | Missing EXIF, AI software signatures, timestamp anomalies |

---

## Live Demo

| Resource | URL |
|----------|-----|
| Website | https://astrashield-rho.vercel.app |
| Backend API | https://astrashield.onrender.com |
| Interactive API Docs | https://astrashield.onrender.com/docs |
| GitHub | https://github.com/Rohankumar2201/astrashield |

> Note: First request may take 30 to 60 seconds to wake the free-tier server. Subsequent requests are fast.

---

## How Detection Works

### 1. Image Deepfake Detection

**EfficientNet-B4 CNN** (fine-tuned on FaceForensics++ — 720,000 frames)

The model detects GAN artifacts invisible to the human eye:
- Checkerboard patterns from transposed convolution upsampling
- Unnatural blending at face boundaries
- Inconsistent skin texture gradients
- Eye reflection anomalies (AI cannot replicate accurate reflections)

**Error Level Analysis (ELA)**

Classical forensics technique that reveals edited regions:

```
1. Re-save image at JPEG quality=90 (controlled compression)
2. Calculate pixel difference: diff = |original - resaved| x 10
3. High-difference regions = tampered or AI-generated areas
4. Score = min(mean_diff / 30.0, 1.0)
```

**Metadata Forensics**

Every real camera embeds EXIF data. AI generators do not.
- Missing EXIF adds 0.35 to suspicion score
- AI software signatures (Stable Diffusion, Midjourney, DALL-E) add 0.50
- Missing camera make and model adds 0.15

---

### 2. Voice Clone Detection

**ResNet-18 Spectrogram CNN** (trained on ASVspoof 2021)

```
Audio → 16kHz resample → 128-bin Mel Spectrogram → ResNet-18 CNN → Real/Fake probability
```

Real voices have natural pitch variations, room acoustics, and breathing patterns.
AI clones leave behind vocoder harmonics, uniform backgrounds, and unnatural pitch transitions.

Detects: ElevenLabs, Tortoise-TTS, VITS, WaveNet, WaveGlow

---

### 3. Document Forgery Detection

Four techniques combined:
- **ELA** — JPEG compression inconsistency analysis
- **PRNU Noise Analysis** — Real scans have consistent camera sensor noise; forgeries do not
- **OCR Font Check** — Tesseract v5 detects mismatched fonts from pasted regions
- **Metadata Check** — Document creation date and software origin validation

---

## Fraud Risk Score

All module outputs feed into a Weighted Ensemble Engine:

```
Raw Score = (image_deepfake x 0.45) + (ela x 0.25) + (metadata x 0.30)

Final Score = Platt_Scaling(Raw Score) x 100
           = 1 / (1 + exp(-2.5 x raw + 1.2)) x 100
```

Platt Scaling calibrates raw model outputs into true probabilities. A score of 87 means the model is 87% confident the content is fake.

| Score | Risk Level | Recommendation |
|-------|-----------|----------------|
| 0 to 30 | LOW | Content appears authentic |
| 31 to 60 | MEDIUM | Manual review recommended |
| 61 to 85 | HIGH | Strong manipulation indicators — escalate |
| 86 to 100 | CRITICAL | High confidence AI generation detected |

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|-----------|---------|---------|
| Next.js | 14.2 | React framework, App Router, API proxy |
| Tailwind CSS | 3.4 | Utility-first styling, cyberpunk theme |
| Framer Motion | 11.2 | Page animations, component transitions |
| React Dropzone | 14.2 | Drag-and-drop file upload |
| Axios | 1.7 | HTTP client |

### Backend
| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.111 | Async web framework |
| Uvicorn | 0.30 | ASGI server |
| Celery | 5.4 | Distributed task queue |
| Redis | 5.0 | Message broker |

### AI and Forensics
| Technology | Version | Purpose |
|-----------|---------|---------|
| PyTorch | 2.1 | Deep learning framework |
| timm | 1.0 | EfficientNet-B4 pretrained models |
| OpenCV | 4.10 | Image processing, ELA computation |
| Librosa | 0.10 | Mel spectrogram generation |
| Scikit-learn | 1.5 | Platt Scaling calibration |
| ExifRead | 3.0 | EXIF metadata extraction |
| PyMuPDF | 1.24 | PDF to image conversion |
| Pytesseract | 0.3 | OCR text extraction |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| MongoDB Atlas | Analysis results, job status (flexible schema) |
| Neon PostgreSQL | User accounts, cases (ACID compliance) |
| Upstash Redis | Task queue, result caching |
| MinIO | S3-compatible file storage |
| Docker Compose | Local development orchestration |
| Vercel | Frontend CDN deployment |
| Render | Backend Python hosting |

---

## Project Structure

```
astrashield/
│
├── frontend/                       Next.js 14 website
│   ├── app/
│   │   ├── layout.tsx              Root layout with sidebar
│   │   ├── globals.css             Cyberpunk theme and animations
│   │   ├── dashboard/page.tsx      Analytics dashboard
│   │   ├── upload/page.tsx         File upload and live progress
│   │   ├── report/[jobId]/page.tsx Detailed fraud report
│   │   ├── reports/page.tsx        Analysis history
│   │   ├── activity/page.tsx       Live feed (5 second refresh)
│   │   ├── components/
│   │   │   ├── Sidebar.tsx         Navigation sidebar
│   │   │   └── FraudMeter.tsx      SVG circular gauge
│   │   └── lib/
│   │       └── api.ts              Centralized API client
│   ├── next.config.js              API proxy rewrites (CORS fix)
│   └── tailwind.config.js          Custom colors, fonts, animations
│
├── backend/                        Python FastAPI server
│   ├── main.py                     App entry point, CORS setup
│   ├── database.py                 PostgreSQL and MongoDB connections
│   ├── models.py                   SQLAlchemy table definitions
│   ├── api/
│   │   ├── upload.py               POST /api/upload/
│   │   ├── analyze.py              GET /api/analyze/status/{id}
│   │   ├── report.py               GET /api/report/list and /{id}
│   │   └── auth.py                 JWT authentication
│   ├── workers/
│   │   ├── image_worker.py         ELA and metadata and AI scoring
│   │   ├── audio_worker.py         Spectrogram and voice clone
│   │   └── document_worker.py      Noise and OCR and ELA
│   ├── scoring/
│   │   └── ensemble.py             Weighted ensemble and Platt Scaling
│   └── utils/
│       ├── ela.py                  Error Level Analysis
│       ├── metadata.py             EXIF forensics
│       ├── file_validator.py       MIME type detection
│       └── storage.py              MinIO and local storage
│
├── models/
│   ├── image/train.py              EfficientNet-B4 training script
│   └── audio/train.py              ResNet-18 spectrogram training
│
├── scripts/
│   ├── generate_demo_data.py       Populate MongoDB with demo analyses
│   ├── init_db.py                  Create PostgreSQL tables
│   └── quickstart.py               Setup checker and instructions
│
├── docker/
│   ├── Dockerfile.backend          Python container
│   └── Dockerfile.frontend         Next.js container (3-stage build)
│
├── docker-compose.yml              Full local stack orchestration
├── render.yaml                     Render deployment config
└── .gitignore                      Excludes .env, node_modules, etc.
```

---

## Quick Start

### Prerequisites
- Python 3.11 — https://www.python.org/downloads/release/python-3119/
- Node.js 20 LTS — https://nodejs.org
- Docker Desktop — https://www.docker.com/products/docker-desktop/

### 1. Clone the repository
```bash
git clone https://github.com/Rohankumar2201/astrashield.git
cd astrashield
```

### 2. Start all databases with Docker
```bash
docker compose up postgres mongo redis minio -d
```

First run downloads database images (around 500MB). Subsequent starts are instant.

### 3. Set up backend
```bash
cd backend
pip install -r requirements.txt
copy .env.example .env
```

### 4. Start the API server
```bash
# Windows
py -3.11 -m uvicorn main:app --reload --port 8000

# Mac/Linux
uvicorn main:app --reload --port 8000
```

### 5. Start the frontend
```bash
cd ../frontend
npm install
npm run dev
```

### 6. Generate demo data
```bash
cd ../backend
py -3.11 ../scripts/generate_demo_data.py
```

### 7. Open in browser
```
http://localhost:3000        Website
http://localhost:8000/docs   API Documentation
```

---

## API Reference

Base URL: `https://astrashield.onrender.com`

| Method | Endpoint | Description |
|--------|---------|-------------|
| POST | /api/upload/ | Upload file for analysis, returns job_id |
| GET | /api/analyze/status/{job_id} | Poll analysis progress (0 to 100 percent) |
| GET | /api/analyze/result/{job_id} | Get full report when completed |
| GET | /api/report/list | List all past analyses |
| GET | /api/report/{job_id} | Get single report |
| GET | /api/report/stats/summary | Dashboard statistics |
| DELETE | /api/report/{job_id} | Delete a report |
| POST | /api/auth/register | Create analyst account |
| POST | /api/auth/login | Login and returns JWT token |

### Example: Upload a file
```bash
curl -X POST https://astrashield.onrender.com/api/upload/ \
  -F "file=@photo.jpg" \
  -F "notes=Test upload"
```

### Example response
```json
{
  "job_id": "astra_a4f9b2c1",
  "filename": "photo.jpg",
  "file_type": "image",
  "status": "queued",
  "message": "File uploaded successfully. Analysis starting..."
}
```

Full interactive docs at: https://astrashield.onrender.com/docs

---

## Deployment

| Service | Provider | Cost |
|---------|---------|------|
| Frontend | Vercel | Free |
| Backend | Render | Free (sleeps after 15 min inactivity) |
| MongoDB | MongoDB Atlas M0 | Free (512MB) |
| Redis | Upstash | Free (10k commands/day) |
| PostgreSQL | Neon | Free (0.5GB) |

### Deploy Your Own

**Frontend on Vercel:**
1. Fork this repo
2. Import to vercel.com
3. Set Root Directory to frontend
4. Add env variable: NEXT_PUBLIC_API_URL = your Render URL
5. Deploy

**Backend on Render:**
1. New Web Service, connect GitHub repo
2. Root Directory: backend
3. Build Command: pip install -r requirements.txt
4. Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
5. Add all environment variables from .env.example
6. Deploy

---

## Use Cases

- **Banks and Fintech** — KYC verification, synthetic identity fraud detection
- **Law Enforcement** — Digital evidence authentication
- **Social Media Platforms** — Automated deepfake content moderation
- **Government Agencies** — Document verification for applications
- **Healthcare** — Patient identity verification
- **HR and Recruitment** — Video interview and credential verification

---

## Roadmap

- [x] Multi-modal detection (images, audio, documents)
- [x] Weighted ensemble scoring with Platt Scaling
- [x] Real-time progress tracking
- [x] Full REST API with interactive documentation
- [x] Cloud deployment (Vercel + Render + MongoDB Atlas)
- [ ] Real-time video deepfake detection via WebSocket streaming
- [ ] Chrome extension for inline social media detection
- [ ] Enterprise API with SLA tiers and webhooks
- [ ] Blockchain-based authenticity certificates
- [ ] Fine-tuned models with latest 2024+ deepfake datasets

---

## Contributing

Contributions are welcome! See CONTRIBUTING.md for guidelines.

```bash
# Fork the repo, then:
git checkout -b feature/amazing-feature
git commit -m "Add amazing feature"
git push origin feature/amazing-feature
# Open a Pull Request
```

---

## License

This project is licensed under the MIT License. See LICENSE for details.

---

## Author

<div align="center">

**Rohan Kumar**
*First Year Engineering Student*

[![GitHub](https://img.shields.io/badge/GitHub-Rohankumar2201-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Rohankumar2201)
[![Live Project](https://img.shields.io/badge/Live_Demo-AstraShield-0d9488?style=for-the-badge&logo=vercel&logoColor=white)](https://astrashield-rho.vercel.app)

</div>

---

<div align="center">

**If AstraShield helped you, please star the repo!**


</div>