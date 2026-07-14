from pydantic import BaseModel, Field, field_validator
import re

CONTAINER_TYPES = {
    "Dry":             "Kuru Yük",
    "Reefer":          "Soğutmalı",
    "Open Top":        "Açık Üst",
    "Flat Rack":       "Platform",
    "Tank":            "Tank",
    "Special Purpose": "Özel Amaçlı",
}


class ContainerData(BaseModel):
    container_no:     str = Field(description="4 harf + 7 rakam (örn: MSCU1234567)")
    container_type:   str = Field(description="Konteyner tipi")
    company_name:     str = Field(description="Şirket adı")
    arrive_port:      str = Field(description="Geliş limanı")
    destination_port: str = Field(description="Varış limanı")

    @field_validator("container_no")
    @classmethod
    def check_container_no(cls, v: str) -> str:
        v = v.upper().replace(" ", "")
        if not re.match(r"^[A-Z]{4}\d{7}$", v):
            raise ValueError("Konteyner numarası formatı: 4 harf + 7 rakam (örn: MSCU1234567)")
        return v

    @field_validator("container_type")
    @classmethod
    def check_container_type(cls, v: str) -> str:
        if v not in CONTAINER_TYPES.values():
            raise ValueError(f"Geçerli tipler: {', '.join(CONTAINER_TYPES.values())}")
        return v

    @field_validator("company_name")
    @classmethod
    def check_company_name(cls, v: str) -> str:
        return v.upper()
