from ultralytics import YOLO

model = YOLO("model/best.pt")

model.train(
    data="dataset_train/data.yaml",
    epochs=50,
    batch=8,
    imgsz=640,
    lr0=0.0005,
    cos_lr=True,
    freeze=10,
    patience=15,
    optimizer="AdamW",
    device=0,
    project="runs/finetune",
    name="container-damage-v2",
    exist_ok=True,
)
