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
| **Database** | MongoDB Atlas (PyMongo) |
| **Authentication** | JWT (python-jose), bcrypt |
| **Image Processing** | OpenCV, Pillow, NumPy |
| **AI / Damage Model** | YOLO — Roboflow Inference API |
| **OCR / Container No** | EasyOCR |
| **Data Validation** | Pydantic v2 |
| **Frontend** | React 18, Vite |
| **CI/CD** | GitHub Actions |

---

## Features

- **AI-Powered Damage Analysis** — Upload up to 6 JPG/PNG/WebP images; run a YOLO model to detect dents, rust, and holes
- **Bounding Box Visualization** — Detected damages are drawn on the image with red boxes and confidence score labels
- **OCR Container Number Detection** — EasyOCR reads the ISO 6346 container number from the image
- **Company Identification** — Automatically resolves the company name from the BIC code lookup table
- **Container Registration** — Add containers with internationally standardized number format (e.g. `MSCU1234567`) and BIC validation
- **Container List & Filtering** — Filter records by number, cargo type, company, port, and date range
- **Inline Delete Confirmation** — A confirmation step appears in-place when the delete button is clicked (no browser popup)
- **JWT Authentication** — Secure registration, login, and session management with TTL-based token invalidation
- **Automated Testing** — GitHub Actions runs 38 tests on every push (21 unit + 17 integration)

---

## Folder Structure

```
Container-Damage-Detection/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD
├── backend/
│   ├── main.py                  # FastAPI entry point, lifespan
│   ├── auth/
│   │   ├── router.py            # Authentication endpoints
│   │   ├── schema.py            # Pydantic schemas
│   │   └── service.py           # User registration / login logic
│   ├── containers/
│   │   ├── router.py            # Container CRUD + BIC map endpoints
│   │   ├── schema.py
│   │   └── service.py
│   ├── ocr/
│   │   └── service.py           # EasyOCR container number detection
│   ├── yolo_model/
│   │   └── service.py           # Roboflow API integration, bbox drawing
│   ├── core/
│   │   ├── bic_table.py         # BIC code → company name lookup table
│   │   ├── database.py          # MongoDB connection, collections, init_db()
│   │   ├── dependencies.py      # FastAPI dependency injection
│   │   └── security.py          # JWT operations
│   └── tests/
│       ├── test_bic.py          # BIC table unit tests
│       ├── test_schema.py       # Pydantic schema unit tests
│       └── test_integration.py  # Auth + container integration tests
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── api.js               # API request layer
│       ├── App.jsx
│       └── components/          # React components
├── .env                         # Environment variables (not committed)
└── requirements.txt             # Pinned Python dependencies
```

---

## Setup & Running

### Prerequisites

- Python 3.12+
- Node.js 18+
- [MongoDB Atlas](https://www.mongodb.com/atlas) account
- [Roboflow](https://roboflow.com) account (for YOLO damage model API key)

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
MONGODB_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/
DB_NAME=port_konteyner
SECRET_KEY=a_long_random_secret_key

# Roboflow — YOLO damage detection
RF_API_KEY=your_roboflow_api_key
RF_MODEL_ID=container-damage-ithvn/1
RF_SERVER=https://detect.roboflow.com
```

> The `.env` file is listed in `.gitignore` — never commit it to the repository.  
> If `SECRET_KEY` is missing, the server will refuse to start.

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

### 5. Run Tests

```bash
cd backend

# Unit tests (no DB needed, fast)
../.venv/bin/pytest tests/test_bic.py tests/test_schema.py -v

# Integration tests (requires live MongoDB Atlas connection)
../.venv/bin/pytest tests/test_integration.py -v

# All tests
../.venv/bin/pytest tests/ -v
```

---

## API Overview

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register a new user | — |
| POST | `/api/v1/auth/login` | Login → returns JWT token | — |
| POST | `/api/v1/auth/logout` | Invalidate token | ✓ |
| GET | `/api/v1/auth/me` | Current user info | ✓ |
| DELETE | `/api/v1/auth/me` | Delete account | ✓ |
| GET | `/api/v1/auth/check-username/{username}` | Check username availability | — |

### Containers

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/containers/list` | Filtered container list | ✓ |
| POST | `/api/v1/containers/register` | Add container (with BIC validation) | ✓ |
| DELETE | `/api/v1/containers/{no}` | Delete container | ✓ |
| POST | `/api/v1/containers/analyze` | YOLO damage + EasyOCR analysis | ✓ |
| GET | `/api/v1/containers/bic-map` | BIC code → company name table | ✓ |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |

---

## CI/CD

GitHub Actions runs two jobs on every push to `main`:

- **Backend** — `pip install`, `pytest` (38 tests: 21 unit + 17 integration)
- **Frontend** — `npm ci`, `npm run build`

Required GitHub Secrets: `MONGODB_URI`, `RF_API_KEY`

---

## License

This project is licensed under the MIT License.
