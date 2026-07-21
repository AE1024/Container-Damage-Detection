import os
import io
import base64
import pathlib
from typing import List

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw
from dotenv import load_dotenv

# .env proje kökünde — backend/yolo_model/ içinden iki üst klasör
_ENV_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_ENV_PATH)

RF_API_KEY  = os.getenv("RF_API_KEY", "")
RF_MODEL_ID = os.getenv("RF_MODEL_ID", "")
RF_SERVER   = os.getenv("RF_SERVER", "https://detect.roboflow.com")

CLASS_CONF: dict[str, float] = {
    "dent": float(os.getenv("RF_CONF_DENT", "0.30")),
    "rust": float(os.getenv("RF_CONF_RUST", "0.20")),
    "hole": float(os.getenv("RF_CONF_HOLE", "0.40")),
}
DEFAULT_CONF = float(os.getenv("RF_CONF", "0.35"))  # tanımsız sınıflar için

_BLUR_LEVELS = [
    (80,  0.55),  
    (200, 0.75),   
    (400, 0.90),   
]

_api_ready: bool = False


def _blur_multiplier(img_bytes: bytes) -> float:
    arr = np.frombuffer(img_bytes, np.uint8)
    gray = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        return 1.0
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    for threshold, multiplier in _BLUR_LEVELS:
        if score < threshold:
            return multiplier
    return 1.0


def _effective_conf(class_name: str, multiplier: float) -> float:
    base = CLASS_CONF.get(class_name.lower(), DEFAULT_CONF)
    return max(base * multiplier, 0.08)


def load_model() -> None:
    global _api_ready
    if not RF_API_KEY:
        raise RuntimeError("RF_API_KEY .env dosyasında tanımlı değil.")
    _api_ready = True


def is_model_loaded() -> bool:
    return _api_ready


def _draw_boxes(image_bytes: bytes, predictions: list) -> str:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    for pred in predictions:
        x, y, w, h = pred["x"], pred["y"], pred["width"], pred["height"]
        x0, y0 = x - w / 2, y - h / 2
        x1, y1 = x + w / 2, y + h / 2
        label = f"{pred['class']} {int(pred['confidence'] * 100)}%"
        draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
        draw.rectangle([x0, y0 - 18, x0 + len(label) * 7, y0], fill="red")
        draw.text((x0 + 2, y0 - 16), label, fill="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _predict_single(img_bytes: bytes) -> dict:
    multiplier = _blur_multiplier(img_bytes)

    img_b64 = base64.b64encode(img_bytes).decode("utf-8")
    url = f"{RF_SERVER}/{RF_MODEL_ID}?api_key={RF_API_KEY}&confidence=0.05"
    try:
        resp = requests.post(url, data=img_b64, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=30)
        if resp.status_code == 402:
            raise RuntimeError("402")
        if resp.status_code == 429:
            raise RuntimeError("429")
        resp.raise_for_status()
        raw = resp.json()
    except RuntimeError:
        raise
    except Exception as e:
        raise

    predictions = [
        p for p in raw.get("predictions", [])
        if p.get("confidence", 0) >= _effective_conf(p.get("class", ""), multiplier)
    ]

    annotated_b64 = _draw_boxes(img_bytes, predictions)

    if not predictions:
        return {
            "hasar_var":  False,
            "hasar":  "Hasar tespit edilmedi",
            "skor": "—",
            "tespit_sayisi": 0,
            "detections":    [],
            "annotated_img": annotated_b64,
        }

    detections = [
        {
            "class":  p["class"],
            "confidence": round(p["confidence"], 4),
            "bbox": [
                round(p["x"] - p["width"]  / 2, 1),
                round(p["y"] - p["height"] / 2, 1),
                round(p["x"] + p["width"]  / 2, 1),
                round(p["y"] + p["height"] / 2, 1),
            ],
        }
        for p in predictions
    ]

    best = max(detections, key=lambda d: d["confidence"])
    class_name = best["class"]
    if class_name.isdigit():
        class_name = "Damage"

    return {
        "hasar_var":   True,
        "hasar":   class_name.capitalize(),
        "skor":   f"{int(best['confidence'] * 100)}%",
        "tespit_sayisi": len(detections),
        "detections":   detections,
        "annotated_img": annotated_b64,
    }


class AnalysisService:
    @staticmethod
    def predict_batch(image_bytes_list: List[bytes]) -> List[dict]:
        if not _api_ready:
            raise RuntimeError("Inference client hazır değil.")
        return [_predict_single(b) for b in image_bytes_list]
