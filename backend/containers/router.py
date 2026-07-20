from typing import List, Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException
from yolo_model.service import AnalysisService
from containers.schema import ContainerData
from containers.service import save_container, get_all_containers, delete_container
from core.dependencies import get_current_user
import asyncio

router = APIRouter(prefix="/containers", tags=["Containers"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
MAX_FILES  = 6
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/analyze")
async def analyze_image(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
):
    if len(files) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"En fazla {MAX_FILES} resim yüklenebilir.")

    image_bytes_list = []
    for f in files:
        if f.content_type not in ALLOWED_TYPES:
            raise HTTPException(status_code=400, detail=f"{f.filename}: Sadece JPG/PNG/WebP dosyaları kabul edilir.")
        data = await f.read()
        if len(data) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"{f.filename}: Dosya boyutu 20 MB sınırını aşıyor ({len(data) // (1024*1024)} MB).",
            )
        image_bytes_list.append(data)

    loop = asyncio.get_event_loop()
    try:
        results = await loop.run_in_executor(None, AnalysisService.predict_batch, image_bytes_list)
    except RuntimeError as e:
        if str(e) == "402":
            raise HTTPException(status_code=402, detail="Roboflow API kotası doldu. Hesabınızı kontrol edin.")
        if str(e) == "429":
            raise HTTPException(status_code=429, detail="Çok fazla istek. Lütfen bekleyin.")
        raise HTTPException(status_code=500, detail=str(e))
    return {"results": results, "count": len(results)}


@router.post("/register", status_code=201)
def register_container(
    container: ContainerData,
    current_user: dict = Depends(get_current_user),
):
    try:
        record = save_container(
            container,
            registered_by=current_user["full_name"],
            registered_by_id=current_user["sub"],
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"status": "success", "data": record}


@router.get("/list")
def list_containers(
    current_user: dict = Depends(get_current_user),
    date_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    limit: int = Query(10, ge=1, le=100),
    container_no: Optional[str] = Query(None, description="Konteyner numarası (kısmi arama)"),
    container_type: Optional[str] = Query(None, description="Konteyner tipi (tam eşleşme)"),
    company_name: Optional[str] = Query(None, description="Şirket adı (kısmi arama)"),
):
    owner_id = None if current_user.get("role") == "admin" else current_user["sub"]
    containers = get_all_containers(
        registered_by_id=owner_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        container_no=container_no,
        container_type=container_type,
        company_name=company_name,
    )
    return {"total": len(containers), "containers": containers}


@router.delete("/{container_no}")
def remove_container(
    container_no: str,
    current_user: dict = Depends(get_current_user),
):
    owner_id = None if current_user.get("role") == "admin" else current_user["sub"]
    deleted = delete_container(container_no.upper(), registered_by_id=owner_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Konteyner bulunamadı veya size ait değil.")
    return {"status": "deleted", "container_no": container_no.upper()}
