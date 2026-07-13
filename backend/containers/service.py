# Mockup in-memory depo — DB gelince sadece bu dosya değişir
from containers.schema import ContainerData

_store: list[dict] = []


def save_container(container: ContainerData, registered_by: str) -> dict:
    record = container.model_dump()
    record["registered_by"] = registered_by
    _store.append(record)
    return record


def get_all_containers() -> list[dict]:
    return _store
