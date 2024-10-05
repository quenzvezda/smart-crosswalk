import cv2
import numpy as np
import tensorflow as tf
from estimator import DistanceEstimator

# Inisialisasi parameter estimasi jarak
focal = 502  # Panjang fokus berdasarkan kalibrasi sebelumnya
real_width = 3.5  # Lebar nyata objek dalam cm

# Inisialisasi object untuk estimator jarak
distance_estimator = DistanceEstimator(focal, real_width)

# Load model SSD dari saved_model
model_path = '../../models/ssd-new-dataset'
model = tf.saved_model.load(model_path)

# Inisialisasi label kelas (sesuaikan dengan model Anda)
class_names = {0: 'background', 1: 'mobil', 2: 'orang'}

# Inisialisasi video capture / webcam
cap = cv2.VideoCapture(0)


def preprocess_image(image):
    """
    Preprocessing untuk SSD MobileNet V2.
    :param image: Frame dari video (BGR)
    :return: Gambar yang di-preprocess (RGB dan scaled)
    """
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)  # Tambahkan dimensi batch
    return img


def run_inference(model, image):
    """
    Menjalankan inferensi pada model SSD.
    :param model: Model SSD yang dimuat dari saved_model
    :param image: Gambar yang telah diproses
    :return: Hasil inferensi (deteksi)
    """
    input_tensor = tf.convert_to_tensor(image, dtype=tf.uint8)
    detections = model(input_tensor)  # Jalankan model
    return detections


while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal mengambil gambar.")
        break

    # Preprocessing gambar
    input_image = preprocess_image(frame)

    # Jalankan deteksi objek menggunakan SSD MobileNet V2
    detections = run_inference(model, input_image)

    # Ekstraksi hasil deteksi
    boxes = detections['detection_boxes'].numpy()[0]  # Bounding boxes
    scores = detections['detection_scores'].numpy()[0]  # Confidence scores
    classes = detections['detection_classes'].numpy()[0].astype(int)  # Class IDs

    height, width, _ = frame.shape

    # Hanya ambil deteksi yang confidence-nya lebih dari 0.5
    for i in range(len(scores)):
        if scores[i] > 0.5:
            class_id = classes[i]
            class_name = class_names.get(class_id, 'Unknown')

            # Konversi box dari normalisasi ke ukuran frame
            y1, x1, y2, x2 = boxes[i]
            x1 = int(x1 * width)
            y1 = int(y1 * height)
            x2 = int(x2 * width)
            y2 = int(y2 * height)

            # Hitung lebar bounding box dalam piksel
            pixel_width = abs(x2 - x1)

            # Estimasi jarak
            estimated_distance = distance_estimator.estimate(pixel_width)

            if estimated_distance:
                # Gambar bounding box di sekitar objek
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Tampilkan kelas dan estimasi jarak di atas bounding box
                label = f'{class_name}: {estimated_distance:.2f} cm'
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Tampilkan hasil di jendela
    cv2.imshow('SSD Object Detection & Distance Estimation', frame)

    # Tekan 'q' untuk keluar dari program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan semua
cap.release()
cv2.destroyAllWindows()
