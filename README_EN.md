# ContainerGuard — Port Container Tracking System

**AI-powered container damage detection and port operations management platform**

---

## Purpose

ContainerGuard is a web application that enables port operators to systematically record container information and automatically detect container damage **(dents, rust, holes)** through AI-powered image analysis.

The system combines user authentication, container registration/listing, and AI-based damage + number analysis in a single interface.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, FastAPI, Uvicorn |
| **Database** | MongoDB (PyMongo) |
| **Authentication** | JWT (python-jose), bcrypt |
| **Image Processing** | OpenCV, Pillow, NumPy |
| **AI / Damage Model** | YOLO — Roboflow Inference API |
| **LLM / Container OCR** | Groq API — `qwen/qwen3.6-27b` (vision) + `llama-3.3-70b-versatile` (judge) |
| **Data Validation** | Pydantic v2 |
| **Frontend** | React 18, Vite |

---

## Features

- **AI-Powered Damage Analysis** — Upload up to 6 JPG/PNG/WebP images; run a YOLO model to detect dents, rust, and holes
- **Bounding Box Visualization** — Detected damages are drawn on the image with red boxes and confidence score labels
- **LLM Container Number Detection** — Groq vision model (`qwen/qwen3.6-27b`) reads the ISO 6346 container number from the image; `llama-3.3-70b-versatile` validates the format
- **Company Identification** — Automatically resolves the company name from the BIC code lookup table
- **Container Registration** — Add containers using internationally standardized number format (e.g. `MSCU1234567`)
- **Container List & Filtering** — Filter records by number, cargo type, company, and date range
- **JWT Authentication** — Secure registration, login, and session management

---

## Folder Structure

```
Container-Damage-Detection/
├── backend/
│   ├── main.py                  # FastAPI application entry point
│   ├── auth/
│   │   ├── router.py            # Authentication endpoints
│   │   ├── schema.py            # Pydantic schemas
│   │   └── service.py           # User registration / login logic
│   ├── containers/
│   │   ├── router.py            # Container CRUD endpoints
│   │   ├── schema.py
│   │   └── service.py
│   ├── yolo_model/
│   │   └── service.py           # Roboflow API integration, bbox drawing
│   ├── llm/
│   │   ├── service.py           # Groq vision + judge calls
│   │   └── bic_table.py         # BIC code → company name lookup table
│   └── core/
│       ├── database.py          # MongoDB connection and collections
│       ├── dependencies.py      # FastAPI dependency injection
│       └── security.py          # JWT operations
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   └── src/                     # React components
├── .env                         # Environment variables (not committed)
└── requirements.txt             # Python dependencies
```

---

## Setup & Running

### Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB (local install or [MongoDB Atlas](https://www.mongodb.com/atlas))
- [Roboflow](https://roboflow.com) account (for YOLO damage model API key)
- [Groq](https://console.groq.com) account (for LLM container number detection)

---

### 1. Clone the Repository

```bash
git clone https://github.com/AE1024/Container-Damage-Detection.git
cd Container-Damage-Detection
```

---

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URI=mongodb://localhost:27017
DB_NAME=port_konteyner
SECRET_KEY=your_secret_key_here

# Roboflow — YOLO damage detection
RF_API_KEY=your_roboflow_api_key
RF_MODEL_ID=container-damage-ithvn/1
RF_SERVER=https://detect.roboflow.com

# Groq — LLM container number / company detection
GROQ_API_KEY=your_groq_api_key
```

> The `.env` file is listed in `.gitignore` — never commit it to the repository.

---

### 3. Backend — Install & Run

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

cd backend
uvicorn main:app --reload --port 8000
```

Verify it's running:

```
http://localhost:8000/health
```

---

### 4. Frontend — Install & Run

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at:

```
http://localhost:5173
```

---

## LLM Pipeline

During image analysis, the Groq LLM pipeline runs in parallel with YOLO damage detection:

1. **Vision** — `qwen/qwen3.6-27b` reads the ISO 6346 container number from the image
2. **Judge** — `llama-3.3-70b-versatile` verifies that the extracted string is a valid container code
3. **BIC Lookup** — If a valid number is found, the first 4 letters are matched against the BIC table to return the company name

---

## API Overview

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/register` | Register a new user | — |
| POST | `/api/v1/login` | Login → returns JWT token | — |
| POST | `/api/v1/logout` | Invalidate token | ✓ |
| GET | `/api/v1/me` | Current user info | ✓ |
| GET | `/api/v1/containers/list` | List containers | ✓ |
| POST | `/api/v1/containers/register` | Add container | ✓ |
| DELETE | `/api/v1/containers/{no}` | Delete container | ✓ |
| POST | `/api/v1/containers/analyze` | YOLO damage + LLM number analysis | ✓ |
| GET | `/health` | System health check | — |

---

## License

This project is licensed under the MIT License.
