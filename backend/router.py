import io
import PIL.Image as Image
from fastapi import APIRouter, UploadFile, File
import ultralytics
from ultralytics import YOLO 
from schemas import ContainerData 

# model = YOLO("model/best/best.pt")

# Tüm route'ların başına otomatik /containers ekler
router = APIRouter(prefix="/containers", tags=["Containers"])

@router.post("/register")
def register_container(container: ContainerData):  
    # Kayıt işlemleri
    return {"status": "success", "data": container}

# @router.post("/predict")
# async def predict(image: UploadFile = File(...)):
#     # 1. Dosyayı asenkron olarak oku
#     image_data = await image.read()
    
#     # 2. PIL Image formatına çevir
#     pil_image = Image.open(io.BytesIO(image_data))
    
#     # 3. Model Tahmini (Ön işlemi YOLO otomatik yapar)
#     #results = model(pil_image)
    
#     # 4. FastAPI'nin döndürebileceği bir sözlük (JSON) yapısı oluştur
#     response_data = {
#         "speed_metrics_ms": {},
#         "detections": []
#     }

#     # 5. Sonuçları ayrıştır
#     #for result in results:
#         #response_data["speed_metrics_ms"] = result.speed
        
#         #for box in result.boxes:
#             detection = {
#                 "class_name": model.names[int(box.cls[0])],
#                 "confidence": round(float(box.conf[0]), 3),
#                 "bbox": box.xyxy[0].tolist()  # Kutunun [x1, y1, x2, y2] koordinatları
#             }
#             response_data["detections"].append(detection)

#     return response_data