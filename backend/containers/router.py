from fastapi import APIRouter, Depends
from containers.schema import ContainerData
from containers.service import save_container, get_all_containers
from core.dependencies import get_current_user

router = APIRouter(prefix="/containers", tags=["Containers"])


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
