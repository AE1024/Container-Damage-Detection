import os
import io
import base64
from typing import List
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


def is_model_loaded() -> bool:
    return _model is not None


def _encode_image(bgr_array: np.ndarray) -> str:
    """BGR numpy array → base64 PNG string."""
    _, buf = cv2.imencode(".png", bgr_array)
    return base64.b64encode(buf).decode("utf-8")

class AnalysisService:
    """Load YOLO model and provide methods for batch image analysis."""
    @staticmethod
    def predict_batch(image_bytes_list: List[bytes]) -> List[dict]:
        """Ana orkestratör metot: Listeyi alır, işler ve formatlı sonucu döner."""
        if _model is None:
            raise RuntimeError("Model henüz yüklenmedi.")

        # 1. HAZIRLIK: Byte listesindeki her elemanı PIL Image formatına çevir
        images = []
        for img_bytes in image_bytes_list:
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            images.append(img)

        # 2. TAHMİN (PREDICTION): YOLO listeleri otomatik olarak batch (toplu) işler!
        raw_results = _model.predict(images, imgsz=640, verbose=False)

        # 3. FORMATLAMA (PROCESSING): Her bir resmin sonucunu kendi JSON formatımıza çevir
        final_responses = []
        for result in raw_results:
            formatted_data = AnalysisService._format_single_result(result)
            final_responses.append(formatted_data)

        return final_responses

    @staticmethod
    def _format_single_result(result) -> dict:
        """YOLO'dan dönen tek bir sonucu alır, dictionary ve base64'e çevirir."""
        # result.plot() → BGR numpy array (bounding box + etiketler çizili)
        annotated_bgr = result.plot()
        annotated_b64 = _encode_image(annotated_bgr)

        detections = []
        for box in result.boxes:
            detections.append({
                "class":      result.names[int(box.cls)],
                "confidence": round(float(box.conf), 4),
                "bbox":       [round(float(x), 1) for x in box.xyxy[0].tolist()],
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