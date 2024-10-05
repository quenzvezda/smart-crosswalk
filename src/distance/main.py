import cv2
from ultralytics import YOLO  # Pastikan YOLOv8 diinstal melalui ultralytics
from estimator import DistanceEstimator

# Inisialisasi parameter estimasi jarak
focal = 502  # Panjang fokus berdasarkan kalibrasi sebelumnya
real_width = 3.5  # Lebar nyata objek dalam cm

# Inisialisasi model YOLOv8
model_path = '../../models/trisakti-yolov8m-roboflow.pt'
model = YOLO(model_path)  # Muat model custom YOLOv8

# Inisialisasi object untuk estimator jarak
distance_estimator = DistanceEstimator(focal, real_width)

# Inisialisasi video capture / webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal mengambil gambar.")
        break

    # Deteksi objek menggunakan YOLOv8
    results = model(frame)

    for result in results:
        for bbox in result.boxes.xyxy:  # Mendapatkan bounding box
            x1, y1, x2, y2 = bbox
            # Hitung / mendapatkan lebar bounding box dalam piksel
            pixel_width = abs(x2 - x1)

            # Estimasi jarak
            estimated_distance = distance_estimator.estimate(pixel_width)

            if estimated_distance:
                # Gambar bounding box di sekitar objek
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                # Tampilkan estimasi jarak di atas bounding box
                cv2.putText(frame, f'{estimated_distance:.2f} cm', (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Tampilkan hasil di jendela
    cv2.imshow('YOLOv8 Object Detection & Distance Estimation', frame)

    # Tekan 'q' untuk keluar dari program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan semua
cap.release()
cv2.destroyAllWindows()
