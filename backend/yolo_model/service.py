import os
import io
import base64
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

_model: YOLO | None = None

_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "model", "best.pt")
MODEL_PATH = os.getenv("MODEL_PATH", _DEFAULT_PATH)


def load_model() -> None:
    global _model
    _model = YOLO(os.path.normpath(MODEL_PATH))


def _encode_image(bgr_array: np.ndarray) -> str:
    """BGR numpy array → base64 PNG string."""
    _, buf = cv2.imencode(".png", bgr_array)
    return base64.b64encode(buf).decode("utf-8")


def predict(image_bytes: bytes) -> dict:
    if _model is None:
        raise RuntimeError("Model henüz yüklenmedi.")

    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    results = _model.predict(image, verbose=False)[0]

    # result.plot() → BGR numpy array (bounding box + etiketler çizili)
    annotated_bgr = results.plot()
    annotated_b64 = _encode_image(annotated_bgr)

    detections = []
    for box in results.boxes:
        detections.append({
            "class":      results.names[int(box.cls)],
            "confidence": round(float(box.conf), 4),
            "bbox":  [round(float(x), 1) for x in box.xyxy[0].tolist()],
        })

    if detections:
        best = max(detections, key=lambda d: d["confidence"])
        return {
            "hasar_var":      True,
            "hasar":          best["class"].capitalize(),
            "skor":           f"{int(best['confidence'] * 100)}%",
            "tespit_sayisi":  len(detections),
            "detections":     detections,
            "annotated_img":  annotated_b64,
        }

    return {
        "hasar_var":      False,
        "hasar":          "Hasar tespit edilmedi",
        "skor":           "—",
        "tespit_sayisi":  0,
        "detections":     [],
        "annotated_img":  annotated_b64,
    }
