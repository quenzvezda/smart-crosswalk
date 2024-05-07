from ultralytics import YOLO

# Ubah lokasi path ke lokasi model .pt Anda
model = YOLO("../models/trisakti-yolov8n.pt")
model.export(format="onnx", imgsz=[640, 640], opset=12)
