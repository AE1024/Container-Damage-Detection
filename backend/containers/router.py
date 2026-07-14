from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from containers.schema import ContainerData
from containers.service import save_container, get_all_containers, delete_container
from core.dependencies import get_current_user

router = APIRouter(prefix="/containers", tags=["Containers"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}


@router.post("/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Sadece JPG/PNG/WebP dosyaları kabul edilir.")

    from yolo_model.service import predict
    image_bytes = await file.read()
    result = predict(image_bytes)
    return result


@router.post("/register")
def register_container(
    container: ContainerData,
    current_user: dict = Depends(get_current_user),
):
    record = save_container(container, registered_by=current_user["full_name"])
    return {"status": "success", "data": record}


@router.get("/list")
def list_containers(current_user: dict = Depends(get_current_user)):
    containers = get_all_containers()
    return {"total": len(containers), "containers": containers}


@router.delete("/{container_no}")
def remove_container(
    container_no: str,
    current_user: dict = Depends(get_current_user),
):
    deleted = delete_container(container_no.upper())
    if not deleted:
        raise HTTPException(status_code=404, detail="Konteyner bulunamadı.")
    return {"status": "deleted", "container_no": container_no.upper()}
