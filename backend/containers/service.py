import uuid
from datetime import datetime, timezone
from containers.schema import ContainerData
from core.database import containers_col


def save_container(container: ContainerData, registered_by: str, registered_by_id: str) -> dict:
    record = container.model_dump()
    record["container_id"]  = str(uuid.uuid4())
    record["registered_by"] = registered_by
    record["registered_by_id"] = registered_by_id
    record["created_at"]  = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    try:
        containers_col.insert_one(record)
    except Exception:
        raise ValueError("Bu konteyner numarası zaten kayıtlı.")
    record.pop("_id", None)
    return record

def get_all_containers(
    registered_by_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 10,
    container_no: str | None = None,
    container_type: str | None = None,
    company_name: str | None = None,
) -> list[dict]:
    query: dict = {}
    if registered_by_id is not None:
        query["registered_by_id"] = registered_by_id

    date_filter: dict = {}
    if date_from:
        date_filter["$gte"] = date_from
    if date_to:
        date_filter["$lte"] = date_to
    if date_filter:
        query["created_at"] = date_filter

    if container_no:
        query["container_no"] = {"$regex": container_no.upper(), "$options": "i"}
    if container_type:
        query["container_type"] = container_type
    if company_name:
        query["company_name"] = {"$regex": company_name.upper(), "$options": "i"}

    cursor = containers_col.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return list(cursor)


def delete_container(container_no: str, registered_by_id: str | None = None) -> bool:
    query = {"container_no": container_no}
    if registered_by_id is not None:
        query["registered_by_id"] = registered_by_id
    result = containers_col.delete_one(query)
    return result.deleted_count == 1
