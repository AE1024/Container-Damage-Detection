from fastapi import FastAPI
from router import router as containers_router 

app = FastAPI(title="Konteyner Takip API")

# Router'ı ana uygulamaya bağlıyoruz
app.include_router(containers_router)

@app.get("/")
def read_root():
    return {"status": "online", "message": "Konteyner API aktif."}