from fastapi import FastAPI
import PIL.Image as Image
import numpy as np
from fastapi import FastAPI, UploadFile, File
from ultralytics import YOLO
import io
app = FastAPI()
model = YOLO("best/best.pt")


@app.get("/")
def read_root():
    return 0

@app.post("/containers/register")
def register_container():
    # Kayıt işlemleri
    pass

@app.post("/containers/predict")
def predict(image: UploadFile = File(...)):
    # Read the image file
    image_data = image.file.read()
    # Convert to PIL Image
    pil_image = Image.open(io.BytesIO(image_data))
    # Run prediction
    result = model(pil_image)
    return result