# ContainerGuard — Port Container Tracking System

**AI-powered container damage detection and port operations management platform**

---

## Purpose

ContainerGuard is a web application that enables port operators to systematically record container information and automatically detect container damage **(dents, rust, holes)** through AI-powered image analysis.

The system combines three core functions in a single interface: user authentication, container registration/listing, and AI-based damage analysis.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, FastAPI, Uvicorn |
| **Database** | MongoDB (PyMongo) |
| **Authentication** | JWT (python-jose), bcrypt |
| **Image Processing** | OpenCV, Pillow, NumPy |
| **AI / Damage Model** | YOLO — Roboflow Inference API |
| **Data Validation** | Pydantic v2 |
| **Frontend** | React 18, Vite |

---

## Features

- **AI-Powered Damage Analysis** — Upload up to 6 JPG/PNG/WebP images; run a YOLO model to detect dents, rust, and holes
- **Bounding Box Visualization** — Detected damages are drawn on the image with red boxes and confidence score labels
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
- [Roboflow](https://roboflow.com) account (for API key)

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

RF_API_KEY=your_roboflow_api_key
RF_MODEL_ID=container-damage-ithvn/1
RF_SERVER=https://detect.roboflow.com
```

> The `.env` file is listed in `.gitignore` — never commit it to the repository.

---

### 3. Backend — Install & Run

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS / Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend
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

## API Overview

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/register` | Register a new user | — |
| POST | `/api/v1/login` | Login → returns JWT token | — |
| POST | `/api/v1/logout` | Invalidate token | ✓ |
| GET | `/api/v1/me` | Current user info | ✓ |
| GET | `/api/v1/containers` | List containers | ✓ |
| POST | `/api/v1/containers` | Add container | ✓ |
| DELETE | `/api/v1/containers/{id}` | Delete container | ✓ |
| POST | `/api/v1/analyze` | AI damage analysis | ✓ |
| GET | `/health` | System health check | — |

---

## License

This project is licensed under the MIT License.
