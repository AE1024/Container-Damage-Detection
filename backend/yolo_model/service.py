import os
import io
import base64
from typing import List

from PIL import Image, ImageDraw
from dotenv import load_dotenv
from inference_sdk import InferenceHTTPClient

load_dotenv()

RF_API_KEY  = os.getenv("RF_API_KEY", "")
RF_MODEL_ID = os.getenv("RF_MODEL_ID", "container-damage-ithvn-dsduq/1")
RF_CONF = float(os.getenv("RF_CONF", "0.25"))
RF_SERVER = os.getenv("RF_SERVER", "http://localhost:9001")

_client: InferenceHTTPClient | None = None
_api_ready: bool = False


def load_model() -> None:
    global _client, _api_ready
    if not RF_API_KEY:
        raise RuntimeError("RF_API_KEY .env dosyasında tanımlı değil.")
    _client = InferenceHTTPClient(
        api_url=RF_SERVER,
        api_key=RF_API_KEY,
    )
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


class AnalysisService:
    @staticmethod
    def predict_batch(image_bytes_list: List[bytes]) -> List[dict]:
        if not _api_ready or _client is None:
            raise RuntimeError("Inference client hazır değil.")
        return [AnalysisService._predict_single(b) for b in image_bytes_list]

    @staticmethod
    def _predict_single(img_bytes: bytes) -> dict:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        try:
            raw = _client.infer(img, model_id=RF_MODEL_ID)
        except Exception as e:
            msg = str(e)
            if "402" in msg:
                raise RuntimeError("402")
            if "429" in msg:
                raise RuntimeError("429")
            raise

        predictions = [
            p for p in raw.get("predictions", [])
            if p.get("confidence", 0) >= RF_CONF
        ]

        annotated_b64 = _draw_boxes(img_bytes, predictions)

        if not predictions:
            return {
                "hasar_var":     False,
                "hasar":         "Hasar tespit edilmedi",
                "skor":          "—",
                "tespit_sayisi": 0,
                "detections":    [],
                "annotated_img": annotated_b64,
            }

        detections = [
            {
                "class":      p["class"],
                "confidence": round(p["confidence"], 4),
                "bbox": [
                    round(p["x"] - p["width"] / 2, 1),
                    round(p["y"] - p["height"] / 2, 1),
                    round(p["x"] + p["width"] / 2, 1),
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
            "hasar_var":     True,
            "hasar":         class_name.capitalize(),
            "skor":          f"{int(best['confidence'] * 100)}%",
            "tespit_sayisi": len(detections),
            "detections":    detections,
            "annotated_img": annotated_b64,
        }
