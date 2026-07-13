from pydantic import BaseModel, Field, field_validator
import re

# Sabitler
CONTAINER_TYPES = {
    "Dry": "Kuru Yük",
    "Reefer": "Soğutmalı",
    "Open Top": "Açık Üst",
    "Flat Rack": "Platform",
    "Tank": "Tank",
    "Special Purpose": "Özel Amaçlı"
}

# Veri Modeli
class ContainerData(BaseModel):
    container_no: str = Field(
        description="4 harf + 7 rakam (örn: MSCU1234567)",
        json_schema_extra={"example": "MSCU1234567"}
    )
    container_type: str = Field(
        description="Konteynerin tipi (örn: Kuru Yük, Soğutmalı)",
        json_schema_extra={"example": "Kuru Yük"}
    )
    company_name: str = Field(
        description="Şirketin ismi",
        json_schema_extra={"example": "MAERSK"}
    )
    arrive_port: str = Field(
        description="Geldiği liman",
        json_schema_extra={"example": "Ambarlı Limanı"}
    )
    destination_port: str = Field(
        description="Gideceği liman",
        json_schema_extra={"example": "Rotterdam Limanı"}
    )
    
# Doğrulamalar (Validators)
    @field_validator("container_no") 
    @classmethod 
    def check_container_no(cls, v) -> str:
        v = v.upper().replace(" ", "") 
        if not re.match(r"^[A-Z]{4}\d{7}$", v):
            raise ValueError("Konteyner numarası bu formatta olmalı : 4 harf + 7 rakam (örn: MSCU1234567)")
        return v

    @field_validator("container_type")
    @classmethod
    def check_container_type(cls, v: str) -> str:
        if v not in CONTAINER_TYPES.values():
            raise ValueError(f"Konteyner tipi geçersiz. Geçerli tipler: {', '.join(CONTAINER_TYPES.values())}")
        return v
    
    @field_validator("company_name")
    @classmethod
    def check_company_name(cls, v: str) -> str:
        return v.upper()