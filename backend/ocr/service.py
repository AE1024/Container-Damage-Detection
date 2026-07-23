import os
import io
import re
import pathlib
import threading
import numpy as np
import cv2
from PIL import Image, ImageEnhance
from dotenv import load_dotenv
import easyocr
from inference_sdk import InferenceHTTPClient

from core.bic_table import BIC_COMPANY_MAP

_ENV_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

RF_API_KEY       = os.getenv("RF_API_KEY", "")
_SERVERLESS_URL  = os.getenv("RF_SERVERLESS_URL", "https://serverless.roboflow.com")
_SERIAL_MODEL_ID = os.getenv("RF_SERIAL_MODEL_ID", "container-serials/1")

_SERIAL_CLASSES = {
    "container_number", "container_number_h", "container_number_v",
    "container-number", "Container-number",
}
_CONTAINER_PATTERN = re.compile(r"^[A-Z]{4}\d{7}$")

_serial_client = None
_reader = None
_reader_lock = threading.Lock()


def _get_serial_client() -> InferenceHTTPClient:
    global _serial_client
    if _serial_client is None:
        _serial_client = InferenceHTTPClient(
            api_url=_SERVERLESS_URL,
            api_key=RF_API_KEY,
        )
    return _serial_client


def _get_reader():
    global _reader
    if _reader is None:
        with _reader_lock:
            if _reader is None:
                print("[OCR] EasyOCR reader başlatılıyor...")
                _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def preload_reader():
    """Startup'ta modeli önceden yükle (paralel çağrılarda race condition önler)."""
    _get_reader()


def _detect_serial_bbox(img_bytes: bytes) -> dict | None:
    arr = np.frombuffer(img_bytes, np.uint8)
    img_np = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    try:
        client = _get_serial_client()
        result = client.infer(img_np, model_id=_SERIAL_MODEL_ID)
        predictions = result.get("predictions", [])
    except Exception as e:
        print(f"[OCR] Roboflow serial detect hata: {e}")
        return None

    candidates = [p for p in predictions if p.get("class") in _SERIAL_CLASSES]
    if not candidates:
        print("[OCR] Konteyner numarası bbox bulunamadı.")
        return None
    return max(candidates, key=lambda p: p.get("confidence", 0))


def _crop_and_enhance(img_bytes: bytes, pred: dict, padding: int = 12) -> bytes:
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
    x0 = max(0, int(x - w / 2) - padding)
    y0 = max(0, int(y - h / 2) - padding)
    x1 = min(img.width,  int(x + w / 2) + padding)
    y1 = min(img.height, int(y + h / 2) + padding)
    crop = img.crop((x0, y0, x1, y1))

    scale = max(1, int(200 / crop.height))
    if scale > 1:
        crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
    crop = ImageEnhance.Contrast(crop).enhance(2.0)

    buf = io.BytesIO()
    crop.save(buf, format="PNG")
    return buf.getvalue()


def _clean_container_no(raw: str) -> str | None:
    cleaned = re.sub(r"[^A-Z0-9]", "", raw.upper())
    if len(cleaned) < 11:
        return None
    letters = cleaned[:4].replace("0", "O").replace("1", "I")
    digits  = cleaned[4:11].replace("O", "0").replace("I", "1")
    result  = letters + digits
    return result if _CONTAINER_PATTERN.match(result) else None


def extract_container_info(image_bytes: bytes) -> dict:
    """
    Görselden konteyner numarası ve şirket adını çıkarır.
    Dönüş: {"container_no": str | None, "company_name": str | None}
    """
    try:
        pred = _detect_serial_bbox(image_bytes)
        if pred is None:
            return {"container_no": None, "company_name": None}

        cropped_bytes = _crop_and_enhance(image_bytes, pred)

        reader = _get_reader()
        results = reader.readtext(cropped_bytes, detail=0, paragraph=False)
        raw_text = " ".join(results)
        print(f"[OCR] EasyOCR çıktı: '{raw_text}'")

        container_no = _clean_container_no(raw_text)
        if container_no is None:
            print(f"[OCR] Geçerli konteyner no elde edilemedi: '{raw_text}'")
            return {"container_no": None, "company_name": None}

        print(f"[OCR] Konteyner no: {container_no}")
        company_name = BIC_COMPANY_MAP.get(container_no[:4])
        return {"container_no": container_no, "company_name": company_name}

    except Exception as e:
        print(f"[OCR] extract_container_info hata: {type(e).__name__}: {e}")
        return {"container_no": None, "company_name": None}
