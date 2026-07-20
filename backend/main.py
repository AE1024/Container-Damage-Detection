from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from auth.router import router as auth_router
from containers.router import router as containers_router
from yolo_model.service import load_model, is_model_loaded
from core.database import client as mongo_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


app = FastAPI(title="Port Konteyner Takip API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(containers_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"status": "online", "message": "Port Konteyner API aktif.", "db": "MongoDB"}


@app.get("/health")
def health_check():
    try:
        mongo_client.admin.command("ping")
        db_status = "ok"
        db_msg    = "Bağlantı başarılı"
    except Exception as e:
        db_status = "error"
        db_msg    = str(e)

    model_ok  = is_model_loaded()
    model_status = "ok" if model_ok else "error"
    model_msg = "Model yüklü" if model_ok else "Model henüz yüklenmedi"

    overall = "ok" if db_status == "ok" and model_status == "ok" else "degraded"
    return {
        "status": overall,
        "database": {"status": db_status, "message": db_msg},
        "model":  {"status": model_status, "message": model_msg},
    }
