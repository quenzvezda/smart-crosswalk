import cv2
from ultralytics import YOLO

# Muat model YOLOv8n yang telah dilatih
model = YOLO('yolov8n.pt')  # Pastikan 'yolov8n.pt' ada di direktori yang tepat atau berikan path lengkap

# Baca gambar menggunakan OpenCV
source = cv2.imread('path/to/image.jpg')  # Ganti 'path/to/image.jpg' dengan path ke gambar Anda

# Jalankan inferensi pada gambar
results = model(source)

# results sekarang mengandung list dari objek hasil yang dapat Anda proses lebih lanjut
# Misalnya, menampilkan bounding boxes dan label pada gambar
results.show()
