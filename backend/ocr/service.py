import os
import io
import pathlib
from typing import cast, Any
import numpy as np
import cv2
from PIL import Image, ImageEnhance
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient

_LANCZOS = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS  # type: ignore[attr-defined]

from core.bic_table import BIC_COMPANY_MAP
from llm.service import extract_bic_code

_ENV_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

_SERIAL_CLASSES = {
    "container_number", "container_number_h", "container_number_v",
    "container-number", "Container-number",
}

_serial_client = None


def _get_serial_client() -> InferenceHTTPClient:
    global _serial_client
    if _serial_client is None:
        _serial_client = InferenceHTTPClient(
            api_url=os.getenv("RF_SERVERLESS_URL", "https://serverless.roboflow.com"),
            api_key=os.getenv("RF_API_KEY", ""),
        )
    return _serial_client


def extract_container_info(image_bytes: bytes) -> dict:
    """
    Akış: Roboflow → bbox tespit → kırp → Qwen vision + tool calling → ISO kodu
    """
    try:
        # 1. Roboflow ile konteyner numarası bölgesini tespit et
        arr = np.frombuffer(image_bytes, np.uint8)
        img_np = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        raw_result = _get_serial_client().infer(
            img_np, model_id=os.getenv("RF_SERIAL_MODEL_ID", "container-serials/1")
        )
        result: dict[str, Any] = cast(dict, raw_result)
        candidates = [
            p for p in result.get("predictions", [])
            if p.get("class") in _SERIAL_CLASSES
        ]
        if not candidates:
            print("[OCR] Konteyner numarası bbox bulunamadı.")
            return {"container_no": None, "company_name": None}

        pred = max(candidates, key=lambda p: p.get("confidence", 0))
        print(f"[OCR] Bbox tespit edildi: class={pred['class']} confidence={pred['confidence']:.2f}")

        # 2. Bbox bölgesini kırp ve iyileştir
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
        padding = 12
        x0 = max(0, int(x - w / 2) - padding)
        y0 = max(0, int(y - h / 2) - padding)
        x1 = min(img.width,  int(x + w / 2) + padding)
        y1 = min(img.height, int(y + h / 2) + padding)
        crop = img.crop((x0, y0, x1, y1))

        scale = max(1, int(200 / crop.height))
        if scale > 1:
            crop = crop.resize((crop.width * scale, crop.height * scale), _LANCZOS)
        crop = ImageEnhance.Contrast(crop).enhance(2.0)

        buf = io.BytesIO()
        crop.save(buf, format="PNG")
        cropped_bytes = buf.getvalue()

        # 3. Qwen vision ile ISO kodunu oku
        container_no = extract_bic_code(cropped_bytes)
        if not container_no:
            print("[OCR] Geçerli ISO kodu bulunamadı.")
            return {"container_no": None, "company_name": None}

        print(f"[OCR] Konteyner no: {container_no}")
        return {"container_no": container_no, "company_name": BIC_COMPANY_MAP.get(container_no[:4])}

    except Exception as e:
        print(f"[OCR] Hata: {type(e).__name__}: {e}")
        return {"container_no": None, "company_name": None}
