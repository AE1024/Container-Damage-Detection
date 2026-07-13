from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.router import router as auth_router
from containers.router import router as containers_router

app = FastAPI(title="Port Konteyner Takip API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(containers_router)


@app.get("/")
def read_root():
    return {"status": "online", "message": "Port Konteyner API aktif."}
