import uuid
from datetime import datetime, timezone
from containers.schema import ContainerData
from core.database import containers_col
from core.bic_table import BIC_COMPANY_MAP

def validate_bic_company(container_no: str, company_name: str) -> bool:
    """Uyumluysa True, uyumsuzsa False döner."""
    code = container_no[:4].upper()
    expected = BIC_COMPANY_MAP.get(code)
    
    if expected is None:
        return True  # Bilinmeyen BIC — geçir
        
    if company_name.upper() not in expected.upper() and expected.upper() not in company_name.upper():
        return False
        
    return True

def _serialize(record: dict) -> dict:
    """MongoDB'den gelen datetime'ı API yanıtı için YYYY-MM-DD string'e çevirir."""
    if isinstance(record.get("created_at"), datetime):
        record["created_at"] = record["created_at"].strftime("%Y-%m-%d")
    return record


def save_container(container: ContainerData, registered_by: str, registered_by_id: str) -> dict:
    now = datetime.now(timezone.utc)
    record = container.model_dump()
    record["container_id"]    = str(uuid.uuid4())
    record["registered_by"]   = registered_by
    record["registered_by_id"] = registered_by_id
    record["created_at"]      = now
    try:
        control = validate_bic_company(container.container_no, container.company_name)
        if not control:
            raise ValueError("BIC kodu ile şirket adı uyuşmuyor.")
    except ValueError as e:
        raise e
    try:
        containers_col.insert_one(record)
    except Exception:
        raise ValueError("Bu konteyner numarası zaten kayıtlı.")
    record.pop("_id", None)
    return _serialize(record)


def get_all_containers(
    registered_by_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 10,
    container_no: str | None = None,
    container_type: str | None = None,
    company_name: str | None = None,
    arrive_port: str | None = None,
    destination_port: str | None = None,
) -> list[dict]:
    query: dict = {}
    if registered_by_id is not None:
        query["registered_by_id"] = registered_by_id

    date_filter: dict = {}
    if date_from:
        date_filter["$gte"] = datetime.strptime(date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    if date_to:
        date_filter["$lte"] = datetime.strptime(date_to, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, tzinfo=timezone.utc
        )
    if date_filter:
        query["created_at"] = date_filter

    if container_no:
        query["container_no"] = {"$regex": container_no.upper(), "$options": "i"}
    if container_type:
        query["container_type"] = container_type
    if company_name:
        query["company_name"] = {"$regex": company_name.upper(), "$options": "i"}
    if arrive_port:
        query["arrive_port"] = arrive_port
    if destination_port:
        query["destination_port"] = destination_port

    cursor = containers_col.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
    return [_serialize(r) for r in cursor]


def delete_container(container_no: str, registered_by_id: str | None = None) -> bool:
    query = {"container_no": container_no}
    if registered_by_id is not None:
        query["registered_by_id"] = registered_by_id
    result = containers_col.delete_one(query)
    return result.deleted_count == 1

def delete_containers_by_user(registered_by_id: str) -> bool:
    result = containers_col.delete_many({"registered_by_id": registered_by_id})
    if result.deleted_count > 0:
        return True
    return False

