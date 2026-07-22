import os
import base64
import re
import pathlib
from groq import Groq
from dotenv import load_dotenv

from llm.bic_table import BIC_COMPANY_MAP

_ENV_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CONTAINER_PATTERN = re.compile(r"^[A-Z]{4}\d{7}$")

_VISION_PROMPT = (
    "Sen bir konteyner tanıma asistanısın. "
    "Görselde ISO 6346 formatında konteyner numarası (4 büyük harf + 7 rakam, örn. MSCU1234567) "
    "net okunabiliyorsa SADECE o numarayı yaz, boşluksuz büyük harflerle. "
    "Okunamazsa, görünmüyorsa ya da emin değilsen tam olarak şunu yaz: BULUNAMADI "
    "Başka hiçbir şey yazma."
)

_JUDGE_PROMPT = (
    "ISO 6346 konteyner numarası formatı: 4 büyük Latin harfi + 7 rakam (örn. MSCU1234567, TRKU2035979). "
    "Verilen string bu formata uyuyor mu ve gerçek bir konteyner kodu gibi görünüyor mu? "
    "Sadece TRUE veya FALSE yaz, başka hiçbir şey yazma."
)


def _to_b64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def _vision_call(image_bytes: bytes) -> str | None:
    """Groq vision modeli ile görselden konteyner numarasını okur."""
    print("[LLM] Vision çağrısı başlıyor...")
    resp = groq_client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[
            {"role": "system", "content": _VISION_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{_to_b64(image_bytes)}"
                        },
                    },
                    {"type": "text", "text": "Konteyner numarasını oku."},
                ],
            },
        ],
        max_tokens=512,
    )
    content = resp.choices[0].message.content or ""
    print(f"[LLM] Vision ham yanıt (ham): '{content[:200]}'")
    
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r"<think>.*",          "", content, flags=re.DOTALL | re.IGNORECASE)
    raw = content.strip().upper().replace(" ", "").replace("\n", "")
    print(f"[LLM] Vision temizlenmiş yanıt: '{raw}'")
    if not raw or raw == "BULUNAMADI" or not CONTAINER_PATTERN.match(raw):
        return None
    return raw


def _judge_call(container_no: str) -> bool:
    """Groq text modeli ile numarayı doğrular."""
    resp = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _JUDGE_PROMPT},
            {"role": "user", "content": container_no},
        ],
        max_tokens=5,
    )
    return resp.choices[0].message.content.strip().upper().startswith("TRUE")


def extract_container_info(image_bytes: bytes) -> dict:
    """
    Görselden konteyner numarası ve şirket adını çıkarır.
    Dönüş: {"container_no": str | None, "company_name": str | None}
    """
    try:
        container_no = _vision_call(image_bytes)
        if container_no is None:
            return {"container_no": None, "company_name": None}

        if not _judge_call(container_no):
            return {"container_no": None, "company_name": None}

        company_name = BIC_COMPANY_MAP.get(container_no[:4])
        return {"container_no": container_no, "company_name": company_name}

    except Exception as e:
        print(f"[LLM] extract_container_info hata: {type(e).__name__}: {e}")
        return {"container_no": None, "company_name": None}
