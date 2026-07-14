from datetime import datetime, timezone
from containers.schema import ContainerData
from core.database import containers_col


def save_container(container: ContainerData, registered_by: str) -> dict:
    record = container.model_dump()
    record["registered_by"] = registered_by
    record["created_at"]    = datetime.now(timezone.utc)
    containers_col.insert_one(record)
    record.pop("_id", None)
    return record


def get_all_containers() -> list[dict]:
    return list(containers_col.find({}, {"_id": 0}))


def delete_container(container_no: str) -> bool:
    result = containers_col.delete_one({"container_no": container_no})
    return result.deleted_count == 1


